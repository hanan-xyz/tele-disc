# Telegram to Discord Forwarder

![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)
![Python version](https://img.shields.io/badge/python-3.8%2B-blue.svg)

Telegram to Discord Forwarder adalah bot yang dirancang untuk meneruskan pesan dari channel Telegram ke thread Discord secara otomatis. Bot ini dilengkapi dengan fitur klasifikasi channel (VIP, Filter, Unfilter), terjemahan pesan ke bahasa Indonesia, serta manajemen channel dan kata kunci oleh admin melalui perintah Telegram. Proyek ini cocok untuk pengguna yang ingin mengintegrasikan komunikasi antara Telegram dan Discord dengan kontrol penuh atas pesan yang diteruskan.

---

## **Fitur Utama**

- **Penerusan Pesan**: Mengirim pesan dari channel Telegram ke thread Discord dengan format yang rapi dan disesuaikan.
- **Klasifikasi Channel**:
  - **VIP**: Pesan dari channel ini diteruskan langsung tanpa filter apa pun.
  - **Filter**: Pesan hanya diteruskan jika mengandung kata kunci tertentu yang telah ditentukan.
  - **Unfilter**: Semua pesan dari channel ini diteruskan tanpa filter.
- **Terjemahan Otomatis**: Pesan dari bahasa asing diterjemahkan ke bahasa Indonesia sebelum dikirim ke Discord.
- **Manajemen Admin**: Admin dapat menambah atau menghapus channel serta kata kunci melalui perintah Telegram.
- **Delay Pengiriman**: Penundaan 5 detik antar pesan untuk menghindari batas kecepatan (rate limit) Discord.
- **Logging**: Sistem logging terperinci untuk memantau aktivitas bot dan mendeteksi kesalahan.

---

## **Struktur Proyek**

Proyek ini terdiri dari beberapa file utama yang masing-masing memiliki fungsi spesifik:

- **`main.py`**: File utama yang menjadi titik masuk aplikasi. Menginisialisasi klien Telegram dan menjalankan semua handler.
- **`config.py`**: Mengelola konfigurasi global, memuat variabel lingkungan dari file `.env`, serta data dari file JSON seperti daftar channel dan kata kunci.
- **`telegram_handlers.py`**: Berisi fungsi handler untuk menangani pesan dari Telegram dan perintah admin.
- **`utils.py`**: Berisi fungsi utilitas seperti terjemahan pesan dan proses login ke Telegram.
- **`discord_utils.py`**: Berisi fungsi untuk mengirim pesan ke thread Discord dengan format yang sesuai.

---

## **Persyaratan**

Untuk menjalankan bot ini, Anda memerlukan:

- **Python 3.8 atau lebih tinggi**.
- **Dependensi Python**:
  - `telethon`: Untuk berinteraksi dengan API Telegram.
  - `aiohttp`: Untuk permintaan HTTP asinkronus.
  - `python-dotenv`: Untuk memuat variabel lingkungan dari file `.env`.
  - `langdetect`: Untuk mendeteksi bahasa pesan.
  - `requests`: Untuk permintaan HTTP tambahan (misalnya, API terjemahan).

### **Instalasi Dependensi**
Jalankan perintah berikut di terminal untuk menginstal semua dependensi:
```bash
pip install telethon aiohttp python-dotenv langdetect requests
Konfigurasi
Sebelum menjalankan bot, Anda perlu mengatur beberapa file konfigurasi. Berikut langkah-langkahnya:
1. File .env
Buat file bernama .env di direktori root proyek dan isi dengan variabel berikut:
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+628123456789
ADMINS=admin1,admin2
TARGET_CHANNEL=@TargetChannel
GOOGLE_API_KEY=your_google_api_key
DISCORD_AUTH_TOKEN=your_discord_token
DISCORD_THREAD_ID=123456789012345678
TELEGRAM_API_ID dan TELEGRAM_API_HASH: Dapatkan dari my.telegram.org.
TELEGRAM_PHONE: Nomor telepon Anda dengan kode negara (contoh: +628123456789).
ADMINS: Daftar username Telegram admin, dipisahkan koma (tanpa @).
TARGET_CHANNEL: Channel Telegram tempat bot akan mengirim perintah admin.
GOOGLE_API_KEY: Kunci API Google untuk terjemahan (opsional, jika menggunakan Google Translate).
DISCORD_AUTH_TOKEN: Token bot Discord Anda.
DISCORD_THREAD_ID: ID thread Discord tempat pesan akan diteruskan.
2. File channels.json
Buat file channels.json di direktori root untuk menyimpan daftar channel yang akan dipantau bot:
json
{
    "FILTERED_CHANNELS": ["@Channel1", "@Channel2"],
    "UNFILTERED_CHANNELS": ["@Channel3"],
    "VIP_CHANNELS": ["@VIPChannel"]
}
FILTERED_CHANNELS: Daftar channel yang pesannya difilter berdasarkan kata kunci.
UNFILTERED_CHANNELS: Daftar channel yang pesannya diteruskan tanpa filter.
VIP_CHANNELS: Daftar channel prioritas yang pesannya selalu diteruskan.
3. File keywords.json
Buat file keywords.json untuk menyimpan kata kunci yang digunakan pada channel bertipe "Filter":
json
{
    "KEYWORDS": ["promo", "diskon"]
}
Tambahkan kata kunci yang relevan sesuai kebutuhan Anda.
Cara Menjalankan
Ikuti langkah-langkah berikut untuk menjalankan bot:
1. Clone Repository
Unduh proyek ini dari GitHub:
bash
git clone https://github.com/username/tele-disc.git
cd tele-disc
Catatan: Ganti username dengan nama pengguna GitHub Anda.
2. Instal Dependensi
Pastikan semua dependensi terinstal:
bash
pip install -r requirements.txt
Jika file requirements.txt belum ada, buat dengan daftar dependensi di atas dan jalankan perintah tersebut.
3. Jalankan Bot
Jalankan file utama:
bash
python main.py
4. Login ke Telegram
Saat pertama kali dijalankan, bot akan meminta Anda memasukkan kode verifikasi yang dikirim ke nomor Telegram Anda.
Jika akun Anda menggunakan autentikasi dua faktor (2FA), masukkan kata sandi 2FA saat diminta.
Setelah login berhasil, bot akan mulai memantau channel Telegram dan meneruskan pesan ke Discord sesuai konfigurasi.
Perintah Admin
Admin dapat mengelola bot melalui perintah Telegram yang dikirim ke TARGET_CHANNEL. Berikut daftar perintah yang tersedia:
Menambah Channel
/add_filter_channel @channelname: Tambah channel ke daftar "Filter".
/add_unfilter_channel @channelname: Tambah channel ke daftar "Unfilter".
/add_vip_channel @channelname: Tambah channel ke daftar "VIP".
Menghapus Channel
/remove_filter_channel @channelname: Hapus channel dari daftar "Filter".
/remove_unfilter_channel @channelname: Hapus channel dari daftar "Unfilter".
/remove_vip_channel @channelname: Hapus channel dari daftar "VIP".
Manajemen Kata Kunci
/add_keyword keyword: Tambah kata kunci baru ke daftar.
/remove_keyword keyword: Hapus kata kunci dari daftar.
Menampilkan Daftar
/list_filter: Tampilkan daftar channel "Filter".
/list_unfilter: Tampilkan daftar channel "Unfilter".
/list_vip: Tampilkan daftar channel "VIP".
/list_keyword: Tampilkan daftar kata kunci.
Logging
Bot menyimpan log aktivitas di file telegram_forwarder.log di direktori root.
Log juga ditampilkan di konsol saat bot berjalan.
Log mencakup:
Info: Aktivitas normal seperti pesan yang diteruskan.
Warning: Peringatan kecil yang tidak mengganggu operasi.
Error: Kesalahan kritis yang perlu diperbaiki.
Gunakan log ini untuk memantau performa bot dan mendiagnosis masalah.
Lisensi
Proyek ini dilisensikan di bawah MIT License (LICENSE). Anda bebas menggunakan, memodifikasi, dan mendistribusikan kode ini sesuai ketentuan lisensi.
Kontribusi
Kami menyambut kontribusi dari komunitas! Jika Anda ingin berkontribusi:
Fork repository ini.
Buat branch baru untuk fitur atau perbaikan Anda:
bash
git checkout -b nama-branch
Commit perubahan Anda:
bash
git commit -m "Deskripsi perubahan"
Push ke branch Anda:
bash
git push origin nama-branch
Buat Pull Request di repository ini.
Jika Anda menemukan bug atau memiliki saran, silakan buka issue di GitHub.
Catatan Tambahan
Pastikan koneksi internet stabil saat menjalankan bot.
Simpan kredensial seperti API key dan token dengan aman, jangan bagikan secara publik.
Untuk pengujian, Anda bisa menambahkan channel Telegram dummy sebelum deploy ke channel utama.
Terima kasih telah menggunakan Telegram to Discord Forwarder! Jika ada pertanyaan, jangan ragu untuk menghubungi melalui issue atau kontak di GitHub.

---

### **Penjelasan README.md**
README ini dirancang dengan struktur yang jelas dan informatif:
- **Header**: Menyertakan badge untuk lisensi dan versi Python agar terlihat profesional di GitHub.
- **Fitur Utama**: Menjelaskan apa yang bisa dilakukan bot secara singkat dan menarik.
- **Struktur Proyek**: Membantu pengguna memahami fungsi setiap file.
- **Konfigurasi dan Cara Menjalankan**: Panduan langkah demi langkah yang mudah diikuti.
- **Perintah Admin**: Daftar perintah yang rapi menggunakan subjudul.
- **Logging, Lisensi, Kontribusi**: Informasi tambahan yang relevan untuk pengguna tingkat lanjut.

File ini siap diunggah ke GitHub dan akan memberikan pengalaman pengguna yang baik bagi siapa saja yang ingin mencoba proyek Anda. Semoga sukses dengan proyeknya!
