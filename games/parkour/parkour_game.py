import pygame
import random
import time
import os

FONT_PATH = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'simhei.ttf')

LEVEL_CONFIGS = {
    1: {"speed": 3, "obstacle_count": 3, "jump_force": -13, "gravity": 0.55, "win_distance": 1500},
    2: {"speed": 4, "obstacle_count": 4, "jump_force": -13, "gravity": 0.6, "win_distance": 2500},
    3: {"speed": 5, "obstacle_count": 5, "jump_force": -14, "gravity": 0.65, "win_distance": 3500},
}


class ParkourGame:
    def __init__(self, screen, level=1):
        self.screen = screen
        self.level = level
        self.config = LEVEL_CONFIGS[level]
        self.speed = self.config["speed"]
        self.obstacle_count = self.config["obstacle_count"]
        self.jump_force = self.config["jump_force"]
        self.gravity = self.config["gravity"]
        self.win_distance = self.config["win_distance"]

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        self.ground_y = self.screen_height - 80

        self.reset()

    def reset(self):
        self.player_x = 100
        self.player_y = self.ground_y
        self.player_velocity_y = 0
        self.is_jumping = False

        self.obstacles = []
        self.spawn_obstacles()

        self.distance = 0
        self.game_over = False
        self.won = False
        self.last_obstacle_spawn = time.time()

    def spawn_obstacles(self):
        self.obstacles = []
        for i in range(self.obstacle_count):
            # 增大障碍物间距，给玩家更多反应时间
            x = self.screen_width + i * 550 + random.randint(150, 350)
            type = random.choice(["crate", "spike"])
            if type == "crate":
                # 降低 crate 高度：50 → 35，避免玩家跳不过去
                w, h = 45, 35
                y = self.ground_y - h
            else:
                # 降低 spike 高度：30 → 25
                w, h = 40, 25
                y = self.ground_y - h
            self.obstacles.append({"x": x, "y": y, "w": w, "h": h, "type": type})

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.is_jumping:
                self.player_velocity_y = self.jump_force
                self.is_jumping = True

    def update(self):
        if self.game_over or self.won:
            return

        self.player_velocity_y += self.gravity
        self.player_y += self.player_velocity_y

        if self.player_y >= self.ground_y:
            self.player_y = self.ground_y
            self.player_velocity_y = 0
            self.is_jumping = False

        for obstacle in self.obstacles:
            obstacle["x"] -= self.speed

        self.distance += self.speed

        if self.distance >= self.win_distance:
            self.won = True
            return

        now = time.time()
        # 增大生成间隔：2.0 → 2.8 秒，让玩家有充足时间反应
        if now - self.last_obstacle_spawn > 2.8:
            self.spawn_new_obstacle()
            self.last_obstacle_spawn = now

        player_rect = pygame.Rect(self.player_x, self.player_y, 40, 60)
        for obstacle in self.obstacles:
            obs_rect = pygame.Rect(obstacle["x"], obstacle["y"], obstacle["w"], obstacle["h"])
            if player_rect.colliderect(obs_rect):
                self.game_over = True
                return

        self.obstacles = [o for o in self.obstacles if o["x"] > -100]

    def spawn_new_obstacle(self):
        x = self.screen_width + 100
        type = random.choice(["crate", "spike"])
        if type == "crate":
            w, h = 45, 35
            y = self.ground_y - h
        else:
            w, h = 40, 25
            y = self.ground_y - h
        self.obstacles.append({"x": x, "y": y, "w": w, "h": h, "type": type})

    def draw(self):
        self.screen.fill((255, 255, 255))

        ground_grad = pygame.Surface((self.screen_width, 80))
        for i in range(80):
            ground_grad.fill((220 - i // 2, 220 - i // 2, 220 - i // 2), rect=(0, i, self.screen_width, 1))
        self.screen.blit(ground_grad, (0, self.ground_y))

        pygame.draw.rect(self.screen, (50, 100, 200),
                         (self.player_x, self.player_y, 40, 60), border_radius=5)

        for obstacle in self.obstacles:
            if obstacle["type"] == "crate":
                pygame.draw.rect(self.screen, (180, 130, 80),
                                 (obstacle["x"], obstacle["y"], obstacle["w"], obstacle["h"]), border_radius=3)
            else:
                points = [
                    (obstacle["x"] + obstacle["w"] // 2, obstacle["y"]),
                    (obstacle["x"] + obstacle["w"], obstacle["y"] + obstacle["h"]),
                    (obstacle["x"], obstacle["y"] + obstacle["h"])
                ]
                pygame.draw.polygon(self.screen, (255, 80, 80), points)

        font = pygame.font.Font(FONT_PATH, 28)
        distance_text = font.render(f"距离: {int(self.distance)}/{self.win_distance}", True, (30, 30, 30))
        level_text = font.render(f"关卡: {self.level}", True, (30, 30, 30))
        self.screen.blit(distance_text, (10, 10))
        self.screen.blit(level_text, (10, 40))

        controls_text = font.render("空格键跳跃", True, (150, 150, 150))
        self.screen.blit(controls_text, (self.screen_width - 150, 10))

    def is_game_over(self):
        return self.game_over

    def is_won(self):
        return self.won