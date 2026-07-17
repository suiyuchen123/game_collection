import requests
import json
import os
import threading
import time
import queue

COZE_API_BASE_URL = "https://api.coze.cn/v3/chat"


class CozeClient:
    def __init__(self, api_key=None, bot_id=None):
        self.api_key = api_key
        self.bot_id = bot_id
        self.user_id = "game_player"
        self.response_queue = queue.Queue()
        self.request_queue = queue.Queue()
        self.worker_thread = None
        self.running = False
        self.pending_requests = {}
        self.lock = threading.Lock()

    def load_config(self, config_path=None):
        env_api_key = os.environ.get("COZE_API_KEY")
        env_bot_id = os.environ.get("COZE_BOT_ID")
        
        if env_api_key:
            self.api_key = env_api_key
        if env_bot_id:
            self.bot_id = env_bot_id
            
        if self.api_key and self.bot_id:
            return True

        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "coze_config.json")

        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.api_key = config.get("api_key", self.api_key)
                    self.bot_id = config.get("bot_id", self.bot_id)
                    return True
            except Exception as e:
                print(f"Failed to load coze config: {e}")
                return False
        return False

    def set_config(self, api_key, bot_id):
        self.api_key = api_key
        self.bot_id = bot_id

    def chat(self, message, user_id=None, history=None, stream=False):
        if not self.api_key or not self.bot_id:
            return {"error": "Coze API config not set", "fallback": True}

        current_user_id = user_id or self.user_id

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        additional_messages = []
        if history:
            additional_messages.extend(history)

        additional_messages.append({
            "role": "user",
            "content": message,
            "content_type": "text"
        })

        payload = {
            "bot_id": self.bot_id,
            "user_id": current_user_id,
            "stream": stream,
            "auto_save_history": True,
            "additional_messages": additional_messages
        }

        try:
            response = requests.post(COZE_API_BASE_URL, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()

            if stream:
                return data
            else:
                if data.get("code") == 0:
                    messages = data.get("data", {}).get("messages", [])
                    for msg in messages:
                        if msg.get("role") == "assistant":
                            content = msg.get("content", "")
                            if content:
                                return {"answer": content}
                            else:
                                return {"answer": "", "fallback": True}
                    return {"answer": "", "fallback": True}
                else:
                    return {"error": data.get("msg", "Unknown error"), "fallback": True}

        except requests.exceptions.RequestException as e:
            return {"error": str(e), "fallback": True}

    def chat_stream(self, message, user_id=None, history=None):
        if not self.api_key or not self.bot_id:
            yield {"error": "Coze API config not set", "fallback": True}
            return

        current_user_id = user_id or self.user_id

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        additional_messages = []
        if history:
            additional_messages.extend(history)

        additional_messages.append({
            "role": "user",
            "content": message,
            "content_type": "text"
        })

        payload = {
            "bot_id": self.bot_id,
            "user_id": current_user_id,
            "stream": True,
            "auto_save_history": False,
            "additional_messages": additional_messages
        }

        try:
            response = requests.post(COZE_API_BASE_URL, headers=headers, json=payload, timeout=30, stream=True)
            response.raise_for_status()

            has_content = False

            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8")

                    if line_str.startswith("data:"):
                        data_str = line_str[5:]
                        try:
                            data = json.loads(data_str)
                            if isinstance(data, dict):
                                content = data.get("content", "")
                                if isinstance(content, str) and content:
                                    if content.startswith('{"msg_type"'):
                                        continue
                                    if content.startswith('{"finish_reason"'):
                                        continue
                                    has_content = True
                                    yield content
                        except json.JSONDecodeError:
                            pass

            if not has_content:
                yield {"fallback": True}

        except requests.exceptions.RequestException as e:
            yield {"error": str(e), "fallback": True}
            return

    def get_chat_response(self, message, user_id=None, history=None):
        result = ""
        suggestions = []
        full_answer_found = False
        
        for chunk in self.chat_stream(message, user_id, history):
            if isinstance(chunk, dict):
                if chunk.get("fallback"):
                    return {"answer": "", "fallback": True}
                elif chunk.get("error"):
                    return {"error": chunk["error"], "fallback": True}
            else:
                if len(chunk) > 0 and len(chunk) < 50 and "？" in chunk:
                    suggestions.append(chunk)
                elif len(chunk) > 20:
                    if full_answer_found:
                        continue
                    full_answer_found = True
                    result = chunk
                else:
                    if not full_answer_found:
                        result += chunk
        
        if result:
            return {"answer": result, "suggestions": suggestions}
        return {"answer": "", "fallback": True}

    def chat_with_context(self, message, game_context=None, history=None):
        context_prompt = ""
        if game_context:
            context_prompt = f"【游戏上下文】当前游戏：{game_context}\n"
        
        if history:
            context_prompt += "【对话历史】\n"
            for msg in history[-5:]:
                role = "用户" if msg.get("role") == "user" else "AI"
                context_prompt += f"{role}: {msg.get('content', '')}\n"
        
        full_query = f"{context_prompt}\n【用户问题】{message}"
        return self.get_chat_response(full_query)

    def start_worker(self):
        if self.running:
            return
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def stop_worker(self):
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)

    def _worker_loop(self):
        while self.running:
            try:
                request = self.request_queue.get(timeout=1)
                if not self.running:
                    break
                request_id = request["request_id"]
                message = request["message"]
                user_id = request.get("user_id")
                history = request.get("history")
                
                result = self.get_chat_response(message, user_id, history)
                self.response_queue.put({"request_id": request_id, "result": result})
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}")

    def send_async_request(self, message, user_id=None, history=None):
        request_id = f"req_{int(time.time() * 1000)}_{id(message)}"
        self.request_queue.put({
            "request_id": request_id,
            "message": message,
            "user_id": user_id,
            "history": history
        })
        return request_id

    def get_response(self, request_id, timeout=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.response_queue.get(timeout=0.1)
                if response.get("request_id") == request_id:
                    return response.get("result")
            except queue.Empty:
                continue
        return {"error": "Timeout", "fallback": True}

    def has_pending_request(self):
        return not self.response_queue.empty()

    def get_any_response(self):
        try:
            return self.response_queue.get_nowait()
        except queue.Empty:
            return None

    def clear_pending(self):
        with self.lock:
            self.pending_requests.clear()
        while not self.response_queue.empty():
            try:
                self.response_queue.get_nowait()
            except queue.Empty:
                break