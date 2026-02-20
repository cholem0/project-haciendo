import asyncio
import aiofiles
from tree_sitter import Language, Parser, Query, QueryCursor
from async_lru import alru_cache
from utils.query_strings import QUERIES as Q_Strings
from utils.conditional_import import get_spc_language

def get_ext(filename: str):
    return filename.split('.')[-1]

def sync_parse_and_find(source_bytes, lang, query_string, func_name):
    parser = Parser(lang)
    tree = parser.parse(source_bytes)
    query = Query(lang, query_string)
    query_cursor = QueryCursor(query)
    matches = query_cursor.matches(tree.root_node)

    for match in matches:
        if match[1].get('name')[0].text.decode('utf-8') == func_name:
            return match[1].get('function.def')[0].text.decode('utf-8')
    return None

@alru_cache(maxsize=4, ttl=5 * 60)
async def get_source_code(file_path):
    print(f"Reading source code from {file_path}")
    try:
        async with aiofiles.open(file_path, mode='r') as f:
            return await f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return ''

async def find_function_by_name(file_path: str, func_name: str) -> str | None:
    file_ext = get_ext(file_path)
    source_code = await get_source_code(file_path)
    if not source_code:
        return ''

    source_bytes = source_code.encode("utf-8")
    query_string = Q_Strings.get(file_ext)
    lang = Language(get_spc_language(file_ext))

    result = await asyncio.to_thread(sync_parse_and_find, source_bytes, lang, query_string, func_name)
    return result