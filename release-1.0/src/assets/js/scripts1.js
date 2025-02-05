fetch('../../api/database/history.json') // Ganti dengan path ke file JSON Anda
  .then(response => response.json()) // Parsing file JSON
  .then(data => {
    // Cek apakah ada objek dengan "role": "user"
    const hasUserRole = data.some(item => item.role === "user");

    // Jika ada, hapus elemen HTML dengan class .row.justify-content-center dan .title
    if (hasUserRole) {
        document.querySelector('.title').style.display = 'none';
        document.querySelector('.row.justify-content-center').style.display = 'none';
    }
  })
  .catch(error => console.error('Error loading JSON file:', error));

function fillInput(text) {
    document.getElementById('userInput').value = text; // Mengisi input dengan teks yang dipilih
}

// Handle keydown events
document.getElementById('userInput').addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault(); // Mencegah new line
        document.getElementById('sendButton').click(); // Trigger send button
    }
    // Shift + Enter akan membuat new line secara default
});

document.getElementById('sendButton').addEventListener('click', function() {
    // Menghilangkan cardBox begitu conversation dimulai
    document.querySelector('.title').style.display = 'none';
    document.querySelector('.row.justify-content-center').style.display = 'none';

    const userInput = document.getElementById('userInput').value;
    if (!userInput) {
        alert("Input tidak boleh kosong!");
        return;
    }

    // Menampilkan pesan pengguna di chat box
    const chatBox = document.getElementById('chatBox');
    chatBox.innerHTML += `<div class="user-message"><strong>Anda:</strong> ${userInput}</div>`;
    document.getElementById('userInput').value = ''; // Kosongkan input

    // Tampilkan indikator loading
    showLoadingIndicator();

    // Mengirim permintaan ke API
    fetch('http://127.0.0.1:5000/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: userInput }),
    })
    .then(response => response.json())
    .then(data => {
        removeLoadingIndicator();
        fetchConversation();
    })
    .catch(error => {
        removeLoadingIndicator();
        console.error('Error:', error);
        chatBox.innerHTML += `<div class="bot-message"><strong>Chatbot:</strong> Terjadi kesalahan saat menghubungi server.</div>`;
    });
});

function fetchConversation() {
    fetch('http://127.0.0.1:5000/api/conversation')
    .then(response => response.json())
    .then(data => {
        const chatBox = document.getElementById('chatBox');
        chatBox.innerHTML = ''; // Kosongkan chat box
        data.forEach(message => {
            const role = message.role === 'user' ? 'Anda' : 'Chatbot';
            const className = message.role === 'user' ? 'user-message' : 'bot-message';
            chatBox.innerHTML += `<div class="${className}"><strong>${role}:</strong> ${marked(message.content)}</div>`;
        });
        chatBox.scrollTop = chatBox.scrollHeight; // Scroll ke bawah
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Panggil fetchConversation saat halaman dimuat
document.addEventListener('DOMContentLoaded', fetchConversation);


// Fungsi untuk handle upload
async function handleFileUpload(event) {
    event.preventDefault(); // Mencegah reload halaman
    const file = event.target.files[0];
    
    // Validasi file
    if (!file) return;
    
    // Sembunyikan cardBox
    document.querySelector('.title').style.display = 'none';
    document.querySelector('.row.justify-content-center').style.display = 'none';

    // Tampilkan file di chat
    const chatBox = document.getElementById('chatBox');
    chatBox.innerHTML += `
        <div class="message user-message">
            <div class="file-display">
                <i class="bi bi-file-earmark"></i>
                <span>${file.name}</span>
            </div>
        </div>
    `;

    // Kirim file via AJAX
    const formData = new FormData();
    formData.append('file', file);

    try {
        showLoadingIndicator();
        
        const response = await fetch('http://localhost:5000/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        removeLoadingIndicator();
        
        // Tampilkan respons di chat box
        chatBox.innerHTML += `
            <div class="message bot-message">
                ${marked.parse(data.response)}
            </div>
        `;
        
        chatBox.scrollTop = chatBox.scrollHeight;
        
    } catch (error) {
        removeLoadingIndicator();
        chatBox.innerHTML += `
            <div class="message bot-message">
                Error: Gagal mengupload file
            </div>
        `;
    }
}

// Tambahkan event listener
document.getElementById('fileInput').addEventListener('change', handleFileUpload);

// Fungsi untuk mengupload file ke API (revisi)
function uploadFileToAPI(file) {
    const formData = new FormData();
    formData.append('file', file);

    // Tampilkan indikator loading
    showLoadingIndicator();
    
    // Menggunakan endpoint yang sama dengan chat dan pola .then/.catch
    fetch('http://127.0.0.1:5000/api/upload', { // Ganti dengan endpoint file yang sesuai
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        removeLoadingIndicator();
        const botResponse = data.response || "Maaf, saya tidak bisa memproses file ini.";
        showMessage(`Bot: ${botResponse}`, 'bot-message');
    })
    .catch(error => {
        removeLoadingIndicator();
        console.error('Error:', error);
        showMessage('Bot: Terjadi kesalahan saat memproses file.', 'bot-message');
    });
}

// Fungsi untuk menampilkan pesan
function showMessage(message, className) {
    const chatBox = document.getElementById('chatBox');
    const formattedMessage = marked.parse(message); // Menggunakan marked.js untuk format markdown
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    messageDiv.innerHTML = formattedMessage;
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Fungsi untuk menampilkan indikator loading
function showLoadingIndicator() {
    const chatBox = document.getElementById('chatBox');
    const loader = `
        <div class="message bot-message">
            <div class="loading-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
    `;
    chatBox.insertAdjacentHTML('beforeend', loader);
}

// Fungsi untuk menghapus indikator loading
function removeLoadingIndicator() {
    const loaders = document.querySelectorAll('.loading-dots');
    if (loaders.length > 0) {
        loaders[loaders.length - 1].remove();
    }
}

// Tambahkan CSS untuk loading indicator
const style = document.createElement('style');
style.textContent = `
.loading-dots {
    display: flex;
    padding: 10px 0;
}
.dot {
    width: 8px;
    height: 8px;
    margin: 0 4px;
    background-color: #888;
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out;
}
@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}
.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }
`;
document.head.appendChild(style);
