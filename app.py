from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/receber_dvr', methods=['POST'])
def receber_dvr():
    data = request.json
    rtsp_url = data.get('url')
    if not rtsp_url:
        return jsonify({"error": "URL RTSP não fornecida"}), 400

    # Aqui você pode salvar ou processar a URL
    return jsonify({"message": f"RTSP recebido: {rtsp_url}"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
