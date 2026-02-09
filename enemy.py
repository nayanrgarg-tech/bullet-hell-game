from ast import Import
import pygame
import math
from PIL import Image
from bullet import Bullet
import random
import player
from peon import Peon

import level 

WHITE = (255, 255, 255)
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800

def load_image_with_white_bg(filename, size):
    """Load image with transparency preserved for pygame"""
    try:
        # Open image and force RGBA (keep alpha)
        pil_image = Image.open(filename).convert("RGBA")

        # Resize while keeping alpha
        pil_image = pil_image.resize(size, Image.Resampling.NEAREST)

        # Convert to string with alpha
        pil_data = pil_image.tobytes()

        # Create pygame surface with alpha
        return pygame.image.fromstring(pil_data, pil_image.size, "RGBA").convert_alpha()
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None


class Enemy:
    def __init__(self, x, y, type, window_width=1200, window_height=800):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.health = 1
        self.shoot_timer = 0
        self.window_width = window_width
        self.window_height = window_height
        self.type = type
        self.peons = []  # List of peons spawned by this builder
        # Load enemy image with no background
        if self.type == 1:
            self.image = load_image_with_white_bg("Images/enemybasic.png", (self.width, self.height))
        elif self.type == 2:
            self.image = load_image_with_white_bg("Images/enemycurve.png", (self.width, self.height))
        elif self.type == 3:
            self.image = load_image_with_white_bg("Images/kamikaze.png", (self.width, self.height))
        elif self.type == 4:
            self.image = load_image_with_white_bg("Images/builder.png", (self.width, self.height))

    def update(self, player_x, player_y):
        # Simple AI: move towards player
        if self.type in [1, 2]:  # Basic and curve enemies move towards player
            dx = player_x - self.x
            dy = player_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                self.x += (dx / distance) * 2
                self.y += (dy / distance) * 2
            self.shoot_timer += 1
        elif self.type == 3:  # Kamikaze moves faster towards player
            if not hasattr(self, 'time_since_spawn'):
                self.time_since_spawn = 0
            self.time_since_spawn += 1
            if self.time_since_spawn < 60:  # Move slower for first 1 sec
                speed = 1
            else:
                speed = self.time_since_spawn / 30  # Gradually increase speed
            dx = player_x - self.x
            dy = player_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                self.x += (dx / distance) * speed
                self.y += (dy / distance) * speed
        elif self.type == 4:  # Builder moves randomly and spawns turrets
            if not hasattr(self, 'random_position'):
                self.random_position = (random.randint(0, self.window_width), random.randint(0, self.window_height))
            if not hasattr(self, 'turret_spawn_timer'):
                self.turret_spawn_timer = 0
            
            dx = self.random_position[0] - self.x
            dy = self.random_position[1] - self.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                self.x += (dx / distance) * 4
                self.y += (dy / distance) * 4
            
            # Spawn a turret periodically
            self.turret_spawn_timer += 1
            if self.turret_spawn_timer >= 120:  # Spawn turret every 2 seconds
                peon = Peon(self.x - 20, self.y - 20, 1, 2, self.window_width, self.window_height)
                self.peons.append(peon)
                self.turret_spawn_timer = 0
            
            # Pick new position periodically
            if distance < 10 or self.turret_spawn_timer % 120 == 0:
                self.random_position = (random.randint(0, self.window_width), random.randint(0, self.window_height))


    def shoot(self, player_x, player_y):
        """Returns a bullet if enemy should shoot, otherwise None"""
        if self.shoot_timer > 100 - level.Level.get_level() / 5:  # Shoot more frequently at higher levels
            dx = player_x - self.x
            dy = player_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                if self.type == 1:
                    bullet = Bullet(self.x + 15, self.y + 15, (dx / distance) * 4, (dy / distance) * 4, self.window_width, self.window_height, bullet_type="enemy", bullet_size=10, sprite="Images/bullets.png")
                    self.shoot_timer = 0
                    return bullet
                elif self.type == 2:
                    bullet = Bullet(self.x + 15, self.y + 15, (dx / distance) * 5, (dy / distance) * 5, self.window_width, self.window_height, bullet_type="enemy", bullet_size=10, sprite="Images/bulletcurve.png")
                    self.shoot_timer = 0
                    return bullet                    
        return None

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
