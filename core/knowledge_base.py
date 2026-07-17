import json
import os


class KnowledgeBase:
    def __init__(self):
        self.knowledge = []
        self.game_categories = {
            "snake": "贪吃蛇",
            "parkour": "横版跑酷",
            "planewar": "飞机大战",
            "spotdifference": "找茬",
            "gomoku": "五子棋"
        }
        self.synonyms = {
            "联机失败": ["连不上好友", "联机不了", "无法联机", "联机失败", "连不上", "联机有问题"],
            "人机难度": ["难度", "电脑太强", "太难了", "简单模式", "困难模式", "难度调整"],
            "禁手": ["禁手", "什么是禁手", "黑棋禁手", "双三", "双四", "长连"],
            "悔棋": ["悔棋", "撤回", "撤销", "走错了", "想重来"],
            "残局推演": ["残局", "最后几步", "残局技巧", "收官", "最后阶段"],
            "提示道具": ["提示", "道具", "找不到", "给个提示", "帮忙找", "放大镜"],
            "关卡图片空白": ["图片空白", "加载不出来", "黑屏", "图片没显示", "画面空白"],
            "找不到差异": ["找不到", "差哪了", "哪里不一样", "没差异", "找不到不同"],
            "每日金币": ["金币", "奖励", "每日奖励", "每日任务", "金币怎么得"],
            "通关": ["过关", "完成", "通关", "胜利", "过关条件"],
            "操作": ["按键", "控制", "怎么操作", "操作说明"],
            "存档": ["保存", "进度", "存档", "记录"]
        }
        self.short_input_expansion = {
            "no": "找不到差异，没有发现不同",
            "不会": "不知道怎么操作，不会玩游戏",
            "没": "没有找到，没有完成，没有通关",
            "难": "游戏太难，难度太高，无法过关",
            "卡": "卡住了，无法继续，卡关了",
            "失败": "游戏失败，通关失败，联机失败",
            "怎么": "怎么玩，怎么操作，怎么通关",
            "什么": "什么是，什么意思，什么规则"
        }
        self.load_default_knowledge()

    def load_default_knowledge(self):
        self.knowledge = [
            {
                "game": "common",
                "keywords": ["你好", "hi", "hello", "嗨", "在吗", "在不在"],
                "answer": "你好！我是游戏助手，有什么问题可以问我~"
            },
            {
                "game": "common",
                "keywords": ["谢谢", "感谢", "thanks", "多谢"],
                "answer": "不客气！有问题随时问我~"
            },
            {
                "game": "common",
                "keywords": ["再见", "拜拜", "bye", "走了"],
                "answer": "再见！祝你游戏愉快~"
            },
            {
                "game": "common",
                "keywords": ["帮助", "help", "能做什么", "功能", "你会什么"],
                "answer": "我可以帮你：\n• 解答关卡解锁问题\n• 说明通关条件\n• 介绍操作按键\n• 解决存档问题\n• 解释称号获取方式\n• 介绍各个游戏的玩法\n\n目前支持：贪吃蛇、横版跑酷、飞机大战、找茬、五子棋"
            },
            {
                "game": "common",
                "keywords": ["解锁", "关卡", "打开", "进入", "锁住", "玩不了", "不能玩", "怎么玩", "如何开始"],
                "answer": "所有游戏默认全部解锁，直接点击游戏卡片即可开始游戏！\n贪吃蛇、横版跑酷、飞机大战、找茬、五子棋任选其一。"
            },
            {
                "game": "common",
                "keywords": ["存档", "保存", "丢失", "进度", "记录", "丢了"],
                "answer": "存档保存在游戏目录的 save_data.json 文件中。\n如果存档丢失，可以点击'重置进度'重新开始。\n聊天记录会自动保存到本地和数据库。"
            },
            {
                "game": "common",
                "keywords": ["重置", "清空", "重来", "重新开始"],
                "answer": "在主菜单点击'重置进度'按钮即可清空通关记录重新开始。\n注意：重置后用户名会保留，所有游戏保持解锁。"
            },
            {
                "game": "common",
                "keywords": ["称号", "标题", "头衔", "成就", "荣誉"],
                "answer": "通关飞机大战后即可获得【游戏高手高手高高手】称号！\n完成所有游戏挑战还能解锁更多成就~"
            },
            {
                "game": "common",
                "keywords": ["作者", "谁做的", "开发", "制作"],
                "answer": "这是一个用 Python + Pygame 制作的单机游戏合集，包含贪吃蛇、横版跑酷、飞机大战、找茬、五子棋五个经典游戏。AI助手由扣子(Coze)提供支持。"
            },
            {
                "game": "common",
                "keywords": ["反馈", "建议", "问题", "bug", "报错"],
                "answer": "感谢你的反馈！你可以通过聊天窗口的「反馈」按钮提交问题或建议，我们会认真处理每一条反馈。\n\n如果遇到游戏报错，请描述：\n• 哪个游戏出现问题\n• 具体的错误信息\n• 复现步骤"
            },
            {
                "game": "snake",
                "keywords": ["贪吃蛇", "蛇"],
                "answer": "🐍 贪吃蛇游戏：\n• 操作：方向键控制移动\n• 目标：吃到3个豆子\n• 注意：不要撞墙和自己\n• 技巧：尽量走开阔路线，避免绕圈"
            },
            {
                "game": "snake",
                "keywords": ["蛇怎么玩", "贪吃蛇操作"],
                "answer": "🐍 贪吃蛇操作指南：\n• ↑↓←→ 方向键控制蛇的移动方向\n• 吃到红色豆子蛇会变长\n• 通关条件：吃到3个豆子\n• 失败条件：撞到墙壁或自己的身体"
            },
            {
                "game": "snake",
                "keywords": ["蛇通关", "贪吃蛇过关"],
                "answer": "🐍 贪吃蛇通关技巧：\n• 第一关：熟悉控制，慢慢吃豆子\n• 第二关：蛇变长后注意走位\n• 第三关：保持冷静，规划路线\n• 提示：不要贪心，安全第一"
            },
            {
                "game": "parkour",
                "keywords": ["跑酷", "跑步", "跳跃", "障碍", "跳"],
                "answer": "🏃 横版跑酷游戏：\n• 操作：空格键跳跃\n• 目标：跑完全程距离\n• 技巧：提前跳跃躲避障碍物\n• 注意：路上会有木箱和尖刺两种障碍"
            },
            {
                "game": "parkour",
                "keywords": ["跑酷怎么玩", "跑酷操作"],
                "answer": "🏃 横版跑酷操作指南：\n• 空格键跳跃，按住空格跳得更高\n• 躲避路上的木箱和尖刺\n• 通关条件：跑完全程距离\n• 技巧：提前观察前方障碍物"
            },
            {
                "game": "parkour",
                "keywords": ["跑酷通关", "跑酷过关"],
                "answer": "🏃 横版跑酷通关技巧：\n• 第一关：适应节奏，练习跳跃\n• 第二关：注意障碍物间距变化\n• 第三关：保持专注，不要分心\n• 提示：提前预判比临场反应更重要"
            },
            {
                "game": "planewar",
                "keywords": ["飞机", "射击", "子弹", "敌机", "射"],
                "answer": "✈️ 飞机大战游戏：\n• 操作：方向键移动，空格发射子弹\n• 目标：击杀50架敌机\n• 技巧：左右移动躲避敌机攻击\n• 注意：敌机也会发射子弹"
            },
            {
                "game": "planewar",
                "keywords": ["飞机怎么玩", "飞机大战操作"],
                "answer": "✈️ 飞机大战操作指南：\n• ↑↓←→ 方向键控制飞机移动\n• 空格键发射子弹\n• 通关条件：击杀50架敌机\n• 失败条件：被敌机或子弹击中"
            },
            {
                "game": "planewar",
                "keywords": ["飞机通关", "飞机过关"],
                "answer": "✈️ 飞机大战通关技巧：\n• 保持移动，不要停留在同一位置\n• 优先消灭前方的敌机\n• 注意躲避敌机发射的子弹\n• 提示：通关后可获得【游戏高手高手高高手】称号"
            },
            {
                "game": "spotdifference",
                "keywords": ["找茬", "找不同", "差异", "哪里不一样"],
                "answer": "🔍 找茬游戏：\n• 操作：鼠标点击两张图片的差异处\n• 目标：在限定时间内找出所有差异\n• 技巧：从整体到局部，逐区域对比\n• 注意：点错会扣分或减少时间"
            },
            {
                "game": "spotdifference",
                "keywords": ["找茬怎么玩", "找茬操作"],
                "answer": "🔍 找茬游戏操作指南：\n• 仔细观察两张图片的差异\n• 用鼠标点击发现差异的位置\n• 找出所有差异即可过关\n• 注意：不要乱点，点错会受到惩罚"
            },
            {
                "game": "spotdifference",
                "keywords": ["找茬技巧", "找茬攻略"],
                "answer": "🔍 找茬技巧：\n• 先看整体布局，再看细节\n• 重点关注颜色、形状、位置变化\n• 从左到右、从上到下逐行扫描\n• 遇到困难时可以休息一下再回来\n• 提示：差异通常在不起眼的地方"
            },
            {
                "game": "spotdifference",
                "keywords": ["提示道具", "提示", "道具", "放大镜"],
                "answer": "🔍 提示道具使用说明：\n• 点击右下角放大镜图标使用提示\n• 每个关卡有3次提示机会\n• 提示会高亮显示一个差异位置\n• 注意：使用提示会扣除少量时间\n• 如果提示用完，可以等待每日奖励补充"
            },
            {
                "game": "spotdifference",
                "keywords": ["关卡图片空白", "图片空白", "加载不出来", "黑屏"],
                "answer": "🔍 图片空白解决方案：\n• 检查网络连接是否正常\n• 尝试重新加载游戏\n• 清理浏览器缓存（网页版）\n• 确保游戏目录有读写权限\n• 如果问题持续，请使用反馈按钮提交问题"
            },
            {
                "game": "spotdifference",
                "keywords": ["找不到差异", "找不到", "差哪了"],
                "answer": "🔍 找不到差异怎么办：\n• 保持耐心，差异可能很小\n• 使用提示道具定位差异\n• 尝试从不同角度观察图片\n• 可以暂时跳过，稍后再来\n• 注意：不要乱点，点错会扣分"
            },
            {
                "game": "spotdifference",
                "keywords": ["每日金币", "金币", "奖励", "每日奖励"],
                "answer": "🔍 金币获取方式：\n• 每日登录奖励：50金币\n• 通关奖励：每关30金币\n• 连续通关加成：额外20金币\n• 使用金币可以购买提示道具\n• 金币不会过期，可累积使用"
            },
            {
                "game": "gomoku",
                "keywords": ["五子棋", "连珠", "五连"],
                "answer": "⚫⚪ 五子棋游戏：\n• 操作：鼠标点击棋盘落子\n• 目标：先连成五子一线（横、竖、斜均可）\n• 技巧：攻守兼备，注意活三、冲四\n• 注意：黑棋先行，连成五子获胜"
            },
            {
                "game": "gomoku",
                "keywords": ["五子棋怎么玩", "五子棋操作"],
                "answer": "⚫⚪ 五子棋操作指南：\n• 黑棋先行，双方轮流落子\n• 鼠标点击棋盘交叉点放置棋子\n• 先在横、竖或斜方向连成五子获胜\n• 注意：不能在已有棋子的位置落子"
            },
            {
                "game": "gomoku",
                "keywords": ["五子棋技巧", "五子棋攻略"],
                "answer": "⚫⚪ 五子棋技巧：\n• 黑棋：主动进攻，争取先手优势\n• 白棋：灵活防守，寻找反击机会\n• 关键棋型：活三、冲四、双三、双四\n• 开局策略：斜三、梅花、八卦阵\n• 提示：既要进攻也要防守，不要只攻不守"
            },
            {
                "game": "gomoku",
                "keywords": ["五子棋规则", "五子棋胜负"],
                "answer": "⚫⚪ 五子棋规则：\n• 黑棋先行，双方轮流在棋盘交叉点上落子\n• 最先将五枚己方棋子连成一线者获胜\n• 连线方向：横、竖、斜均可\n• 平局：棋盘摆满仍未分出胜负\n• 禁手规则（部分模式）：黑棋不能走双三、双四、长连"
            },
            {
                "game": "gomoku",
                "keywords": ["联机失败", "连不上好友", "联机不了"],
                "answer": "⚫⚪ 联机失败解决方案：\n• 检查双方网络连接\n• 确保版本一致\n• 尝试重新邀请好友\n• 关闭防火墙重试\n• 如果问题持续，请使用反馈按钮提交"
            },
            {
                "game": "gomoku",
                "keywords": ["人机难度", "难度", "电脑太强"],
                "answer": "⚫⚪ 人机难度说明：\n• 简单模式：电脑随机落子，适合新手\n• 中等模式：电脑有基础策略\n• 困难模式：电脑使用高级算法\n• 建议从简单模式开始练习\n• 随着水平提高逐步增加难度"
            },
            {
                "game": "gomoku",
                "keywords": ["禁手", "什么是禁手", "双三", "双四"],
                "answer": "⚫⚪ 禁手规则详解：\n• 禁手仅适用于黑棋\n• 双三：同时形成两个或以上活三\n• 双四：同时形成两个或以上冲四\n• 长连：连成6子或以上\n• 白棋无禁手限制\n• 部分模式可能不启用禁手"
            },
            {
                "game": "gomoku",
                "keywords": ["悔棋", "撤回", "撤销", "走错了"],
                "answer": "⚫⚪ 悔棋功能说明：\n• 单人模式：可以随时悔棋\n• 联机模式：需要对方同意\n• 每局最多悔棋3次\n• 点击悔棋按钮撤销上一步\n• 注意：悔棋会重置当前回合"
            },
            {
                "game": "gomoku",
                "keywords": ["残局推演", "残局", "收官"],
                "answer": "⚫⚪ 残局推演技巧：\n• 先检查自己的获胜点\n• 再防守对方的威胁\n• 利用冲四逼对方防守\n• 制造双杀局面\n• 保持冷静，不要急于求成\n• 练习残局可以快速提升水平"
            },
            {
                "game": "common",
                "keywords": ["操作", "按键", "控制", "键盘", "按什么", "怎么操作", "怎么控制"],
                "answer": "🎮 操作按键总览：\n• 贪吃蛇：方向键控制移动\n• 横版跑酷：空格键跳跃\n• 飞机大战：方向键移动 + 空格射击\n• 找茬：鼠标点击差异处\n• 五子棋：鼠标点击棋盘落子"
            },
            {
                "game": "common",
                "keywords": ["通关", "完成", "过关", "条件", "赢", "胜利", "目标", "怎么赢", "如何通关"],
                "answer": "🎯 通关条件总览：\n• 贪吃蛇：吃到3个豆子\n• 横版跑酷：跑完全程距离\n• 飞机大战：击杀50架敌机\n• 找茬：找出所有差异\n• 五子棋：连成五子一线"
            },
        ]

    def expand_query(self, query):
        query = query.strip()
        if len(query) <= 2:
            for short, expanded in self.short_input_expansion.items():
                if short in query.lower():
                    return expanded
        return query

    def expand_with_synonyms(self, query):
        expanded = query
        for main_term, synonyms in self.synonyms.items():
            for synonym in synonyms:
                if synonym in query:
                    expanded += " " + main_term
                    break
        return expanded

    def search_layer1(self, query, current_game=None):
        expanded_query = self.expand_query(query)
        expanded_query = self.expand_with_synonyms(expanded_query)

        best_match = None
        best_score = 0
        best_category = ""

        for item in self.knowledge:
            score = 0
            game_match = 0

            if current_game and item["game"] == current_game:
                game_match = 4

            for keyword in item["keywords"]:
                if keyword in expanded_query:
                    score += 3
                elif keyword.lower() in expanded_query.lower():
                    score += 1

            total_score = score + game_match

            if total_score > best_score:
                best_score = total_score
                best_match = item
                best_category = item["game"]

        if best_match and best_score >= 3:
            return best_match["answer"], best_category, best_score

        return None, None, 0

    def search_layer2(self, query, current_game=None):
        expanded_query = self.expand_query(query)
        expanded_query = self.expand_with_synonyms(expanded_query)

        best_match = None
        best_score = 0
        best_category = ""

        for item in self.knowledge:
            score = 0
            game_match = 0

            if current_game and item["game"] == current_game:
                game_match = 2

            query_chars = set(expanded_query)
            for keyword in item["keywords"]:
                keyword_chars = set(keyword)
                overlap = query_chars & keyword_chars
                if overlap:
                    score += len(overlap) * 0.5

            total_score = score + game_match

            if total_score > best_score:
                best_score = total_score
                best_match = item
                best_category = item["game"]

        if best_match and best_score >= 2:
            return best_match["answer"], best_category, best_score

        return None, None, 0

    def search(self, query, current_game=None):
        answer, category, score = self.search_layer1(query, current_game)
        if answer:
            return answer, category, score, "layer1"

        answer, category, score = self.search_layer2(query, current_game)
        if answer:
            return answer, category, score, "layer2"

        return None, None, 0, "layer3"

    def load_from_file(self, file_path):
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.knowledge.extend(data)
                    elif isinstance(data, dict) and "knowledge" in data:
                        self.knowledge.extend(data["knowledge"])
                return True
            except Exception as e:
                print(f"Failed to load knowledge from {file_path}: {e}")
                return False
        return False

    def add_knowledge(self, game, keywords, answer):
        self.knowledge.append({
            "game": game,
            "keywords": keywords,
            "answer": answer
        })

    def remove_knowledge(self, index):
        if 0 <= index < len(self.knowledge):
            del self.knowledge[index]
            return True
        return False

    def get_game_knowledge(self, game):
        return [item for item in self.knowledge if item["game"] == game]

    def get_stats(self):
        stats = {
            "total": len(self.knowledge),
            "by_game": {}
        }
        for item in self.knowledge:
            game = item["game"]
            stats["by_game"][game] = stats["by_game"].get(game, 0) + 1
        return stats