import sys

import trio

from lib.login import check_and_login
from lib.target import get_needed_info
from lib.search import *
import creds


async def main():
    if not creds.email or not creds.password:
        exit("[-] Please fill the credentials in creds.py.")

    link = sys.argv[1]
    if "linkedin.com/in/" in link:
        handle = link.strip("/").split("linkedin.com/in/")[-1].split("/")[0]
    else:
        handle = link

    print(f"[+] Handle : {handle}\n")

    as_client = await check_and_login()

    target = await get_needed_info(as_client, handle)
    print(f"{vars(target)}\n")

    if len(target.last_name) != 2 or not target.last_name.endswith("."):
        await as_client.aclose()
        exit(f"[-] The target does not seems to have a masked name.\nName : {target.first_name} {target.last_name}")

    await search_autocomplete(as_client, target)

    await as_client.aclose()

trio.run(main)