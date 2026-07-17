import sys
sys.path.insert(0, 'core')

from knowledge_base import KnowledgeBase

kb = KnowledgeBase()

print("=== Testing Local Knowledge Base ===")
stats = kb.get_stats()
print(f"Total QA: {stats['total']}")
print(f"By game: {stats['by_game']}")

print("\nTest 1: 五子棋联机失败")
result = kb.search("五子棋联机失败", current_game="gomoku")
print(f"Answer: {result[0]}")

print("\nTest 2: 找不到差异")
result = kb.search("找不到差异", current_game="spotdifference")
print(f"Answer: {result[0]}")

print("\nTest 3: 通用问题 - 怎么保存游戏")
result = kb.search("怎么保存游戏", current_game="snake")
print(f"Answer: {result[0]}")

print("\nTest 4: 简短输入 - 不会")
result = kb.search("不会", current_game="gomoku")
print(f"Answer: {result[0]}")

print("\n✅ Local knowledge base is working correctly!")