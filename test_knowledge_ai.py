import sys
sys.path.insert(0, 'core')

from knowledge_base import KnowledgeBase
from coze_client import CozeClient
from context_manager import ContextManager

print("=== 知识库测试 ===")
kb = KnowledgeBase()

test_queries = [
    "你好",
    "贪吃蛇怎么玩",
    "跑酷怎么跳",
    "飞机大战怎么通关",
    "存档丢失了怎么办",
    "怎么解锁关卡",
    "五子棋规则",
    "操作按键",
]

for query in test_queries:
    answer, category, score, layer = kb.search(query)
    source = "本地知识库(L1)" if layer == "layer1" else "本地知识库(L2)" if layer == "layer2" else "无匹配"
    print(f"Q: {query}")
    print(f"  → {source}, 分数: {score}, 分类: {category}")
    print(f"  答: {answer[:50]}..." if answer else "  答: 无")
    print()

print("\n=== Coze AI测试 ===")
client = CozeClient()
client.load_config()

print(f"API Key: {client.api_key[:20]}...")
print(f"Bot ID: {client.bot_id}")

ai_tests = [
    "你好",
    "贪吃蛇怎么玩",
    "飞机大战操作指南",
    "游戏怎么存档",
]

for query in ai_tests:
    result = client.get_chat_response(query)
    print(f"Q: {query}")
    if result.get("answer"):
        print(f"  → {result['answer'][:80]}...")
    else:
        print(f"  → 无响应: {result}")
    print()

print("\n=== 完整流程测试 ===")
cm = ContextManager()
cm.set_current_game("snake")

for query in ["贪吃蛇怎么玩", "通关有什么技巧"]:
    expanded = cm.expand_query_with_context(query)
    print(f"原始查询: {query}")
    print(f"扩展查询: {expanded}")
    
    answer, category, score, layer = kb.search(expanded, cm.current_game)
    
    if layer in ["layer1", "layer2"]:
        print(f"  → 知识库回答: {answer[:60]}...")
    else:
        print(f"  → 知识库无匹配，调用Coze...")
        history = cm.get_context_prompt()
        full_query = f"当前游戏：贪吃蛇\n{history}\n\n用户问题：{query}" if history else query
        result = client.get_chat_response(full_query)
        print(f"  → Coze回答: {result.get('answer', '无')[:60]}...")
    
    cm.add_message("user", query)
    print()