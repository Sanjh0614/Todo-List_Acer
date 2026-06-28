import requests
import json

url = "https://integrate.api.nvidia.com/v1/models"
headers = {
    "Authorization": "Bearer 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"
}

print("Fetching models...")
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    models = [m['id'] for m in data.get('data', []) if 'gemma' in m['id'].lower()]
    print("Available Gemma Models:")
    for m in models:
        print(m)
else:
    print("Failed:", response.status_code, response.text)
