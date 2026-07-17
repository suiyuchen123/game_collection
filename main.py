import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

FONT_PATH = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'simhei.ttf')

from core.save_manager import SaveManager
from core.ui import Button, Popup, GameCard, InputField, Avatar, AIChatPopup
from core.game_state import GameState, GameResult
from games.snake.snake_game import SnakeGame
from games.parkour.parkour_game import ParkourGame
from games.planewar.planewar_game import PlanewarGame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

GAMES_INFO = [
    {"id": 1, "key": "game1", "title": "贪吃蛇", "description": "简单难度 - 3关", "icon_color": (50, 200, 50),
     "game_class": SnakeGame, "max_levels": 3},
    {"id": 2, "key": "game2", "title": "横版跑酷", "description": "中等难度 - 3关", "icon_color": (50, 150, 255),
     "game_class": ParkourGame, "max_levels": 3},
    {"id": 3, "key": "game3", "title": "飞机大战", "description": "困难难度 - 1关", "icon_color": (255, 100, 100),
     "game_class": PlanewarGame, "max_levels": 1},
]


class GameCollection:
    def __init__(self):
        pygame.init()
        # 启用文本输入事件，让 IME 中文输入法生效
        try:
            pygame.key.start_text_input()
        except Exception:
            pass
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("游戏闯关合集")
        self.clock = pygame.time.Clock()

        self.save_manager = SaveManager()
        self.game_state = GameState()

        self.current_game_instance = None
        self.current_game_info = None

        self.game_cards = []
        self.popup = None

        self.avatar = Avatar(SCREEN_WIDTH - 70, 15, 50)
        self.ai_button = Button(SCREEN_WIDTH - 70, 75, 50, 50, "🎧", (240, 240, 240), (220, 220, 220),
                                text_color=(30, 30, 30), font_size=28)
        self.ai_chat_popup = None

        self.username = self.save_manager.get_username()
        self.current_screen = "login" if not self.username else "menu"

        # 登录页面：用户名 + 密码两个输入框
        input_x = SCREEN_WIDTH // 2 - 150
        self.login_username_input = InputField(input_x, 245, 300, 45, "请输入用户名")
        # 密码框默认显示明文，方便用户确认输入；右侧加切换按钮可隐藏
        self.login_password_input = InputField(input_x, 330, 245, 45, "请输入密码", password=True, show_password=True)
        self.login_password_toggle = Button(input_x + 255, 330, 55, 45, "隐藏",
                                             (240, 240, 240), (220, 220, 220),
                                             text_color=(30, 30, 30), font_size=18, shadow=False)
        self.login_button = Button(SCREEN_WIDTH // 2 - 100, 400, 200, 45, "登录")
        self.login_error = ""
        # 默认激活用户名输入框，省去用户先点击的步骤
        if self.current_screen == "login":
            self.login_username_input.active = True

        self.user_menu_buttons = None
        self.user_menu_input = None

        self.setup_main_menu()

    def setup_main_menu(self):
        self.game_cards = []
        card_width = SCREEN_WIDTH - 200
        card_height = 100
        start_y = 100

        for i, game_info in enumerate(GAMES_INFO):
            unlocked = self.save_manager.is_game_unlocked(game_info["id"])
            completed = self.save_manager.get_completed_levels(game_info["key"])
            desc = f"{game_info['description']} | 已通关: {completed}/{game_info['max_levels']}"
            card = GameCard(
                80, start_y + i * (card_height + 20),
                card_width, card_height,
                game_info["id"], game_info["title"],
                desc, unlocked, game_info["icon_color"]
            )
            self.game_cards.append(card)

        title_btn_y = start_y + len(GAMES_INFO) * (card_height + 20) + 30
        self.title_button = Button(
            SCREEN_WIDTH // 2 - 150, title_btn_y, 300, 50,
            "查看称号", (50, 100, 200), (70, 120, 220),
            text_color=(255, 255, 255), font_size=24
        )

        reset_btn_y = title_btn_y + 70
        self.reset_button = Button(
            SCREEN_WIDTH // 2 - 100, reset_btn_y, 200, 40,
            "重置进度", (200, 100, 100), (220, 120, 120),
            text_color=(255, 255, 255), font_size=20
        )

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                self.update_hover(mouse_pos)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                if self.current_screen == "login":
                    if self.login_username_input.rect.collidepoint(mouse_pos):
                        self.login_username_input.active = True
                        self.login_password_input.active = False
                    elif self.login_password_input.rect.collidepoint(mouse_pos):
                        self.login_password_input.active = True
                        self.login_username_input.active = False
                    if self.login_password_toggle.is_clicked(mouse_pos):
                        self.login_password_input.toggle_visibility()
                        self.login_password_toggle.text = "显示" if not self.login_password_input.show_password else "隐藏"
                    else:
                        self.handle_login_click(mouse_pos)
                elif self.game_state.current_state in [GameState.LEVEL_COMPLETE, GameState.GAME_OVER]:
                    self.handle_popup_click(mouse_pos)
                elif self.game_state.current_state == GameState.TITLE_VIEW:
                    self.game_state.current_state = GameState.MENU
                elif self.current_screen == "menu":
                    if self.ai_chat_popup:
                        if not self.ai_chat_popup.rect.collidepoint(mouse_pos):
                            self.ai_chat_popup = None
                    else:
                        if self.user_menu_buttons:
                            if self.handle_user_menu_click(mouse_pos):
                                continue
                        self.handle_menu_click(mouse_pos)

            if event.type == pygame.KEYDOWN:
                if self.current_screen == "login":
                    if event.key == pygame.K_RETURN:
                        self.try_login()
                    elif event.key == pygame.K_TAB:
                        # 在用户名和密码输入框之间切换
                        if self.login_username_input.active:
                            self.login_username_input.active = False
                            self.login_password_input.active = True
                        else:
                            self.login_password_input.active = False
                            self.login_username_input.active = True
                elif self.user_menu_input and event.key == pygame.K_RETURN:
                    new_name = self.user_menu_input.get_text().strip()
                    if new_name:
                        self.username = new_name
                        self.save_manager.set_username(new_name)
                    self.close_user_menu()

            if self.current_screen == "login":
                self.login_username_input.handle_event(event)
                self.login_password_input.handle_event(event)
            elif self.user_menu_input:
                self.user_menu_input.handle_event(event)
            elif self.ai_chat_popup:
                self.ai_chat_popup.handle_event(event)
            elif self.game_state.current_state == GameState.PLAYING:
                if self.current_game_instance:
                    self.current_game_instance.handle_event(event)

    def update_hover(self, mouse_pos):
        if self.current_screen == "login":
            self.login_button.check_hover(mouse_pos)
            self.login_password_toggle.check_hover(mouse_pos)
        elif self.current_screen == "menu":
            for card in self.game_cards:
                card.check_hover(mouse_pos)
            self.title_button.check_hover(mouse_pos)
            self.reset_button.check_hover(mouse_pos)
            self.avatar.check_hover(mouse_pos)
            self.ai_button.check_hover(mouse_pos)
            if self.user_menu_buttons:
                for btn in self.user_menu_buttons:
                    btn.check_hover(mouse_pos)

    def handle_login_click(self, mouse_pos):
        if self.login_button.is_clicked(mouse_pos):
            self.try_login()

    def try_login(self):
        """校验用户名和密码，全部非空则登录成功"""
        username = self.login_username_input.get_text().strip()
        password = self.login_password_input.get_text().strip()
        if not username:
            self.login_error = "请输入用户名"
            self.login_username_input.active = True
            self.login_password_input.active = False
        elif not password:
            self.login_error = "请输入密码"
            self.login_password_input.active = True
            self.login_username_input.active = False
        else:
            self.username = username
            self.save_manager.set_username(username)
            self.current_screen = "menu"
            self.login_error = ""

    def handle_menu_click(self, mouse_pos):
        for card in self.game_cards:
            if card.is_clicked(mouse_pos):
                self.start_game(card.game_id)
                return

        if self.title_button.is_clicked(mouse_pos):
            self.game_state.current_state = GameState.TITLE_VIEW
            return

        if self.reset_button.is_clicked(mouse_pos):
            self.save_manager.reset_progress()
            self.setup_main_menu()
            return

        if self.avatar.is_clicked(mouse_pos):
            self.show_user_menu()
            return

        if self.ai_button.is_clicked(mouse_pos):
            self.ai_chat_popup = AIChatPopup(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 200, 500, 400, self.username)
            return

    def handle_user_menu_click(self, mouse_pos):
        menu_rect = pygame.Rect(230, 150, 340, 250)
        
        if self.user_menu_input:
            if not menu_rect.collidepoint(mouse_pos):
                self.close_user_menu()
            return

        for btn in self.user_menu_buttons:
            if btn.is_clicked(mouse_pos):
                if btn.text == "退出登录":
                    self.save_manager.set_username("")
                    self.username = ""
                    self.current_screen = "login"
                    self.close_user_menu()
                elif btn.text == "修改用户名":
                    self.user_menu_input = InputField(250, 220, 300, 50, self.username)
                    self.user_menu_input.text = self.username
                elif btn.text == "关闭":
                    self.close_user_menu()
                return

        if not menu_rect.collidepoint(mouse_pos):
            self.close_user_menu()

    def handle_ai_chat_click(self, mouse_pos):
        if not self.ai_chat_popup.rect.collidepoint(mouse_pos):
            self.ai_chat_popup = None
            return True
        return False

    def handle_popup_click(self, mouse_pos):
        if self.popup:
            for btn in self.popup.buttons:
                if btn.is_clicked(mouse_pos):
                    if btn.text == "返回主菜单":
                        self.back_to_menu()
                    elif btn.text == "下一关":
                        self.next_level()
                    elif btn.text == "重新开始":
                        self.restart_level()
                    return

    def show_user_menu(self):
        self.user_menu_buttons = [
            Button(250, 180, 300, 45, "修改用户名"),
            Button(250, 280, 300, 45, "退出登录"),
            Button(250, 340, 300, 45, "关闭", (200, 200, 200), (180, 180, 180), text_color=(30, 30, 30))
        ]
        self.user_menu_input = None

    def close_user_menu(self):
        self.user_menu_buttons = None
        self.user_menu_input = None

    def update(self):
        if self.game_state.current_state == GameState.PLAYING:
            if self.current_game_instance:
                self.current_game_instance.update()
                if self.current_game_instance.is_game_over():
                    self.show_game_over()
                elif self.current_game_instance.is_won():
                    self.show_level_complete()

        if self.ai_chat_popup:
            self.ai_chat_popup.update()

    def draw(self):
        if self.current_screen == "login":
            self.draw_login_screen()
        elif self.game_state.current_state == GameState.PLAYING:
            if self.current_game_instance:
                self.current_game_instance.draw()
        elif self.game_state.current_state in [GameState.LEVEL_COMPLETE, GameState.GAME_OVER]:
            if self.current_game_instance:
                self.current_game_instance.draw()
            if self.popup:
                self.popup.draw(self.screen)
        elif self.game_state.current_state == GameState.TITLE_VIEW:
            self.draw_title_view()
        elif self.current_screen == "menu":
            self.draw_main_menu()

    def draw_login_screen(self):
        self.screen.fill((255, 255, 255))

        font_title = pygame.font.Font(FONT_PATH, 50)
        title_surface = font_title.render("🎮 游戏闯关合集", True, (30, 30, 30))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 110))
        self.screen.blit(title_surface, title_rect)

        font_subtitle = pygame.font.Font(FONT_PATH, 22)
        subtitle_surface = font_subtitle.render("请登录开始游戏", True, (100, 100, 100))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 165))
        self.screen.blit(subtitle_surface, subtitle_rect)

        font_label = pygame.font.Font(FONT_PATH, 18)
        # 用户名标签
        user_label = font_label.render("用户名", True, (60, 60, 60))
        self.screen.blit(user_label, (SCREEN_WIDTH // 2 - 150, 220))
        # 密码标签
        pwd_label = font_label.render("密码", True, (60, 60, 60))
        self.screen.blit(pwd_label, (SCREEN_WIDTH // 2 - 150, 305))

        self.login_username_input.draw(self.screen)
        self.login_password_input.draw(self.screen)
        self.login_password_toggle.draw(self.screen)
        self.login_button.draw(self.screen)

        # 错误提示
        if self.login_error:
            font_error = pygame.font.Font(FONT_PATH, 18)
            error_surface = font_error.render(self.login_error, True, (220, 50, 50))
            error_rect = error_surface.get_rect(center=(SCREEN_WIDTH // 2, 470))
            self.screen.blit(error_surface, error_rect)

        font_hint = pygame.font.Font(FONT_PATH, 16)
        hint_surface = font_hint.render("回车键登录  |  Tab 键切换输入框", True, (150, 150, 150))
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(hint_surface, hint_rect)

    def draw_main_menu(self):
        self.screen.fill((255, 255, 255))

        font_title = pygame.font.Font(FONT_PATH, 50)
        title_surface = font_title.render("🎮 游戏闯关合集", True, (30, 30, 30))
        title_rect = title_surface.get_rect(topleft=(30, 25))
        self.screen.blit(title_surface, title_rect)

        self.avatar.draw(self.screen, self.username)
        
        font_user = pygame.font.Font(FONT_PATH, 16)
        user_surface = font_user.render(self.username, True, (100, 100, 100))
        user_rect = user_surface.get_rect(center=(SCREEN_WIDTH - 45, 70))
        self.screen.blit(user_surface, user_rect)

        self.ai_button.draw(self.screen)

        for card in self.game_cards:
            card.draw(self.screen)

        self.title_button.draw(self.screen)
        self.reset_button.draw(self.screen)

        if self.user_menu_buttons:
            shadow_rect = pygame.Rect(230, 150, 340, 250)
            pygame.draw.rect(self.screen, (200, 200, 200), shadow_rect, border_radius=15)
            pygame.draw.rect(self.screen, (255, 255, 255), shadow_rect, 2, border_radius=15)
            
            font_menu_title = pygame.font.Font(FONT_PATH, 28)
            menu_title_surface = font_menu_title.render("用户设置", True, (30, 30, 30))
            menu_title_rect = menu_title_surface.get_rect(center=(SCREEN_WIDTH // 2, 185))
            self.screen.blit(menu_title_surface, menu_title_rect)
            
            if self.user_menu_input:
                self.user_menu_input.draw(self.screen)
            else:
                for btn in self.user_menu_buttons:
                    btn.draw(self.screen)

        if self.ai_chat_popup:
            self.ai_chat_popup.draw(self.screen)

    def draw_title_view(self):
        self.screen.fill((255, 255, 255))

        font_title = pygame.font.Font(FONT_PATH, 40)
        title_surface = font_title.render("🏆 称号展示", True, (30, 30, 30))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title_surface, title_rect)

        earned = self.save_manager.has_title()
        title_text = "游戏高手高手高高手"
        font_big = pygame.font.Font(FONT_PATH, 36)
        text_color = (255, 180, 0) if earned else (180, 180, 180)
        title_surface = font_big.render(title_text, True, text_color)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(title_surface, title_rect)

        if earned:
            stars = "⭐⭐⭐⭐⭐"
            star_font = pygame.font.Font(FONT_PATH, 30)
            star_surface = star_font.render(stars, True, (255, 180, 0))
            star_rect = star_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(star_surface, star_rect)

            desc_font = pygame.font.Font(FONT_PATH, 24)
            desc_surface = desc_font.render("恭喜你通关了所有游戏！", True, (50, 200, 50))
            desc_rect = desc_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
            self.screen.blit(desc_surface, desc_rect)
        else:
            desc_font = pygame.font.Font(FONT_PATH, 24)
            desc_surface = desc_font.render("通关所有游戏即可解锁此称号", True, (150, 150, 150))
            desc_rect = desc_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(desc_surface, desc_rect)

        hint_font = pygame.font.Font(FONT_PATH, 20)
        hint_surface = hint_font.render("点击任意位置返回主菜单", True, (150, 150, 150))
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(hint_surface, hint_rect)

    def start_game(self, game_id):
        game_info = next(g for g in GAMES_INFO if g["id"] == game_id)
        self.current_game_info = game_info

        completed = self.save_manager.get_completed_levels(game_info["key"])
        start_level = completed + 1 if completed < game_info["max_levels"] else 1

        self.current_game_instance = game_info["game_class"](self.screen, start_level)
        self.game_state.current_game = game_id
        self.game_state.current_level = start_level
        self.game_state.current_state = GameState.PLAYING

    def show_level_complete(self):
        game_key = self.current_game_info["key"]
        max_levels = self.current_game_info["max_levels"]
        self.save_manager.add_completed_level(game_key)

        has_next_level = self.game_state.current_level < max_levels

        if has_next_level:
            message = f"🎉 第 {self.game_state.current_level} 关通关！\n进度: {self.game_state.current_level}/{max_levels}"
            btn_next = Button(350, 340, 100, 40, "下一关", (50, 150, 50), (60, 170, 60))
            btn_menu = Button(220, 340, 100, 40, "返回主菜单", (200, 200, 200), (180, 180, 180), text_color=(30, 30, 30))
            self.popup = Popup(200, 180, 400, 200, "关卡通关", message, [btn_menu, btn_next])
        else:
            message = f"🎉 恭喜通关全部关卡！\n解锁新游戏！"
            btn_menu = Button(350, 340, 100, 40, "返回主菜单", (50, 150, 50), (60, 170, 60))
            self.popup = Popup(200, 180, 400, 200, "游戏通关", message, [btn_menu])

        self.game_state.current_state = GameState.LEVEL_COMPLETE

    def show_game_over(self):
        message = f"💀 游戏结束\n当前关卡: {self.game_state.current_level}"
        btn_restart = Button(350, 340, 100, 40, "重新开始", (50, 150, 50), (60, 170, 60))
        btn_menu = Button(220, 340, 100, 40, "返回主菜单", (200, 200, 200), (180, 180, 180), text_color=(30, 30, 30))
        self.popup = Popup(200, 180, 400, 200, "游戏失败", message, [btn_menu, btn_restart])
        self.game_state.current_state = GameState.GAME_OVER

    def next_level(self):
        self.game_state.current_level += 1
        self.current_game_instance = self.current_game_info["game_class"](
            self.screen, self.game_state.current_level
        )
        self.popup = None
        self.game_state.current_state = GameState.PLAYING

    def restart_level(self):
        self.current_game_instance = self.current_game_info["game_class"](
            self.screen, self.game_state.current_level
        )
        self.popup = None
        self.game_state.current_state = GameState.PLAYING

    def back_to_menu(self):
        self.popup = None
        self.current_game_instance = None
        self.current_game_info = None
        self.game_state.current_game = None
        self.game_state.current_level = None
        self.game_state.current_state = GameState.MENU
        self.setup_main_menu()


if __name__ == "__main__":
    game = GameCollection()
    game.run()