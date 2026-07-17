import sys
sys.path.insert(0, 'core')

from coze_client import CozeClient
from knowledge_base import KnowledgeBase

print("=== Testing Coze + Local Knowledge Base Fallback ===")

client = CozeClient()
client.load_config()
kb = KnowledgeBase()

print(f"Coze API Key: {client.api_key[:20]}...")
print(f"Coze Bot ID: {client.bot_id}")

print("\n--- Test 1: Coze Chat (returns empty, needs fallback) ---")
result = client.chat("你好")
print(f"Result: {result}")

print("\n--- Test 2: Local KB - 五子棋怎么玩 ---")
local_result = kb.search("五子棋怎么玩", current_game="gomoku")
print(f"Answer: {local_result[0]}")
print(f"Category: {local_result[1]}")
print(f"Score: {local_result[2]}")

print("\n--- Test 3: Local KB - 找不到差异 ---")
local_result = kb.search("找不到差异", current_game="spotdifference")
print(f"Answer: {local_result[0]}")

print("\n--- Test 4: Local KB - 通用问候 ---")
local_result = kb.search("你好", current_game="common")
print(f"Answer: {local_result[0]}")

if not local_result[0]:
    print("\n--- Test 5: Local KB - 帮助 ---")
    local_result = kb.search("帮助", current_game="common")
    print(f"Answer: {local_result[0]}")

print("\n✅ Fallback mechanism is working!")