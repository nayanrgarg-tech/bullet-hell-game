import pygame
from PIL import Image
from bullet import *
import math
import random

WHITE = (255, 255, 255)

def load_image_with_white_bg(filename, size):
    """Load image with transparency preserved for Pygame"""
    try:
        pil_image = Image.open(filename).convert("RGBA")  # keep alpha

        # Resize while preserving alpha
        pil_image = pil_image.resize(size, Image.Resampling.NEAREST)

        # Convert to bytes and create a Pygame surface with alpha
        pil_data = pil_image.tobytes()
        return pygame.image.fromstring(pil_data, pil_image.size, "RGBA").convert_alpha()

    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None


class Player:
    def __init__(self, x, y, window_width=1200, window_height=800):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.speed = 5
        self.health = 3
        self.window_width = window_width
        self.window_height = window_height
        self.shoot_cooldown = 50
        self.shot_speed = 80
        self.bullet_speed = 5
        self.healing_amount = 1
        self.bullet_count = 1
        self.pierce_count = 1 # Number of enemies a bullet can pierce through
        self.upgrade_choices = 2 # Number of upgrade choices to present
        self.multishot_spread_deg = 30  # degrees between bullets in multishot
        self.immunity_duration = 0  # Duration of immunity after being hit
        self.immunity = 0  # Current immunity timer
        self.bullet_size = 10  # Size of the player's bullets
        self.min_luck = 1 # Minimum luck value for upgrades
        self.homing_count = 0 # Number of homing bullets to shoot
        self.homing_cooldown_max = 200  # frames between homing shots
        self.homing_cooldown = 0        # current cooldown timer
        self.retaliation_chance = 0  # Chance to reflect damage back to enemies
        self.vampireism = False # Life steal ability
        self.kill_count = 0 # Number of enemies killed
        # Load player image with white background
        self.orbital_saw = False # Whether player has orbital saw
        self.orbital_saw_angle = 0  # Angle of rotation for the saw
        self.orbital_saw_speed = 3  # Speed of saw rotation
        self.orbital_saw_radius = 60  # Distance from the player (radius of orbit)
        self.orbital_saw_size = 50  # Size of the saw image
        self.rigged_ships = False # Whether player has rigged ships upgrade
        self.last_stand = False # Whether player has last stand upgrade
        self.orbital_saw_image = load_image_with_white_bg("Images/orbital_saw.png", (50, 50))  # Image for saw

        self.image = load_image_with_white_bg("Images/hero.png", (self.width, self.height))
        self.homing_bullet_image = load_image_with_white_bg("Images/homingBullet.png", (20, 20))

    def handle_input(self, window_width, window_height):
        keys = pygame.key.get_pressed()
        # Arrow keys
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < window_width - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < window_height - self.height:
            self.y += self.speed
        
        # WASD controls
        if keys[pygame.K_a] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_d] and self.x < window_width - self.width:
            self.x += self.speed
        if keys[pygame.K_w] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_s] and self.y < window_height - self.height:
            self.y += self.speed
        
        self.shoot_cooldown = max(self.shoot_cooldown - 1, 0)
        self.homing_cooldown = max(self.homing_cooldown - 1, 0)

        # Update orbital saw angle
        if self.orbital_saw:
            self.orbital_saw_angle += self.orbital_saw_speed
        if self.orbital_saw_angle >= 360:
            self.orbital_saw_angle -= 360


    def shoot(self, target_x, target_y, enemies=[]):
        # Check for collisions with orbital saw
        if self.orbital_saw:
            saw_x = self.x + self.width // 2 + math.cos(math.radians(self.orbital_saw_angle)) * self.orbital_saw_radius
            saw_y = self.y + self.height // 2 + math.sin(math.radians(self.orbital_saw_angle)) * self.orbital_saw_radius

            # Create a small rect around the saw to check for collisions
            saw_rect = pygame.Rect(saw_x - self.orbital_saw_size // 2, saw_y - self.orbital_saw_size // 2, self.orbital_saw_size, self.orbital_saw_size)

            for enemy in enemies[:]:
                if saw_rect.colliderect(enemy.get_rect()):
                    # Enemy is hit by the saw
                    enemies.remove(enemy)
                    break  # Only remove one enemy at a time

        bullets = []

        player_center_x = self.x + self.width // 2
        player_center_y = self.y + self.height // 2

        dx = target_x - player_center_x
        dy = target_y - player_center_y

        # --- NORMAL BULLETS ---
        if self.shoot_cooldown <= 0:
            if dx != 0 or dy != 0:
                base_angle = math.atan2(dy, dx)
                spread_rad = math.radians(self.multishot_spread_deg)

                for i in range(self.bullet_count):
                    offset = (i - (self.bullet_count - 1) / 2) * spread_rad
                    angle = base_angle + offset

                    vx = math.cos(angle) * self.bullet_speed
                    vy = math.sin(angle) * self.bullet_speed

                    for _ in range(self.pierce_count):
                        bullets.append(
                            Bullet(
                                player_center_x,
                                player_center_y,
                                vx,
                                vy,
                                self.window_width,
                                self.window_height,
                                bullet_type="player",
                                bullet_size=self.bullet_size,
                                sprite="Images/pbullet.png"
                            )
                        )
            else:
                bullets.append(
                    Bullet(
                        player_center_x,
                        player_center_y,
                        0,
                        -self.bullet_speed,
                        self.window_width,
                        self.window_height,
                        bullet_type="player",
                        bullet_size=self.bullet_size,
                        sprite="Images/pbullet.png"
                    )
                )
            self.shoot_cooldown = self.shot_speed
        # Homing bullets
        if self.homing_count > 0 and self.homing_cooldown <= 0:
            for i in range(self.homing_count):
                target = enemies[0] if enemies else None
                if target:
                    # Spread in fan
                    angle_to_target = math.atan2(target.y - player_center_y, target.x - player_center_x)
                    offset = (i - (self.homing_count - 1)/2) * math.radians(self.multishot_spread_deg)
                    angle = angle_to_target + offset
                    vx = math.cos(angle) * self.bullet_speed
                    vy = math.sin(angle) * self.bullet_speed
                else:
                    angle = random.uniform(0, 2*math.pi)
                    vx = math.cos(angle) * self.bullet_speed
                    vy = math.sin(angle) * self.bullet_speed

                bullet = HomingBullet(
                    player_center_x,
                    player_center_y,
                    speed=self.bullet_speed,
                    target=target,
                    window_width=self.window_width,
                    window_height=self.window_height,
                    bullet_size=self.bullet_size,
                    bullet_type="player",
                    image=self.homing_bullet_image
                )
                bullet.vx = vx
                bullet.vy = vy
                bullets.append(bullet)
            self.homing_cooldown = self.homing_cooldown_max
        
        # LAST STAND UPGRADE
        if self.last_stand and self.health == 1:
            if not hasattr(self, 'previous_stats'):
                self.previous_stats = {
                    'bullet_count': self.bullet_count,
                    'multishot_spread_deg': self.multishot_spread_deg,
                    'bullet_size': self.bullet_size,
                    'bullet_speed': self.bullet_speed,
                    'shot_speed': self.shot_speed
                }
            self.multishot_spread_deg = 5
            self.bullet_count = 10
            self.bullet_size = 20
            self.bullet_speed = 20
            self.shot_speed = 10
        elif self.last_stand and hasattr(self, 'previous_stats'):
            self.bullet_count = self.previous_stats['bullet_count']
            self.multishot_spread_deg = self.previous_stats['multishot_spread_deg']
            self.bullet_size = self.previous_stats['bullet_size']
            self.bullet_speed = self.previous_stats['bullet_speed']
            self.shot_speed = self.previous_stats['shot_speed']
            self.last_stand = False
            del self.previous_stats


        return bullets


    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        if self.orbital_saw:
            # Calculate the position of the saw
            saw_x = self.x + self.width // 2 + math.cos(math.radians(self.orbital_saw_angle)) * self.orbital_saw_radius
            saw_y = self.y + self.height // 2 + math.sin(math.radians(self.orbital_saw_angle)) * self.orbital_saw_radius
            
            # Rotate the saw image around the player
            rotated_saw = pygame.transform.rotate(self.orbital_saw_image, self.orbital_saw_angle)
            saw_rect = rotated_saw.get_rect(center=(saw_x, saw_y))
            
            # Draw the saw
            screen.blit(rotated_saw, saw_rect.topleft)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

     