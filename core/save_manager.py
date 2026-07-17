import json
import os

SAVE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "save_data.json")

# 所有游戏默认解锁，玩家可自由选择任意游戏开始
ALL_GAME_IDS = [1, 2, 3]

DEFAULT_DATA = {
    "username": "",
    "unlocked_games": [1, 2, 3],
    "completed_levels": {
        "game1": 0,
        "game2": 0,
        "game3": 0
    },
    "title_earned": False
}


class SaveManager:
    def __init__(self):
        self.data = self.load()
        # 持久化迁移后的数据（兼容旧存档时补全解锁状态）
        self.save()

    def load(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = DEFAULT_DATA.copy()
        else:
            data = DEFAULT_DATA.copy()

        # 兼容旧存档：确保 unlocked_games / completed_levels 字段存在
        # 并且所有游戏都已解锁（旧版默认只解锁游戏1）
        if "unlocked_games" not in data:
            data["unlocked_games"] = []
        for gid in ALL_GAME_IDS:
            if gid not in data["unlocked_games"]:
                data["unlocked_games"].append(gid)

        if "completed_levels" not in data:
            data["completed_levels"] = {}
        for key in ["game1", "game2", "game3"]:
            data["completed_levels"].setdefault(key, 0)

        if "title_earned" not in data:
            data["title_earned"] = False

        return data

    def save(self):
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def is_game_unlocked(self, game_id):
        return game_id in self.data["unlocked_games"]

    def unlock_game(self, game_id):
        if game_id not in self.data["unlocked_games"]:
            self.data["unlocked_games"].append(game_id)
            self.save()

    def get_completed_levels(self, game_key):
        return self.data["completed_levels"].get(game_key, 0)

    def add_completed_level(self, game_key):
        self.data["completed_levels"][game_key] = self.data["completed_levels"].get(game_key, 0) + 1
        self.save()
        self.check_unlock_conditions()

    def check_unlock_conditions(self):
        # 所有游戏默认解锁，这里只保留称号判断
        if self.data["completed_levels"]["game3"] >= 1:
            self.data["title_earned"] = True
            self.save()

    def has_title(self):
        return self.data["title_earned"]

    def get_username(self):
        return self.data.get("username", "")

    def set_username(self, username):
        self.data["username"] = username
        self.save()

    def reset_progress(self):
        # 重置时保留用户名，所有游戏保持解锁
        username = self.data.get("username", "")
        self.data = DEFAULT_DATA.copy()
        self.data["username"] = username
        self.save()
        self.clear_chat_history()

    def clear_chat_history(self):
        history_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chat_history.json")
        if os.path.exists(history_path):
            try:
                os.remove(history_path)
            except Exception as e:
                print(f"Failed to clear chat history: {e}")