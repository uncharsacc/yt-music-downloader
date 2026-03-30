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
        return jsonify({'error': 'No URL provided'}), 400
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'extract_flat': False,
        'ignoreerrors': True,
        # Opciones importantes para servidores
        'socket_timeout': 30,
        'retries': 3,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        if not info:
            return jsonify({'error': 'No se pudo extraer información del video'}), 400
        
        duration = info.get('duration', 0) or 0
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        return jsonify({
            'title': info.get('title', 'Sin título'),
            'uploader': info.get('uploader', 'Desconocido'),
            'duration': f"{minutes}:{seconds:02d}",
            'thumbnail': info.get('thumbnail') or info.get('thumbnails', [{}])[0].get('url'),
            'success': True
        })
    except Exception as e:
        print("Error en /info:", str(e))  # Esto aparecerá en los logs de Render
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return "URL inválida", 400
    
    temp_dir = tempfile.mkdtemp()
    
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'socket_timeout': 60,
        'retries': 5,
        'restrictfilenames': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
        
        if not os.path.exists(file_path):
            return "Error al descargar el archivo", 500
        
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
    except Exception as e:
        print("Error en /download:", str(e))
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)