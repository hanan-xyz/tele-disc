```markdown
# Telegram to Discord Forwarder Bot 🤖

![GitHub License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-green.svg)

Bot otomatis untuk meneruskan pesan dari channel Telegram ke thread Discord dengan fitur klasifikasi, filter, dan manajemen terpusat. Cocok untuk komunitas yang membutuhkan integrasi lintas platform dengan kontrol penuh.

---

## Daftar Isi 📜

- [Fitur Utama](#-fitur-utama)
- [Instalasi](#%EF%B8%8F-instalasi)
- [Konfigurasi](#-konfigurasi)
- [Cara Menjalankan](#-cara-menjalankan)
- [Perintah Admin](#-perintah-admin)
- [Struktur Proyek](#-struktur-proyek)
- [Lisensi](#-lisensi)
- [Kontribusi](#-kontribusi)

---

## 🚀 Fitur Utama

- **Multi-Klasifikasi Channel**  
  - **VIP**: Teruskan semua pesan tanpa filter.
  - **Filter**: Hanya teruskan pesan yang mengandung kata kunci.
  - **Unfilter**: Teruskan semua pesan tanpa pengecualian.
  
- **Terjemahan Otomatis**  
  Terjemahkan pesan asing ke Bahasa Indonesia menggunakan Google Translate API.

- **Manajemen Dinamis**  
  Admin dapat mengelola channel dan kata kunci langsung via Telegram:
  ```bash
  /add_filter_channel @namachannel   # Tambah channel filter
  /remove_keyword promo             # Hapus kata kunci
  ```

- **Anti Rate-Limit**  
  Delay 5 detik antar pengiriman pesan ke Discord.

- **Logging Terpusat**  
  Lacak aktivitas bot melalui file `telegram_forwarder.log`.

---

## ⚙️ Instalasi

### Prasyarat
- Python 3.8+
- Akun [Developer Telegram](https://my.telegram.org/) (untuk API ID/HASH)
- Token Bot Discord (lihat [panduan](https://discordpy.readthedocs.io/en/stable/discord.html))

### Langkah-langkah
1. Clone repositori:
   ```bash
   git clone https://github.com/username/telegram-discord-forwarder.git
   cd telegram-discord-forwarder
   ```

2. Instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔧 Konfigurasi

### 1. File `.env`
Buat file `.env` di root direktori dengan konten:
```env
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH="abc123def456"
TELEGRAM_PHONE="+628123456789"
ADMINS="admin1,admin2"
DISCORD_AUTH_TOKEN="your.discord.token"
DISCORD_THREAD_ID=112233445566778899
```

### 2. File `channels.json`
```json
{
  "VIP_CHANNELS": ["@VIP_Group"],
  "FILTERED_CHANNELS": ["@PromoChannel"],
  "UNFILTERED_CHANNELS": ["@GeneralChat"]
}
```

### 3. File `keywords.json`
```json
{
  "KEYWORDS": ["giveaway", "diskon", "flashsale"]
}
```

---

## 🖥️ Cara Menjalankan

1. Pastikan semua file konfigurasi sudah diisi.
2. Jalankan bot:
   ```bash
   python main.py
   ```
3. Ikuti instruksi login Telegram di konsol.

---

## 👨💻 Perintah Admin

| Perintah                      | Deskripsi                           | Contoh                           |
|-------------------------------|-------------------------------------|----------------------------------|
| `/add_filter_channel @channel`| Tambah channel filter              | `/add_filter_channel @PromoBot`  |
| `/list_vip`                   | Tampilkan channel VIP              | `/list_vip`                      |
| `/add_keyword <kata>`         | Tambah kata kunci                  | `/add_keyword promo`             |
| `/remove_keyword <kata>`      | Hapus kata kunci                   | `/remove_keyword expired`        |

---

## 📂 Struktur Proyek

```
├── main.py              → Entry point aplikasi
├── config.py            → Manajemen konfigurasi
├── telegram_handlers.py → Handler event Telegram
├── discord_utils.py     → Fungsi pengiriman ke Discord
├── utils.py             → Helper (terjemahan, login)
├── .env                 → Variabel lingkungan
└── data/                → File JSON konfigurasi
    ├── channels.json
    └── keywords.json
```

---

## 📜 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).

---

## 🤝 Kontribusi

1. Fork repositori
2. Buat branch fitur (`git checkout -b fitur/namafitur`)
3. Commit perubahan (`git commit -m 'Tambahkan fitur X'`)
4. Push ke branch (`git push origin fitur/namafitur`)
5. Buat Pull Request

**Laporkan Issue** di [sini](https://github.com/username/telegram-discord-forwarder/issues).

---

> **Catatan**: Pastikan token API tidak pernah dibagikan publik! 🔒
``` 

### Perubahan Utama:
1. **Struktur Lebih Hierarkis**  
   Menggunakan header dengan emoji dan anchor links untuk navigasi mudah.

2. **Tabel Perintah Admin**  
   Menampilkan perintah dalam format tabel yang rapi.

3. **Penjelasan Visual**  
   Diagram struktur folder dan badge versi untuk informasi cepat.

4. **Panduan Konfigurasi Terperinci**  
   Contoh file konfigurasi dengan blok kode yang diformat sesuai sintaks.

5. **Catatan Keamanan**  
   Peringatan tentang pentingnya menjaga kredensial API.

6. **Call-to-Action Kontribusi**  
   Langkah-langkah kontribusi yang jelas dengan link langsung ke issues.
