import pygame
import math
from PIL import Image
from bullet import Bullet

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


class Peon:
    def __init__(self, x, y, peon_type, health=5, window_width=1400, window_height=800):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.health = health
        self.peon_type = peon_type
        self.window_width = window_width
        self.window_height = window_height
        self.shoot_timer = 0
        
        # Load peon image with no background
        if self.peon_type == 1:  # Turret
            self.image = load_image_with_white_bg("Images/turret.png", (self.width, self.height))
    
    def update(self, player_x, player_y):
        """Update peon state - turrets don't move"""
        self.shoot_timer += 1
        
    def shoot(self, player_x, player_y):
        """Returns a bullet if peon should shoot, otherwise None"""
        # Peons shoot slower than regular enemies
        if self.peon_type == 1 and self.shoot_timer > 120:  # Shoot every ~1 second
            dx = player_x - self.x
            dy = player_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                bullet = Bullet(
                    self.x + self.width // 2, 
                    self.y + self.height // 2, 
                    (dx / distance) * 3, 
                    (dy / distance) * 3, 
                    self.window_width, 
                    self.window_height, 
                    bullet_type="enemy", 
                    bullet_size=8, 
                    sprite="Images/bullets.png"
                )
                self.shoot_timer = 0
                return bullet
        return None

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)