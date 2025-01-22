from flask import Flask, request
import cv2
import requests

app = Flask(__name__)

# Configurações
RTSP_URL = "rtsp://admin:juss1403@10.0.0.110:554/cam/realmonitor?channel=1&subtype=0"
TELEGRAM_TOKEN = "8062258264:AAHTdhpbkiH7QB7JaNK9keXkhcici2aJGaY"
TELEGRAM_CHAT_ID = "6784880297"

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
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
            data={"chat_id": TELEGRAM_CHAT_ID},
            files={"photo": file}
        )
    return response.ok

# Função para enviar mensagem de texto ao Telegram
def enviar_mensagem_telegram(mensagem):
    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}
    )
    return response.ok

# Rota para capturar imagem e enviar ao Telegram
@app.route("/capture", methods=["POST"])
def capture():
    image_path = capturar_imagem()
    if image_path and enviar_para_telegram(image_path):
        return {"status": "success", "message": "Imagem enviada para o Telegram!"}, 200
    return {"status": "error", "message": "Falha ao capturar ou enviar imagem!"}, 500

# Rota para teste (recebe sinal do ESP8266 e envia mensagem "Hello World")
@app.route("/teste", methods=["POST"])
def teste():
    mensagem = "Notificação flask: Tem gente no portão!."
    if enviar_mensagem_telegram(mensagem):
        return {"status": "success", "message": "Mensagem enviada para o Telegram!"}, 200
    return {"status": "error", "message": "Falha ao enviar mensagem!"}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
