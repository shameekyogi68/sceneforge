import httpx

urls = [
    "https://b2d09cec-8f73-4370-b726-2907b4163a38.fly.dev/ping",
    "https://b2d09cec-8f73-4370-b726-2907b4163a38.fly.dev/debug-env",
    "https://sceneforge-aqua-ocean.reflex.run/ping",
]

for url in urls:
    try:
        resp = httpx.get(url, timeout=5.0)
        print(f"URL: {url} -> Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
    except Exception as e:
        print(f"URL: {url} -> Error: {e}")
