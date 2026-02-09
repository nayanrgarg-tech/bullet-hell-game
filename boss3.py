import random
import math
import pygame
from PIL import ImageFont
from enemy import load_image_with_white_bg, Enemy
from bullet import Bullet

pil_font_large = ImageFont.truetype("Melon Pop.ttf", 48)
pil_font_medium = ImageFont.truetype("Melon Pop.ttf", 36)
pil_font_small = ImageFont.truetype("Melon Pop.ttf", 28)

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

enemy_kamikaze = 3
enemy_builder = 4


class Boss3:
    def __init__(self, x, y, max_health, sprite, phase, player, bullets, enemies=None):
        self.x = x
        self.y = y
        self.health = max_health
        self.max_health = max_health
        self.phase = phase
        self.image = load_image_with_white_bg(sprite, (220, 220))
        self.isDefeated = False
        self.attacking = False
        self.player = player
        self.bullets = bullets
        self.enemies = enemies if enemies is not None else []

    def take_damage(self, damage):
        self.health -= damage
        if self.health / self.max_health <= 0.5:
            self.phase = 2
        if self.health / self.max_health <= 0.25:
            self.phase = 3

    def _count_enemy_type(self, enemy_type):
        return sum(1 for enemy in self.enemies if getattr(enemy, "type", None) == enemy_type)

    def _spawn_enemy(self, enemy_type, x, y):
        if self.enemies is None:
            return
        self.enemies.append(Enemy(x, y, enemy_type, WINDOW_WIDTH, WINDOW_HEIGHT))

    def _spawn_kamikaze_wave(self, count):
        if self._count_enemy_type(enemy_kamikaze) >= 20:
            return
        for _ in range(count):
            edge = random.randint(1, 4)
            if edge == 1:
                spawn_x = random.randint(0, WINDOW_WIDTH)
                spawn_y = -30
            elif edge == 2:
                spawn_x = WINDOW_WIDTH + 30
                spawn_y = random.randint(0, WINDOW_HEIGHT)
            elif edge == 3:
                spawn_x = random.randint(0, WINDOW_WIDTH)
                spawn_y = WINDOW_HEIGHT + 30
            else:
                spawn_x = -30
                spawn_y = random.randint(0, WINDOW_HEIGHT)
            self._spawn_enemy(enemy_kamikaze, spawn_x, spawn_y)

    def _spawn_builder(self, x, y):
        if self._count_enemy_type(enemy_builder) >= 6:
            return
        self._spawn_enemy(enemy_builder, x, y)

    # Phase 1 attacks
    def kamikaze_waves(self, bullets):
        self.attacking = True
        if not hasattr(self, "last_spawn_time"):
            self.last_spawn_time = pygame.time.get_ticks()
        if not hasattr(self, "wave_count"):
            self.wave_count = 0

        if self.move_toward(WINDOW_WIDTH / 2, 80, 8):
            now = pygame.time.get_ticks()
            if now - self.last_spawn_time > 350 and self.wave_count < 8:
                self._spawn_kamikaze_wave(2)
                self.wave_count += 1
                self.last_spawn_time = now

        if self.wave_count >= 8:
            del self.last_spawn_time
            del self.wave_count
            del self.attack
            self.attacking = False

    def builder_drop(self, bullets):
        self.attacking = True
        if not hasattr(self, "drop_count"):
            self.drop_count = 0
        if not hasattr(self, "drop_target"):
            self.drop_target = (
                random.randint(150, WINDOW_WIDTH - 150),
                random.randint(150, WINDOW_HEIGHT - 150),
            )

        if self.move_toward(self.drop_target[0], self.drop_target[1], 7):
            if self.drop_count < 4:
                self._spawn_builder(self.x - 20, self.y - 20)
                self.drop_count += 1
                self.drop_target = (
                    random.randint(150, WINDOW_WIDTH - 150),
                    random.randint(150, WINDOW_HEIGHT - 150),
                )

        if self.drop_count >= 4:
            del self.drop_count
            del self.drop_target
            del self.attack
            self.attacking = False

    def kamikaze_pincer(self, bullets):
        self.attacking = True
        if not hasattr(self, "pincer_count"):
            self.pincer_count = 0
        if not hasattr(self, "last_spawn_time"):
            self.last_spawn_time = pygame.time.get_ticks()

        if self.move_toward(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, 6):
            now = pygame.time.get_ticks()
            if now - self.last_spawn_time > 300 and self.pincer_count < 6:
                self._spawn_kamikaze_wave(4)
                self.pincer_count += 1
                self.last_spawn_time = now

        if self.pincer_count >= 6:
            del self.pincer_count
            del self.last_spawn_time
            del self.attack
            self.attacking = False

    # Phase 2 attacks
    def turret_ring(self, bullets):
        self.attacking = True
        if not hasattr(self, "ring_index"):
            self.ring_index = 0
        if not hasattr(self, "last_spawn_time"):
            self.last_spawn_time = pygame.time.get_ticks()

        if self.move_toward(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, 5):
            now = pygame.time.get_ticks()
            if now - self.last_spawn_time > 400 and self.ring_index < 6:
                ring_positions = [
                    (100, 100),
                    (WINDOW_WIDTH - 100, 100),
                    (100, WINDOW_HEIGHT - 100),
                    (WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100),
                    (WINDOW_WIDTH / 2, 120),
                    (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 120),
                ]
                x, y = ring_positions[self.ring_index]
                self._spawn_builder(x, y)
                self.ring_index += 1
                self.last_spawn_time = now

        if self.ring_index >= 6:
            del self.ring_index
            del self.last_spawn_time
            del self.attack
            self.attacking = False

    def swarm_and_build(self, bullets):
        self.attacking = True
        if not hasattr(self, "swarm_count"):
            self.swarm_count = 0
        if not hasattr(self, "last_spawn_time"):
            self.last_spawn_time = pygame.time.get_ticks()

        if self.move_toward(WINDOW_WIDTH / 2, 100, 6):
            now = pygame.time.get_ticks()
            if now - self.last_spawn_time > 250 and self.swarm_count < 10:
                self._spawn_kamikaze_wave(3)
                if self.swarm_count % 2 == 0:
                    self._spawn_builder(random.randint(100, WINDOW_WIDTH - 100), random.randint(120, WINDOW_HEIGHT - 120))
                self.swarm_count += 1
                self.last_spawn_time = now

        if self.swarm_count >= 10:
            del self.swarm_count
            del self.last_spawn_time
            del self.attack
            self.attacking = False

    def kamikaze_sweep(self, bullets):
        self.attacking = True
        if not hasattr(self, "sweep_index"):
            self.sweep_index = 0
        if not hasattr(self, "last_spawn_time"):
            self.last_spawn_time = pygame.time.get_ticks()

        target_x = 140 + self.sweep_index * 220
        if self.move_toward(target_x, 120, 10):
            now = pygame.time.get_ticks()
            if now - self.last_spawn_time > 200:
                self._spawn_kamikaze_wave(2)
                self.shoot(self.player.x, self.player.y, 7, bullets, 6, 0.008)
                self.sweep_index += 1
                self.last_spawn_time = now

        if self.sweep_index >= 5:
            del self.sweep_index
            del self.last_spawn_time
            del self.attack
            self.attacking = False

    # Phase 3 attacks
    def siege_grid(self, bullets):
        self.attacking = True
        if not hasattr(self, "grid_index"):
            self.grid_index = 0
        if not hasattr(self, "last_spawn_time"):
            self.last_spawn_time = pygame.time.get_ticks()

        grid_positions = [
            (200, 200),
            (WINDOW_WIDTH / 2, 200),
            (WINDOW_WIDTH - 200, 200),
            (200, WINDOW_HEIGHT / 2),
            (WINDOW_WIDTH - 200, WINDOW_HEIGHT / 2),
            (200, WINDOW_HEIGHT - 200),
            (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 200),
            (WINDOW_WIDTH - 200, WINDOW_HEIGHT - 200),
        ]

        if self.move_toward(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, 5):
            now = pygame.time.get_ticks()
            if now - self.last_spawn_time > 300 and self.grid_index < len(grid_positions):
                x, y = grid_positions[self.grid_index]
                self._spawn_builder(x, y)
                self.grid_index += 1
                self.last_spawn_time = now

        if self.grid_index >= len(grid_positions):
            del self.grid_index
            del self.last_spawn_time
            del self.attack
            self.attacking = False

    def kamikaze_storm(self, bullets):
        self.attacking = True
        if not hasattr(self, "storm_count"):
            self.storm_count = 0
        if not hasattr(self, "last_spawn_time"):
            self.last_spawn_time = pygame.time.get_ticks()

        if self.move_toward(WINDOW_WIDTH / 2, 80, 6):
            now = pygame.time.get_ticks()
            if now - self.last_spawn_time > 200 and self.storm_count < 8:
                self._spawn_kamikaze_wave(5)
                self.storm_count += 1
                self.last_spawn_time = now

        if self.storm_count >= 8:
            del self.storm_count
            del self.last_spawn_time
            del self.attack
            self.attacking = False

    def overload(self, bullets):
        self.attacking = True
        if not hasattr(self, "overload_count"):
            self.overload_count = 0
        if not hasattr(self, "last_spawn_time"):
            self.last_spawn_time = pygame.time.get_ticks()

        if self.move_toward(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, 7):
            now = pygame.time.get_ticks()
            if now - self.last_spawn_time > 250 and self.overload_count < 10:
                self._spawn_kamikaze_wave(4)
                if self.overload_count % 3 == 0:
                    self._spawn_builder(random.randint(120, WINDOW_WIDTH - 120), random.randint(120, WINDOW_HEIGHT - 120))
                self.shoot(self.player.x, self.player.y, 8, bullets, 8, 0.01)
                self.overload_count += 1
                self.last_spawn_time = now

        if self.overload_count >= 10:
            del self.overload_count
            del self.last_spawn_time
            del self.attack
            self.attacking = False

    def choose_attack(self, bullets):
        if not hasattr(self, "attack") and not self.attacking:
            self.attack = random.randint(1, 3)

        if self.phase == 1:
            if self.attack == 1:
                self.kamikaze_waves(bullets)
            elif self.attack == 2:
                self.builder_drop(bullets)
            elif self.attack == 3:
                self.kamikaze_pincer(bullets)
        elif self.phase == 2:
            if self.attack == 1:
                self.turret_ring(bullets)
            elif self.attack == 2:
                self.swarm_and_build(bullets)
            elif self.attack == 3:
                self.kamikaze_sweep(bullets)
        elif self.phase == 3:
            if self.attack == 1:
                self.siege_grid(bullets)
            elif self.attack == 2:
                self.kamikaze_storm(bullets)
            elif self.attack == 3:
                self.overload(bullets)

    def draw(self, screen):
        rect = self.image.get_rect(center=(self.x, self.y))
        screen.blit(self.image, rect)

    def move_toward(self, target_x, target_y, speed):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance <= speed or distance == 0:
            self.x = target_x
            self.y = target_y
            return True

        self.x += (dx / distance) * speed
        self.y += (dy / distance) * speed
        return False

    def shoot(self, target_x, target_y, speed, bullets, amplitude, frequency):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            bullet = Bullet(
                self.x,
                self.y,
                (dx / distance) * speed,
                (dy / distance) * speed,
                WINDOW_WIDTH,
                WINDOW_HEIGHT,
                bullet_type="enemy",
                sprite="Images/bulletcurve.png",
                amplitude=amplitude,
                frequency=frequency,
            )
            bullets.append(bullet)

        return None

    def defeat(self):
        if self.isDefeated:
            return

    def get_rect(self):
        return self.image.get_rect(center=(self.x, self.y))
