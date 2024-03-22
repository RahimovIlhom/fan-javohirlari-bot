import json
import requests
import warnings
from environs import Env

env = Env()
env.read_env()

ADD_USER_URL = env.str("ADD_USER_URL")
CREATE_TOKEN_URL = env.str("CREATE_TOKEN_URL")
ADMISSION_USERNAME = env.str('ADMISSION_USERNAME')
ADMISSION_PASSWORD = env.str('ADMISSION_PASSWORD')


async def get_token():
    warnings.filterwarnings("ignore", message="Unverified HTTPS request")

    user_login = {
        "username": ADMISSION_USERNAME,
        "password": ADMISSION_PASSWORD
    }

    resp = requests.post(CREATE_TOKEN_URL, json=user_login, verify=False)
    return resp


async def post_or_put_data(id, tg_id, language, fullname, phone_number, region, district, school_number, olimpia_science, created_time, update_time, science_1, science_2, science_3, pinfl, *args, **kwargs):
    from loader import db
    warnings.filterwarnings("ignore", message="Unverified HTTPS request")

    BEARER_TOKEN = await db.get_token()
    if BEARER_TOKEN is None:
        resp = await get_token()
        new_token = resp.json()['token']
        await db.add_token(new_token)
        BEARER_TOKEN = new_token
    else:
        BEARER_TOKEN = BEARER_TOKEN[3]

    data = {
        "id": id,
        "telegrammId": tg_id,
        "language": language,
        "fullName": fullname,
        "mobilePhone": phone_number,
        "region": region,
        "district": district,
        "schoolNumber": school_number,
        "olimpiaScience": olimpia_science,
        "science1": science_1,
        "science2": science_2,
        "science3": science_3,
        "pinfl": pinfl
    }

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(ADD_USER_URL, json=data, headers=headers, verify=False)

    if response.status_code == 401:
        resp = await get_token()
        new_token = resp.json()['token']
        await db.add_token(new_token)
        headers['Authorization'] = f"Bearer {new_token}"
        response = requests.post(ADD_USER_URL, json=data, headers=headers, verify=False)
    return response.status_code
