import asyncio
from datetime import datetime
import pytz
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

    ### Using placeholder Spond group to test API calls and see format of output JSON
    # group = await s.get_group(group_id_test)
    # events = await s.get_events(group_id_test)
    # json_format(events, "Events_Test_Json")

    ### Make API calls
    group = await s.get_group(group_id_archers)
    events = await s.get_events(group_id_archers)
    # json_format(group, "Group_Archers_JSON")
    # json_format(events, "Events_Archers_JSON")

    event = events[0]

    ### Testing with Date/Time info
    # event_start_time_string = event["startTimestamp"]
    # event_end_time_string = event["endTimestamp"]
    # event_start_time = datetime.strptime(event_start_time_string, "%Y-%m-%dT%H:%M:%SZ")
    # event_end_time = datetime.strptime(event_end_time_string, "%Y-%m-%dT%H:%M:%SZ")
    # bst = pytz.timezone('Europe/London')
    # print(bst.localize(event_start_time))
    # print(bst.localize(event_end_time))

    ### Building dictionary for IDs and info
    members_dict = {}
    for member in group["members"]:
        ## Profiles that do not have a picture do not have an "imageUrl" key in their "profile" dict. Inserting None to avoid KeyError
        if "imageUrl" not in member["profile"]:
            member["profile"]["imageUrl"] = None
        members_dict[member["id"]] = {"first_name": member["firstName"],
                                      "last_name": member["lastName"],
                                      "profile_id": member["profile"]["id"],
                                      "profile_first_name": member["profile"]["firstName"],
                                      "profile_last_name": member["profile"]["lastName"],
                                      "profile_image_url": member["profile"]["imageUrl"]}
    
        


    ### Parsing responses
    accepted_list = event["responses"]["acceptedIds"]
    for mem_id in accepted_list:
        first_name = members_dict[mem_id]["first_name"]
        last_name = members_dict[mem_id]["last_name"]
        image = members_dict[mem_id]["profile_image_url"]
        print(mem_id, first_name, last_name, image)

    await s.clientsession.close()

asyncio.run(main())