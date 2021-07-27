import json

from lib.utils import *


class Target:
    first_name = ""
    last_name = ""
    urn = ""

async def get_needed_info(as_client, handle):
    req = await as_client.get(f"https://www.linkedin.com/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity={handle}&decorationId=com.linkedin.voyager.dash.deco.identity.profile.FullProfile-64")

    if req.status_code != 200:
        await safe_exit(as_client, f"[-] Can't request the endpoint, response code : {req.status_code}\n\n Text : {req.text}")

    data = json.loads(req.text)
    if not data["elements"]:
        await safe_exit(as_client, f"[-] This member does not exist.\nAre you sure you can access it at https://www.linkedin.com/in/{handle} ?")

    target = Target()
        
    target.urn = data["elements"][0]["objectUrn"]
    target.first_name = data["elements"][0]["firstName"]
    target.last_name = data["elements"][0]["lastName"]

    return target