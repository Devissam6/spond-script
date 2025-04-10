import asyncio
from spond import spond
from dotenv import load_dotenv
import os

from json_formatter import json_format

load_dotenv()

username = os.getenv('SPOND_USERNAME')
password = os.getenv('SPOND_PASSWORD')
group_id_jnp = os.getenv('GROUP_ID_JNP')
group_id_archers = os.getenv('GROUP_ID_ARCHERS')
group_id_test = os.getenv('GROUP_ID_TEST')

async def main():
    s = spond.Spond(username=username, password=password)
    group = await s.get_group(group_id_test)
    events = await s.get_events(group_id_test)
    json_format(events, "Events_Test_Json")

    await s.clientsession.close()

asyncio.run(main())