import math
import pygame
from PIL import Image

# Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)

def load_image_with_white_bg(filename, size):
    try:
        pil_image = Image.open(filename).convert("RGBA")

        # Resize while keeping alpha
        pil_image = pil_image.resize(size, Image.Resampling.NEAREST)

        # Convert to string INCLUDING alpha
        pil_data = pil_image.tobytes()

        # Create pygame surface with alpha
        return pygame.image.fromstring(pil_data, pil_image.size, "RGBA").convert_alpha()
    except Exception as e:
        print("Error loading image:", e)
        return None


class Bullet:
    def __init__(self, x, y, vx, vy, window_width=1400, window_height=800, bullet_type="enemy", bullet_size=10, sprite=None, amplitude=10, frequency=0.01):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = bullet_size # Bullet size
        self.window_width = window_width
        self.window_height = window_height
        self.bullet_type = bullet_type
        # Try to load bullet image
        self.sprite = sprite
        self.image = load_image_with_white_bg(self.sprite, (int(self.radius * 2), int(self.radius * 2)))
        self.amplitude = amplitude
        self.frequency = frequency

    def update(self):
        if self.sprite == "Images/bulletcurve.png":
            self.x += self.vx 
            self.y += self.vy

            # Perpendicular vector
            px = -self.vy
            py = self.vx

            # Normalize
            length = math.hypot(px, py)
            px /= length 
            py /= length

            # Apply sine wave
            offset = math.sin(pygame.time.get_ticks() * self.frequency) * self.amplitude
            self.x += px * offset
            self.y += py * offset
        else:
            self.x += self.vx
            self.y += self.vy


    def is_offscreen(self):
        return self.x < -200 or self.x > self.window_width + 200 or self.y < -10 or self.y > self.window_height + 10

    def draw(self, screen):
        if self.image:
            screen.blit(
            self.image,
            (self.x - self.radius, self.y - self.radius)
            )
        else:
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
    
class HomingBullet(Bullet):
    def __init__(self, x, y, speed, target, window_width=1400, window_height=800, bullet_size=10, bullet_type="player"):
        # Start with 0 velocity; will home in update
        super().__init__(x, y, 0, 0, window_width, window_height, bullet_type, bullet_size, sprite="Images/homingBullet.png")
        self.speed = speed          # constant speed of homing bullet
        self.target = target        # should be an enemy object with x, y

    def update(self):
        if self.target:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            angle = math.atan2(dy, dx)
            self.vx = math.cos(angle) * self.speed
            self.vy = math.sin(angle) * self.speed

        # Call normal Bullet movement
        super().update()

        