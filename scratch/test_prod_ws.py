import asyncio
import websockets
import ssl

async def test_origin(origin):
    uri = "wss://00152787-d926-49c9-910f-975d1eae00ca.fly.dev/_event"
    print(f"Testing Origin: {origin}")
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    try:
        async with websockets.connect(uri, origin=origin, ssl=ssl_context) as ws:
            print(f"  SUCCESS for Origin: {origin}!")
            # try to receive a greeting
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=2.0)
                print(f"  Received: {response[:100]}")
            except Exception as re:
                print(f"  Connected, but receive failed: {re}")
    except Exception as e:
        print(f"  FAILED: {repr(e)}")

async def main():
    origins = [
        "https://sceneforge-lime-wood.reflex.run",
        "https://00152787-d926-49c9-910f-975d1eae00ca.fly.dev",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        None
    ]
    for o in origins:
        await test_origin(o)
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
