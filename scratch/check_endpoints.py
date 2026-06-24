import asyncio
import websockets
import ssl
import httpx

async def test_websocket(name, url):
    print(f"Testing WebSocket {name} at {url}...")
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    try:
        async with asyncio.timeout(3.0):
            async with websockets.connect(url, ssl=ssl_context) as ws:
                print(f"  {name} WebSocket: SUCCESS!")
    except Exception as e:
        print(f"  {name} WebSocket: FAILED -> {repr(e)}")

async def test_http(name, url):
    print(f"Testing HTTP {name} at {url}...")
    try:
        async with httpx.AsyncClient(verify=False, timeout=3.0) as client:
            resp = await client.get(url)
            print(f"  {name} HTTP: SUCCESS! Status {resp.status_code}, Body: {resp.text[:100]}")
    except Exception as e:
        print(f"  {name} HTTP: FAILED -> {repr(e)}")

async def main():
    await test_http("Reflex Cloud Health", "https://sceneforge-aqua-ocean.reflex.run/health")
    await test_websocket("Reflex Cloud WS", "wss://sceneforge-aqua-ocean.reflex.run/_event")
    print("-" * 50)
    await test_http("Fly.dev Health", "https://00152787-d926-49c9-910f-975d1eae00ca.fly.dev/health")
    await test_websocket("Fly.dev WS", "wss://00152787-d926-49c9-910f-975d1eae00ca.fly.dev/_event")

if __name__ == "__main__":
    asyncio.run(main())
