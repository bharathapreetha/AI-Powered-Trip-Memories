import httpx

try:
    response = httpx.post(
        "http://127.0.0.1:11434/api/chat",
        json={
            "model": "llama3.2",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello"
                }
            ],
            "stream": False
        },
        timeout=120
    )

    print("Status:", response.status_code)
    print("Response:", response.json())

except Exception as e:
    print("Error:", repr(e))