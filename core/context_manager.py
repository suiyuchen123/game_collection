class ContextManager:
    def __init__(self, max_history=10):
        self.max_history = max_history
        self.history = []
        self.current_game = None
        self.current_topic = None

    def set_current_game(self, game_id):
        self.current_game = game_id

    def add_message(self, role, content):
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": None,
            "game": self.current_game
        })

        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

        self.update_topic()

    def update_topic(self):
        game_keywords = {
            "snake": ["蛇", "贪吃蛇"],
            "parkour": ["跑酷", "跳跃", "障碍"],
            "planewar": ["飞机", "射击", "敌机"],
            "spotdifference": ["找茬", "找不同", "差异"],
            "gomoku": ["五子棋", "连珠", "五连"]
        }

        for msg in reversed(self.history):
            for game_id, keywords in game_keywords.items():
                for kw in keywords:
                    if kw in msg["content"]:
                        self.current_topic = game_id
                        return

        self.current_topic = self.current_game

    def get_context(self):
        return self.history.copy()

    def get_context_prompt(self):
        if not self.history:
            return ""

        lines = ["对话历史："]
        for msg in self.history[-5:]:
            role = "用户" if msg["role"] == "user" else "AI"
            game_tag = f"[{self.current_game}]" if self.current_game else ""
            lines.append(f"{game_tag} {role}: {msg['content']}")

        return "\n".join(lines)

    def get_topic(self):
        return self.current_topic

    def expand_query_with_context(self, query):
        expanded = query

        if self.current_topic:
            game_names = {
                "snake": "贪吃蛇",
                "parkour": "跑酷",
                "planewar": "飞机大战",
                "spotdifference": "找茬",
                "gomoku": "五子棋"
            }
            game_name = game_names.get(self.current_topic, "")
            if game_name:
                expanded = f"{game_name} {query}"

        for msg in reversed(self.history[-3:]):
            if msg["role"] == "assistant":
                for kw in ["联机", "难度", "禁手", "悔棋", "残局", "提示", "图片", "金币", "通关", "操作"]:
                    if kw in msg["content"] and kw not in expanded:
                        expanded += " " + kw
                        break

        return expanded

    def clear(self):
        self.history = []
        self.current_topic = None

    def extract_keywords(self, query):
        game_keywords = {
            "snake": ["蛇", "贪吃蛇"],
            "parkour": ["跑酷", "跳跃", "障碍"],
            "planewar": ["飞机", "射击", "敌机"],
            "spotdifference": ["找茬", "找不同", "差异"],
            "gomoku": ["五子棋", "连珠", "五连"]
        }

        for game_id, keywords in game_keywords.items():
            for kw in keywords:
                if kw in query:
                    return game_id

        return None

    def get_suggested_questions(self):
        common_questions = [
            "游戏怎么开始？",
            "操作按键有哪些？",
            "存档怎么保存？",
            "如何通关？"
        ]

        game_specific = {
            "snake": [
                "贪吃蛇怎么玩？",
                "贪吃蛇通关技巧",
                "贪吃蛇操作指南",
                "贪吃蛇常见问题"
            ],
            "parkour": [
                "跑酷怎么跳更高？",
                "跑酷通关技巧",
                "跑酷操作按键",
                "跑酷常见问题"
            ],
            "planewar": [
                "飞机大战怎么玩？",
                "飞机大战通关技巧",
                "飞机大战操作指南",
                "飞机大战常见问题"
            ],
            "spotdifference": [
                "找茬怎么找？",
                "提示道具怎么用？",
                "图片空白怎么办？",
                "每日金币怎么得？"
            ],
            "gomoku": [
                "五子棋怎么联机？",
                "人机难度怎么调？",
                "禁手规则是什么？",
                "悔棋功能怎么用？"
            ],
            "common": []
        }

        if self.current_game and self.current_game in game_specific:
            return common_questions + game_specific[self.current_game]

        return common_questions + game_specific["common"]

    def get_summary(self):
        if len(self.history) < 2:
            return ""

        user_messages = [msg["content"] for msg in self.history if msg["role"] == "user"]
        ai_messages = [msg["content"] for msg in self.history if msg["role"] == "assistant"]

        if not user_messages or not ai_messages:
            return ""

        recent_user = user_messages[-1] if user_messages else ""
        recent_ai = ai_messages[-1] if ai_messages else ""

        summary = f"最近用户问：{recent_user}\nAI回答：{recent_ai}"
        if self.current_topic:
            game_names = {
                "snake": "贪吃蛇",
                "parkour": "跑酷",
                "planewar": "飞机大战",
                "spotdifference": "找茬",
                "gomoku": "五子棋"
            }
            summary = f"当前话题：{game_names.get(self.current_topic, '')}\n" + summary

        return summary