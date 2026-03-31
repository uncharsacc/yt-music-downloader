from flask import Flask, render_template, request, send_file, jsonify, after_this_request
import yt_dlp
import os
import tempfile
import shutil

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/info', methods=['POST'])
def get_info():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'No URL'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'socket_timeout': 30,
        'retries': 10,
        # Trucos anti-bot sin cookies
        'extractor_args': {'youtube': {'player_client': ['ios', 'android', 'web_embedded']}},
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        duration = info.get('duration', 0) or 0
        return jsonify({
            'title': info.get('title', 'Sin título'),
            'uploader': info.get('uploader', 'Desconocido'),
            'duration': f"{duration//60}:{duration%60:02d}",
            'thumbnail': info.get('thumbnail'),
            'success': True
        })
    except Exception as e:
        print("Error /info:", str(e))
        return jsonify({'error': 'YouTube bloqueó el servidor. Prueba con cookies o otro link'}), 500

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return "URL inválida", 400

    temp_dir = tempfile.mkdtemp()

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'socket_timeout': 90,
        'retries': 10,
        'extractor_args': {'youtube': {'player_client': ['ios', 'android', 'web_embedded']}},
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'restrictfilenames': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'

        @after_this_request
        def cleanup(response):
            shutil.rmtree(temp_dir, ignore_errors=True)
            return response

        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"{info.get('title', 'audio')}.mp3"
        )
    except Exception as e:
        print("Error /download:", str(e))
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)