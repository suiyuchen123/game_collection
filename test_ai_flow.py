import sys
sys.path.insert(0, 'core')

from knowledge_base import KnowledgeBase
from coze_client import CozeClient
from context_manager import ContextManager

print("=== AI助手完整调用流程测试 ===")
print()

kb = KnowledgeBase()
client = CozeClient()
client.load_config()
cm = ContextManager()

test_cases = [
    {"query": "你好", "game": None},
    {"query": "贪吃蛇怎么玩", "game": "snake"},
    {"query": "跑酷怎么跳", "game": "parkour"},
    {"query": "飞机大战怎么通关", "game": "planewar"},
    {"query": "存档丢失了怎么办", "game": None},
    {"query": "五子棋规则", "game": "gomoku"},
    {"query": "操作按键", "game": None},
    {"query": "这个游戏好玩吗", "game": None},
    {"query": "谢谢", "game": None},
]

for case in test_cases:
    query = case["query"]
    game = case["game"]
    
    print(f"📝 用户问题: {query}")
    if game:
        print(f"🎮 当前游戏: {game}")
    
    cm.set_current_game(game)
    expanded_query = cm.expand_query_with_context(query)
    
    answer, category, score, layer = kb.search(expanded_query, game)
    
    if layer in ["layer1", "layer2"]:
        source = "本地知识库"
        print(f"✅ 来源: {source}")
        print(f"📊 匹配分数: {score}")
        print(f"📋 分类: {category}")
        print(f"💬 回答: {answer}")
    else:
        print("❌ 知识库无匹配，尝试调用Coze AI...")
        
        game_names = {
            "snake": "贪吃蛇",
            "parkour": "横版跑酷",
            "planewar": "飞机大战",
            "spotdifference": "找茬",
            "gomoku": "五子棋"
        }
        game_context = game_names.get(game, "") if game else ""
        history = cm.get_context()
        
        result = client.chat_with_context(query, game_context, history)
        
        if result.get("answer"):
            coze_answer = result["answer"]
            if "无法为你解答" in coze_answer or "暂时无法" in coze_answer:
                print("⚠️ Coze无法回答，回退到本地知识库...")
                fallback_answer, fb_category, fb_score, fb_layer = kb.search(query, game)
                if fallback_answer:
                    print(f"✅ 来源: 本地知识库(回退)")
                    print(f"💬 回答: {fallback_answer}")
                else:
                    print(f"❌ 来源: Coze AI(受限)")
                    print(f"💬 回答: {coze_answer}")
            else:
                print(f"✅ 来源: Coze AI")
                print(f"💬 回答: {coze_answer}")
        else:
            print("❌ Coze无响应，回退到本地知识库...")
            fallback_answer, fb_category, fb_score, fb_layer = kb.search(query, game)
            if fallback_answer:
                print(f"✅ 来源: 本地知识库(回退)")
                print(f"💬 回答: {fallback_answer}")
            else:
                print(f"❌ 来源: 无")
                print(f"💬 回答: 抱歉，我不太理解你的问题。")
    
    cm.add_message("user", query)
    print("-" * 60)
    print()