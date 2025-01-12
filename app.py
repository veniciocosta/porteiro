import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/receber_dvr', methods=['POST'])
def receber_dvr():
    data = request.json
    rtsp_url = data.get('url')
    if not rtsp_url:
        return jsonify({"error": "URL RTSP não fornecida"}), 400
    return jsonify({"message": f"RTSP recebido: {rtsp_url}"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

