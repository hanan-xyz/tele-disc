import aiohttp
import asyncio

DISCORD_AUTH_TOKEN = "OTg3MzQ1MTAyMzIwMDQyMDA0.G71_td.2N6peozOjyj-ZaXPZqho8WWZlpJRZBdCHzcD3w"

async def test_token():
    headers = {"Authorization": DISCORD_AUTH_TOKEN}
    async with aiohttp.ClientSession() as session:
        async with session.get("https://discord.com/api/v10/users/@me", headers=headers) as resp:
            print(f"Status: {resp.status}")
            print(await resp.text())

asyncio.run(test_token())