from telethon import events
import json
from config import FILTERED_CHANNELS, UNFILTERED_CHANNELS, VIP_CHANNELS, KEYWORDS, ADMINS, TARGET_CHANNEL, DISCORD_THREAD_ID, setup_logging
from utils import extract_username, contains_keyword, translate_text
from discord_bot import send_discord_message

logger = setup_logging()

# Fungsi untuk memperbarui channel yang dipantau
async def update_monitored_chats(client):
    client.remove_event_handler(forward_message)
    client.add_event_handler(forward_message, events.NewMessage(chats=FILTERED_CHANNELS + UNFILTERED_CHANNELS + VIP_CHANNELS))
    logger.info("Channel yang dipantau diperbarui.")

# Handler untuk meneruskan pesan dari channel yang dipantau
@events.register(events.NewMessage(chats=FILTERED_CHANNELS + UNFILTERED_CHANNELS + VIP_CHANNELS))
async def forward_message(event):
    try:
        message = event.message
        chat_id = event.chat.id
        source_username = f"@{event.chat.username}" if event.chat.username else f"Channel ID: {chat_id}"
        logger.debug(f"Memproses pesan {message.id} dari {chat_id}")

        translated_text = message.text
        if message.text:
            translated_text = await translate_text(message.text)
            base_message = f"{translated_text} - {source_username}"
        else:
            base_message = f"(Tidak ada teks) - {source_username}"

        if chat_id in VIP_CHANNELS:
            final_message_telegram = f"**[VIP] {base_message}**"
            final_message_discord = f"### **[VIP] {base_message}**"
            await event.client.send_message(TARGET_CHANNEL, final_message_telegram)
            await send_discord_message(DISCORD_THREAD_ID, final_message_discord)
            logger.info(f"Pesan VIP {message.id} diteruskan dari {chat_id} ke {TARGET_CHANNEL} dan Discord thread")
        elif chat_id in FILTERED_CHANNELS:
            if message.text and contains_keyword(message.text, KEYWORDS):
                final_message_telegram = base_message
                final_message_discord = f"### **{base_message}**"
                await event.client.send_message(TARGET_CHANNEL, final_message_telegram)
                await send_discord_message(DISCORD_THREAD_ID, final_message_discord)
                logger.info(f"Pesan {message.id} diteruskan dari {chat_id} ke {TARGET_CHANNEL} dan Discord thread")
            else:
                logger.info(f"Pesan dari {chat_id} tidak mengandung kata kunci: {message.text}")
        elif chat_id in UNFILTERED_CHANNELS:
            final_message_telegram = base_message
            final_message_discord = f"**{base_message}**"
            await event.client.send_message(TARGET_CHANNEL, final_message_telegram)
            await send_discord_message(DISCORD_THREAD_ID, final_message_discord)
            logger.info(f"Pesan {message.id} diteruskan dari {chat_id} ke {TARGET_CHANNEL} dan Discord thread")
    except Exception as e:
        logger.error(f"Gagal memproses pesan {message.id}: {str(e)}")
        for admin in ADMINS:
            await event.client.send_message(int(admin), f"Galat memproses pesan {message.id} dari {source_username}: {str(e)}\nTeks: {message.text}")

# Handler untuk menambah channel filter
@events.register(events.NewMessage(pattern='/add_filter_channel (.+)'))
async def add_filter_channel(event):
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    try:
        entity = await event.client.get_entity(channel_name)
        channel_id = entity.id
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

# Handler untuk menambah channel tanpa filter
@events.register(events.NewMessage(pattern='/add_unfilter_channel (.+)'))
async def add_unfilter_channel(event):
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    try:
        entity = await event.client.get_entity(channel_name)
        channel_id = entity.id
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

# Handler untuk menambah kata kunci
@events.register(events.NewMessage(pattern='/add_keyword (.+)'))
async def add_keyword(event):
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

# Handler untuk menghapus channel filter
@events.register(events.NewMessage(pattern='/remove_filter_channel (.+)'))
async def remove_filter_channel(event):
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    try:
        entity = await event.client.get_entity(channel_name)
        channel_id = entity.id
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

# Handler untuk menghapus channel tanpa filter
@events.register(events.NewMessage(pattern='/remove_unfilter_channel (.+)'))
async def remove_unfilter_channel(event):
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    try:
        entity = await event.client.get_entity(channel_name)
        channel_id = entity.id
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

# Handler untuk menghapus kata kunci
@events.register(events.NewMessage(pattern='/remove_keyword (.+)'))
async def remove_keyword(event):
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

# Handler untuk menampilkan daftar channel filter
@events.register(events.NewMessage(pattern='/list_filter'))
async def list_filter_channel(event):
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    if FILTERED_CHANNELS:
        list_str = "Daftar Channel Filter:\n"
        list_str += "\n".join([f"{i+1}. Channel ID: {channel}" for i, channel in enumerate(FILTERED_CHANNELS)])
        await event.reply(f"```\n{list_str}\n```")
    else:
        await event.reply("Tidak ada channel di FILTERED_CHANNELS.")

# Handler untuk menampilkan daftar channel tanpa filter
@events.register(events.NewMessage(pattern='/list_unfilter'))
async def list_unfilter_channel(event):
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    if UNFILTERED_CHANNELS:
        list_str = "Daftar Channel Tanpa Filter:\n"
        list_str += "\n".join([f"{i+1}. Channel ID: {channel}" for i, channel in enumerate(UNFILTERED_CHANNELS)])
        await event.reply(f"```\n{list_str}\n```")
    else:
        await event.reply("Tidak ada channel di UNFILTERED_CHANNELS.")

# Handler untuk menampilkan daftar kata kunci
@events.register(events.NewMessage(pattern='/list_keyword'))
async def list_keyword(event):
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    if KEYWORDS:
        list_str = "Daftar Kata Kunci:\n"
        list_str += "\n".join([f"{i+1}. {keyword}" for i, keyword in enumerate(KEYWORDS)])
        await event.reply(f"```\n{list_str}\n```")
    else:
        await event.reply("Tidak ada kata kunci yang ditambahkan.")

# Handler untuk menambah channel VIP
@events.register(events.NewMessage(pattern='/add_vip_channel (.+)'))
async def add_vip_channel(event):
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    try:
        entity = await event.client.get_entity(channel_name)
        channel_id = entity.id
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

# Handler untuk menampilkan daftar channel VIP
@events.register(events.NewMessage(pattern='/list_vip'))
async def list_vip_channel(event):
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    if VIP_CHANNELS:
        list_str = "Daftar Channel VIP:\n"
        list_str += "\n".join([f"{i+1}. Channel ID: {channel}" for i, channel in enumerate(VIP_CHANNELS)])
        await event.reply(f"```\n{list_str}\n```")
    else:
        await event.reply("Tidak ada channel di VIP_CHANNELS.")

# Handler untuk menghapus channel VIP
@events.register(events.NewMessage(pattern='/remove_vip_channel (.+)'))
async def remove_vip_channel(event):
    if str(event.sender_id) not in ADMINS:
        await event.reply("Kamu tidak berwenang menggunakan perintah ini.")
        return
    input_str = event.pattern_match.group(1)
    channel_name = extract_username(input_str)
    try:
        entity = await event.client.get_entity(channel_name)
        channel_id = entity.id
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
