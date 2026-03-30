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
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,  # solo una canción
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    
    duration = info.get('duration', 0)
    minutes = duration // 60
    seconds = duration % 60
    
    return jsonify({
        'title': info.get('title', 'Sin título'),
        'uploader': info.get('uploader', 'Desconocido'),
        'duration': f"{minutes}:{seconds:02d}",
        'thumbnail': info.get('thumbnail'),
    })

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    temp_dir = tempfile.mkdtemp()
    
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'restrictfilenames': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
    
    @after_this_request
    def cleanup(response):
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        return response
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"{info.get('title', 'audio')}.m4a"
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)