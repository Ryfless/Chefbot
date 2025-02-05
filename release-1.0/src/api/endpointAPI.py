from flask import Flask, request, jsonify
import requests
import json
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import PyPDF2
import docx
from typing import Dict, Any

app = Flask(__name__)
CORS(app)  # Untuk development, restrict domain di production

# Konfigurasi
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

LLM_URL = "http://127.0.0.1:1234/v1/chat/completions"

# Path ke file dalam folder sys_prompt
SYSTEM_PROMPT_PATH = os.path.join('sys_prompt', 'preset.txt')
with open(SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read().strip()

# Path ke file untuk conversation history
HISTORY_PATH = os.path.join('database', 'history.json')
CONVERSATION_FILE = HISTORY_PATH

def setup_environment():
    """Membuat folder upload jika tidak ada"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename: str) -> bool:
    """Validasi ekstensi file"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_pdf(file_path: str) -> str:
    """Membaca isi file PDF dengan error handling"""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return '\n'.join([page.extract_text() for page in reader.pages if page.extract_text()])
    except Exception as e:
        raise RuntimeError(f"Gagal membaca PDF: {str(e)}")

def read_docx(file_path: str) -> str:
    """Membaca isi file DOCX dengan error handling"""
    try:
        doc = docx.Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs if para.text])
    except Exception as e:
        raise RuntimeError(f"Gagal membaca DOCX: {str(e)}")

def process_llm_response(response: requests.Response) -> Dict[str, Any]:
    """Memproses response dari LLM service"""
    if response.status_code != 200:
        return {"error": f"Error LLM: {response.status_code} - {response.text}"}
    
    try:
        data = response.json()
        if not data.get("choices"):
            return {"error": "Format response LLM tidak valid"}
        
        message = data["choices"][0].get("message", {})
        return {"response": message.get("content", "Tidak ada konten yang diterima")}
    
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from LLM"}

def chat_with_llm(content: str, is_file: bool = False) -> Dict[str, Any]:
    """Mengirim permintaan ke LLM service"""
    system_msg = SYSTEM_PROMPT + ("\n[File Context]" if is_file else "")
    
    payload = {
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": content}
        ],
        "temperature": 0.8,
        "max_tokens": 1000,
        "stream": False
    }

    try:
        response = requests.post(
            LLM_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30  # Timeout 30 detik
        )
        return process_llm_response(response)
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Koneksi ke LLM gagal: {str(e)}"}

def save_conversation(role, content):
    conversation = []
    if os.path.exists(CONVERSATION_FILE):
        with open(CONVERSATION_FILE, 'r', encoding='utf-8') as f:
            conversation = json.load(f)
    conversation.append({"role": role, "content": content})
    with open(CONVERSATION_FILE, 'w', encoding='utf-8') as f:
        json.dump(conversation, f, ensure_ascii=False, indent=4)

@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.json.get('input')
    save_conversation("user", user_input)
    
    llm_response = chat_with_llm(user_input)
    bot_response = llm_response.get("response", "Maaf, saya tidak bisa memproses permintaan Anda saat ini.")
    save_conversation("assistant", bot_response)
    
    return jsonify({"response": bot_response})


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"response": "Tidak ada file yang diterima"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"response": "Nama file kosong"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"response": "Tipe file tidak diizinkan"}), 400

    try:
        # Simpan file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Baca isi file
        if filename.lower().endswith('.pdf'):
            file_content = read_pdf(file_path)
        elif filename.lower().endswith('.docx'):
            file_content = read_docx(file_path)
        else:
            return jsonify({"response": "Tipe file tidak didukung"}), 400

        if not file_content.strip():
            return jsonify({"response": "File kosong atau tidak bisa dibaca"}), 400

        # Dapatkan respons dari LLM berdasarkan isi file
        llm_response = chat_with_llm(file_content, is_file=True)
        
        if 'error' in llm_response:
            return jsonify({"response": llm_response['error']}), 500
            
        bot_response = llm_response.get('response', 'Tidak bisa memproses dokumen')

        # Simpan ke riwayat percakapan
        save_conversation("user", f"[Mengunggah file] {filename}")
        save_conversation("assistant", bot_response)

        return jsonify({
            "response": bot_response,
            "filename": filename,
            "content_preview": file_content[:200] + "..."  # Preview 200 karakter
        })

    except Exception as e:
        app.logger.error(f"Error processing file: {str(e)}")
        return jsonify({"response": f"Terjadi kesalahan saat memproses file: {str(e)}"}), 500

    finally:
        # Bersihkan file yang sudah diproses (opsional)
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/conversation', methods=['GET'])
def get_conversation():
    if os.path.exists(CONVERSATION_FILE):
        with open(CONVERSATION_FILE, 'r', encoding='utf-8') as f:
            conversation = json.load(f)
        return jsonify(conversation)
    return jsonify([])

if __name__ == "__main__":
    setup_environment()
    app.run(debug=True, port=5000)