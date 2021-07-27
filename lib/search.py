import json
from pprint import pprint
from urllib.parse import quote

import trio

from lib.utils import *
import config


async def is_name_good(as_client, target, tmprinter, guessed_name, limiter):
    global found_fullname
    async def do_query(query, start, guessed_name, limiter):
        global found_fullname
        async with limiter:
            req = await as_client.get(f"https://www.linkedin.com/voyager/api/voyagerMessagingTypeaheadHits?keyword=%22{query}%22&q=typeaheadKeyword&types=List(PEOPLE)&start={start}&count=100")
            if req.status_code == 429:
                tmprinter.clear()
                await safe_exit(as_client, "[-] Rate limit detected.")
            data = json.loads(req.text)
            for element in data["elements"]:
                member_urn = element["hitInfo"]['com.linkedin.voyager.typeahead.TypeaheadHitV2']["image"]["attributes"][0]["miniProfile"]["objectUrn"]
                if target.urn == member_urn:
                    found_fullname = True
                    tmprinter.clear()
                    print("[+] Finished !")
                    guessed_name = guessed_name.strip()
                    print(f"[+] Fullname => {target.first_name} {guessed_name.capitalize()}")
                    break

    query = quote(f"{target.first_name.lower()} {guessed_name.strip()}")
    found_fullname = False
    async with trio.open_nursery() as nursery:
        for start in range(0,config.max_paging*100,100):
            nursery.start_soon(do_query, query, start, guessed_name, limiter)

    return found_fullname

async def search_autocomplete(as_client, target):
    global found, guessed_name
    async def do_query(query, start, char, limiter):
        global found, guessed_name

        async with limiter:
            req = await as_client.get(f"https://www.linkedin.com/voyager/api/voyagerMessagingTypeaheadHits?keyword={query}&q=typeaheadKeyword&types=List(PEOPLE)&start={start}&count=100")
            if req.status_code == 429:
                tmprinter.clear()
                await safe_exit(as_client, "[-] Rate limit detected.")
            data = json.loads(req.text)
            for element in data["elements"]:
                member_urn = element["hitInfo"]['com.linkedin.voyager.typeahead.TypeaheadHitV2']["image"]["attributes"][0]["miniProfile"]["objectUrn"]
                if target.urn == member_urn:
                    found = True
                    tmprinter.clear()
                    guessed_name += char
                    print(f"[+] Last name => {guessed_name}")
                    break

    charset = get_charset() # a-z + space
    limiter = trio.CapacityLimiter(10)

    guessed_name = target.last_name[0].lower() # Debut

    tmprinter = TMPrinter()
    while True:
        for start in range(0,config.max_paging*100,100):
            tmprinter.out(f"Paging => {start}/{config.max_paging*100}")
            found = False
            async with trio.open_nursery() as nursery:
                for char in charset:
                    query = quote(f"{target.first_name.lower()} {guessed_name+char}")
                    nursery.start_soon(do_query, query, start, char, limiter)

            if found:
                if guessed_name[-1] == " ":
                    tmprinter.clear()
                    print("Space detected, checking if the extracted name is the full name...")
                    found_fullname = await is_name_good(as_client, target, tmprinter, guessed_name, limiter)
                    if found_fullname:
                        await safe_exit(as_client, "")

                break
