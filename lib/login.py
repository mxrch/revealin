import httpx
import trio
from bs4 import BeautifulSoup as bs

import creds
import config

import json
from pprint import pprint
from pathlib import Path


async def check_session():
    """
    To avoid login everytime, we save the cookies so we can check them later.
    """

    if not Path(config.cookies_file).is_file():
        return False

    cookies = None
    with open(config.cookies_file, 'r') as f:
        cookies = json.loads(f.read())

    as_client = httpx.AsyncClient(cookies=cookies)

    req = await as_client.get("https://www.linkedin.com/in/me", allow_redirects=False)
    if req.status_code == 200:
        return as_client
    else:
        return False

async def check_and_login():
    as_client = await check_session()
    if not as_client:
        print("[DEBUG] Cookie no more active, I re-login...")
        as_client = await login()
        if not as_client:
            exit("[DEBUG] I can't login, are you sure your credentials are correct ?")
        print("[DEBUG] Cookies re-generated and valid !")
    else:
        print("[DEBUG] Cookie valid !")

    as_client.headers = {**config.headers, **{
        "Csrf-Token": as_client.cookies["JSESSIONID"].strip('"'),
        "X-Restli-Protocol-Version": "2.0.0"
        }}
    as_client.timeout = config.timeout

    return as_client

async def login():
    as_client = httpx.AsyncClient()

    req = await as_client.get("https://www.linkedin.com")
    body = bs(req.text, "html.parser")

    input_login = body.find("input", {"name": "loginCsrfParam"})
    csrf_login = input_login.attrs["value"]

    data = {
        "session_key": creds.email,
        "loginCsrfParam": csrf_login,
        "session_password": creds.password
    }

    req = await as_client.post("https://www.linkedin.com/checkpoint/lg/login-submit", allow_redirects=False, data=data)
    if req.status_code == 200:
        with open(config.cookies_file, "w") as f:
            f.write(json.dumps(dict(as_client.cookies)))

        return as_client

    return False