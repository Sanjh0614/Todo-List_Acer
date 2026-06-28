import requests
import json

invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
headers = {
    "Authorization": "Bearer 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",
    "Accept": "application/json"
}

payload = {
    "model": "nvidia/llama-3.1-nemotron-70b-instruct",
    "messages": [{"role": "user", "content": "Hello, world!"}],
    "max_tokens": 100,
    "temperature": 1.0,
    "top_p": 0.95,
    "stream": False
}

print("Sending request to NVIDIA with known model...")
try:
    response = requests.post(invoke_url, headers=headers, json=payload, timeout=30)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)
except Exception as e:
    print("Exception:", e)
