from flask import Flask, request, jsonify
import cv2
import requests
import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from threading import Thread

app = Flask(__name__)

# Diretório para salvar as imagens enviadas via FTP
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Configurações do Telegram e RTSP
RTSP_URL = "rtsp://admin:juss1403@10.0.0.110:554/cam/realmonitor?channel=1&subtype=0"
TELEGRAM_TOKEN = "8062258264:AAHTdhpbkiH7QB7JaNK9keXkhcici2aJGaY"
TELEGRAM_CHAT_ID = "6784880297"  # ID padrão usado em outras rotas
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
DEEP_SEAK_APIP_KEY = "sk-333f1bf2aea14144a87dfd82e751de59"

# Função para capturar imagem via RTSP
def capturar_imagem():
    cap = cv2.VideoCapture(RTSP_URL)
    ret, frame = cap.read()
    cap.release()
    if ret:
        image_path = "frame.jpg"
        cv2.imwrite(image_path, frame)
        return image_path
    return None

# Função para enviar imagem ao Telegram
def enviar_para_telegram(image_path):
    with open(image_path, "rb") as file:
        response = requests.post(
            f"{TELEGRAM_API_URL}/sendPhoto",
            data={"chat_id": TELEGRAM_CHAT_ID},
            files={"photo": file}
        )
    return response.ok

# Função para enviar mensagem ao Telegram
def enviar_mensagem_telegram(chat_id, mensagem):
    response = requests.post(
        f"{TELEGRAM_API_URL}/sendMessage",
        data={"chat_id": chat_id, "text": mensagem}
    )
    return response.ok

# Rota para capturar imagem e enviar ao Telegram
@app.route("/capture", methods=["POST"])
def capture():
    image_path = capturar_imagem()
    if image_path and enviar_para_telegram(image_path):
        return {"status": "success", "message": "Imagem enviada para o Telegram!"}, 200
    return {"status": "error", "message": "Falha ao capturar ou enviar imagem!"}, 500

# Rota para teste de mensagem ao ID específico do Telegram
@app.route("/send_message", methods=["POST"])
def send_message():
    mensagem = "Mensagem de teste para o ID específico do Telegram."
    if enviar_mensagem_telegram(TELEGRAM_CHAT_ID, mensagem):
        return {"status": "success", "message": "Mensagem enviada com sucesso!"}, 200
    return {"status": "error", "message": "Falha ao enviar mensagem!"}, 500

# Rota de teste para o ESP8266
@app.route("/teste", methods=["POST"])
def teste():
    mensagem = "Hello World! Mensagem recebida do ESP8266."
    if enviar_mensagem_telegram(TELEGRAM_CHAT_ID, mensagem):
        return {"status": "success", "message": "Mensagem enviada para o Telegram!"}, 200
    return {"status": "error", "message": "Falha ao enviar mensagem!"}, 500

# Rota para lidar com o webhook do Telegram
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    # Verificar se os dados possuem o campo "message"
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        texto = data["message"].get("text", "")

        # Processar a mensagem recebida
        if texto.lower() == "olá":
            mensagem_resposta = "Olá! Como posso ajudar você hoje?"
        elif texto.lower() == "id":
            mensagem_resposta = f"Seu ID do Telegram é: {chat_id}"
        else:
            mensagem_resposta = f"Você disse: {texto}"

        # Enviar a resposta ao usuário
        enviar_mensagem_telegram(chat_id, mensagem_resposta)

    return {"status": "ok"}, 200

# Configurar o servidor FTP
def iniciar_servidor_ftp():
    authorizer = DummyAuthorizer()
    # Usuário anônimo com permissão para fazer upload
    authorizer.add_anonymous(UPLOAD_DIR, perm="elradfmw")
    
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "Servidor FTP Flask pronto para receber arquivos."
    
    # Configurar o servidor no host e porta específicos
    server = FTPServer(("0.0.0.0", 21), handler)
    print("Servidor FTP iniciado na porta 21.")
    server.serve_forever()

# Iniciar o servidor FTP em uma thread separada
Thread(target=iniciar_servidor_ftp, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
