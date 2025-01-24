from flask import Flask, request, jsonify
import requests
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Mengizinkan CORS untuk semua domain

url = "http://127.0.0.1:1234/v1/chat/completions"

def chat_with_llm(prompt):
    payload = {
        "messages": [
            {"role": "system", "content": "hanya menjawab pertanyaan yang berkaitan dengan makanan dan minuman, selain itu jawab dengan pesan error"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": -1,
        "stream": False
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Request failed with status code " + str(response.status_code)}

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('input')

    if not user_input:
        return jsonify({"error": "Input is required"}), 400

    response = chat_with_llm(user_input)
    bot_response = response.get("choices")[0].get("message").get("content") if response.get("choices") else "Maaf, saya tidak bisa memberikan respons."

    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True, port=5000)