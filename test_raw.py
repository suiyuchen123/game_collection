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

print("=== Testing raw response parsing ===")

try:
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30, stream=True)
    response.raise_for_status()
    
    all_content = ""
    skipped_count = 0
    
    for line in response.iter_lines():
        if line:
            line_str = line.decode("utf-8")
            
            if line_str.startswith("data:"):
                data_str = line_str[5:]
                try:
                    data = json.loads(data_str)
                    if isinstance(data, dict):
                        content = data.get("content", "")
                        if isinstance(content, str) and content:
                            if content.startswith('{"msg_type"'):
                                skipped_count += 1
                                continue
                            if content.startswith('{"finish_reason"'):
                                skipped_count += 1
                                continue
                            print(f"Got content: '{content}'")
                            all_content += content
                except json.JSONDecodeError:
                    pass
    
    print(f"\nFinal answer: '{all_content}'")
    print(f"Skipped {skipped_count} internal messages")
    
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")