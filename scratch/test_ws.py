import asyncio
import sys

try:
    import websockets
except ImportError:
    print("websockets library not installed. Installing it...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets"])
    import websockets

async def test_local_origin(origin):
    uri = "ws://localhost:8000/_event"
    print(f"Testing local Origin: {origin}")
    try:
        async with websockets.connect(uri, origin=origin) as ws:
            print(f"  SUCCESS for Origin: {origin}!")
    except Exception as e:
        print(f"  FAILED for Origin: {origin} -> {repr(e)}")

async def main():
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://sceneforge-lime-wood.reflex.run",
        "https://00152787-d926-49c9-910f-975d1eae00ca.fly.dev",
        None
    ]
    for o in origins:
        await test_local_origin(o)
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
