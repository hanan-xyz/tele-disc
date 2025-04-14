# telegram_handlers.py
import json
import re
import os
import tempfile
from collections import deque
from telethon import events
from telethon.tl.types import MessageMediaPhoto
from config import FILTERED_CHANNELS, UNFILTERED_CHANNELS, VIP_CHANNELS, SUMMARY_CHANNELS, IMAGE_CHANNELS, KEYWORDS, SUMMARY_KEYWORDS, BLOCKED_KEYWORDS, ADMINS, TARGET_CHANNEL, DISCORD_THREAD_ID, logger
from utils import extract_username, contains_keyword, contains_blocked_keyword, translate_text, remove_markdown, contains_username
from discord_utils import send_message_to_discord_thread, failed_message_queue

# Gunakan deque untuk melacak pesan yang sudah diproses (batas maksimal 1000 pesan)
processed_messages = deque(maxlen=1000)

async def update_monitored_chats(client):
    """
    Memperbarui daftar channel yang dipantau oleh bot.
    
    Args:
        client: Objek TelegramClient.
    """
    chats = list(set(FILTERED_CHANNELS + UNFILTERED_CHANNELS + VIP_CHANNELS + SUMMARY_CHANNELS + IMAGE_CHANNELS))
    if not chats:
        logger.warning("Tidak ada channel yang dipantau.")
        return
    
    try:
        client.remove_event_handler(forward_message)  # Hapus handler lama
        client.add_event_handler(forward_message, events.NewMessage(chats=chats))
        logger.info(f"Channel yang dipantau diperbarui: {chats}")
    except Exception as e:
        logger.critical(f"Gagal memperbarui channel yang dipantau: {str(e)}")
        raise

def transform_summary_message(message, for_discord=False):
    """
    Mengubah pesan untuk hanya menampilkan bagian penting dengan format khusus.
    
    Args:
        message (str): Pesan asli.
        for_discord (bool): Jika True, hapus tautan untuk Discord.
    
    Returns:
        str: Pesan yang telah diringkas dan diformat.
    """
    logger.debug(f"Masuk transform_summary_message: {message}, for_discord={for_discord}")
    lines = message.split('\n')
    important_message = lines[0].strip() if lines else message.strip()

    wallet_pattern = r'0x[a-fA-F0-9]{40}'
    wallets = re.findall(wallet_pattern, important_message)
    for wallet in wallets:
        shortened_wallet = f"{wallet[:3]}...{wallet[-2:]}"
        important_message = important_message.replace(wallet, shortened_wallet)

    url_pattern = r'(https?://[^\s]+)'
    if for_discord:
        important_message = re.sub(url_pattern, '', important_message)
    else:
        urls = re.findall(url_pattern, important_message)
        for url in urls:
            modified_url = url.replace('.', '[.]', 1)
            important_message = important_message.replace(url, modified_url)

    cleaned_message = important_message.strip()
    logger.debug(f"Keluar transform_summary_message: {cleaned_message}")
    return cleaned_message

async def forward_message(event):
    """
    Meneruskan pesan dari channel sumber ke target berdasarkan aturan.
    
    Args:
        event: Event dari Telethon yang berisi pesan baru.
    """
    try:
        message = event.message
        chat_id = event.chat_id
        message_id = message.id
        
        unique_id = f"{chat_id}:{message_id}"
        if unique_id in processed_messages:
            logger.debug(f"Pesan {unique_id} sudah diproses, dilewati.")
            return
        
        processed_messages.append(unique_id)
        
        source_username = f"@{event.chat.username}" if event.chat.username else f"Channel ID: {chat_id}"
        logger.info(f"Memproses pesan {message.id} dari {chat_id}: {message.text}")

        # Tangani pesan bergambar dari IMAGE_CHANNELS
        if chat_id in IMAGE_CHANNELS and message.media and isinstance(message.media, MessageMediaPhoto):
            translated_text = ""
            if message.text:
                if contains_username(message.text):
                    logger.debug(f"Pesan mengandung username, melewati terjemahan: {message.text}")
                    translated_text = message.text.strip()
                else:
                    translated_text = await translate_text(message.text.strip())
                    logger.debug(f"Teks setelah terjemahan (image): {translated_text}")
                translated_text = remove_markdown(translated_text)
                logger.debug(f"Teks setelah remove_markdown (image): {translated_text}")
            else:
                translated_text = ""

            final_message_telegram = f"{translated_text} - {source_username}" if translated_text else f"- {source_username}"
            await event.client.send_message(TARGET_CHANNEL, file=message.media, message=final_message_telegram)
            logger.info(f"Pesan bergambar {message.id} diteruskan dari {chat_id} ke {TARGET_CHANNEL}")
            
            final_message_discord = f"## {translated_text} - {source_username}" if translated_text else f"- {source_username}"
            if translated_text and contains_blocked_keyword(translated_text, BLOCKED_KEYWORDS):
                logger.warning(f"Pesan {message.id} tidak dikirim ke Discord karena mengandung kata yang diblokir: {translated_text}")
                await failed_message_queue.put((final_message_discord, "Mengandung kata yang diblokir"))
            else:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                media_path = temp_file.name
                try:
                    await event.client.download_media(message.media, media_path)
                    await send_message_to_discord_thread(final_message_discord, media_path=media_path)
                    logger.info(f"Pesan bergambar {message.id} dikirim ke antrian Discord dari {chat_id}")
                except Exception as e:
                    logger.error(f"Gagal mengunduh atau mengirim gambar ke Discord: {str(e)}")
                    await failed_message_queue.put((final_message_discord, f"Gagal mengunduh gambar: {str(e)}"))
                finally:
                    temp_file.close()
            return

        # Tangani pesan teks
        translated_text = message.text
        if message.text:
            if contains_username(message.text):
                logger.debug(f"Pesan mengandung username, melewati terjemahan: {message.text}")
                translated_text = message.text.strip()
            else:
                translated_text = await translate_text(message.text.strip())
                logger.debug(f"Teks setelah terjemahan: {translated_text}")
            translated_text = remove_markdown(translated_text)
            logger.debug(f"Teks setelah remove_markdown: {translated_text}")
        else:
            translated_text = "(Tidak ada teks)"

        # Prioritaskan aturan untuk mencegah pemrosesan ganda
        if chat_id in SUMMARY_CHANNELS and message.text and contains_keyword(message.text, SUMMARY_KEYWORDS):
            base_message_telegram = transform_summary_message(translated_text, for_discord=False)
            base_message_discord = transform_summary_message(translated_text, for_discord=True)
            final_message_telegram = f"{base_message_telegram} - {source_username}"
            final_message_discord = f"### {base_message_discord} - {source_username}"
            await event.client.send_message(TARGET_CHANNEL, final_message_telegram)
            if contains_blocked_keyword(base_message_discord, BLOCKED_KEYWORDS):
                logger.warning(f"Pesan {message.id} tidak dikirim ke Discord karena mengandung kata yang diblokir: {base_message_discord}")
                await failed_message_queue.put((final_message_discord, "Mengandung kata yang diblokir"))
            else:
                await send_message_to_discord_thread(final_message_discord)
                logger.info(f"Pesan ringkasan {message.id} diteruskan dari {chat_id} ke {TARGET_CHANNEL} dan antrian Discord")
            return  # Keluar setelah memproses sebagai SUMMARY_CHANNEL
        elif chat_id in VIP_CHANNELS:
            base_message = translated_text
            final_message_telegram = f"**{base_message} - {source_username}**"
            final_message_discord = f"### {base_message} - {source_username}"
            await event.client.send_message(TARGET_CHANNEL, final_message_telegram)
            if contains_blocked_keyword(base_message, BLOCKED_KEYWORDS):
                logger.warning(f"Pesan {message.id} tidak dikirim ke Discord karena mengandung kata yang diblokir: {base_message}")
                await failed_message_queue.put((final_message_discord, "Mengandung kata yang diblokir"))
            else:
                await send_message_to_discord_thread(final_message_discord)
                logger.info(f"Pesan VIP {message.id} diteruskan dari {chat_id} ke {TARGET_CHANNEL} dan antrian Discord")
            return  # Keluar setelah memproses sebagai VIP_CHANNEL
        elif chat_id in FILTERED_CHANNELS and message.text and contains_keyword(message.text, KEYWORDS):
            base_message = translated_text
            final_message_telegram = f"{base_message} - {source_username}"
            final_message_discord = f"### {base_message} - {source_username}"
            await event.client.send_message(TARGET_CHANNEL, final_message_telegram)
            if contains_blocked_keyword(base_message, BLOCKED_KEYWORDS):
                logger.warning(f"Pesan {message.id} tidak dikirim ke Discord karena  karena mengandung kata yang diblokir: {base_message}")
                await failed_message_queue.put((final_message_discord, "Mengandung kata yang diblokir"))
            else:
                await send_message_to_discord_thread(final_message_discord)
                logger.info(f"Pesan {message.id} diteruskan dari {chat_id} ke {TARGET_CHANNEL} dan antrian Discord")
            return  # Keluar setelah memproses sebagai FILTERED_CHANNEL
        elif chat_id in UNFILTERED_CHANNELS:
            base_message = translated_text
            final_message_telegram = f"{base_message} - {source_username}"
            final_message_discord = f"{base_message} - {source_username}"
            await event.client.send_message(TARGET_CHANNEL, final_message_telegram)
            if contains_blocked_keyword(base_message, BLOCKED_KEYWORDS):
                logger.warning(f"Pesan {message.id} tidak dikirim ke Discord karena mengandung kata yang diblokir: {base_message}")
                await failed_message_queue.put((final_message_discord, "Mengandung kata yang diblokir"))
            else:
                await send_message_to_discord_thread(final_message_discord)
                logger.info(f"Pesan {message.id} diteruskan dari {chat_id} ke {TARGET_CHANNEL} dan antrian Discord")
            return  # Keluar setelah memproses sebagai UNFILTERED_CHANNEL
        else:
            logger.info(f"Pesan dari {chat_id} tidak memenuhi kriteria pengiriman: {message.text}")
    
    except Exception as e:
        logger.critical(f"Gagal memproses pesan {message.id}: {str(e)}")
        for admin in ADMINS:
            try:
                await event.client.send_message(int(admin), f"Galat memproses pesan {message.id} dari {source_username}: {str(e)}\nTeks: {message.text}")
            except Exception as send_error:
                logger.error(f"Gagal mengirim pesan ke admin {admin}: {str(send_error)}")

async def update_channel_list(event, channel_list, list_name, action, channel_name):
    """
    Utilitas untuk menambah atau menghapus channel dari daftar.
    
    Args:
        event: Event dari Telethon.
        channel_list: Daftar channel yang akan diubah.
        list_name: Nama daftar (untuk logging dan pesan).
        action: 'add' atau 'remove'.
        channel_name: Nama atau ID channel.
    """
    if event.sender_id not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    
    try:
        entity = await event.client.get_entity(channel_name)
        channel_id = entity.id
        if channel_id > 0:
            channel_id = -1000000000000 - channel_id
        
        if action == "add" and channel_id not in channel_list:
            channel_list.append(channel_id)
            message = f"Channel {channel_name} ditambahkan ke {list_name}."
            logger.info(f"Channel {channel_id} ditambahkan ke {list_name}: {channel_list}")
        elif action == "remove" and channel_id in channel_list:
            channel_list.remove(channel_id)
            message = f"Channel {channel_name} dihapus dari {list_name}."
            logger.info(f"Channel {channel_id} dihapus dari {list_name}: {channel_list}")
        else:
            message = f"Channel {channel_name} sudah ada di {list_name}." if action == "add" else f"Channel {channel_name} tidak ditemukan di {list_name}."
            await event.reply(message)
            return
        
        with open('channels.json', 'w') as f:
            json.dump({
                'FILTERED_CHANNELS': FILTERED_CHANNELS,
                'UNFILTERED_CHANNELS': UNFILTERED_CHANNELS,
                'VIP_CHANNELS': VIP_CHANNELS,
                'SUMMARY_CHANNELS': SUMMARY_CHANNELS,
                'IMAGE_CHANNELS': IMAGE_CHANNELS
            }, f)
        await event.reply(message)
        await update_monitored_chats(event.client)
    except Exception as e:
        await event.reply(f"Gagal {action} channel: {str(e)}")
        logger.error(f"Galat {action} channel {channel_name}: {str(e)}")

async def add_image_channel(event):
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    await update_channel_list(event, IMAGE_CHANNELS, "IMAGE_CHANNELS", "add", channel_name)

async def remove_image_channel(event):
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    await update_channel_list(event, IMAGE_CHANNELS, "IMAGE_CHANNELS", "remove", channel_name)

async def list_image_channel(event):
    if event.sender_id not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    
    if IMAGE_CHANNELS:
        list_str = "Daftar Channel Gambar:\n"
        for i, channel_id in enumerate(IMAGE_CHANNELS):
            try:
                entity = await event.client.get_entity(channel_id)
                name = entity.username or f"Channel ID: {channel_id}"
                list_str += f"{i+1}. @{name}\n"
            except Exception:
                list_str += f"{i+1}. Channel ID: {channel_id} (tidak dapat diambil)\n"
        await event.reply(f"```\n{list_str}\n```")
    else:
        await event.reply("Tidak ada channel di IMAGE_CHANNELS.")

async def add_summary_channel(event):
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    await update_channel_list(event, SUMMARY_CHANNELS, "SUMMARY_CHANNELS", "add", channel_name)

async def remove_summary_channel(event):
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    await update_channel_list(event, SUMMARY_CHANNELS, "SUMMARY_CHANNELS", "remove", channel_name)

async def list_summary_channel(event):
    if event.sender_id not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    
    if SUMMARY_CHANNELS:
        list_str = "Daftar Channel Summary:\n"
        for i, channel_id in enumerate(SUMMARY_CHANNELS):
            try:
                entity = await event.client.get_entity(channel_id)
                name = entity.username or f"Channel ID: {channel_id}"
                list_str += f"{i+1}. @{name}\n"
            except Exception:
                list_str += f"{i+1}. Channel ID: {channel_id} (tidak dapat diambil)\n"
        await event.reply(f"```\n{list_str}\n```")
    else:
        await event.reply("Tidak ada channel di SUMMARY_CHANNELS.")

async def add_keyword_summary(event):
    if event.sender_id not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    
    keyword = event.pattern_match.group(1).strip()
    if keyword not in SUMMARY_KEYWORDS:
        SUMMARY_KEYWORDS.append(keyword)
        with open('summary_keywords.json', 'w') as f:
            json.dump({'SUMMARY_KEYWORDS': SUMMARY_KEYWORDS}, f)
        await event.reply(f"Kata kunci summary {keyword} ditambahkan.")
        logger.info(f"Kata kunci summary {keyword} ditambahkan: {SUMMARY_KEYWORDS}")
    else:
        await event.reply(f"Kata kunci summary {keyword} sudah ada.")

async def remove_keyword_summary(event):
    if event.sender_id not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    
    keyword = event.pattern_match.group(1).strip()
    if keyword in SUMMARY_KEYWORDS:
        SUMMARY_KEYWORDS.remove(keyword)
        with open('summary_keywords.json', 'w') as f:
            json.dump({'SUMMARY_KEYWORDS': SUMMARY_KEYWORDS}, f)
        await event.reply(f"Kata kunci summary {keyword} dihapus.")
        logger.info(f"Kata kunci summary {keyword} dihapus: {SUMMARY_KEYWORDS}")
    else:
        await event.reply(f"Kata kunci summary {keyword} tidak ditemukan.")

async def list_keyword_summary(event):
    if event.sender_id not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    
    if SUMMARY_KEYWORDS:
        list_str = "Daftar Kata Kunci Summary:\n"
        list_str += "\n".join([f"{i+1}. {keyword}" for i, keyword in enumerate(SUMMARY_KEYWORDS)])
        await event.reply(f"```\n{list_str}\n```")
    else:
        await event.reply("Tidak ada kata kunci summary yang ditambahkan.")

async def add_filter_channel(event):
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    await update_channel_list(event, FILTERED_CHANNELS, "FILTERED_CHANNELS", "add", channel_name)

async def add_unfilter_channel(event):
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    await update_channel_list(event, UNFILTERED_CHANNELS, "UNFILTERED_CHANNELS", "add", channel_name)

async def add_keyword(event):
    if event.sender_id not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    
    keyword = event.pattern_match.group(1).strip()
    if keyword not in KEYWORDS:
        KEYWORDS.append(keyword)
        with open('keywords.json', 'w') as f:
            json.dump({'KEYWORDS': KEYWORDS}, f)
        await event.reply(f"Kata kunci {keyword} ditambahkan.")
        logger.info(f"Kata kunci {keyword} ditambahkan: {KEYWORDS}")
    else:
        await event.reply(f"Kata kunci {keyword} sudah ada.")

async def remove_filter_channel(event):
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    await update_channel_list(event, FILTERED_CHANNELS, "FILTERED_CHANNELS", "remove", channel_name)

async def remove_unfilter_channel(event):
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    await update_channel_list(event, UNFILTERED_CHANNELS, "UNFILTERED_CHANNELS", "remove", channel_name)

async def remove_keyword(event):
    if event.sender_id not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    
    keyword = event.pattern_match.group(1).strip()
    if keyword in KEYWORDS:
        KEYWORDS.remove(keyword)
        with open('keywords.json', 'w') as f:
            json.dump({'KEYWORDS': KEYWORDS}, f)
        await event.reply(f"Kata kunci {keyword} dihapus.")
        logger.info(f"Kata kunci {keyword} dihapus: {KEYWORDS}")
    else:
        await event.reply(f"Kata kunci {keyword} tidak ditemukan.")

async def list_filter_channel(event):
    if event.sender_id not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    
    if FILTERED_CHANNELS:
        list_str = "Daftar Channel Filter:\n"
        for i, channel_id in enumerate(FILTERED_CHANNELS):
            try:
                entity = await event.client.get_entity(channel_id)
                name = entity.username or f"Channel ID: {channel_id}"
                list_str += f"{i+1}. @{name}\n"
            except Exception:
                list_str += f"{i+1}. Channel ID: {channel_id} (tidak dapat diambil)\n"
        await event.reply(f"```\n{list_str}\n```")
    else:
        await event.reply("Tidak ada channel di FILTERED_CHANNELS.")

async def list_unfilter_channel(event):
    if event.sender_id not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    
    if UNFILTERED_CHANNELS:
        list_str = "Daftar Channel Tanpa Filter:\n"
        for i, channel_id in enumerate(UNFILTERED_CHANNELS):
            try:
                entity = await event.client.get_entity(channel_id)
                name = entity.username or f"Channel ID: {chat_id}"
                list_str += f"{i+1}. @{name}\n"
            except Exception:
                list_str += f"{i+1}. Channel ID: {channel_id} (tidak dapat diambil)\n"
        await event.reply(f"```\n{list_str}\n```")
    else:
        await event.reply("Tidak ada channel di UNFILTERED_CHANNELS.")

async def list_keyword(event):
    if event.sender_id not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    
    if KEYWORDS:
        list_str = "Daftar Kata Kunci:\n"
        list_str += "\n".join([f"{i+1}. {keyword}" for i, keyword in enumerate(KEYWORDS)])
        await event.reply(f"```\n{list_str}\n```")
    else:
        await event.reply("Tidak ada kata kunci yang ditambahkan.")

async def add_vip_channel(event):
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    await update_channel_list(event, VIP_CHANNELS, "VIP_CHANNELS", "add", channel_name)

async def list_vip_channel(event):
    if event.sender_id not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    
    if VIP_CHANNELS:
        list_str = "Daftar Channel VIP:\n"
        for i, channel_id in enumerate(VIP_CHANNELS):
            try:
                entity = await event.client.get_entity(channel_id)
                name = entity.username or f"Channel ID: {channel_id}"
                list_str += f"{i+1}. @{name}\n"
            except Exception:
                list_str += f"{i+1}. Channel ID: {channel_id} (tidak dapat diambil)\n"
        await event.reply(f"```\n{list_str}\n```")
    else:
        await event.reply("Tidak ada channel di VIP_CHANNELS.")

async def remove_vip_channel(event):
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    await update_channel_list(event, VIP_CHANNELS, "VIP_CHANNELS", "remove", channel_name)

async def add_blocked_keyword(event):
    if event.sender_id not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    
    keyword = event.pattern_match.group(1).strip()
    if keyword not in BLOCKED_KEYWORDS:
        BLOCKED_KEYWORDS.append(keyword)
        with open('blocked_keywords.json', 'w') as f:
            json.dump({'BLOCKED_KEYWORDS': BLOCKED_KEYWORDS}, f)
        await event.reply(f"Kata yang diblokir {keyword} ditambahkan.")
        logger.info(f"Kata yang diblokir {keyword} ditambahkan: {BLOCKED_KEYWORDS}")
    else:
        await event.reply(f"Kata yang diblokir {keyword} sudah ada.")

async def remove_blocked_keyword(event):
    if event.sender_id not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    
    keyword = event.pattern_match.group(1).strip()
    if keyword in BLOCKED_KEYWORDS:
        BLOCKED_KEYWORDS.remove(keyword)
        with open('blocked_keywords.json', 'w') as f:
            json.dump({'BLOCKED_KEYWORDS': BLOCKED_KEYWORDS}, f)
        await event.reply(f"Kata yang diblokir {keyword} dihapus.")
        logger.info(f"Kata yang diblokir {keyword} dihapus: {BLOCKED_KEYWORDS}")
    else:
        await event.reply(f"Kata yang diblokir {keyword} tidak ditemukan.")

async def list_blocked_keyword(event):
    if event.sender_id not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    
    if BLOCKED_KEYWORDS:
        list_str = "Daftar Kata yang Diblokir:\n"
        list_str += "\n".join([f"{i+1}. {keyword}" for i, keyword in enumerate(BLOCKED_KEYWORDS)])
        await event.reply(f"```\n{list_str}\n```")
    else:
        await event.reply("Tidak ada kata yang diblokir.")