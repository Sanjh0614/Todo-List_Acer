import requests

invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
headers = {
    "Authorization": "Bearer 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",
    "Accept": "text/event-stream"
}

payload = {
    "model": "google/gemma-4-31b-it",
    "messages": [{"role": "user", "content": "Say hello!"}],
    "max_tokens": 100,
    "temperature": 1.0,
    "top_p": 0.95,
    "stream": True,
    "chat_template_kwargs": {"enable_thinking": True}
}

print("Testing streaming...")
try:
    response = requests.post(invoke_url, headers=headers, json=payload, stream=True, timeout=10)
    for line in response.iter_lines():
        if line:
            print(line.decode("utf-8"))
except Exception as e:
    print("Exception:", e)
