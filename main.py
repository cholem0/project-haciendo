import asyncio
import json
import websockets
from core.aparat_token import get_user_data
# from core.config import APARAT_LUSER , APARAT_LTOKEN
import core.config
from core.state import state
from api.server import start_local_server
from services.aparat_client import get_jwt, send_llm_response, send_periodic_request, extract_payload, ask_user_prompt
from services.llm_agent import agent_tool_match, formatting_tools, agent_code_sum


async def send_buffer(lock , shared_buffer , ws , streamer_key):
    while True:
        await asyncio.sleep(5)
        if len(shared_buffer) > 0:
            async with lock:
                entry = shared_buffer[0]
                await send_llm_response(ws , entry.get('message') ,streamer_key ,entry.get('guid'))
                shared_buffer.pop(0)


async def main():
    shared_send_reply = []
    lock = asyncio.Lock()

    await start_local_server()
    
    websocket_url = "wss://lws.aparat.com/socket.io/?EIO=3&transport=websocket"
    streamer_data = await get_jwt()
    streamer_jwt = streamer_data.get('jwt')
    streamer_key = streamer_data.get('live_code')
    payload = ["join_room", {
        "data": {"key": streamer_key, "name": "Felan Room", "udid": "a0k21iqw4"},
        "header": {"luser": core.config.APARAT_LUSER, "ltoken": core.config.APARAT_LTOKEN, "jwt": streamer_jwt, "source": "aparat"}
    }]
    join_packet = f"420{json.dumps(payload)}"
    headers = {
        "Origin": "https://www.aparat.com",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    try:
        async with websockets.connect(websocket_url, additional_headers=headers, max_size=65536) as websocket:
            print("Connected to Aparat WebSocket")
            await websocket.send(join_packet)

            asyncio.create_task(send_periodic_request(websocket, streamer_data, interval=5))
            asyncio.create_task(send_buffer(lock , shared_send_reply , websocket , streamer_key))
            
            async for message in websocket:
                if message == "2":
                    await websocket.send("3")
                    
                if message.startswith('''42["comment"'''):
                    # print(message)
                    payload_json = extract_payload(ws_payload=message)
                    tool_match_prompt_dict = await ask_user_prompt(payload=payload_json)
                    
                    if tool_match_prompt_dict:
                        agent_tool_resp = await agent_tool_match(tool_match_prompt_dict.get('comment'))
                        if agent_tool_resp:
                            source_code = await formatting_tools(
                                agent_tool_resp.get('tool_name'), 
                                agent_tool_resp.get('parameter'), 
                                state.latest_file_path
                            )
                            async with lock:
                                if source_code:
                                    agent_sum_to_user = await agent_code_sum(source_code=source_code)
                                    print("RESPONSE:", agent_sum_to_user)
                                    shared_send_reply.append({
                                        'message' : agent_sum_to_user[:300],
                                        'guid' : tool_match_prompt_dict.get('reply_guid')
                                    })
                                        
                                else:
                                    shared_send_reply.append({
                                        'message' : "😛",
                                        'guid' : tool_match_prompt_dict.get('reply_guid')
                                    })
    except Exception as e:
        print(f"Fatal error in main loop: {e}")
    finally:
        state.save_state()
        print("State saved. Shutting down.")
    


if __name__ == "__main__":
    user_data = get_user_data()
    if user_data:
        asyncio.run(main())