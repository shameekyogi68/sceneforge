import asyncio
import websockets
import ssl

async def test():
    url = "wss://b2d09cec-8f73-4370-b726-2907b4163a38.fly.dev/_event"
    origins = [
        None,
        "https://b2d09cec-8f73-4370-b726-2907b4163a38.fly.dev",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://sceneforge-aqua-ocean.reflex.run",
    ]
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    for origin in origins:
        print(f"Testing origin: {origin}")
        try:
            headers = {"Origin": origin} if origin else {}
            async with asyncio.timeout(3.0):
                async with websockets.connect(url, additional_headers=headers, ssl=ssl_context) as ws:
                    print(f"  SUCCESS! Connected with origin {origin}")
        except Exception as e:
            print(f"  FAILED! {repr(e)}")

asyncio.run(test())
