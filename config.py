import os
import json
import logging
from dotenv import load_dotenv

# Variabel global
API_ID = None
API_HASH = None
PHONE = None
ADMINS = []
TARGET_CHANNEL = None
GOOGLE_API_KEY = None
DISCORD_AUTH_TOKEN = None
DISCORD_THREAD_ID = None

# Variabel global untuk channel dan keywords
FILTERED_CHANNELS = []
UNFILTERED_CHANNELS = []
VIP_CHANNELS = []
KEYWORDS = []

def load_env():
    """Memuat variabel lingkungan dari file .env"""
    global API_ID, API_HASH, PHONE, ADMINS, TARGET_CHANNEL, GOOGLE_API_KEY, DISCORD_AUTH_TOKEN, DISCORD_THREAD_ID
    load_dotenv()
    
    # Ambil variabel dari .env
    api_id_str = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE')
    admins = os.getenv('ADMINS', '')
    target_channel = os.getenv('TARGET_CHANNEL')
    google_api_key = os.getenv('GOOGLE_API_KEY')
    discord_auth_token = os.getenv('DISCORD_AUTH_TOKEN')
    discord_thread_id = os.getenv('DISCORD_THREAD_ID')
    
    # Validasi variabel wajib sebelum konversi
    required_vars = {
        'TELEGRAM_API_ID': api_id_str,
        'TELEGRAM_API_HASH': api_hash,
        'TELEGRAM_PHONE': phone,
        'TARGET_CHANNEL': target_channel,
        'DISCORD_AUTH_TOKEN': discord_auth_token,
        'DISCORD_THREAD_ID': discord_thread_id
    }
    missing_vars = [key for key, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(f"Variabel wajib berikut kosong atau tidak valid di .env: {', '.join(missing_vars)}")
    
    # Konversi API_ID ke integer dengan penanganan error
    try:
        API_ID = int(api_id_str)
    except (ValueError, TypeError):
        raise ValueError("TELEGRAM_API_ID harus berupa angka integer yang valid.")
    
    # Tetapkan nilai ke variabel global
    API_HASH = api_hash
    PHONE = phone
    ADMINS = [admin.strip() for admin in admins.split(',') if admin.strip()]
    TARGET_CHANNEL = target_channel
    GOOGLE_API_KEY = google_api_key
    DISCORD_AUTH_TOKEN = discord_auth_token
    DISCORD_THREAD_ID = discord_thread_id

def setup_logging():
    """Mengatur logging untuk aplikasi"""
    logging.basicConfig(
        filename='telegram_forwarder.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def load_config():
    """Memuat konfigurasi dari channels.json dan keywords.json"""
    global FILTERED_CHANNELS, UNFILTERED_CHANNELS, VIP_CHANNELS, KEYWORDS
    try:
        with open('channels.json', 'r') as f:
            channels_data = json.load(f)
            FILTERED_CHANNELS = channels_data.get('FILTERED_CHANNELS', [])
            UNFILTERED_CHANNELS = channels_data.get('UNFILTERED_CHANNELS', [])
            VIP_CHANNELS = channels_data.get('VIP_CHANNELS', [])
    except FileNotFoundError:
        FILTERED_CHANNELS = []
        UNFILTERED_CHANNELS = []
        VIP_CHANNELS = []
        print("File channels.json tidak ditemukan. Menggunakan daftar kosong.")
    
    try:
        with open('keywords.json', 'r') as f:
            keywords_data = json.load(f)
            KEYWORDS = keywords_data.get('KEYWORDS', [])
    except FileNotFoundError:
        KEYWORDS = []
        print("File keywords.json tidak ditemukan. Menggunakan daftar kosong.")

# Panggil fungsi load_env() dan load_config() saat modul diimpor
load_env()
load_config()
