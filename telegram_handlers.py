import json
from telethon import events
from config import FILTERED_CHANNELS, UNFILTERED_CHANNELS, VIP_CHANNELS, KEYWORDS, ADMINS, TARGET_CHANNEL, DISCORD_THREAD_ID, setup_logging
from utils import extract_username, contains_keyword, translate_text
from discord_utils import send_message_to_discord_thread

# Inisialisasi logger
logger = setup_logging()

# Fungsi untuk memperbarui channel yang dipantau
async def update_monitored_chats(client):
    """
    Memperbarui daftar channel yang dipantau oleh bot.
    
    Args:
        client: Objek TelegramClient.
    """
    chats = FILTERED_CHANNELS + UNFILTERED_CHANNELS + VIP_CHANNELS
    if not chats:
        logger.warning("Tidak ada channel yang dipantau.")
        return
    try:
        client.remove_event_handler(forward_message)
        client.add_event_handler(forward_message, events.NewMessage(chats=chats))
        logger.info("Channel yang dipantau diperbarui.")
    except Exception as e:
        logger.critical(f"Gagal memperbarui channel yang dipantau: {str(e)}")
        raise

# Fungsi untuk meneruskan pesan
async def forward_message(event):
    try:
        message = event.message
        chat_id = event.chat_id
        source_username = f"@{event.chat.username}" if event.chat.username else f"Channel ID: {chat_id}"
        logger.debug(f"Memproses pesan {message.id} dari {chat_id}")

        translated_text = message.text
        if message.text:
            translated_text = await translate_text(message.text)
            base_message = f"{translated_text} - {source_username}"
        else:
            base_message = f"(Tidak ada teks) - {source_username}"

        # Tentukan opsi pengiriman untuk Telegram
        send_options = {}
        if chat_id in VIP_CHANNELS or chat_id in FILTERED_CHANNELS:
            send_options['link_preview'] = False  # Nonaktifkan pratinjau tautan di Telegram

        # Tentukan apakah pesan Discord harus dibungkus untuk mencegah embed
        discord_message = base_message
        if chat_id in VIP_CHANNELS or chat_id in FILTERED_CHANNELS:
            discord_message = f"{base_message}"  # Bungkus dengan < > untuk mencegah embed di Discord

        if chat_id in VIP_CHANNELS:
            final_message_telegram = f"{base_message}"
            final_message_discord = f"### {discord_message}"
            await event.client.send_message(TARGET_CHANNEL, final_message_telegram, **send_options)
            await send_message_to_discord_thread(final_message_discord)
            logger.info(f"Pesan VIP {message.id} diteruskan dari {chat_id} ke {TARGET_CHANNEL} dan Discord thread")
        elif chat_id in FILTERED_CHANNELS:
            if message.text and contains_keyword(message.text, KEYWORDS):
                final_message_telegram = base_message
                final_message_discord = f"### {discord_message}"
                await event.client.send_message(TARGET_CHANNEL, final_message_telegram, **send_options)
                await send_message_to_discord_thread(final_message_discord)
                logger.info(f"Pesan {message.id} diteruskan dari {chat_id} ke {TARGET_CHANNEL} dan Discord thread")
            else:
                logger.info(f"Pesan dari {chat_id} tidak mengandung kata kunci: {message.text}")
        elif chat_id in UNFILTERED_CHANNELS:
            final_message_telegram = base_message
            final_message_discord = f"{base_message}"
            await event.client.send_message(TARGET_CHANNEL, final_message_telegram, **send_options)
            await send_message_to_discord_thread(final_message_discord)
            logger.info(f"Pesan {message.id} diteruskan dari {chat_id} ke {TARGET_CHANNEL} dan Discord thread")
    except Exception as e:
        logger.critical(f"Gagal memproses pesan {message.id}: {str(e)}")
        for admin in ADMINS:
            try:
                await event.client.send_message(int(admin), f"Galat memproses pesan {message.id} dari {source_username}: {str(e)}\nTeks: {message.text}")
            except Exception as send_error:
                logger.error(f"Gagal mengirim pesan ke admin {admin}: {str(send_error)}")

# Handler perintah admin untuk menambah channel ke FILTERED_CHANNELS
async def add_filter_channel(event):
    """
    Menambahkan channel ke daftar FILTERED_CHANNELS.
    
    Args:
        event: Event dari Telethon yang berisi perintah dan data.
    """
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    try:
        entity = await event.client.get_entity(channel_name)
        channel_id = entity.id
        if channel_id > 0:
            channel_id = -1000000000000 - channel_id  # Konversi ke format channel ID
        if channel_id not in FILTERED_CHANNELS:
            FILTERED_CHANNELS.append(channel_id)
            with open('channels.json', 'w') as f:
                json.dump({'FILTERED_CHANNELS': FILTERED_CHANNELS, 'UNFILTERED_CHANNELS': UNFILTERED_CHANNELS, 'VIP_CHANNELS': VIP_CHANNELS}, f)
            await event.reply(f"Channel {channel_name} ditambahkan ke FILTERED_CHANNELS.")
            logger.info(f"Channel {channel_id} ditambahkan ke FILTERED_CHANNELS: {FILTERED_CHANNELS}")
            await update_monitored_chats(event.client)
        else:
            await event.reply(f"Channel {channel_name} sudah ada di FILTERED_CHANNELS.")
    except Exception as e:
        await event.reply(f"Gagal menambah channel: {str(e)}")
        logger.error(f"Galat menambah channel {channel_name}: {str(e)}")

# Handler perintah admin untuk menambah channel ke UNFILTERED_CHANNELS
async def add_unfilter_channel(event):
    """
    Menambahkan channel ke daftar UNFILTERED_CHANNELS.
    
    Args:
        event: Event dari Telethon yang berisi perintah dan data.
    """
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    try:
        entity = await event.client.get_entity(channel_name)
        channel_id = entity.id
        if channel_id > 0:
            channel_id = -1000000000000 - channel_id
        if channel_id not in UNFILTERED_CHANNELS:
            UNFILTERED_CHANNELS.append(channel_id)
            with open('channels.json', 'w') as f:
                json.dump({'FILTERED_CHANNELS': FILTERED_CHANNELS, 'UNFILTERED_CHANNELS': UNFILTERED_CHANNELS, 'VIP_CHANNELS': VIP_CHANNELS}, f)
            await event.reply(f"Channel {channel_name} ditambahkan ke UNFILTERED_CHANNELS.")
            logger.info(f"Channel {channel_id} ditambahkan ke UNFILTERED_CHANNELS: {UNFILTERED_CHANNELS}")
            await update_monitored_chats(event.client)
        else:
            await event.reply(f"Channel {channel_name} sudah ada di UNFILTERED_CHANNELS.")
    except Exception as e:
        await event.reply(f"Gagal menambah channel: {str(e)}")
        logger.error(f"Galat menambah channel {channel_name}: {str(e)}")

# Handler perintah admin untuk menambah kata kunci
async def add_keyword(event):
    """
    Menambahkan kata kunci ke daftar KEYWORDS.
    
    Args:
        event: Event dari Telethon yang berisi perintah dan data.
    """
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    keyword = event.pattern_match.group(1)
    if keyword not in KEYWORDS:
        KEYWORDS.append(keyword)
        with open('keywords.json', 'w') as f:
            json.dump({'KEYWORDS': KEYWORDS}, f)
        await event.reply(f"Kata kunci {keyword} ditambahkan.")
        logger.info(f"Kata kunci {keyword} ditambahkan: {KEYWORDS}")
    else:
        await event.reply(f"Kata kunci {keyword} sudah ada.")

# Handler perintah admin untuk menghapus channel dari FILTERED_CHANNELS
async def remove_filter_channel(event):
    """
    Menghapus channel dari daftar FILTERED_CHANNELS.
    
    Args:
        event: Event dari Telethon yang berisi perintah dan data.
    """
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    try:
        entity = await event.client.get_entity(channel_name)
        channel_id = entity.id
        if channel_id > 0:
            channel_id = -1000000000000 - channel_id
        if channel_id in FILTERED_CHANNELS:
            FILTERED_CHANNELS.remove(channel_id)
            with open('channels.json', 'w') as f:
                json.dump({'FILTERED_CHANNELS': FILTERED_CHANNELS, 'UNFILTERED_CHANNELS': UNFILTERED_CHANNELS, 'VIP_CHANNELS': VIP_CHANNELS}, f)
            await event.reply(f"Channel {channel_name} dihapus dari FILTERED_CHANNELS.")
            logger.info(f"Channel {channel_id} dihapus dari FILTERED_CHANNELS: {FILTERED_CHANNELS}")
            await update_monitored_chats(event.client)
        else:
            await event.reply(f"Channel {channel_name} tidak ditemukan di FILTERED_CHANNELS.")
    except Exception as e:
        await event.reply(f"Gagal menghapus channel: {str(e)}")
        logger.error(f"Galat menghapus channel {channel_name}: {str(e)}")

# Handler perintah admin untuk menghapus channel dari UNFILTERED_CHANNELS
async def remove_unfilter_channel(event):
    """
    Menghapus channel dari daftar UNFILTERED_CHANNELS.
    
    Args:
        event: Event dari Telethon yang berisi perintah dan data.
    """
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    try:
        entity = await event.client.get_entity(channel_name)
        channel_id = entity.id
        if channel_id > 0:
            channel_id = -1000000000000 - channel_id
        if channel_id in UNFILTERED_CHANNELS:
            UNFILTERED_CHANNELS.remove(channel_id)
            with open('channels.json', 'w') as f:
                json.dump({'FILTERED_CHANNELS': FILTERED_CHANNELS, 'UNFILTERED_CHANNELS': UNFILTERED_CHANNELS, 'VIP_CHANNELS': VIP_CHANNELS}, f)
            await event.reply(f"Channel {channel_name} dihapus dari UNFILTERED_CHANNELS.")
            logger.info(f"Channel {channel_id} dihapus dari UNFILTERED_CHANNELS: {UNFILTERED_CHANNELS}")
            await update_monitored_chats(event.client)
        else:
            await event.reply(f"Channel {channel_name} tidak ditemukan di UNFILTERED_CHANNELS.")
    except Exception as e:
        await event.reply(f"Gagal menghapus channel: {str(e)}")
        logger.error(f"Galat menghapus channel {channel_name}: {str(e)}")

# Handler perintah admin untuk menghapus kata kunci
async def remove_keyword(event):
    """
    Menghapus kata kunci dari daftar KEYWORDS.
    
    Args:
        event: Event dari Telethon yang berisi perintah dan data.
    """
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    keyword = event.pattern_match.group(1)
    if keyword in KEYWORDS:
        KEYWORDS.remove(keyword)
        with open('keywords.json', 'w') as f:
            json.dump({'KEYWORDS': KEYWORDS}, f)
        await event.reply(f"Kata kunci {keyword} dihapus.")
        logger.info(f"Kata kunci {keyword} dihapus: {KEYWORDS}")
    else:
        await event.reply(f"Kata kunci {keyword} tidak ditemukan.")

# Handler perintah admin untuk menampilkan daftar FILTERED_CHANNELS
async def list_filter_channel(event):
    """
    Menampilkan daftar channel di FILTERED_CHANNELS.
    
    Args:
        event: Event dari Telethon yang berisi perintah dan data.
    """
    if str(event.sender_id) not in ADMINS:
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

# Handler perintah admin untuk menampilkan daftar UNFILTERED_CHANNELS
async def list_unfilter_channel(event):
    """
    Menampilkan daftar channel di UNFILTERED_CHANNELS.
    
    Args:
        event: Event dari Telethon yang berisi perintah dan data.
    """
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    if UNFILTERED_CHANNELS:
        list_str = "Daftar Channel Tanpa Filter:\n"
        for i, channel_id in enumerate(UNFILTERED_CHANNELS):
            try:
                entity = await event.client.get_entity(channel_id)
                name = entity.username or f"Channel ID: {channel_id}"
                list_str += f"{i+1}. @{name}\n"
            except Exception:
                list_str += f"{i+1}. Channel ID: {channel_id} (tidak dapat diambil)\n"
        await event.reply(f"```\n{list_str}\n```")
    else:
        await event.reply("Tidak ada channel di UNFILTERED_CHANNELS.")

# Handler perintah admin untuk menampilkan daftar kata kunci
async def list_keyword(event):
    """
    Menampilkan daftar kata kunci di KEYWORDS.
    
    Args:
        event: Event dari Telethon yang berisi perintah dan data.
    """
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    if KEYWORDS:
        list_str = "Daftar Kata Kunci:\n"
        list_str += "\n".join([f"{i+1}. {keyword}" for i, keyword in enumerate(KEYWORDS)])
        await event.reply(f"```\n{list_str}\n```")
    else:
        await event.reply("Tidak ada kata kunci yang ditambahkan.")

# Handler perintah admin untuk menambah channel ke VIP_CHANNELS
async def add_vip_channel(event):
    """
    Menambahkan channel ke daftar VIP_CHANNELS.
    
    Args:
        event: Event dari Telethon yang berisi perintah dan data.
    """
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    try:
        entity = await event.client.get_entity(channel_name)
        channel_id = entity.id
        if channel_id > 0:
            channel_id = -1000000000000 - channel_id
        if channel_id not in VIP_CHANNELS:
            VIP_CHANNELS.append(channel_id)
            with open('channels.json', 'w') as f:
                json.dump({'FILTERED_CHANNELS': FILTERED_CHANNELS, 'UNFILTERED_CHANNELS': UNFILTERED_CHANNELS, 'VIP_CHANNELS': VIP_CHANNELS}, f)
            await event.reply(f"Channel {channel_name} ditambahkan ke VIP_CHANNELS.")
            logger.info(f"Channel {channel_id} ditambahkan ke VIP_CHANNELS: {VIP_CHANNELS}")
            await update_monitored_chats(event.client)
        else:
            await event.reply(f"Channel {channel_name} sudah ada di VIP_CHANNELS.")
    except Exception as e:
        await event.reply(f"Gagal menambah channel VIP: {str(e)}")
        logger.error(f"Galat menambah channel VIP {channel_name}: {str(e)}")

# Handler perintah admin untuk menampilkan daftar VIP_CHANNELS
async def list_vip_channel(event):
    """
    Menampilkan daftar channel di VIP_CHANNELS.
    
    Args:
        event: Event dari Telethon yang berisi perintah dan data.
    """
    if str(event.sender_id) not in ADMINS:
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

# Handler perintah admin untuk menghapus channel dari VIP_CHANNELS
async def remove_vip_channel(event):
    """
    Menghapus channel dari daftar VIP_CHANNELS.
    
    Args:
        event: Event dari Telethon yang berisi perintah dan data.
    """
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    try:
        entity = await event.client.get_entity(channel_name)
        channel_id = entity.id
        if channel_id > 0:
            channel_id = -1000000000000 - channel_id
        if channel_id in VIP_CHANNELS:
            VIP_CHANNELS.remove(channel_id)
            with open('channels.json', 'w') as f:
                json.dump({'FILTERED_CHANNELS': FILTERED_CHANNELS, 'UNFILTERED_CHANNELS': UNFILTERED_CHANNELS, 'VIP_CHANNELS': VIP_CHANNELS}, f)
            await event.reply(f"Channel {channel_name} dihapus dari VIP_CHANNELS.")
            logger.info(f"Channel {channel_id} dihapus dari VIP_CHANNELS: {VIP_CHANNELS}")
            await update_monitored_chats(event.client)
        else:
            await event.reply(f"Channel {channel_name} tidak ditemukan di VIP_CHANNELS.")
    except Exception as e:
        await event.reply(f"Gagal menghapus channel VIP: {str(e)}")
        logger.error(f"Galat menghapus channel VIP {channel_name}: {str(e)}")
