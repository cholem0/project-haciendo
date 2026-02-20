from aiohttp import web
from core.state import state

async def handle_post(request):
    try:
        data = await request.json()
        state.latest_file_path = data.get('path')
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)
    return web.Response(text="Success!")

async def start_local_server(port=10000):
    app = web.Application()
    app.add_routes([web.post('/filepath', handle_post)])
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, 'localhost', port)
    await site.start()
    print(f"Local server listening on localhost:{port}")
    return runner