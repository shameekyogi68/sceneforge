import asyncio
import websockets
import ssl

async def test_websocket(uri, origin):
    print(f"Testing URI: {uri}")
    print(f"  Origin: {origin}")
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    try:
        async with websockets.connect(uri, origin=origin, ssl=ssl_context) as ws:
            print(f"  SUCCESS!")
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=2.0)
                print(f"  Received: {response[:150]}")
            except Exception as re:
                print(f"  Connected, but receive failed: {re}")
    except Exception as e:
        print(f"  FAILED: {repr(e)}")

async def main():
    uris = [
        ("wss://b2d09cec-8f73-4370-b726-2907b4163a38.fly.dev/_event/?EIO=4&transport=websocket", "https://sceneforge-aqua-ocean.reflex.run"),
        ("wss://b2d09cec-8f73-4370-b726-2907b4163a38.fly.dev/_event/?EIO=4&transport=websocket", "http://localhost:3000"),
        ("wss://b2d09cec-8f73-4370-b726-2907b4163a38.fly.dev/_event/?EIO=4&transport=websocket", "https://b2d09cec-8f73-4370-b726-2907b4163a38.fly.dev"),
    ]
    for uri, origin in uris:
        await test_websocket(uri, origin)
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
