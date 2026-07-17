import requests
import json

API_KEY = "pat_BunEgZyhVD4wTRwdeMsHFyj4u6sGBTjX2zD5k7gpAaGDi6Ju0M79xjEYv6wADvZE"
BOT_ID = "7663049264947380260"
API_URL = "https://api.coze.cn/v3/chat"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "bot_id": BOT_ID,
    "user_id": "test_user",
    "stream": True,
    "auto_save_history": False,
    "additional_messages": [
        {
            "role": "user",
            "content": "你好",
            "content_type": "text"
        }
    ]
}

print(f"Testing Bot ID: {BOT_ID}")

try:
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30, stream=True)
    response.raise_for_status()
    
    current_event = None
    
    for line in response.iter_lines():
        if line:
            line_str = line.decode("utf-8")
            
            if line_str.startswith("event:"):
                current_event = line_str[6:].strip()
            elif line_str.startswith("data:"):
                data_str = line_str[5:]
                try:
                    data = json.loads(data_str)
                    print(f"\n=== Event: {current_event} ===")
                    print(f"Keys: {list(data.keys())}")
                    if "content" in data:
                        content = data["content"]
                        print(f"Content type: {type(content)}")
                        if isinstance(content, str):
                            print(f"Content length: {len(content)}")
                            if len(content) > 0 and len(content) < 500:
                                print(f"Content: {content}")
                            else:
                                print(f"Content preview: {content[:100]}...")
                        elif isinstance(content, dict):
                            print(f"Content dict keys: {list(content.keys())}")
                except json.JSONDecodeError:
                    print(f"\n=== Event: {current_event} ===")
                    print(f"Raw data (not JSON): {data_str[:200]}")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")