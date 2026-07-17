import pygame
import random
import time
import os

FONT_PATH = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'simhei.ttf')

LEVEL_CONFIGS = {
    1: {"enemy_speed": 3, "enemy_spawn_rate": 0.8, "player_bullet_speed": 10,
        "enemy_bullet_speed": 5, "win_score": 50, "max_enemies": 8},
}


class PlanewarGame:
    def __init__(self, screen, level=1):
        self.screen = screen
        self.level = level
        self.config = LEVEL_CONFIGS[level]
        self.enemy_speed = self.config["enemy_speed"]
        self.enemy_spawn_rate = self.config["enemy_spawn_rate"]
        self.player_bullet_speed = self.config["player_bullet_speed"]
        self.enemy_bullet_speed = self.config["enemy_bullet_speed"]
        self.win_score = self.config["win_score"]
        self.max_enemies = self.config["max_enemies"]

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        self.reset()

    def reset(self):
        self.player_x = self.screen_width // 2 - 25
        self.player_y = self.screen_height - 80
        self.player_speed = 8

        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []

        self.score = 0
        self.game_over = False
        self.won = False
        self.last_enemy_spawn = time.time()
        self.last_enemy_shoot = time.time()

    def handle_event(self, event):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player_x -= self.player_speed
        if keys[pygame.K_RIGHT]:
            self.player_x += self.player_speed
        if keys[pygame.K_UP]:
            self.player_y -= self.player_speed
        if keys[pygame.K_DOWN]:
            self.player_y += self.player_speed

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.shoot()

    def shoot(self):
        bullet_x = self.player_x + 25 - 3
        bullet_y = self.player_y
        self.bullets.append({"x": bullet_x, "y": bullet_y, "w": 6, "h": 15})

    def update(self):
        if self.game_over or self.won:
            return

        self.player_x = max(0, min(self.screen_width - 50, self.player_x))
        self.player_y = max(0, min(self.screen_height - 60, self.player_y))

        for bullet in self.bullets:
            bullet["y"] -= self.player_bullet_speed

        for enemy in self.enemies:
            enemy["y"] += self.enemy_speed

        for eb in self.enemy_bullets:
            eb["y"] += self.enemy_bullet_speed

        now = time.time()
        if now - self.last_enemy_spawn > self.enemy_spawn_rate and len(self.enemies) < self.max_enemies:
            self.spawn_enemy()
            self.last_enemy_spawn = now

        if now - self.last_enemy_shoot > 1.5:
            self.enemy_shoot()
            self.last_enemy_shoot = now

        player_rect = pygame.Rect(self.player_x, self.player_y, 50, 50)

        for eb in self.enemy_bullets:
            eb_rect = pygame.Rect(eb["x"], eb["y"], eb["w"], eb["h"])
            if player_rect.colliderect(eb_rect):
                self.game_over = True
                return

        for enemy in self.enemies:
            enemy_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["w"], enemy["h"])
            if player_rect.colliderect(enemy_rect):
                self.game_over = True
                return

        for bullet in self.bullets[:]:
            bullet_rect = pygame.Rect(bullet["x"], bullet["y"], bullet["w"], bullet["h"])
            for enemy in self.enemies[:]:
                enemy_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["w"], enemy["h"])
                if bullet_rect.colliderect(enemy_rect):
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 1
                    break

        self.bullets = [b for b in self.bullets if b["y"] > -20]
        self.enemies = [e for e in self.enemies if e["y"] < self.screen_height + 50]
        self.enemy_bullets = [eb for eb in self.enemy_bullets if eb["y"] < self.screen_height + 20]

        if self.score >= self.win_score:
            self.won = True

    def spawn_enemy(self):
        x = random.randint(20, self.screen_width - 40)
        self.enemies.append({"x": x, "y": -40, "w": 35, "h": 35})

    def enemy_shoot(self):
        if self.enemies:
            shooter = random.choice(self.enemies)
            self.enemy_bullets.append({
                "x": shooter["x"] + shooter["w"] // 2 - 4,
                "y": shooter["y"] + shooter["h"],
                "w": 8,
                "h": 12
            })

    def draw(self):
        self.screen.fill((245, 245, 255))

        for i in range(0, self.screen_height, 40):
            for j in range(0, self.screen_width, 40):
                pygame.draw.circle(self.screen, (200, 200, 230), (j + random.randint(0, 30), i), 2)

        pygame.draw.polygon(self.screen, (50, 150, 200), [
            (self.player_x + 25, self.player_y),
            (self.player_x + 50, self.player_y + 50),
            (self.player_x + 25, self.player_y + 40),
            (self.player_x, self.player_y + 50)
        ])

        for bullet in self.bullets:
            pygame.draw.rect(self.screen, (255, 150, 50),
                             (bullet["x"], bullet["y"], bullet["w"], bullet["h"]), border_radius=2)

        for enemy in self.enemies:
            pygame.draw.polygon(self.screen, (255, 80, 80), [
                (enemy["x"] + enemy["w"] // 2, enemy["y"] + enemy["h"]),
                (enemy["x"] + enemy["w"], enemy["y"]),
                (enemy["x"] + enemy["w"] // 2, enemy["y"] + 15),
                (enemy["x"], enemy["y"])
            ])

        for eb in self.enemy_bullets:
            pygame.draw.rect(self.screen, (200, 80, 120),
                             (eb["x"], eb["y"], eb["w"], eb["h"]), border_radius=2)

        font = pygame.font.Font(FONT_PATH, 28)
        score_text = font.render(f"击杀: {self.score}/{self.win_score}", True, (30, 30, 30))
        level_text = font.render(f"关卡: {self.level}", True, (30, 30, 30))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 40))

        controls_text = font.render("方向键移动 | 空格射击", True, (150, 150, 150))
        self.screen.blit(controls_text, (self.screen_width - 280, 10))

    def is_game_over(self):
        return self.game_over

    def is_won(self):
        return self.won