import traceback
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_debug():
    print("Getting token...")
    login_resp = client.post("/auth/demo-login")
    if login_resp.status_code != 200:
        print(f"Failed to login: {login_resp.text}")
        return
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    print("Testing /api/ai/chat...")
    chat_payload = {
        "message": "I feel overwhelmed with my work today.",
        "history": []
    }
    
    try:
        resp = client.post("/api/ai/chat", json=chat_payload, headers=headers)
        print("Status:", resp.status_code)
        print("Response:", resp.text)
    except Exception as e:
        print("EXCEPTION RAISED:")
        traceback.print_exc()

if __name__ == "__main__":
    run_debug()
