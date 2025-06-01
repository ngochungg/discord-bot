from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

GPT4ALL_API_URL = "http://localhost:5000/chat"  # Hoặc địa chỉ container

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Gửi prompt đến GPT4All API
    try:
        response = requests.post(GPT4ALL_API_URL, json={"prompt": prompt})
        response.raise_for_status()
        result = response.json()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
