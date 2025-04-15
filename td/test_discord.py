import aiohttp
import asyncio

DISCORD_AUTH_TOKEN = ""

async def test_token():
    headers = {"Authorization": DISCORD_AUTH_TOKEN}
    async with aiohttp.ClientSession() as session:
        async with session.get("https://discord.com/api/v10/users/@me", headers=headers) as resp:
            print(f"Status: {resp.status}")
            print(await resp.text())

asyncio.run(test_token())
