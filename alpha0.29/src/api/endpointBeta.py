from flask import Flask, request, jsonify
import requests
import json
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import PyPDF2
import docx

app = Flask(__name__)
CORS(app)  # Mengizinkan CORS untuk semua domain

# Konfigurasi folder upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Pastikan folder upload ada
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

url = "http://127.0.0.1:1234/v1/chat/completions"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
    return text.strip()

def read_docx(file_path):
    doc = docx.Document(file_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text.strip()

def chat_with_llm(prompt):
    payload = {
        "messages": [
            {"role": "system", "content": "only answer about food and drink question, otherwise say error message."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 500,
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

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'response': 'Tidak ada file yang diupload.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'response': 'Tidak ada file yang dipilih.'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Membaca konten file
        if filename.endswith('.pdf'):
            content = read_pdf(file_path)
        elif filename.endswith('.docx'):
            content = read_docx(file_path)
        else:
            return jsonify({'response': 'Format file tidak diizinkan.'}), 400

        # Mengirim konten ke LLM
        response = chat_with_llm(content)
        bot_response = response.get("choices")[0].get("message").get("content") if response.get("choices") else "Maaf, saya tidak bisa memberikan respons."

        return jsonify({'response': bot_response}), 200

    return jsonify({'response': 'Format file tidak diizinkan.'}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)