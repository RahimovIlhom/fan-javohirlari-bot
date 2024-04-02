import warnings

import requests

from utils.db_api.send_data_API import get_token, env

ADD_RESULT_URL = env.str("ADD_RESULT_URL")


async def post_or_put_result(id, tg_id, result, certificateImage, *args, **kwargs):
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
        "result": result,
        "certificateImage": certificateImage
    }

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(ADD_RESULT_URL, json=data, headers=headers, verify=False)

    if response.status_code == 401:
        resp = await get_token()
        new_token = resp.json()['token']
        await db.add_token(new_token)
        headers['Authorization'] = f"Bearer {new_token}"
        response = requests.post(ADD_RESULT_URL, json=data, headers=headers, verify=False)
    return response.status_code
