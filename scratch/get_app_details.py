import subprocess
import json

try:
    res = subprocess.run(
        ["./venv/bin/reflex", "cloud", "apps", "inspect", "b2d09cec-8f73-4370-b726-2907b4163a38", "--loglevel", "debug"],
        capture_output=True,
        text=True
    )
    print("STDOUT:")
    print(res.stdout)
    print("STDERR:")
    print(res.stderr)
except Exception as e:
    print("Error:", e)
