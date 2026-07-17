import sys
sys.path.insert(0, 'core')

from coze_client import CozeClient

client = CozeClient()
client.load_config()

print(f"API Key: {client.api_key[:20]}...")
print(f"Bot ID: {client.bot_id}")

print("\n--- Testing chat_stream ---")
answer = ""
for chunk in client.chat_stream("你好"):
    print(chunk, end="")
    answer += chunk

print(f"\n\nFinal answer: {answer}")

if not answer:
    print("\n⚠️ Warning: Coze returned empty content. Your Bot may not have proper instructions configured.")