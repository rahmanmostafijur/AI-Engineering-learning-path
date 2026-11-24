import os
import time
from openai import OpenAI
import httpx
from dotenv import load_dotenv

load_dotenv()

URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"}

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

def get_reply(messages, model="openai/gpt-oss-20b"):
    body = {"model": model, "messages": messages}

    for _ in range(3):
        response = httpx.post(URL, headers=HEADERS, json=body, timeout=30)
        if response.status_code == 429 or response.status_code >= 500:
            time.sleep(2)
            continue
        break

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def stream_reply(messages, model="openai/gpt-oss-20b"):
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        piece = chunk.choices[0].delta.content
        if piece:
            yield piece