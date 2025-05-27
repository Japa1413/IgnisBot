from bot import client
import asyncio

@client.event
async def on_ready():
    print("+++ SYSTEM INITIALIZATION COMPLETE +++")
    await asyncio.sleep(2)
    print("+++ SERVITOR ONLINE +++")
    await asyncio.sleep(2)
    print(f"+++ The Holy Servitor {client.user} has been Awakened! +++")
    await asyncio.sleep(2)
    print("+++ Praise the Omnissiah! +++")
    await asyncio.sleep(2)
    print("+++ Scanning for Heretical Activities... +++")
    await asyncio.sleep(3)
    print("+++ Establishing Connections to the Astronomican... +++")
    await asyncio.sleep(3)
    print("+++ All Systems Nominal. The Imperium's Will Shall Be Done. +++")