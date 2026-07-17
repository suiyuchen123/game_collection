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

print(f"Testing Bot ID: {BOT_ID} (stream mode)")

try:
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30, stream=True)
    response.raise_for_status()
    
    current_event = None
    all_content = ""
    
    for line in response.iter_lines():
        if line:
            line_str = line.decode("utf-8")
            
            if line_str.startswith("event:"):
                current_event = line_str[6:].strip()
            elif line_str.startswith("data:"):
                data_str = line_str[5:]
                try:
                    data = json.loads(data_str)
                    if current_event == "conversation.message.delta":
                        content = data.get("content", "")
                        if content:
                            print(content, end="")
                            all_content += content
                    elif current_event == "conversation.message.completed":
                        content = data.get("content", "")
                        if content:
                            print(content, end="")
                            all_content += content
                except json.JSONDecodeError:
                    pass
    
    print(f"\n\nFinal answer: '{all_content}'")
    
    if not all_content:
        print("\n⚠️ Warning: Coze returned empty content.")
        print("Please configure your Bot in Coze platform with system prompt.")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")