from flask import Flask, request, jsonify, send_file, render_template_string
import os
from datetime import datetime

app = Flask(__name__)

# Diretório para salvar as imagens
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Página HTML para exibir a imagem
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Imagem da Câmera</title>
    <meta http-equiv="refresh" content="10">
</head>
<body>
    <h1>Imagem da Câmera</h1>
    <img src="/imagem" alt="Imagem da Câmera" style="max-width: 100%; height: auto;">
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Salvar a imagem recebida
        image_data = request.data
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = os.path.join(UPLOAD_FOLDER, f"imagem_{timestamp}.jpeg")
        with open(filename, "wb") as f:
            f.write(image_data)
        return jsonify({"message": "Imagem recebida com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/imagem')
def imagem():
    # Buscar a última imagem salva
    try:
        imagens = sorted(os.listdir(UPLOAD_FOLDER))
        if imagens:
            caminho_imagem = os.path.join(UPLOAD_FOLDER, imagens[-1])
            return send_file(caminho_imagem, mimetype='image/jpeg')
        else:
            return "Nenhuma imagem disponível", 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

