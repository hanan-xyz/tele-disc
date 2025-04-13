# test_discord_thread.py
import aiohttp
import asyncio

DISCORD_AUTH_TOKEN = "OTg3MzQ1MTAyMzIwMDQyMDA0.G71_td.2N6peozOjyj-ZaXPZqho8WWZlpJRZBdCHzcD3w"  # Ganti dengan token Anda
DISCORD_THREAD_ID = "1359690390646816880"

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