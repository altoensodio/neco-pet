import asyncio, threading

loop = asyncio.new_event_loop()

def start_asyncio_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()

thread = threading.Thread(target=start_asyncio_loop, daemon=True)
thread.start()

def get_event_loop():
    return loop
