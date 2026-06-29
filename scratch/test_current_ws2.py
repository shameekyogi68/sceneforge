import asyncio
import websockets
import ssl

async def test_websocket(uri, origin):
    result = f"Testing URI: {uri}\n  Origin: {origin}\n"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    try:
        async with websockets.connect(uri, origin=origin, ssl=ssl_context) as ws:
            result += "  SUCCESS!\n"
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=2.0)
                result += f"  Received: {response[:150]}\n"
            except Exception as re:
                result += f"  Connected, but receive failed: {re}\n"
    except Exception as e:
        result += f"  FAILED: {repr(e)}\n"
    return result

async def main():
    uris = [
        ("wss://b2d09cec-8f73-4370-b726-2907b4163a38.fly.dev/_event", "https://sceneforge-aqua-ocean.reflex.run"),
        ("wss://sceneforge-aqua-ocean.reflex.run/_event", "https://sceneforge-aqua-ocean.reflex.run"),
    ]
    out = ""
    for uri, origin in uris:
        res = await test_websocket(uri, origin)
        out += res + "-" * 50 + "\n"
    with open("scratch/test_ws_results.txt", "w") as f:
        f.write(out)
    print("Done")

if __name__ == "__main__":
    asyncio.run(main())
