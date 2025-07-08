import asyncio
from datetime import datetime
from dotenv import load_dotenv
import os
import pytz
from data_exporter import json_format, member_csv

from spond import spond
from monzo.authentication import Authentication


### Environment variables
load_dotenv()
## Spond
username = os.getenv('SPOND_USERNAME')
password = os.getenv('SPOND_PASSWORD')
group_id_jnp = os.getenv('GROUP_ID_JNP')
group_id_archers = os.getenv('GROUP_ID_ARCHERS')
group_id_test = os.getenv('GROUP_ID_TEST')
current_group = group_id_test
## Monzo
# client_id = os.getenv('MONZO_CLIENT_ID')
# client_secret = os.getenv('MONZO_CLIENT_SECRET')
# redirect_uri = os.getenv('MONZO_REDIRECT_URI')


def display_next_event(group, events, members_dict, profile_dict):
    event = events[0]

    ### Testing with Date/Time info
    event_start_time_string = event["startTimestamp"]
    event_end_time_string = event["endTimestamp"]
    event_start_time = datetime.strptime(event_start_time_string, "%Y-%m-%dT%H:%M:%SZ")
    event_end_time = datetime.strptime(event_end_time_string, "%Y-%m-%dT%H:%M:%SZ")
    bst = pytz.timezone('Europe/London')
    print(bst.localize(event_start_time))
    print(bst.localize(event_end_time))

    ### Parsing responses
    accepted_id_list = event["responses"]["acceptedIds"]

    print("Participants")
    for mem_id in accepted_id_list:
        first_name = members_dict[mem_id]["first_name"]
        last_name = members_dict[mem_id]["last_name"]
        print(mem_id, first_name, last_name)
    print(f'Total participants: {len(accepted_id_list)}\n')

    ### Reading text file of paid members
    file = open("paid.txt")
    
    paid_people_list = file.read().splitlines()
    # print(paid_list)
    
    file.close()

    ### Using native get_person
    paid_id_list = []
    print("Paid")
    for paid_person_id in paid_people_list:
        paid_id_list.append(paid_person_id)
        print(paid_person_id, members_dict[paid_person_id]["first_name"], members_dict[paid_person_id]["last_name"])
    print(f'Total paid: {len(paid_id_list)}\n')

    ### Matching attendance list to paid list
    # Can match id in paid_people to id in accepted_list
    print("Not Paid")
    not_paid_counter = 0
    not_paid_id_list = []
    for not_paid_person_id in accepted_id_list:
        if not_paid_person_id not in paid_id_list:
            not_paid_id_list.append(not_paid_person_id)
            print(not_paid_person_id, members_dict[not_paid_person_id]["first_name"], members_dict[not_paid_person_id]["last_name"])
            not_paid_counter += 1
    print(f'Total not paid: {not_paid_counter}\n')

    return not_paid_id_list

def testing(group, events, members_dict, profile_dict):
    print(f'Written to file: {json_format(group, "Group_Archers_JSON")}')
    print(f'Written to file: {json_format(events, "Events_Archers_JSON")}')
    print(f'Written to file: {json_format(members_dict, "Members_Archers_JSON")}')
    print(f'Written to file: {json_format(profile_dict, "Profile_Archers_JSON")}')

    write_to_csv = ""
    for member_id in members_dict:
        write_to_csv += f'{member_id},{members_dict[member_id]["first_name"]} {members_dict[member_id]["last_name"]}\n'
    print(f'Written to file: {member_csv(write_to_csv, "Members_Archers_CSV")}\n')


async def main():
    s = spond.Spond(username=username, password=password)

    ### Using placeholder Spond group to test API calls and see format of output JSON
    # group = await s.get_group(group_id_test)
    # events = await s.get_events(group_id_test)
    # json_format(events, "Events_Test_Json")

    ### Make API calls
    ## Spond
    group = await s.get_group(current_group)
    events = await s.get_events(current_group)

    ## Monzo (API integration paused)
    # monzo = Authentication(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
    # print(monzo.authentication_url)
    # input("Press Enter to continue")

    ### Building dictionary for IDs and info
    ## One to hold person's group-specific profile and translate from member_id to profile_id
    ## Other holds person's account profile and translates back from profile_id to member_id
    members_dict = {}
    profile_dict = {}
    for member_id in group["members"]:
        ## Profiles that do not have a picture do not have an "imageUrl" key in their "profile" dict. Inserting None to avoid KeyError
        try:
            if "imageUrl" not in member_id["profile"]:
                member_id["profile"]["imageUrl"] = None
            members_dict[member_id["id"]] = {"first_name": member_id["firstName"],
                                        "last_name": member_id["lastName"],
                                        "profile_id": member_id["profile"]["id"]}
            profile_dict[member_id["profile"]["id"]] = {"first_name": member_id["profile"]["firstName"],
                                                    "last_name": member_id["profile"]["lastName"],
                                                    "image_url": member_id["profile"]["imageUrl"],
                                                    "group_id": member_id["id"]}
        except KeyError:
            print(f'Member {member_id["firstName"]} {member_id["lastName"]} does not have a profile. Ommitting from profile_dict but still present in members_dict.')
            members_dict[member_id["id"]] = {"first_name": member_id["firstName"],
                                             "last_name": member_id["lastName"]}
    
    # Logic control
    state = 0
    not_paid_id_list = []
    while state != -1:
        if state == 0:
            print("-1: quit\n0: idle\n1: view next event info\n2: amend participant responses\n3: diagnostics")
            state_temp = None
            valid_states = [-1, 0, 1, 2, 3]
            while state_temp not in valid_states:
                user_input_str = input("Select action: ")
                print("\n")
                try:
                    state_temp = int(user_input_str)
                    if state_temp in valid_states:
                        state = state_temp
                except ValueError:
                    print("Invalid input")
            state = state_temp
        if state == 1:
            not_paid_id_list = display_next_event(group, events, members_dict, profile_dict)
            state = 0
        if state == 2:
            event_id = events[0]["id"]
            
            for member in not_paid_id_list:
                await s.change_response(event_id, member, {"accepted": "false"})
                print(f"Member {members_dict[member]['first_name']} {members_dict[member]['last_name']} has been moved off 'attending' list.")
            
            state = 0
        if state == 3:
            testing(group, events, members_dict, profile_dict)
            state = 0


    await s.clientsession.close()

asyncio.run(main())