import re
import aiohttp
import requests  # Tetap untuk Google Translate cadangan
from langdetect import detect
from config import GOOGLE_API_KEY, setup_logging

logger = setup_logging()

def extract_username(input_str):
    if not isinstance(input_str, str):
        logger.error(f"Input untuk extract_username bukan string: {input_str}")
        return None
    if input_str.startswith('@'):
        return input_str[1:]
    url_pattern = r'https?://t\.me/(\w+)'
    match = re.search(url_pattern, input_str)
    if match:
        return match.group(1)
    return input_str

def contains_keyword(text, keywords):
    if not text or not keywords:
        return False
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)

async def translate_text(text, target_lang="id"):
    try:
        if not text or detect(text) == "id":
            logger.info(f"Teks sudah dalam bahasa Indonesia atau kosong: {text}")
            return text
        url = "https://sysapi.wordvice.ai/tools/non-member/fetch-llm-result"
        payload = {
            "prompt": "Translate the following English text into Indonesian.",
            "text": text,
            "tool": "translate"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "origin": "https://wordvice.ai",
            "referer": "https://wordvice.ai/"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    raise Exception(f"Wordvice API error: {response.status}")
                data = await response.json()
                if data.get("code") == "0000":
                    translated_text = data["result"][0]["text"]
                    logger.info(f"Terjemahan berhasil: {translated_text}")
                    return translated_text
                else:
                    logger.error(f"API error: {data.get('message')}")
                    raise Exception("API Wordvice gagal")
    except Exception as e:
        logger.error(f"Terjemahan utama gagal: {str(e)}, mencoba cadangan...")
        try:
            if GOOGLE_API_KEY:
                url = f"https://translation.googleapis.com/language/translate/v2?key={GOOGLE_API_KEY}"
                payload = {"q": text, "target": target_lang, "format": "text"}
                response = requests.post(url, json=payload)
                response.raise_for_status()
                return response.json()["data"]["translations"][0]["translatedText"]
            else:
                logger.warning("Tidak ada kunci API cadangan.")
                return text
        except Exception as fallback_e:
            logger.critical(f"API cadangan gagal: {str(fallback_e)}")
            return text

async def login(client):
    from config import PHONE
    try:
        await client.start(phone=PHONE)
        if not await client.is_user_authorized():
            logger.info("Memulai proses login...")
            for _ in range(3):  # Maksimal 3 percobaan
                code = input("Masukkan kode verifikasi yang diterima: ")
                try:
                    await client.sign_in(PHONE, code)
                    break
                except Exception as e:
                    if "Two-steps verification" in str(e):
                        password = input("Masukkan kata sandi 2FA kamu: ")
                        await client.sign_in(password=password)
                        break
                    logger.error(f"Kode salah: {str(e)}")
            else:
                logger.critical("Gagal login setelah 3 percobaan.")
                raise Exception("Gagal login setelah 3 percobaan.")
        logger.info("Login berhasil!")
    except Exception as e:
        logger.critical(f"Login gagal: {str(e)}")
        raise

async def shutdown_client(client):
    logger.info("Menghentikan klien...")
    try:
        await client.disconnect()
        logger.info("Klien berhenti.")
    except Exception as e:
        logger.critical(f"Gagal menghentikan klien: {str(e)}")
        raise
