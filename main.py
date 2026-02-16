import asyncio
from itertools import islice
import aiofiles
import websockets
import httpx
import orjson
import json
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
from tree_sitter import Language, Parser, Node, Query, QueryCursor
from query_strings import QUERIES as Q_Strings
from conditional_import import get_spc_language

load_dotenv()
# socks_proxy = os.getenv("GEMINI_PROXY")
OPENROUTER_API = os.getenv("OPENR_API_KEY")
FILE_PATH = "standalone-backend.ts"

OPENROUTER_CLIENT = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key = OPENROUTER_API,
)


    
def get_ext(filename : str):
    return filename.split('.')[-1]

async def find_function_by_name(
    file_path : str,
    func_name: str,
) -> str | list[str] | None:
    file_ext = get_ext(file_path)
    async with aiofiles.open(FILE_PATH, mode='r') as f:
        source_code = await f.read()
    if isinstance(source_code, str):
        source_bytes = source_code.encode("utf-8")
    else:
        source_bytes = source_code

    query_string = Q_Strings.get(file_ext)
    lang = Language(get_spc_language(file_ext))

    parser = Parser(lang)
    tree = parser.parse(source_bytes)

    query = Query(lang, query_string)

    query_cursor = QueryCursor(query)
    matches = query_cursor.matches(tree.root_node)

    for match in matches:
        if match[1].get('name')[0].text.decode('utf-8') == func_name:
            return match[1].get('function.def')[0].text.decode('utf-8')

    return None

async def formatting_tools(tool_name, param):
    if tool_name == "whole_project_summary":
        async with aiofiles.open(FILE_PATH, mode='r') as f:
            contents = await f.read()
            return contents
    if tool_name == "code_section_summary":
        lines = param.split(',')
        async with aiofiles.open(FILE_PATH, mode='r') as f:
            subset = islice(f, lines[0], lines[1])
            code_section = list(subset)

            return code_section
    if tool_name == "function_summary":
        contents = await find_function_by_name(file_path=FILE_PATH , func_name=param)
        return contents
    return ''
    
with open('prompts/match_to_tool.txt' , 'r') as f:
    SYS_INST_TOOL_MATCH = f.read()
with open('prompts/source_code.txt' , 'r') as f:
    SYS_INST_SOURCE_SUM = f.read()

async def agent_tool_match(user_prompt: str):
    response = await OPENROUTER_CLIENT.chat.completions.create(
    model="arcee-ai/trinity-large-preview:free", 
    # model="arcee-ai/trinity-mini:free", 
    
    messages=[
        {"role": "system", "content": SYS_INST_TOOL_MATCH},
        {"role": "user", "content": f"User's prompt:\n{user_prompt}"}
    ],
    temperature=1,
)   
    try:
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return ''
    
async def agent_code_sum(source_code: str):
    response = await OPENROUTER_CLIENT.chat.completions.create(
    model="arcee-ai/trinity-large-preview:free", 
    # model="arcee-ai/trinity-mini:free", 
    messages=[
        {"role": "system", "content": SYS_INST_SOURCE_SUM},
        {"role": "user", "content": f"Source Code to analyze:\n{source_code}"}
    ],
    temperature=1,
    )

    try:
        return response.choices[0].message.content
    except Exception as e:
        return ''

def extract_payload(ws_payload : str):
    return json.loads(ws_payload.split(',' ,maxsplit=1)[1][:-1])


def ask_user_prompt(comment : str , username : str):
    if username in ['cholemo' , 'looping']:
        if comment.startswith('$ask'):
            return comment.split('$ask' , maxsplit= 1)[-1]
        else: return ''
    else: return ''

# Simulated helper functions (replace with your actual logic)
async def get_jwt(streamer_name = "cholemo"):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://www.aparat.com/api/fa/v2/Live/LiveStream/show/username/{streamer_name}")
        resp_json = json.loads(resp.text)
        return {'jwt' : resp_json['jwt'],
           'live_code' : resp_json['live_code']}

async def send_periodic_request(websocket,streamer_data, interval=5):
    pingpong_counter = 1
    while True:
        try:
            await asyncio.sleep(interval)
            # heartbeat = "2" 
            await websocket.send('2')

            pingpong = ["pingpong", {
    "data": {"key": streamer_data.get('live_code'), 'duration' : '5000', "udid": "v2as23u9n"},
    "header": {"luser": "", "ltoken": "", "jwt": streamer_data.get('jwt'), "source": "aparat"}
}]
            # print(f"current : {pingpong_counter}")
            await websocket.send(f"42{pingpong_counter}{json.dumps(pingpong)}")
            pingpong_counter += 1
            # print("Sent periodic heartbeat (2)")
            
        except websockets.ConnectionClosed:
            print("Periodic task stopped: Connection closed.")
            break

async def main():
    websocket_url = "wss://lws.aparat.com/socket.io/?EIO=3&transport=websocket"
    streamer_data = await get_jwt()
    # Payload for joining the room
    payload = ["join_room", {
    "data": {"key": streamer_data.get('live_code'), "name": "Felan Room", "udid": "a0k21iqw4"},
    "header": {"luser": "", "ltoken": "", "jwt": streamer_data.get('jwt'), "source": "aparat"}
}]
    join_packet = f"420{json.dumps(payload)}"
    headers = {
        "Origin": "https://www.aparat.com",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    # try:
    async with websockets.connect(websocket_url , additional_headers=headers , max_size=65536) as websocket:
        print("Connected to WebSocket")
        # msg = await websocket.recv()
        # print(msg)
        await websocket.send(join_packet)

        asyncio.create_task(send_periodic_request(websocket , streamer_data , interval=5))
        async for message in websocket:
            # print(f"Message received: {message}")
            
            if message == "2":
                await websocket.send("3")
                print("Received Ping (2), Sent Pong (3)")
            if message.startswith('''42["comment"'''):
                payload_json = extract_payload(ws_payload=message)
                tool_match_prompt = ask_user_prompt(payload_json.get('comment') , payload_json.get('username'))
                if tool_match_prompt:
                    print(tool_match_prompt)

                    agent_tool_resp = await agent_tool_match(tool_match_prompt)
                    if agent_tool_match:
                        print('agent_tool_match')
                        source_code = await formatting_tools(agent_tool_resp.get('tool_name'),agent_tool_resp.get('param'))
                        if source_code:
                            print('agent_source_code')

                            agent_sum_to_user = await agent_code_sum(source_code=source_code)
                            print(agent_sum_to_user)




    # except Exception as e:
    #     print(f"Error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())