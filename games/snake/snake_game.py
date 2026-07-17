import pygame
import random
import time
import os

FONT_PATH = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'simhei.ttf')

LEVEL_CONFIGS = {
    1: {"grid_size": 20, "speed": 150, "win_score": 3, "border_padding": 4},
    2: {"grid_size": 20, "speed": 120, "win_score": 3, "border_padding": 6},
    3: {"grid_size": 20, "speed": 90, "win_score": 3, "border_padding": 8},
}


class SnakeGame:
    def __init__(self, screen, level=1):
        self.screen = screen
        self.level = level
        self.config = LEVEL_CONFIGS[level]
        self.grid_size = self.config["grid_size"]
        self.speed = self.config["speed"]
        self.win_score = self.config["win_score"]
        self.border_padding = self.config["border_padding"]

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        self.cols = self.screen_width // self.grid_size
        self.rows = self.screen_height // self.grid_size

        self.inner_cols = self.cols - self.border_padding * 2
        self.inner_rows = self.rows - self.border_padding * 2

        self.reset()

    def reset(self):
        start_x = self.border_padding + self.inner_cols // 2
        start_y = self.border_padding + self.inner_rows // 2
        self.snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = (1, 0)
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self.won = False
        self.last_update = time.time()

    def spawn_food(self):
        while True:
            x = random.randint(self.border_padding, self.border_padding + self.inner_cols - 1)
            y = random.randint(self.border_padding, self.border_padding + self.inner_rows - 1)
            if (x, y) not in self.snake:
                return (x, y)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.direction != (0, 1):
                self.direction = (0, -1)
            elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                self.direction = (0, 1)
            elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                self.direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                self.direction = (1, 0)

    def update(self):
        if self.game_over or self.won:
            return

        now = time.time()
        if now - self.last_update < self.speed / 1000:
            return
        self.last_update = now

        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        min_x = self.border_padding
        min_y = self.border_padding
        max_x = self.border_padding + self.inner_cols - 1
        max_y = self.border_padding + self.inner_rows - 1

        if new_head[0] < min_x or new_head[0] > max_x or \
           new_head[1] < min_y or new_head[1] > max_y:
            self.game_over = True
            return

        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
            if self.score >= self.win_score:
                self.won = True
        else:
            self.snake.pop()

    def draw(self):
        self.screen.fill((255, 255, 255))

        border_rect = pygame.Rect(
            self.border_padding * self.grid_size,
            self.border_padding * self.grid_size,
            self.inner_cols * self.grid_size,
            self.inner_rows * self.grid_size
        )
        pygame.draw.rect(self.screen, (200, 200, 200), border_rect, 2)

        for segment in self.snake:
            rect = pygame.Rect(
                segment[0] * self.grid_size + 1,
                segment[1] * self.grid_size + 1,
                self.grid_size - 2,
                self.grid_size - 2
            )
            pygame.draw.rect(self.screen, (50, 200, 50), rect, border_radius=3)

        food_rect = pygame.Rect(
            self.food[0] * self.grid_size + 2,
            self.food[1] * self.grid_size + 2,
            self.grid_size - 4,
            self.grid_size - 4
        )
        pygame.draw.rect(self.screen, (255, 80, 80), food_rect, border_radius=5)

        font = pygame.font.Font(FONT_PATH, 28)
        score_text = font.render(f"得分: {self.score}/{self.win_score}", True, (30, 30, 30))
        level_text = font.render(f"关卡: {self.level}", True, (30, 30, 30))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 40))

        controls_text = font.render("方向键控制移动", True, (150, 150, 150))
        self.screen.blit(controls_text, (self.screen_width - 200, 10))

    def is_game_over(self):
        return self.game_over

    def is_won(self):
        return self.won