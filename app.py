from flask import Flask, request, jsonify, send_from_directory, render_template_string
import subprocess
import os

app = Flask(__name__)

# Diretório para salvar os vídeos gerados
output_dir = "videos"
os.makedirs(output_dir, exist_ok=True)

# Página HTML com o player
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Stream RTSP</title>
    <link href="https://vjs.zencdn.net/7.20.3/video-js.css" rel="stylesheet">
</head>
<body>
    <h1>Stream ao Vivo</h1>
    <video id="my-video" class="video-js" controls preload="auto" width="640" height="360" data-setup="{}">
        <source src="{{ stream_url }}" type="application/x-mpegURL">
    </video>
    <script src="https://vjs.zencdn.net/7.20.3/video.js"></script>
</body>
</html>
"""

@app.route('/')
def index():
    # Define a URL do stream para o player
    stream_url = f"https://porteiro-production.up.railway.app/stream/stream.m3u8"
    return render_template_string(html_template, stream_url=stream_url)

@app.route('/stream/<path:filename>', methods=['GET'])
def serve_stream(filename):
    # Servir os arquivos HLS gerados
    return send_from_directory(output_dir, filename)

@app.route('/receber_dvr', methods=['POST'])
def receber_dvr():
    data = request.json
    rtsp_url = data.get('url')
    if not rtsp_url:
        return jsonify({"error": "URL RTSP não fornecida"}), 400

    # Nome do arquivo HLS
    output_file = os.path.join(output_dir, "stream.m3u8")

    # Comando FFmpeg para transcodificar o stream RTSP para HLS
    command = [
        "ffmpeg",
        "-i", rtsp_url,
        "-hls_time", "2",
        "-hls_list_size", "5",
        "-hls_wrap", "10",
        output_file
    ]

    try:
        # Inicia o processo FFmpeg
        subprocess.Popen(command)
        return jsonify({"message": f"Processando stream RTSP: {rtsp_url}", "output": output_file}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
