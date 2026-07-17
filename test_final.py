import sys
sys.path.insert(0, 'core')

from coze_client import CozeClient

client = CozeClient()
client.load_config()

print(f"Coze API Key: {client.api_key[:20]}...")
print(f"Coze Bot ID: {client.bot_id}")

print("\n--- Test 1: Coze Chat (get_chat_response) ---")
result = client.get_chat_response("你好")
print(f"Result: {result}")

print("\n--- Test 2: Coze Chat - 五子棋怎么玩 ---")
result = client.get_chat_response("五子棋怎么玩")
print(f"Result: {result}")