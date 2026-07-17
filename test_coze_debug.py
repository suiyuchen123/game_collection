import requests
import json

API_KEY = "pat_BunEgZyhVD4wTRwdeMsHFyj4u6sGBTjX2zD5k7gpAaGDi6Ju0M79xjEYv6wADvZE"
BOT_ID = "7663304071075741738"
API_URL = "https://api.coze.cn/v3/chat"

print(f"API Key: {API_KEY[:20]}...")
print(f"Bot ID: {BOT_ID}")
print(f"API URL: {API_URL}")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "bot_id": BOT_ID,
    "user_id": "test_user",
    "stream": False,
    "auto_save_history": True,
    "additional_messages": [
        {
            "role": "user",
            "content": "你好",
            "content_type": "text"
        }
    ]
}

print("\nRequest headers:")
for k, v in headers.items():
    print(f"  {k}: {v[:30] if k == 'Authorization' else v}...")

print("\nRequest payload:")
print(json.dumps(payload, indent=2, ensure_ascii=False))

print("\n--- Sending request ---")
try:
    response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
    print(f"Status code: {response.status_code}")
    print(f"Response text: {response.text[:1000]}")
    
    try:
        data = response.json()
        print(f"\nParsed JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print("\nResponse is not JSON")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")