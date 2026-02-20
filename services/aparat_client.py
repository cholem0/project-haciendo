import json
import httpx
import asyncio
import websockets
from core.config import UNAME_CACHE, STREAMER_NAMES

def extract_payload(ws_payload: str):
    return json.loads(ws_payload.split(',', maxsplit=1)[1][:-1])

async def ask_user_prompt(payload: dict):
    username = payload.get('username')
    comment = payload.get('comment')
    
    if username in STREAMER_NAMES and comment.startswith('$ask'):
        if await UNAME_CACHE.exists(username):
            print(f"{username} is on cooldown!")
            return ''
        
        await UNAME_CACHE.set(username, True, ttl=60)
        return comment.split('$ask', maxsplit=1)[-1].strip()
    return ''

async def get_jwt(streamer_name="cholemo"):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://www.aparat.com/api/fa/v2/Live/LiveStream/show/username/{streamer_name}")
        resp_json = resp.json()
        return {
            'jwt': resp_json['jwt'],
            'live_code': resp_json['live_code']
        }

async def send_periodic_request(websocket, streamer_data, interval=5):
    pingpong_counter = 1
    while True:
        try:
            await asyncio.sleep(interval)
            await websocket.send('2')

            pingpong = ["pingpong", {
                "data": {"key": streamer_data.get('live_code'), 'duration': '5000', "udid": "v2as23u9n"},
                "header": {"luser": "", "ltoken": "", "jwt": streamer_data.get('jwt'), "source": "aparat"}
            }]
            await websocket.send(f"42{pingpong_counter}{json.dumps(pingpong)}")
            pingpong_counter += 1
        except websockets.ConnectionClosed:
            print("Periodic task stopped: Connection closed.")
            break