import requests
import json

url = "http://127.0.0.1:5000/chat"
payload = {
    "session_id": "just_for_test_session",
    "prompt": "Hi, Who are you?"
}

response = requests.post(url, json=payload)

if response.ok:
    result = response.json()
    print(result["response"])
else:
    print("Error:", response.status_code, response.text)

