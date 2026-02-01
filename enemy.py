from ast import Import
import pygame
import math
from PIL import Image
from bullet import Bullet
import random
import player

import level 

WHITE = (255, 255, 255)

def load_image_with_white_bg(filename, size):
    """Load image with transparency preserved for pygame"""
    try:
        # Open image and force RGBA (keep alpha)
        pil_image = Image.open(filename).convert("RGBA")

        # Resize while keeping alpha
        pil_image = pil_image.resize(size, Image.Resampling.LANCZOS)

        # Convert to string with alpha
        pil_data = pil_image.tobytes()

        # Create pygame surface with alpha
        return pygame.image.fromstring(pil_data, pil_image.size, "RGBA").convert_alpha()
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None


class Enemy:
    def __init__(self, x, y, window_width=1200, window_height=800):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.health = 1
        self.shoot_timer = 0
        self.window_width = window_width
        self.window_height = window_height
        # Load enemy image with white background
        self.image = load_image_with_white_bg("Images/enemybasic.png", (self.width, self.height))

    def update(self, player_x, player_y):
        # Simple AI: move towards player
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            self.x += (dx / distance) * 2
            self.y += (dy / distance) * 2
        self.shoot_timer += 1

    def shoot(self, player_x, player_y):
        """Returns a bullet if enemy should shoot, otherwise None"""
        if self.shoot_timer > 100 - level.Level.get_level() / 5:  # Shoot more frequently at higher levels
            dx = player_x - self.x
            dy = player_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                bullet = Bullet(self.x + 15, self.y + 15, (dx / distance) * 4, (dy / distance) * 4, self.window_width, self.window_height, bullet_type="enemy")
                self.shoot_timer = 0
                return bullet
        return None

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
