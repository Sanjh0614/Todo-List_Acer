import requests
import json

invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
headers = {
    "Authorization": "Bearer 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",
    "Accept": "application/json"
}
payload = {
    "model": "google/gemma-4-31b-it",
    "messages": [{"role": "user", "content": "Hello, world!"}],
    "max_tokens": 16384,
    "temperature": 1.0,
    "top_p": 0.95,
    "stream": False,
    "chat_template_kwargs": {"enable_thinking": True}
}

print("Sending request...")
response = requests.post(invoke_url, headers=headers, json=payload)
print("Status Code:", response.status_code)
print("Response Text:", response.text)
