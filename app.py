from flask import Flask, request, jsonify
from flask import send_from_directory
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os
import threading
import telegram

# Configuração inicial do Flask
app = Flask(__name__)

# Diretório onde as imagens serão armazenadas
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Cria o diretório se não existir
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Token do Bot do Telegram (substitua pelo seu token)
TELEGRAM_TOKEN = '8062258264:AAHTdhpbkiH7QB7JaNK9keXkhcici2aJGaY'
TELEGRAM_CHAT_ID = '6784880297'  # Substitua pelo chat_id do Telegram
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Função para enviar uma mensagem ao Telegram
def enviar_telegram(mensagem, arquivo=None):
    try:
        if arquivo:
            bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=open(arquivo, 'rb'))
        else:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)
    except Exception as e:
        print(f"Erro ao enviar mensagem para o Telegram: {e}")

# Rota para receber acionamento do ESP8266
@app.route('/acionar', methods=['GET'])
def acionar():
    """
    Essa rota será acionada pelo ESP8266 ao pressionar o botão.
    """
    # Envia uma mensagem de confirmação ao Telegram
    enviar_telegram("Botão pressionado! Enviando a última imagem do DVR.")
    
    # Encontra a última imagem salva no diretório
    arquivos = sorted(os.listdir(app.config['UPLOAD_FOLDER']), reverse=True)
    if arquivos:
        ultima_imagem = os.path.join(app.config['UPLOAD_FOLDER'], arquivos[0])
        enviar_telegram("Última imagem capturada:", arquivo=ultima_imagem)
        return jsonify({'status': 'Imagem enviada para o Telegram!'})
    else:
        return jsonify({'status': 'Nenhuma imagem encontrada no servidor.'})

# Rota para teste de envio ao Telegram
@app.route('/teste', methods=['GET'])
def teste_envio():
    """
    Rota para testar envio de mensagens ao Telegram sem o ESP8266.
    """
    enviar_telegram("Teste de envio para o Telegram funcionando!")
    return jsonify({'status': 'Teste enviado com sucesso!'})

# Configuração do servidor FTP
def iniciar_servidor_ftp():
    """
    Configura e inicia um servidor FTP para receber imagens do DVR.
    """
    authorizer = DummyAuthorizer()
    authorizer.add_user('user', 'password', UPLOAD_FOLDER, perm='elradfmw')  # Substitua por usuário/senha seguros
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "Servidor FTP pronto para receber arquivos."
    
    address = ('0.0.0.0', 21)  # IP e porta do servidor FTP
    server = FTPServer(address, handler)
    print("Servidor FTP iniciado na porta 21...")
    server.serve_forever()

# Inicializa o servidor FTP em uma thread separada
ftp_thread = threading.Thread(target=iniciar_servidor_ftp, daemon=True)
ftp_thread.start()

# Inicializa o servidor Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


