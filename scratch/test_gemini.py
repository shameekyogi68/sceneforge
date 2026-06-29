import os
import sys
from dotenv import load_dotenv

sys.path.append("/Users/shameekyogi/My Apps/ScriptForge")
dotenv_path = "/Users/shameekyogi/My Apps/ScriptForge/.env"
load_dotenv(dotenv_path)

from google.genai import Client

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key: {api_key[:10]}...")

client = Client(api_key=api_key)

models = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
for model in models:
    try:
        print(f"Testing model: {model}")
        response = client.models.generate_content(
            model=model,
            contents="Hello, reply with only one word 'success'."
        )
        print(f"Result for {model}: {response.text}")
    except Exception as e:
        print(f"Error for {model}: {e}")
