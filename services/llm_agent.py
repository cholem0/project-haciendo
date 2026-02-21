import json
from async_lru import alru_cache
from core.config import OPENROUTER_CLIENT, SYS_INST_TOOL_MATCH, SYS_INST_SOURCE_SUM
from services.code_analyzer import get_source_code, find_function_by_name

async def formatting_tools(tool_name, param, file_path):
    if tool_name == "whole_project_summary":
        return await get_source_code(file_path)
    if tool_name == "function_summary":
        return await find_function_by_name(file_path=file_path, func_name=param)
    return ''

async def agent_tool_match(user_prompt: str):
    response = await OPENROUTER_CLIENT.chat.completions.create(
        model="arcee-ai/trinity-large-preview:free", 
        messages=[
            {"role": "system", "content": SYS_INST_TOOL_MATCH},
            {"role": "user", "content": f"User's prompt:\n{user_prompt}"}
        ],
        temperature=1,
    )   
    try:
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Agent tool match error: {e}")
        return ''
    
@alru_cache(maxsize=4, ttl=5 * 60)
async def agent_code_sum(source_code: str):
    print("Generating code summary...")
    response = await OPENROUTER_CLIENT.chat.completions.create(
        model="arcee-ai/trinity-large-preview:free", 
        messages=[
            {"role": "system", "content": SYS_INST_SOURCE_SUM},
            {"role": "user", "content": f"Source Code to analyze:\n{source_code}"}
        ],
        temperature=0,
        top_p=0,
        max_tokens=300
    )
    try:
        return response.choices[0].message.content
    except Exception as e:
        print(f"Agent sum error: {e}")
        return ''