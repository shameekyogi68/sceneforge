import asyncio
import websockets

async def test_ws(uri, origin):
    headers = {"Origin": origin} if origin else None
    try:
        async with websockets.connect(uri, extra_headers=headers) as ws:
            print(f"SUCCESS: uri={uri}, origin={origin}")
            return True
    except Exception as e:
        print(f"FAILED: uri={uri}, origin={origin} -> {e}")
        return False

async def main():
    uris = [
        "ws://localhost:8000/_event",
        "ws://127.0.0.1:8000/_event",
        "ws://localhost:8000/event",
        "ws://127.0.0.1:8000/event",
    ]
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        None
    ]
    for uri in uris:
        for origin in origins:
            await test_ws(uri, origin)

if __name__ == "__main__":
    asyncio.run(main())
