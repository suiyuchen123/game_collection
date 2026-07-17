import sqlite3
import os
import json
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chat.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                username TEXT,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                source TEXT NOT NULL,
                game_category TEXT,
                score INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                username TEXT,
                message TEXT NOT NULL,
                rating INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game TEXT NOT NULL,
                keywords TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                total_queries INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                coze_count INTEGER DEFAULT 0,
                local_count INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0
            )
        ''')

        conn.commit()
        conn.close()

    def insert_chat_log(self, user_id, username, query, response, source, game_category=None, score=0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_logs (user_id, username, query, response, source, game_category, score, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, query, response, source, game_category, score, datetime.now()))
        conn.commit()
        conn.close()

    def get_chat_logs(self, user_id=None, limit=50, offset=0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if user_id:
            cursor.execute('''
                SELECT * FROM chat_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT ? OFFSET ?
            ''', (user_id, limit, offset))
        else:
            cursor.execute('''
                SELECT * FROM chat_logs ORDER BY timestamp DESC LIMIT ? OFFSET ?
            ''', (limit, offset))

        logs = cursor.fetchall()
        conn.close()

        return [self._row_to_dict(log) for log in logs]

    def get_stats_by_date(self, start_date=None, end_date=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if start_date and end_date:
            cursor.execute('''
                SELECT date, total_queries, success_count, coze_count, local_count, avg_response_time
                FROM stats WHERE date BETWEEN ? AND ? ORDER BY date DESC
            ''', (start_date, end_date))
        else:
            cursor.execute('''
                SELECT date, total_queries, success_count, coze_count, local_count, avg_response_time
                FROM stats ORDER BY date DESC LIMIT 30
            ''')

        stats = cursor.fetchall()
        conn.close()

        return stats

    def update_daily_stats(self, date_str, query_count=1, success=True, source="local"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM stats WHERE date = ?
        ''', (date_str,))
        row = cursor.fetchone()

        if row:
            total = row[2] + query_count
            success_count = row[3] + (1 if success else 0)
            coze_count = row[4] + (1 if source == "coze" else 0)
            local_count = row[5] + (1 if source == "local" else 0)

            cursor.execute('''
                UPDATE stats SET total_queries = ?, success_count = ?, coze_count = ?, local_count = ?
                WHERE date = ?
            ''', (total, success_count, coze_count, local_count, date_str))
        else:
            cursor.execute('''
                INSERT INTO stats (date, total_queries, success_count, coze_count, local_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (date_str, query_count, 1 if success else 0,
                  1 if source == "coze" else 0, 1 if source == "local" else 0))

        conn.commit()
        conn.close()

    def insert_feedback(self, user_id, username, message, rating=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO feedback (user_id, username, message, rating, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, message, rating, datetime.now()))
        conn.commit()
        conn.close()

    def get_feedback(self, limit=50, offset=0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM feedback ORDER BY timestamp DESC LIMIT ? OFFSET ?
        ''', (limit, offset))

        feedbacks = cursor.fetchall()
        conn.close()

        return [self._row_to_dict(feedback, table="feedback") for feedback in feedbacks]

    def insert_knowledge(self, game, keywords, answer):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        keywords_str = json.dumps(keywords, ensure_ascii=False)
        cursor.execute('''
            INSERT INTO knowledge_base (game, keywords, answer, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (game, keywords_str, answer, datetime.now(), datetime.now()))
        conn.commit()
        conn.close()

    def get_knowledge(self, game=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if game:
            cursor.execute('''
                SELECT * FROM knowledge_base WHERE game = ? ORDER BY updated_at DESC
            ''', (game,))
        else:
            cursor.execute('''
                SELECT * FROM knowledge_base ORDER BY updated_at DESC
            ''')

        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            item = self._row_to_dict(row, table="knowledge_base")
            item["keywords"] = json.loads(item["keywords"])
            results.append(item)

        return results

    def update_knowledge(self, kb_id, game=None, keywords=None, answer=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        params = []

        if game:
            updates.append("game = ?")
            params.append(game)
        if keywords:
            updates.append("keywords = ?")
            params.append(json.dumps(keywords, ensure_ascii=False))
        if answer:
            updates.append("answer = ?")
            params.append(answer)

        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.now())
            params.append(kb_id)

            cursor.execute(f'''
                UPDATE knowledge_base SET {", ".join(updates)} WHERE id = ?
            ''', params)
            conn.commit()

        conn.close()

    def delete_knowledge(self, kb_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM knowledge_base WHERE id = ?
        ''', (kb_id,))
        conn.commit()
        conn.close()

    def get_top_queries(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT query, COUNT(*) as count
            FROM chat_logs
            GROUP BY query
            ORDER BY count DESC
            LIMIT ?
        ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [{"query": row[0], "count": row[1]} for row in rows]

    def get_source_distribution(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT source, COUNT(*) as count
            FROM chat_logs
            GROUP BY source
        ''')

        rows = cursor.fetchall()
        conn.close()

        return {row[0]: row[1] for row in rows}

    def _row_to_dict(self, row, table="chat_logs"):
        if table == "chat_logs":
            return {
                "id": row[0],
                "user_id": row[1],
                "username": row[2],
                "query": row[3],
                "response": row[4],
                "source": row[5],
                "game_category": row[6],
                "score": row[7],
                "timestamp": row[8]
            }
        elif table == "feedback":
            return {
                "id": row[0],
                "user_id": row[1],
                "username": row[2],
                "message": row[3],
                "rating": row[4],
                "timestamp": row[5]
            }
        elif table == "knowledge_base":
            return {
                "id": row[0],
                "game": row[1],
                "keywords": row[2],
                "answer": row[3],
                "created_at": row[4],
                "updated_at": row[5]
            }
        else:
            return dict(zip(range(len(row)), row))