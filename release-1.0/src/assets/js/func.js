// Fungsi untuk mengonversi JSON ke PDF
function jsonToPdf(jsonData) {
    const { jsPDF } = window.jspdf; // Menggunakan library jsPDF
    const doc = new jsPDF();

    // Menambahkan konten ke PDF
    doc.text(`role: ${jsonData.role}`, 10, 10);
    doc.text(`content: ${jsonData.content}`, 10, 20);

    return doc.output('blob'); // Mengembalikan PDF sebagai Blob
}

// Fungsi untuk mengunduh file PDF
function downloadPdfFile(fileName, pdfBlob) {
    const url = URL.createObjectURL(pdfBlob);

    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;

    document.body.appendChild(a);
    a.click();

    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Fungsi utama untuk mengambil JSON dan mengunduh PDF
async function downloadPdfFromJson() {
    const fileName = document.getElementById('Filename').value;

    if (!fileName) {
        alert("Silakan masukkan nama file terlebih dahulu!");
        return;
    }

    try {
        // Mengambil data JSON dari path relatif
        const response = await fetch('../../api/database/history.json');
        if (!response.ok) {
            throw new Error("Gagal mengambil data JSON.");
        }
        const jsonData = await response.json();

        // Mengonversi JSON ke PDF
        const pdfBlob = jsonToPdf(jsonData);

        // Mengunduh file PDF
        downloadPdfFile(`${fileName}.pdf`, pdfBlob);
    } catch (error) {
        console.error("Terjadi kesalahan:", error);
        alert("Gagal mengambil atau mengonversi data JSON.");
    }
}

// Time stamp heading
const chatHistory = document.getElementById('chat-history');
const chatInput = document.getElementById('chat-input');

// Helper function to format timestamp
function formatTimestamp(timestamp) {
  const now = new Date();
  const messageTime = new Date(timestamp);
  const diffInMilliseconds = now - messageTime;
  const diffInHours = diffInMilliseconds / (1000 * 60 * 60);

  if (diffInHours < 24) {
    return `${Math.floor(diffInHours)} hour(s) ago`;
  } else {
    const diffInDays = diffInHours / 24;
    return `${Math.floor(diffInDays)} day(s) ago`;
  }
}

// Fungsi untuk mengelompokkan chat berdasarkan waktu
function displayChatHeadings(chats) {
    const chatContainer = document.getElementById('chat-time');
    const now = new Date();

    // Objek untuk menyimpan heading yang sudah ditampilkan
    const headings = {};

    chats.forEach(chat => {
        const chatTime = new Date(chat.timestamp);
        const diffInHours = Math.floor((now - chatTime) / (1000 * 60 * 60));
        let headingText = '';

        // Menentukan kategori waktu
        if (diffInHours < 24) {
            headingText = 'Hari Ini';
        } else if (diffInHours < 48) {
            headingText = 'Kemarin';
        } else {
            const daysAgo = Math.floor(diffInHours / 24);
            headingText = `${daysAgo} hari yang lalu`;
        }

        // Cek apakah heading sudah ada, jika belum tambahkan
        if (!headings[headingText]) {
            const headingElement = document.createElement('h3');
            headingElement.textContent = headingText;
            chatContainer.appendChild(headingElement);
            headings[headingText] = true;
        }

        // Tampilkan chat di bawah heading
        const chatElement = document.createElement('div');
        chatElement.textContent = chat.content;
        chatContainer.appendChild(chatElement);
    });
}

// Fungsi untuk memuat data chat dari file JSON
function loadChatData() {
    fetch('../../api/database/history.json') // Path ke file JSON
        .then(response => {
            if (!response.ok) {
                throw new Error('Gagal memuat data');
            }
            return response.json();
        })
        .then(data => {
            displayChatHeadings(data); // Panggil fungsi untuk menampilkan chat
        })
        .catch(error => {
            console.error('Terjadi kesalahan:', error);
        });
}

// Panggil fungsi saat halaman dimuat
window.onload = function() {
    loadChatData();
};
