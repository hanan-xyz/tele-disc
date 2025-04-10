import aiohttp
import asyncio
import time
from config import DISCORD_AUTH_TOKEN, DISCORD_THREAD_ID, setup_logging

logger = setup_logging()

async def send_message_to_discord_thread(message):
    """
    Mengirim pesan ke thread Discord menggunakan Discord API secara async.
    
    Args:
        message (str): Pesan yang akan dikirim ke thread Discord.
    """
    if not DISCORD_AUTH_TOKEN or not DISCORD_THREAD_ID:
        logger.critical("DISCORD_AUTH_TOKEN atau DISCORD_THREAD_ID tidak valid atau kosong.")
        return False

    url = f"https://discord.com/api/v10/channels/{DISCORD_THREAD_ID}/messages"
    headers = {
        "Authorization": DISCORD_AUTH_TOKEN,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "sec-ch-ua-platform": "\"Linux\"",
        "x-debug-options": "bugReporterEnabled",
        "sec-ch-ua": "\"Brave\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
        "sec-ch-ua-mobile": "?0",
        "x-discord-timezone": "Asia/Jakarta",
        "x-super-properties": "eyJvcyI6IkFuZHJvaWQiLCJicm93c2VyIjoiQW5kcm9pZCBDaHJvbWUiLCJkZXZpY2UiOiJBbmRyb2lkIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFgxMTsgTGludXggeDg2XzY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTM1LjAuMC4wIFNhZmFyaS81MzcuMzYiLCJicm93c2VyX3ZlcnNpb24iOiIxMzUuMC4wLjAiLCJvc192ZXJzaW9uIjoiIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjM4ODI1NywiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbCwiaGFzX2NsaWVudF9tb2RzIjpmYWxzZX0=",
        "x-discord-locale": "en-US",
        "sec-gpc": "1",
        "accept-language": "en-US,en;q=0.5",
        "origin": "https://discord.com",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": f"https://discord.com/channels/1359368728034279614/1359688462550175887/threads/{DISCORD_THREAD_ID}",
        "priority": "u=1, i",
    }
    payload = {
        "mobile_network_type": "unknown",
        "content": message[:2000],  # Batasi 2000 karakter sesuai Discord
        "nonce": str(int(time.time() * 1000)),
        "tts": False,
        "flags": 0
    }

    # Tambahkan delay 5 detik sebelum mengirim pesan
    logger.info("Menunggu 5 detik sebelum mengirim pesan ke Discord...")
    await asyncio.sleep(7)
    logger.info("Delay selesai, mengirim pesan ke Discord.")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response_text = await response.text()
                logger.debug(f"Discord response: {response.status} - {response_text}")
                if response.status == 200:
                    logger.info(f"Pesan berhasil dikirim ke thread Discord {DISCORD_THREAD_ID}")
                    return True
                elif response.status == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    logger.warning(f"Rate limit tercapai. Menunggu {retry_after} detik...")
                    await asyncio.sleep(retry_after)
                    return False
                else:
                    logger.critical(f"Gagal mengirim pesan ke thread Discord {DISCORD_THREAD_ID}: {response.status} - {response_text}")
                    return False
        except Exception as e:
            logger.critical(f"Error saat mengirim pesan ke Discord: {str(e)}")
            return False
