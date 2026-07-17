import pygame
import os

FONT_PATH = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'simhei.ttf')


class Button:
    def __init__(self, x, y, width, height, text, color=(50, 100, 200), hover_color=(70, 120, 220),
                 text_color=(255, 255, 255), font_size=24, border_color=None, border_width=0, shadow=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.Font(FONT_PATH, font_size)
        self.border_color = border_color
        self.border_width = border_width
        self.hovered = False
        self.shadow = shadow

    def draw(self, screen):
        if self.shadow:
            shadow_rect = self.rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(screen, (200, 200, 200), shadow_rect, border_radius=10)
        
        current_color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=10)
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(screen, self.border_color, self.rect, self.border_width, border_radius=10)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class Popup:
    def __init__(self, x, y, width, height, title, message, buttons):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.message = message
        self.buttons = buttons
        self.font_title = pygame.font.Font(FONT_PATH, 36)
        self.font_message = pygame.font.Font(FONT_PATH, 24)

    def draw(self, screen):
        shadow_rect = self.rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(screen, (200, 200, 200), shadow_rect, border_radius=15)
        
        pygame.draw.rect(screen, (255, 255, 255), self.rect, border_radius=15)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=15)

        title_surface = self.font_title.render(self.title, True, (30, 30, 30))
        title_rect = title_surface.get_rect(center=(self.rect.centerx, self.rect.top + 40))
        screen.blit(title_surface, title_rect)

        message_surface = self.font_message.render(self.message, True, (80, 80, 80))
        message_rect = message_surface.get_rect(center=(self.rect.centerx, self.rect.centery))
        screen.blit(message_surface, message_rect)

        for btn in self.buttons:
            btn.draw(screen)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.check_hover(mouse_pos)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn.is_clicked(mouse_pos):
                    return btn.text
        return None


class GameCard:
    def __init__(self, x, y, width, height, game_id, title, description, unlocked, icon_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.game_id = game_id
        self.title = title
        self.description = description
        self.unlocked = unlocked
        self.icon_color = icon_color
        self.font_title = pygame.font.Font(FONT_PATH, 30)
        self.font_desc = pygame.font.Font(FONT_PATH, 18)
        self.hovered = False

    def draw(self, screen):
        shadow_rect = self.rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(screen, (200, 200, 200), shadow_rect, border_radius=12)

        if self.unlocked:
            bg_color = (245, 245, 245) if not self.hovered else (230, 230, 230)
        else:
            bg_color = (200, 200, 200)
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=12)

        if not self.unlocked:
            lock_surface = pygame.font.Font(FONT_PATH, 48).render("🔒", True, (150, 150, 150))
            lock_rect = lock_surface.get_rect(center=self.rect.center)
            screen.blit(lock_surface, lock_rect)

        icon_rect = pygame.Rect(self.rect.left + 20, self.rect.top + 20, 50, 50)
        pygame.draw.rect(screen, self.icon_color, icon_rect, border_radius=8)

        title_surface = self.font_title.render(self.title, True, (30, 30, 30) if self.unlocked else (150, 150, 150))
        title_rect = title_surface.get_rect(topleft=(self.rect.left + 80, self.rect.top + 25))
        screen.blit(title_surface, title_rect)

        desc_surface = self.font_desc.render(self.description, True, (100, 100, 100) if self.unlocked else (180, 180, 180))
        desc_rect = desc_surface.get_rect(topleft=(self.rect.left + 80, self.rect.top + 55))
        screen.blit(desc_surface, desc_rect)

    def check_hover(self, mouse_pos):
        if self.unlocked:
            self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return self.unlocked and self.rect.collidepoint(mouse_pos)


class InputField:
    def __init__(self, x, y, width, height, placeholder="", font_size=24, password=False, max_length=20, show_password=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.font = pygame.font.Font(FONT_PATH, font_size)
        self.active = False
        self.text_color = (30, 30, 30)
        self.placeholder_color = (150, 150, 150)
        self.border_color = (200, 200, 200)
        self.active_border_color = (50, 100, 200)
        self.password = password
        self.max_length = max_length
        # 密码模式下是否显示明文，默认显示（方便用户确认输入）
        self.show_password = show_password

    def draw(self, screen):
        shadow_rect = self.rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(screen, (200, 200, 200), shadow_rect, border_radius=8)

        pygame.draw.rect(screen, (255, 255, 255), self.rect, border_radius=8)

        border_color = self.active_border_color if self.active else self.border_color
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)

        if self.text == "" and not self.active:
            text_surface = self.font.render(self.placeholder, True, self.placeholder_color)
        else:
            # 密码模式且未显示明文时，用 * 占位；否则显示明文
            if self.password and not self.show_password:
                display_text = "*" * len(self.text)
            else:
                display_text = self.text
            text_surface = self.font.render(display_text, True, self.text_color)

        text_rect = text_surface.get_rect(left=self.rect.left + 15, centery=self.rect.centery)
        screen.blit(text_surface, text_rect)

        if self.active:
            cursor_x = text_rect.right + 5
            cursor_y = self.rect.top + 10
            cursor_height = self.rect.height - 20
            pygame.draw.line(screen, (50, 100, 200), (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # 只有点击在自身上才激活，点击其他地方不修改 active
            # 多输入框场景下的失焦/互斥由调用方统一管理
            if self.rect.collidepoint(mouse_pos):
                self.active = True
                pygame.key.set_text_input_rect(self.rect)
                pygame.key.start_text_input()

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            # 普通字符由 TEXTINPUT 事件处理（更好地支持中文 IME 输入法）

        if event.type == pygame.TEXTINPUT and self.active:
            if len(self.text) < self.max_length:
                self.text += event.text

        return False

    def get_text(self):
        return self.text

    def set_active(self, active):
        """设置输入框激活状态"""
        self.active = active

    def toggle_visibility(self):
        """切换密码显示/隐藏"""
        self.show_password = not self.show_password


class Avatar:
    def __init__(self, x, y, size=50):
        self.rect = pygame.Rect(x, y, size, size)
        self.hovered = False

    def draw(self, screen, username):
        shadow_rect = self.rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.circle(screen, (200, 200, 200), shadow_rect.center, self.rect.width // 2)

        pygame.draw.circle(screen, (50, 100, 200), self.rect.center, self.rect.width // 2)
        
        if self.hovered:
            pygame.draw.circle(screen, (70, 120, 220), self.rect.center, self.rect.width // 2, 3)

        font = pygame.font.Font(FONT_PATH, 24)
        initial = username[0] if username else "?"
        text_surface = font.render(initial, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


from .coze_client import CozeClient
from .knowledge_base import KnowledgeBase
from .context_manager import ContextManager
from .chat_history import ChatHistoryManager


class AIChatPopup:
    def __init__(self, x, y, width, height, username="玩家"):
        self.rect = pygame.Rect(x, y, width, height)
        self.font_title = pygame.font.Font(FONT_PATH, 30)
        self.font_message = pygame.font.Font(FONT_PATH, 18)
        self.font_input = pygame.font.Font(FONT_PATH, 20)
        self.font_suggest = pygame.font.Font(FONT_PATH, 16)

        self.username = username
        self.user_id = f"user_{hash(username) % 10000}"

        self.input_field = InputField(x + 20, y + height - 65, width - 200, 40, "输入问题...")
        self.input_field.active = True
        pygame.key.set_text_input_rect(self.input_field.rect)
        pygame.key.start_text_input()

        self.send_button = Button(x + width - 180, y + height - 65, 70, 40, "发送")
        self.feedback_button = Button(x + width - 100, y + height - 65, 80, 40, "反馈")

        self.messages = []
        self.current_source = ""

        self.knowledge_base = KnowledgeBase()
        self.context_manager = ContextManager()
        self.chat_history = ChatHistoryManager(self.user_id)
        self.coze_client = CozeClient()
        self.coze_client.load_config()
        self.use_coze = self.coze_client.api_key and self.coze_client.bot_id
        if self.use_coze:
            self.coze_client.start_worker()

        self.suggested_questions = []
        self.update_suggestions()

        self.error_message = ""
        self.error_timer = 0

        self.add_message("AI客服", "你好！我是游戏助手，有什么问题可以问我~")

        self.feedback_mode = False
        self.feedback_input = None

        self.pending_request_id = None
        self.processing = False

    def add_message(self, sender, text):
        self.messages.append({"sender": sender, "text": text})
        if len(self.messages) > 10:
            self.messages = self.messages[-10:]

    def update_suggestions(self):
        self.suggested_questions = self.context_manager.get_suggested_questions()

    def set_current_game(self, game_id):
        self.context_manager.set_current_game(game_id)
        self.update_suggestions()

    def draw(self, screen):
        shadow_rect = self.rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(screen, (200, 200, 200), shadow_rect, border_radius=15)

        pygame.draw.rect(screen, (255, 255, 255), self.rect, border_radius=15)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=15)

        title_surface = self.font_title.render("🤖 AI游戏助手", True, (30, 30, 30))
        title_rect = title_surface.get_rect(center=(self.rect.centerx, self.rect.top + 35))
        screen.blit(title_surface, title_rect)

        source_text = "智能助手"
        if self.current_source == "coze":
            source_text = "Coze AI"
        elif self.current_source == "local":
            source_text = "本地知识库"
        source_surface = self.font_message.render(f"[{source_text}]", True, (150, 150, 150))
        source_rect = source_surface.get_rect(right=self.rect.right - 20, top=self.rect.top + 15)
        screen.blit(source_surface, source_rect)

        if self.error_message:
            error_surface = self.font_message.render(self.error_message, True, (255, 80, 80))
            error_rect = error_surface.get_rect(center=(self.rect.centerx, self.rect.top + 70))
            screen.blit(error_surface, error_rect)

        input_area_top = self.rect.bottom - 70
        max_message_y = input_area_top - 10
        message_area_top = self.rect.top + 80

        max_width = self.rect.width - 60
        line_height = 24
        padding = 15

        all_lines = []
        for msg in self.messages:
            lines = self.wrap_text(msg["text"], max_width)
            all_lines.append({
                "sender": msg["sender"],
                "lines": lines,
                "line_count": len(lines)
            })

        total_message_height = sum((line_count * line_height + 35 + padding) for line_count in [m["line_count"] for m in all_lines])
        scroll_offset = max(0, total_message_height - (max_message_y - message_area_top))

        current_y = message_area_top - scroll_offset

        for msg_data in all_lines:
            sender = msg_data["sender"]
            lines = msg_data["lines"]
            line_count = msg_data["line_count"]

            if current_y + line_count * line_height + 35 > max_message_y:
                break

            if sender == "AI客服":
                bubble_color = (50, 120, 200)
                text_color = (255, 255, 255)
                sender_color = (50, 120, 200)
                align_left = True
                bubble_padding = (15, 10)
            else:
                bubble_color = (230, 230, 230)
                text_color = (30, 30, 30)
                sender_color = (100, 100, 100)
                align_left = True
                bubble_padding = (15, 10)

            sender_surface = self.font_message.render(f"{sender}:", True, sender_color)
            sender_width = sender_surface.get_rect().width

            if align_left:
                bubble_x = self.rect.left + 20
                max_text_width = max_width
            else:
                max_text_width = max_width

            bubble_height = line_count * line_height + bubble_padding[1] * 2
            bubble_width = max_text_width + bubble_padding[0] * 2

            bubble_rect = pygame.Rect(bubble_x, current_y + 25, bubble_width, bubble_height)
            pygame.draw.rect(screen, bubble_color, bubble_rect, border_radius=10)

            screen.blit(sender_surface, (bubble_x, current_y))

            for i, line in enumerate(lines):
                text_surface = self.font_message.render(line, True, text_color)
                screen.blit(text_surface, (bubble_x + bubble_padding[0], current_y + 25 + bubble_padding[1] + i * line_height))

            current_y += 25 + bubble_height + padding

        suggest_y = current_y + 10
        if suggest_y + 35 < input_area_top and self.suggested_questions:
            suggest_label = self.font_suggest.render("快捷提问：", True, (100, 100, 100))
            screen.blit(suggest_label, (self.rect.left + 20, suggest_y))

            common_questions = self.suggested_questions[:4]
            game_questions = self.suggested_questions[4:8]

            button_x = self.rect.left + 20 + suggest_label.get_width() + 10
            button_y = suggest_y - 5

            for i, question in enumerate(common_questions):
                btn_width = min(self.font_suggest.size(question)[0] + 20, 140)
                btn = Button(button_x, button_y, btn_width, 28, question,
                            (245, 245, 255), (225, 225, 245),
                            text_color=(0, 102, 204), font_size=14, shadow=False)
                btn.draw(screen)
                button_x += btn_width + 10
                if button_x + 100 > self.rect.right - 20:
                    button_x = self.rect.left + 20 + suggest_label.get_width() + 10
                    button_y += 35

            if game_questions:
                game_label = self.font_suggest.render("当前游戏：", True, (100, 100, 100))
                button_x = self.rect.left + 20 + game_label.get_width() + 10
                screen.blit(game_label, (self.rect.left + 20, button_y))

                for i, question in enumerate(game_questions):
                    btn_width = min(self.font_suggest.size(question)[0] + 20, 140)
                    btn = Button(button_x, button_y, btn_width, 28, question,
                                (230, 245, 255), (210, 230, 245),
                                text_color=(0, 128, 255), font_size=14, shadow=False)
                    btn.draw(screen)
                    button_x += btn_width + 10
                    if button_x + 100 > self.rect.right - 20:
                        button_x = self.rect.left + 20 + game_label.get_width() + 10
                        button_y += 35

        self.input_field.draw(screen)
        self.send_button.draw(screen)
        self.feedback_button.draw(screen)

        if self.feedback_mode and self.feedback_input:
            overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, self.rect.topleft)

            feedback_title = self.font_title.render("💬 意见反馈", True, (255, 255, 255))
            screen.blit(feedback_title, (self.rect.left + 50, self.rect.top + 80))

            self.feedback_input.draw(screen)

            cancel_btn = Button(self.rect.left + 50, self.rect.top + 200, 100, 40, "取消")
            submit_btn = Button(self.rect.left + 250, self.rect.top + 200, 100, 40, "提交")
            cancel_btn.draw(screen)
            submit_btn.draw(screen)

    def wrap_text(self, text, max_width):
        lines = []
        current_line = ""

        for char in text:
            if char == "\n":
                lines.append(current_line)
                current_line = ""
                continue

            test_line = current_line + char
            text_width, _ = self.font_message.size(test_line)
            if text_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = char

        if current_line:
            lines.append(current_line)

        return lines

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.send_button.check_hover(mouse_pos)
        self.feedback_button.check_hover(mouse_pos)

        if self.feedback_mode:
            return self.handle_feedback_event(event, mouse_pos)

        handled = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.input_field.rect.collidepoint(mouse_pos):
                self.input_field.active = True
                pygame.key.set_text_input_rect(self.input_field.rect)
                handled = True
            else:
                self.input_field.active = False

            input_area_top = self.rect.bottom - 70
            max_message_y = input_area_top - 10
            message_area_top = self.rect.top + 80

            all_lines = []
            for msg in self.messages:
                lines = self.wrap_text(msg["text"], self.rect.width - 60)
                all_lines.append(len(lines))

            total_height = sum((lc * 24 + 35 + 15) for lc in all_lines)
            scroll_offset = max(0, total_height - (max_message_y - message_area_top))

            suggest_y = message_area_top - scroll_offset + total_height + 10

            suggest_label_width = self.font_suggest.size("快捷提问：")[0]
            game_label_width = self.font_suggest.size("当前游戏：")[0]

            button_x = self.rect.left + 20 + suggest_label_width + 10
            button_y = suggest_y - 5

            common_questions = self.suggested_questions[:4]
            for question in common_questions:
                btn_width = min(self.font_suggest.size(question)[0] + 20, 140)
                btn_rect = pygame.Rect(button_x, button_y, btn_width, 28)
                if btn_rect.collidepoint(mouse_pos):
                    self.handle_quick_question(question)
                    return True
                button_x += btn_width + 10
                if button_x + 100 > self.rect.right - 20:
                    button_x = self.rect.left + 20 + suggest_label_width + 10
                    button_y += 35

            game_questions = self.suggested_questions[4:8]
            if game_questions:
                button_x = self.rect.left + 20 + game_label_width + 10
                button_y = button_y if button_y > suggest_y + 30 else suggest_y + 30

                for question in game_questions:
                    btn_width = min(self.font_suggest.size(question)[0] + 20, 140)
                    btn_rect = pygame.Rect(button_x, button_y, btn_width, 28)
                    if btn_rect.collidepoint(mouse_pos):
                        self.handle_quick_question(question)
                        return True
                    button_x += btn_width + 10
                    if button_x + 100 > self.rect.right - 20:
                        button_x = self.rect.left + 20 + game_label_width + 10
                        button_y += 35

            if self.send_button.is_clicked(mouse_pos):
                user_text = self.input_field.get_text().strip()
                if user_text:
                    self.process_query(user_text)
                    return True

            if self.feedback_button.is_clicked(mouse_pos):
                self.start_feedback_mode()
                return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and self.input_field.active:
            user_text = self.input_field.get_text().strip()
            if user_text:
                self.process_query(user_text)
                return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.input_field.active = False

        input_handled = self.input_field.handle_event(event)
        return handled or input_handled

    def handle_quick_question(self, question):
        self.input_field.text = question
        self.process_query(question)

    def process_query(self, user_text):
        if self.processing:
            return

        self.processing = True
        self.add_message("你", user_text)
        self.context_manager.add_message("user", user_text)

        detected_game = self.context_manager.extract_keywords(user_text)
        if detected_game:
            self.context_manager.set_current_game(detected_game)

        response, source, game_category, score = self.get_response(user_text)

        self.add_message("AI客服", response)
        self.context_manager.add_message("assistant", response)
        self.current_source = source
        self.input_field.text = ""

        try:
            self.chat_history.add_message(
                username=self.username,
                query=user_text,
                response=response,
                source=source,
                game_category=game_category,
                score=score
            )
        except Exception as e:
            print(f"Failed to save chat history: {e}")

        self.update_suggestions()
        self.processing = False

    def get_response(self, question):
        detected_game = self.context_manager.extract_keywords(question)
        current_topic = self.context_manager.get_topic()
        effective_game = detected_game or current_topic or self.context_manager.current_game

        expanded_query = self.context_manager.expand_query_with_context(question)

        answer, category, score, layer = self.knowledge_base.search(expanded_query, effective_game)

        if layer == "layer1":
            return answer, "local", category, score

        if layer == "layer2":
            return answer, "local", category, score

        if self.use_coze:
            try:
                game_names = {
                    "snake": "贪吃蛇",
                    "parkour": "横版跑酷",
                    "planewar": "飞机大战",
                    "spotdifference": "找茬",
                    "gomoku": "五子棋"
                }
                game_context = game_names.get(effective_game, "") if effective_game else ""
                
                history = self.context_manager.get_context()
                
                full_query = ""
                if game_context:
                    full_query = f"【游戏上下文】当前游戏：{game_context}\n"
                if history:
                    full_query += "【对话历史】\n"
                    for msg in history[-5:]:
                        role = "用户" if msg.get("role") == "user" else "AI"
                        full_query += f"{role}: {msg.get('content', '')}\n"
                full_query += f"\n【用户问题】{question}"

                self.pending_request_id = self.coze_client.send_async_request(full_query)
                self.pending_question = question
                return "正在思考...", "coze", effective_game, 0
            except Exception as e:
                self.show_error("网络连接异常，切换本地模式")
                print(f"Coze exception: {e}")

        fallback_answer, fb_category, fb_score, fb_layer = self.knowledge_base.search(question, effective_game)
        if fallback_answer:
            return fallback_answer, "local", fb_category, fb_score
            
        fallback = "抱歉，我不太理解你的问题。你可以问我：\n• 关卡怎么解锁\n• 通关条件是什么\n• 操作按键怎么按\n• 存档丢失怎么办\n• 称号怎么获得"
        return fallback, "local", effective_game, 0

    def show_error(self, message):
        self.error_message = message
        self.error_timer = 50

    def update(self):
        if self.error_timer > 0:
            self.error_timer -= 1
            if self.error_timer <= 0:
                self.error_message = ""

        if self.use_coze and self.pending_request_id:
            response = self.coze_client.get_response(self.pending_request_id, timeout=0.1)
            if response and response != {"error": "Timeout", "fallback": True}:
                self._handle_async_response(response)
                self.pending_request_id = None

    def _handle_async_response(self, response):
        if response.get("answer"):
            coze_answer = response["answer"]
            if "无法为你解答" in coze_answer or "暂时无法" in coze_answer:
                fallback_answer, fb_category, fb_score, fb_layer = self.knowledge_base.search(
                    self.pending_question, self.context_manager.current_game
                )
                if fallback_answer:
                    coze_answer = fallback_answer
            self.add_message("AI客服", coze_answer)
            self.context_manager.add_message("assistant", coze_answer)
            self.current_source = "coze"
        elif response.get("error"):
            self.show_error("Coze连接失败，切换本地模式")

        try:
            self.chat_history.add_message(
                username=self.username,
                query=self.pending_question,
                response=response.get("answer", ""),
                source="coze",
                game_category=self.context_manager.current_game,
                score=0
            )
        except Exception as e:
            print(f"Failed to save chat history: {e}")

        self.update_suggestions()
        self.processing = False
        self.pending_question = None

    def start_feedback_mode(self):
        self.feedback_mode = True
        input_x = self.rect.left + 50
        input_y = self.rect.top + 140
        self.feedback_input = InputField(input_x, input_y, 400, 45, "请输入您的反馈或建议...")
        self.feedback_input.active = True

    def handle_feedback_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cancel_btn = pygame.Rect(self.rect.left + 50, self.rect.top + 200, 100, 40)
            submit_btn = pygame.Rect(self.rect.left + 250, self.rect.top + 200, 100, 40)

            if cancel_btn.collidepoint(mouse_pos):
                self.feedback_mode = False
                self.feedback_input = None
                return True

            if submit_btn.collidepoint(mouse_pos):
                feedback_text = self.feedback_input.get_text().strip() if self.feedback_input else ""
                if feedback_text:
                    success = self.chat_history.add_feedback(self.username, feedback_text)
                    if success:
                        self.add_message("AI客服", "感谢您的反馈！我们会认真处理。")
                    else:
                        self.add_message("AI客服", "反馈提交失败，请稍后再试。")
                else:
                    self.add_message("AI客服", "请输入反馈内容。")
                self.feedback_mode = False
                self.feedback_input = None
                return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.feedback_mode = False
            self.feedback_input = None
            return True

        if self.feedback_input:
            return self.feedback_input.handle_event(event)

        return False