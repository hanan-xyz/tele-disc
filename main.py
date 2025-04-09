# main.py
import asyncio
import signal
from datetime import datetime
from telethon import TelegramClient
from config import setup_logging, load_env, load_config, API_ID, API_HASH, PHONE, TARGET_CHANNEL, FILTERED_CHANNELS, UNFILTERED_CHANNELS, VIP_CHANNELS
from telegram_handlers import forward_message, add_filter_channel, add_unfilter_channel, add_keyword, remove_filter_channel, remove_unfilter_channel, remove_keyword, list_filter_channel, list_unfilter_channel, list_keyword, add_vip_channel, list_vip_channel, remove_vip_channel
from utils import login, shutdown_client

logger = setup_logging()
client = TelegramClient('telegram_session', API_ID, API_HASH)

# Tambahkan semua handler
client.on(events.NewMessage(chats=FILTERED_CHANNELS + UNFILTERED_CHANNELS + VIP_CHANNELS))(forward_message)
client.on(events.NewMessage(pattern='/add_filter_channel (.+)'))(add_filter_channel)
client.on(events.NewMessage(pattern='/add_unfilter_channel (.+)'))(add_unfilter_channel)
client.on(events.NewMessage(pattern='/add_keyword (.+)'))(add_keyword)
client.on(events.NewMessage(pattern='/remove_filter_channel (.+)'))(remove_filter_channel)
client.on(events.NewMessage(pattern='/remove_unfilter_channel (.+)'))(remove_unfilter_channel)
client.on(events.NewMessage(pattern='/remove_keyword (.+)'))(remove_keyword)
client.on(events.NewMessage(pattern='/list_filter'))(list_filter_channel)
client.on(events.NewMessage(pattern='/list_unfilter'))(list_unfilter_channel)
client.on(events.NewMessage(pattern='/list_keyword'))(list_keyword)
client.on(events.NewMessage(pattern='/add_vip_channel (.+)'))(add_vip_channel)  # Handler baru
client.on(events.NewMessage(pattern='/list_vip'))(list_vip_channel)  # Handler baru
client.on(events.NewMessage(pattern='/remove_vip_channel (.+)'))(remove_vip_channel)  # Handler baru

async def main():
    try:
        await login(client)
        logger.info("Klien berjalan, memantau channel...")
        print(f"Skrip berjalan pada {datetime.now()}. Periksa telegram_forwarder.log untuk detail.")
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Galat di fungsi utama: {str(e)}")
        print(f"Terjadi kesalahan, periksa log untuk detail: {str(e)}")

if __name__ == "__main__":
    load_env()
    load_config()
    loop = asyncio.get_event_loop()
    task = loop.create_task(main())

    def handle_interrupt():
        logger.info("Menerima sinyal shutdown, menghentikan klien...")
        loop.create_task(shutdown_client(client))

    signal.signal(signal.SIGINT, lambda s, f: handle_interrupt())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(asyncio.sleep(1))
        loop.close()
        logger.info("Skrip selesai.")
