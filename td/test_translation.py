import asyncio
import os
from utils import translate_text, setup_logging
from dotenv import load_dotenv

# Inisialisasi logger
logger = setup_logging()

async def test_translation():
    """Fungsi untuk menguji translate_text dari utils.py."""
    # Memuat variabel lingkungan untuk GOOGLE_API_KEY
    load_dotenv()
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        logger.warning("GOOGLE_API_KEY tidak ditemukan di .env, cadangan mungkin tidak berfungsi.")

    # Teks uji
    test_texts = [
        "RTRS: WHITE HOUSE ECONOMIC ADVISER HASSETT: CONVERSATIONS ON CHINA HAVE NOT BEGUN YET - CNBC INTERVIEW",
        "Hello world!",
        "Sudah dalam bahasa Indonesia"  # Teks ini seharusnya tidak diterjemahkan
    ]

    # Uji setiap teks
    for text in test_texts:
        logger.info(f"Menguji terjemahan untuk teks: {text}")
        try:
            translated = await translate_text(text, target_lang="id")
            logger.info(f"Hasil terjemahan: {translated}")
        except Exception as e:
            logger.error(f"Gagal menerjemahkan teks '{text}': {str(e)}")

if __name__ == "__main__":
    # Jalankan fungsi pengujian
    asyncio.run(test_translation())