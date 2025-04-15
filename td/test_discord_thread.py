# test_discord_thread.py
import aiohttp
import asyncio

DISCORD_AUTH_TOKEN = ""  # Ganti dengan token Anda
DISCORD_THREAD_ID = ""

async def test_thread_access():
    url = f"https://discord.com/api/v10/channels/{DISCORD_THREAD_ID}"
    headers = {
        "Authorization": DISCORD_AUTH_TOKEN,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            print(f"Status: {response.status}")
            print(await response.text())

asyncio.run(test_thread_access())
