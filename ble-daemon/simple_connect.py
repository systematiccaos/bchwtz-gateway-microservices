import asyncio
from bleak import BleakClient


async def con():
    address = "C1:FC:9B:69:04:8B"
    async with BleakClient(address) as client:
        print(client)


asyncio.run(con())