import requests

invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
headers = {
    "Authorization": "Bearer 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",
    "Accept": "application/json"
}

payload = {
    "model": "google/gemma-3-12b-it",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100,
    "temperature": 1.0,
    "top_p": 0.95,
    "stream": False
}

print("Testing google/gemma-3-12b-it...")
try:
    response = requests.post(invoke_url, headers=headers, json=payload, timeout=10)
    print("Status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Exception:", e)
