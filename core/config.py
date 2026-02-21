import os
from dotenv import load_dotenv
from aiocache import Cache
from openai import AsyncOpenAI

load_dotenv()

OPENROUTER_API = os.getenv("OPENR_API_KEY")

APARAT_EMAIL = os.getenv("APARAT_EMAIL")
APARAT_PASS = os.getenv("APARAT_PASS")

APARAT_LUSER = None
APARAT_LTOKEN = None

HACIENDO_ENV_PATH = ".env.haciendo"
CACHE_DURATION = 5
STREAMER_NAMES = ['cholemo', 'looping'] 

OPENROUTER_CLIENT = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API,
)

UNAME_CACHE = Cache(Cache.MEMORY)

def load_prompt(filename):  
    with open(f'prompts/{filename}', 'r') as f:
        return f.read()

SYS_INST_TOOL_MATCH = load_prompt('match_to_tool.txt')
SYS_INST_SOURCE_SUM = load_prompt('source_code.txt')

