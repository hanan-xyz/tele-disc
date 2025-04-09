# config.py
import logging
import os
import json
from dotenv import load_dotenv

def setup_logging():
    logging.basicConfig(
        filename='telegram_forwarder.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def load_env():
    load_dotenv()
    global API_ID, API_HASH, PHONE, ADMINS, TARGET_CHANNEL, GOOGLE_API_KEY, DISCORD_AUTH_TOKEN, DISCORD_THREAD_ID
    API_ID = os.getenv('TELEGRAM_API_ID')
    API_HASH = os.getenv('TELEGRAM_API_HASH')
    PHONE = os.getenv('TELEGRAM_PHONE')
    ADMINS = [admin.strip() for admin in os.getenv('ADMINS').split(',')]
    TARGET_CHANNEL = os.getenv('TARGET_CHANNEL')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    DISCORD_AUTH_TOKEN = os.getenv('DISCORD_AUTH_TOKEN')
    DISCORD_THREAD_ID = os.getenv('DISCORD_THREAD_ID')

    if not all([API_ID, API_HASH, PHONE, TARGET_CHANNEL, DISCORD_AUTH_TOKEN, DISCORD_THREAD_ID]):
        raise ValueError("Salah satu variabel wajib di .env kosong!")

def load_config():
    global FILTERED_CHANNELS, UNFILTERED_CHANNELS, KEYWORDS, VIP_CHANNELS
    CHANNELS_FILE = 'channels.json'
    KEYWORDS_FILE = 'keywords.json'
    logger = setup_logging()
    try:
        with open(CHANNELS_FILE, 'r') as f:
            channels_data = json.load(f)
            FILTERED_CHANNELS = channels_data.get('FILTERED_CHANNELS', [])
            UNFILTERED_CHANNELS = channels_data.get('UNFILTERED_CHANNELS', [])
            VIP_CHANNELS = channels_data.get('VIP_CHANNELS', [])  # Tambah VIP_CHANNELS
        with open(KEYWORDS_FILE, 'r') as f:
            keywords_data = json.load(f)
            KEYWORDS = keywords_data.get('KEYWORDS', [])
    except FileNotFoundError:
        FILTERED_CHANNELS = []
        UNFILTERED_CHANNELS = []
        VIP_CHANNELS = []  # Inisialisasi VIP_CHANNELS
        KEYWORDS = []
        logger.warning("File konfigurasi tidak ditemukan. Menggunakan daftar kosong.")
        with open(CHANNELS_FILE, 'w') as f:
            json.dump({'FILTERED_CHANNELS': [], 'UNFILTERED_CHANNELS': [], 'VIP_CHANNELS': []}, f)
        with open(KEYWORDS_FILE, 'w') as f:
            json.dump({'KEYWORDS': []}, f)
