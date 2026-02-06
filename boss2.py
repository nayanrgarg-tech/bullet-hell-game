import random
from time import time
from enemy import load_image_with_white_bg
import pygame
from PIL import ImageFont
from PIL import Image
import math
from bullet import Bullet

pil_font_large = ImageFont.truetype("Melon Pop.ttf", 48)  
pil_font_medium = ImageFont.truetype("Melon Pop.ttf", 36) 
pil_font_small = ImageFont.truetype("Melon Pop.ttf", 28)  
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
elapsed_time = pygame.time.get_ticks()

class Boss2:
    def __init__(self, x, y, max_health, sprite, phase, player, bullets):
        self.x = x
        self.y = y
        self.health = max_health
        self.max_health = max_health
        self.phase = phase
        self.image = load_image_with_white_bg(sprite, (200, 200))
        self.isDefeated = False
        self.attacking = False
        self.player = player
        self.bullets = bullets

    #attacks
    def waves(self, bullets):
        self.attacking = True
        #persistent variables
        if not hasattr(self, 'last_shot_time'):
            self.last_shot_time = pygame.time.get_ticks()
        if not hasattr(self, 'wave_count'):
            self.wave_count = 0
        if not hasattr(self, 'shot_count'):
            self.shot_count = 0

        if self.move_toward(WINDOW_WIDTH / 2, 800 - self.wave_count * 80, 15):
            now = pygame.time.get_ticks()
            if now - self.last_shot_time > 200:  # Shoot every 500 ms
                self.shoot(0, 800 - self.wave_count * 80, 8, bullets, 5, 0.01)
                self.shoot(WINDOW_WIDTH, 800 - self.wave_count * 80, 8, bullets, 5, 0.01)
                self.shot_count += 1
                self.last_shot_time = now

            if self.shot_count >= 5:  # After shooting 5 times, move to next wave position
                self.wave_count += 1
                self.shot_count = 0

            if self.wave_count >= 10:  # Reset after 10 waves
                del self.last_shot_time
                del self.wave_count
                del self.shot_count
                del self.attack
                self.attacking = False

    def corner_sweep(self, bullets):
        self.attacking = True
        #persistent variables
        if not hasattr(self, 'random_corner'):
            self.random_corner = random.randint(1, 4)
        if not hasattr(self, 'last_shot_time'):
            self.last_shot_time = pygame.time.get_ticks()
        if not hasattr(self, 'shot_count'):
            self.shot_count = 0

        if self.random_corner == 1:
            if self.move_toward(50, 50, 7):
                now = pygame.time.get_ticks()
                if now - self.last_shot_time > 100 and self.shot_count < 20:  # Shoot every 100 ms
                    self.shoot(random.randint(0, WINDOW_WIDTH), WINDOW_HEIGHT, 6, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shot_count += 1
                    self.last_shot_time = now
        elif self.random_corner == 2:
            if self.move_toward(WINDOW_WIDTH - 50, 50, 7):
                now = pygame.time.get_ticks()
                if now - self.last_shot_time > 100 and self.shot_count < 20:  # Shoot every 100 ms
                    self.shoot(random.randint(0, WINDOW_WIDTH), WINDOW_HEIGHT, 6, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shot_count += 1
                    self.last_shot_time = now
        elif self.random_corner == 3:
            if self.move_toward(WINDOW_WIDTH - 50, WINDOW_HEIGHT - 50, 7):
                now = pygame.time.get_ticks()
                if now - self.last_shot_time > 100 and self.shot_count < 20:  # Shoot every 100 ms
                    self.shoot(random.randint(0, WINDOW_WIDTH), 0, 6, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shot_count += 1
                    self.last_shot_time = now
        elif self.random_corner == 4:
            if self.move_toward(50, WINDOW_HEIGHT - 50, 7):
                now = pygame.time.get_ticks()
                if now - self.last_shot_time > 100 and self.shot_count < 20: # Shoot every 100 ms
                    self.shoot(random.randint(0, WINDOW_WIDTH), 0, 6, bullets, random.randint(5,15), random.random() * 0.01)
                    self.shot_count += 1
                    self.last_shot_time = now
        
        if self.shot_count >= 20:
            del self.last_shot_time
            del self.shot_count
            del self.random_corner
            del self.attack
            self.attacking = False

    def snipe_shot(self, bullets):
        self.attacking = True
        #persistent variables
        if not hasattr(self, 'last_shot_time'):
            self.last_shot_time = pygame.time.get_ticks()
        if not hasattr(self, 'shot_count'):
            self.shot_count = 0
        if not hasattr(self, 'random_edge'):
            rand = random.randint(1, 4)
            if rand == 1:
                self.random_edge = (random.randint(0, WINDOW_WIDTH), 0)  # Top edge
            elif rand == 2:
                self.random_edge = (WINDOW_WIDTH, random.randint(0, WINDOW_HEIGHT))  # Right edge
            elif rand == 3:
                self.random_edge = (random.randint(0, WINDOW_WIDTH), WINDOW_HEIGHT)  # Bottom edge
            elif rand == 4:
                self.random_edge = (0, random.randint(0, WINDOW_HEIGHT))  # Left edge

        if self.move_toward(self.random_edge[0], self.random_edge[1], 8):
            now = pygame.time.get_ticks()
            if now - self.last_shot_time > 200:  # Shoot every 150 ms
                self.shoot(self.player.x, self.player.y, 8, bullets, random.randint(10, 20), 0.008)
                self.shot_count += 1
                self.last_shot_time = now

            if self.shot_count >= 15:  # After shooting 15 times, end attack
                del self.last_shot_time
                del self.shot_count
                del self.random_edge
                del self.attack
                self.attacking = False

    def fanshots(self, bullets):
        self.attacking = True

        #persistent variables
        if not hasattr(self, 'last_shot_time'):
            self.last_shot_time = pygame.time.get_ticks()
        if not hasattr(self, 'shot_count'):
            self.shot_count = 0

        if self.move_toward(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50, 3):
            now = pygame.time.get_ticks()
            if now - self.last_shot_time > 500:  # Shoot every 500 ms
                for i in range(3):
                    self.shoot(0, 0, 8, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shoot(140, 0, 8, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shoot(280, 0, 8, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shoot(420, 0, 8, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shoot(560, 0, 8, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shoot(700, 0, 8, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shoot(840, 0, 8, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shoot(980, 0, 8, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shoot(1120, 0, 8, bullets, random.randint( 5, 15), random.random() * 0.01)
                    self.shoot(1260, 0, 8, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shoot(1400, 0, 8, bullets, random.randint(5, 15), random.random() * 0.01)
                self.shot_count += 1
                self.last_shot_time = now

            if self.shot_count >= 5:
                del self.last_shot_time
                del self.shot_count
                del self.attack
                self.attacking = False


    def four_courners(self, bullets):
        self.attacking = True

        #persistent variables
        if not hasattr(self, 'random_corner'):
            self.random_corner = random.randint(1, 4)
        if not hasattr(self, 'last_shot_time'):
            self.last_shot_time = pygame.time.get_ticks()
        if not hasattr(self, 'shot_count'):
            self.shot_count = 0
        if not hasattr(self, 'total_corners'):
            self.total_corners = 0

        if self.random_corner == 1:
            if self.move_toward(50, 50, 25):
                now = pygame.time.get_ticks()
                if now - self.last_shot_time > 100 and self.shot_count < 10:  # Shoot every 100 ms
                    self.shoot(WINDOW_WIDTH, WINDOW_HEIGHT, 6, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shoot(WINDOW_WIDTH, 0, 6, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shot_count += 1
                    self.last_shot_time = now
        elif self.random_corner == 2:
            if self.move_toward(WINDOW_WIDTH - 50, 50, 25):
                now = pygame.time.get_ticks()
                if now - self.last_shot_time > 100 and self.shot_count < 10:  # Shoot every 100 ms
                    self.shoot(0, WINDOW_HEIGHT, 6, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shoot(0, 0, 6, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shot_count += 1
                    self.last_shot_time = now
        elif self.random_corner == 3:
            if self.move_toward(WINDOW_WIDTH - 50, WINDOW_HEIGHT - 50, 25):
                now = pygame.time.get_ticks()
                if now - self.last_shot_time > 100 and self.shot_count < 10:  # Shoot every 100 ms
                    self.shoot(0, 0, 6, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shoot(0, WINDOW_HEIGHT, 6, bullets, random.randint(5, 15), random.random() * 0.01)
                    self.shot_count += 1
                    self.last_shot_time = now
        elif self.random_corner == 4:
            if self.move_toward(50, WINDOW_HEIGHT - 50, 25):
                now = pygame.time.get_ticks()
                if now - self.last_shot_time > 100 and self.shot_count < 10: # Shoot every 100 ms
                    self.shoot(WINDOW_WIDTH, 0, 6, bullets, random.randint(5,15), random.random() * 0.01)
                    self.shoot(WINDOW_WIDTH, WINDOW_HEIGHT, 6, bullets, random.randint(5,15), random.random() * 0.01)
                    self.shot_count += 1
                    self.last_shot_time = now
        
        if self.shot_count >= 10:
            self.total_corners += 1
            self.shot_count = 0
            self.random_corner = random.randint(1, 4)

            if self.total_corners >= 4:
                del self.last_shot_time
                del self.shot_count
                del self.random_corner
                del self.total_corners
                del self.attack
                self.attacking = False

    def no_busses(self, bullets):
        self.attacking = True

        #persistent variables
        if not hasattr(self, 'shot_count'):
            self.shot_count = 0
        if not hasattr(self, 'random_position_y'):
            self.random_position_y = random.randint(100, WINDOW_HEIGHT - 100)

        if self.move_toward(0, self.random_position_y, 12):
            self.shoot(WINDOW_WIDTH, self.random_position_y, 10, bullets, random.randint(5, 10), random.random() * 0.008)
            self.shoot(WINDOW_WIDTH, self.random_position_y, 10, bullets, random.randint(5, 10), random.random() * 0.007)
            self.shoot(WINDOW_WIDTH, self.random_position_y, 10, bullets, random.randint(5, 10), random.random() * 0.006)
            self.shot_count += 1
            self.random_position_y = random.randint(100, WINDOW_HEIGHT - 100)

            if self.shot_count >= 8:
                del self.shot_count
                del self.random_position_y
                del self.attack
                self.attacking = False

    def gridlocked(self, bullets):
        self.attacking = True

        #persistent variables
        if not hasattr(self, 'last_shot_time'):
            self.last_shot_time = pygame.time.get_ticks()
        if not hasattr(self, 'shot_count'):
            self.shot_count = 0
        if not hasattr(self, 'grid_index'):
            self.grid_index = 0

        if self.grid_index % 2 == 0:
            if self.move_toward(self.grid_index * (WINDOW_WIDTH / 10), 0, 50):
                now = pygame.time.get_ticks()
                if now - self.last_shot_time > 50:  # Shoot every 100 ms
                    self.shot_count += 1
                    self.shoot(self.grid_index * (WINDOW_WIDTH / 10), WINDOW_HEIGHT, 10, bullets, random.randint(5, 15), random.random() * 0.003)
                    self.last_shot_time = now

        else:
            if self.move_toward(0, self.grid_index * (WINDOW_HEIGHT / 10), 50):
                now = pygame.time.get_ticks()
                if now - self.last_shot_time > 100:  # Shoot every 100 ms
                    self.shot_count += 1
                    self.shoot(WINDOW_WIDTH, self.grid_index * (WINDOW_HEIGHT / 10), 10, bullets, random.randint(5, 15), random.random() * 0.003)
                    self.last_shot_time = now
            
        if self.shot_count >= 10:
            self.grid_index += 1
            self.shot_count = 0

        if self.grid_index >= 10:
            del self.last_shot_time
            del self.shot_count
            del self.grid_index
            del self.attack
            self.attacking = False

    def sweeping_spiral(self, bullets):
        self.attacking = True

        # persistent variables
        if not hasattr(self, 'spiral_angle'):
            self.spiral_angle = 0
        if not hasattr(self, 'spiral_radius'):
            self.spiral_radius = 40
        if not hasattr(self, 'spiral_center'):
            self.spiral_center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        cx, cy = self.spiral_center

        # compute next spiral target
        target_x = cx + math.cos(self.spiral_angle) * self.spiral_radius
        target_y = cy + math.sin(self.spiral_angle) * self.spiral_radius

        # move toward the spiral point
        if self.move_toward(target_x, target_y, 10):

            # fire ONE volley in 4 directions
            self.shoot(self.x, 0, 6, bullets, 5, random.random() * 0.01)                 # Up
            self.shoot(self.x, WINDOW_HEIGHT, 6, bullets, 5, random.random() * 0.01)     # Down
            self.shoot(0, self.y, 6, bullets, 5, random.random() * 0.01)                 # Left
            self.shoot(WINDOW_WIDTH, self.y, 6, bullets, 5, random.random() * 0.01)      # Right

            # advance spiral
            self.spiral_angle += 0.4
            self.spiral_radius += 8

        # end attack when spiral reaches edge
        if self.spiral_radius > 450:
            del self.spiral_angle
            del self.spiral_radius
            del self.spiral_center
            del self.attack
            self.attacking = False

    def crushing_walls(self, bullets):
        self.attacking = True

        # persistent variables
        if not hasattr(self, 'wall_position'):
            self.wall_position = 0
        if not hasattr(self, 'direction'):
            self.direction = random.randint(1, 2) # 1 for left-right, 2 for right-left
        if not hasattr(self, 'total_cycle'):
            self.total_cycle = 0

        if self.direction == 1:
            if self.move_toward(50, self.wall_position * 80, 15):
                self.shoot(1400, self.wall_position * 80, 8, bullets, random.randint(5, 20), random.random() * 0.005)
                self.shoot(1400, self.wall_position * 80, 8, bullets, random.randint(5, 20), random.random() * 0.005)
                self.shoot(1400, self.wall_position * 80, 8, bullets, random.randint(5, 20), random.random() * 0.005)
                self.wall_position += 1
            if self.wall_position >= 10:
                self.direction = 2
                self.total_cycle += 1
                self.wall_position = 0
        elif self.direction == 2:
            if self.move_toward(1350, self.wall_position * 80, 15):
                self.shoot(0, self.wall_position * 80, 8, bullets, random.randint(5, 20), random.random() * 0.005)
                self.shoot(0, self.wall_position * 80, 8, bullets, random.randint(5, 20), random.random() * 0.005)
                self.shoot(0, self.wall_position * 80, 8, bullets, random.randint(5, 20), random.random() * 0.005)
                self.wall_position += 1
            if self.wall_position >= 10:
                self.direction = 1
                self.total_cycle += 1
                self.wall_position = 0
        if self.total_cycle >= 2:
            del self.wall_position
            del self.direction
            del self.total_cycle
            del self.attack
            self.attacking = False

    def take_damage(self, damage):
        self.health -= damage
        if self.health / self.max_health <= 0.5:
            self.phase = 2
        
        if self.health / self.max_health <= 0.25:
            self.phase = 3

    def choose_attack(self, bullets):
            
        if not hasattr(self, 'attack') and not self.attacking:
            self.attack = random.randint(1,3)
        
        if self.phase == 1:
            if self.attack == 1:
                self.waves(bullets)
            elif self.attack == 2:
                self.corner_sweep(bullets)
            elif self.attack == 3:
                self.snipe_shot(bullets)
        elif self.phase == 2:
            if self.attack == 1:
                self.fanshots(bullets)
            elif self.attack == 2:
                self.four_courners(bullets)
            elif self.attack == 3:
                self.no_busses(bullets)
        elif self.phase == 3:
            if self.attack == 1:
                self.gridlocked(bullets)
            elif self.attack == 2:
                self.sweeping_spiral(bullets)
            elif self.attack == 3:
                self.crushing_walls(bullets)
        

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

        # Move proportionally
        self.x += (dx / distance) * speed
        self.y += (dy / distance) * speed
        return False

    def shoot(self, target_x, target_y, speed, bullets, amplitude, frequency):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            bullet = Bullet(self.x, self.y, (dx / distance) * speed, (dy / distance) * speed, WINDOW_WIDTH, WINDOW_HEIGHT, bullet_type="enemy", sprite="Images/bulletcurve.png", amplitude=amplitude, frequency=frequency)
            bullets.append(bullet)

        return None
    
    def defeat(self):
        # Game over text
        if self.isDefeated:
            return

    def get_rect(self):
        return self.image.get_rect(center=(self.x, self.y))

