import asyncio
from spond import spond
from dotenv import load_dotenv
import os

load_dotenv()

username = os.getenv('SPOND_USERNAME')
password = os.getenv('SPOND_PASSWORD')
group_id = os.getenv('GROUP_ID')

async def main():
    s = spond.Spond(username=username, password=password)
    group = await s.get_group(group_id)
    print(group)
    await s.clientsession.close()

asyncio.run(main())