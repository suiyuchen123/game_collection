from core.coze_client import CozeClient

c = CozeClient()
c.load_config()

print(f"API Key set: {bool(c.api_key)}")
print(f"Bot ID set: {bool(c.bot_id)}")
print(f"API Key value: {c.api_key[:20] if c.api_key else 'None'}...")
print(f"Bot ID value: {c.bot_id[:20] if c.bot_id else 'None'}...")

is_configured = bool(c.api_key and c.bot_id and c.api_key != "your_coze_api_key_here")
print(f"Can connect to Coze: {'YES' if is_configured else 'NO'}")

if is_configured:
    print("Testing Coze connection...")
    result = c.chat("你好")
    print(f"Coze test result: {result}")