import json
import os
from datetime import datetime

from database.db import DatabaseManager


class ChatHistoryManager:
    def __init__(self, user_id="default"):
        self.user_id = user_id
        self.db = DatabaseManager()
        self.local_history = []
        self.load_local_history()

    def load_local_history(self):
        history_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chat_history.json")
        if os.path.exists(history_path):
            try:
                with open(history_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.local_history = data
                    elif isinstance(data, dict) and self.user_id in data:
                        self.local_history = data[self.user_id]
            except Exception as e:
                print(f"Failed to load local history: {e}")
                self.local_history = []

    def save_local_history(self):
        history_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chat_history.json")
        try:
            with open(history_path, "w", encoding="utf-8") as f:
                json.dump({self.user_id: self.local_history}, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Failed to save local history: {e}")
            return False

    def add_message(self, username, query, response, source, game_category=None, score=0):
        message = {
            "user_id": self.user_id,
            "username": username,
            "query": query,
            "response": response,
            "source": source,
            "game_category": game_category,
            "score": score,
            "timestamp": datetime.now().isoformat()
        }

        self.local_history.append(message)

        if len(self.local_history) > 100:
            self.local_history = self.local_history[-100:]

        self.save_local_history()

        try:
            self.db.insert_chat_log(
                user_id=self.user_id,
                username=username,
                query=query,
                response=response,
                source=source,
                game_category=game_category,
                score=score
            )

            today = datetime.now().strftime("%Y-%m-%d")
            self.db.update_daily_stats(today, source=source)
        except Exception as e:
            print(f"Failed to save to database: {e}")

    def get_history(self, limit=50):
        return self.local_history[-limit:]

    def get_history_for_coze(self):
        messages = []
        for msg in self.local_history[-5:]:
            messages.append({"role": "user", "content": msg["query"]})
            messages.append({"role": "assistant", "content": msg["response"]})
        return messages

    def add_feedback(self, username, message, rating=None):
        try:
            self.db.insert_feedback(
                user_id=self.user_id,
                username=username,
                message=message,
                rating=rating
            )
            return True
        except Exception as e:
            print(f"Failed to add feedback: {e}")
            return False

    def clear_history(self):
        self.local_history = []
        self.save_local_history()

    def get_stats(self):
        try:
            return {
                "total_messages": len(self.local_history),
                "top_queries": self.db.get_top_queries(10),
                "source_distribution": self.db.get_source_distribution(),
                "daily_stats": self.db.get_stats_by_date()
            }
        except Exception as e:
            print(f"Failed to get stats: {e}")
            return {"total_messages": len(self.local_history)}