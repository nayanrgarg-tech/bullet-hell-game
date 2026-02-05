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

class Boss():
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

    def take_damage(self, damage):
        self.health -= damage
        if self.health / self.max_health <= 0.5:
            self.phase = 2
        
        if self.health / self.max_health <= 0.25:
            self.phase = 3

    #All attacks
    def bullet_rain(self, bullets):
        self.attacking = True

        # Initialize target if first frame of this attack
        if not hasattr(self, "bullet_rain_target"):
            self.bullet_rain_target = random.randint(100, WINDOW_WIDTH - 100)
        # Initialize attack counter if first frame
        if not hasattr(self, "bullet_rain_attack_counter"):
            self.bullet_rain_attack_counter = 0

        # Move toward the stored target
        if self.move_toward(self.bullet_rain_target, 50, 20):
            # Fire a volley when reached
            self.shoot(self.x - 100, 700, random.randint(2, 8), bullets)
            self.shoot(self.x, 700, random.randint(2, 8), bullets)
            self.shoot(self.x + 100, 700, random.randint(2, 8), bullets)
            self.bullet_rain_attack_counter += 1

            # Prepare next target if more volleys remain
            if self.bullet_rain_attack_counter < 10:
                self.bullet_rain_target = random.randint(100, WINDOW_WIDTH - 100)
            else:
                # Finished all volleys
                del self.bullet_rain_attack_counter
                self.attacking = False
                del self.bullet_rain_target
                del self.attack
                return

    def line_shot(self, bullets):
        self.attacking = True

        # Initialize persistent counters if they don't exist yet
        if not hasattr(self, "line_attack_counter"):
            self.line_attack_counter = 0  # Tracks which line we're on
        if not hasattr(self, "line_shot_counter"):
            self.line_shot_counter = 0  # Tracks bullets in the current line
        if not hasattr(self, "line_previous_shot_time"):
            self.line_previous_shot_time = pygame.time.get_ticks()
        if not hasattr(self, "direction"):
            self.direction = random.choice([-1, 1])  # -1 for left-to-right, 1 for right-to-left

        # Stop attack after 10 lines
        if self.line_attack_counter >= 10:
            del self.line_attack_counter
            del self.line_shot_counter
            del self.line_previous_shot_time
            del self.attack
            del self.direction
            self.attacking = False
            return

        # Move toward the current line's position
        if self.direction == 1:
            target_x = self.line_attack_counter * 140
        else:
            target_x = WINDOW_WIDTH - self.line_attack_counter * 140
        if self.move_toward(target_x, 50, 20):
            now = pygame.time.get_ticks()
            # Fire bullets at fixed intervals
            if now - self.line_previous_shot_time >= 20 and self.line_shot_counter < 10:
                self.shoot(self.x, 700, random.randint(1, 8), bullets)
                self.line_shot_counter += 1
                self.line_previous_shot_time = now

            # When current line is done, move to next line
            if self.line_shot_counter >= 10:
                self.line_attack_counter += 1
                self.line_shot_counter = 0

        
    def pursuit_player(self, bullets):
        self.attacking = True

        # Initialize persistent counters if they don't exist yet
        if not hasattr(self, "pursuit_counter"):
            self.pursuit_counter = 0
        if not hasattr(self, "shot_counter"):
            self.shot_counter = 0
        if not hasattr(self, "previous_shot_time"):
            self.previous_shot_time = pygame.time.get_ticks()

        if self.pursuit_counter < 5:
            if not hasattr(self, 'last_player_pos'):
                self.last_player_pos = (self.player.x, self.player.y)
            if self.move_toward(self.last_player_pos[0], self.last_player_pos[1], 10):  # Move toward player
                now = pygame.time.get_ticks() 
                if now - self.previous_shot_time >= 200 and self.shot_counter < 10:
                    self.shoot(self.player.x, self.player.y, 10, bullets)
                    self.shot_counter += 1
                    self.previous_shot_time = now
                
                if self.shot_counter >= 10:
                    self.pursuit_counter += 1
                    self.shot_counter = 0
                    self.last_player_pos = (self.player.x, self.player.y)

        if self.pursuit_counter >= 5:
            del self.pursuit_counter
            del self.shot_counter
            del self.previous_shot_time
            del self.attack
            del self.last_player_pos
            self.attacking = False
            return
        

    def array_shot(self, bullets):
        self.attacking = True

        # Persistent counters
        if not hasattr(self, "direction"):
            self.direction = random.randint(1, 4)  # 1: TL, 2: TR, 3: BL, 4: BR
        if not hasattr(self, "array_shot_counter"):
            self.array_shot_counter = 0
        if not hasattr(self, "array_count"):
            self.array_count = 0
        if not hasattr(self, "previous_array_shot_time"):
            self.previous_array_shot_time = pygame.time.get_ticks()

        # Determine starting coordinates for each corner
        if self.direction == 1:  # Top-left
            start_x = 0
            start_y = 0
        elif self.direction == 2:  # Top-right
            start_x = WINDOW_WIDTH
            start_y = 0
        elif self.direction == 3:  # Bottom-left
            start_x = 0
            start_y = WINDOW_HEIGHT
        elif self.direction == 4:  # Bottom-right
            start_x = WINDOW_WIDTH
            start_y = WINDOW_HEIGHT

        # Main attack logic
        if self.array_shot_counter < 10:
            target_x = start_x + self.array_shot_counter * 140 * (-1 if self.direction in [2, 4] else 1)
            target_y = start_y + self.array_shot_counter * 80 * (-1 if self.direction in [3, 4] else 1)
            self.move_toward(target_x, target_y, 10)

            now = pygame.time.get_ticks()
            if now - self.previous_array_shot_time >= 200:
                # Fire bullets in four directions
                self.shoot(self.x, WINDOW_HEIGHT, 5, bullets)
                self.shoot(WINDOW_WIDTH, self.y, 5, bullets)
                self.shoot(0, self.y, 5, bullets)
                self.shoot(self.x, 0, 5, bullets)
                self.previous_array_shot_time = now
                self.array_count += 1

            if self.array_count >= 5:
                self.array_shot_counter += 1
                self.array_count = 0

        # Finish attack
        if self.array_shot_counter >= 10:
            del self.array_shot_counter
            del self.array_count
            del self.previous_array_shot_time
            del self.direction
            del self.attack
            self.attacking = False
            return



    def rotating_lasers(self, bullets):
        self.attacking = True

        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2

        # Persistent angle and timing
        if not hasattr(self, "rotating_angle"):
            self.rotating_angle = 0
        
        if not hasattr(self, "last_shot_time"):
            self.last_shot_time = pygame.time.get_ticks()

        #Attack logic
        if self.move_toward(center_x, center_y, 3):
            now = pygame.time.get_ticks()
            if now - self.last_shot_time >= 20:
                angle = self.rotating_angle
                target_x = center_x + math.cos(angle) * 400
                target_y = center_y + math.sin(angle) * 400
                self.shoot(target_x, target_y, 2, bullets)
                self.rotating_angle += math.pi / 17  # Increment angle for next shot
                self.last_shot_time = now

            #Finish attack after 2 full rotations
            if self.rotating_angle >= 4 * math.pi:
                del self.rotating_angle
                del self.last_shot_time
                del self.attack
                self.attacking = False
                return

    def random_bursts(self, bullets):
        self.attacking = True

        #Persistent counters
        if not hasattr(self, "random_burst_counter"):
            self.random_burst_counter = 0
        if not hasattr(self, "burst_count"):
            self.burst_count = 0
        if not hasattr(self, "previous_burst_time"):
            self.previous_burst_time = pygame.time.get_ticks()
        if not hasattr(self, "position"):
            self.position = (random.randint(100, WINDOW_WIDTH - 100), random.randint(100, WINDOW_HEIGHT - 100))
        if not hasattr(self, "attack_position"):
            self.attack_position = (random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT))

        #Main attack logic
        if self.move_toward(self.position[0], self.position[1], 5):
            now = pygame.time.get_ticks()
            if now - self.previous_burst_time >= 50 and self.burst_count < 20:
                self.shoot(self.attack_position[0], self.attack_position[1], random.randint(3, 7), bullets)
                self.burst_count += 1
                self.previous_burst_time = now
                self.attack_position = (random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT))

                if self.burst_count >= 20:
                    self.random_burst_counter += 1
                    self.burst_count = 0
                    self.position = (random.randint(100, WINDOW_WIDTH - 100), random.randint(100, WINDOW_HEIGHT - 100))
        
            # Finish attack
            if self.random_burst_counter >= 5:
                del self.random_burst_counter
                del self.burst_count
                del self.previous_burst_time
                del self.position
                del self.attack_position
                del self.attack
                self.attacking = False
                return
    
    def omnidirectional_blast(self, bullets):
        self.attacking = True

        #persistent counters
        if not hasattr(self, "blast_shot_counter"):
            self.blast_shot_counter = 0
        if not hasattr(self, "blast_previous_shot_time"):
            self.blast_previous_shot_time = pygame.time.get_ticks()
        if not hasattr(self, "total_blasts"):
            self.total_blasts = 0
        if not hasattr(self, "random_target"):
            self.random_target = (random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT))


        #main attack logic
        if self.move_toward(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, 5):
            now = pygame.time.get_ticks()
            if now - self.blast_previous_shot_time >= 300 and self.total_blasts < 20:
                if self.blast_shot_counter <= 8:
                    self.shoot(self.random_target[0], self.random_target[1], random.randint(3, 8), bullets)
                    self.blast_shot_counter += 1
                    self.random_target = (random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT))
                else:
                    self.total_blasts += 1
                    self.blast_shot_counter = 0
                
            if self.total_blasts >= 20:
                del self.blast_shot_counter
                del self.blast_previous_shot_time
                del self.total_blasts
                del self.random_target
                del self.attack
                self.attacking = False
                return

    def downpour(self, bullets):
        self.attacking = True

        # Persistent position and counters
        if not hasattr(self, "downpour_position_x"):
            self.downpour_position_x = random.randint(100, WINDOW_WIDTH - 100)
        if not hasattr(self, "downpour_shot_counter"):
            self.downpour_shot_counter = 0
        if self.move_toward(self.downpour_position_x, 50, 10):
            self.shoot(self.x - 300, 800, random.randint(5, 8), bullets)
            self.shoot(self.x - 200, 800, random.randint(5, 8), bullets)
            self.shoot(self.x - 100, 800, random.randint(5, 8), bullets)
            self.shoot(self.x, 800, random.randint(5, 8), bullets)
            self.shoot(self.x + 100, 800, random.randint(5, 8), bullets)
            self.shoot(self.x + 200, 800, random.randint(5, 8), bullets)
            self.shoot(self.x + 300, 800, random.randint(5, 8), bullets)
            self.downpour_shot_counter += 1
            self.downpour_position_x = random.randint(100, WINDOW_WIDTH - 100)
        
        if self.downpour_shot_counter >= 20:
            del self.downpour_position_x
            del self.downpour_shot_counter
            del self.attack
            self.attacking = False
            return

    def chaos(self, bullets):
        self.attacking = True

        #Persistent counters
        if not hasattr(self, "random_burst_counter"):
            self.random_burst_counter = 0
        if not hasattr(self, "burst_count"):
            self.burst_count = 0
        if not hasattr(self, "random_position"):
            self.random_position = (random.randint(100, WINDOW_WIDTH - 100), random.randint(100, WINDOW_HEIGHT - 100))
        if not hasattr(self, "shot_position"):
            self.shot_position = (random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT))

        if self.move_toward(self.random_position[0], self.random_position[1], 10):
            if self.burst_count < 20:
                self.shoot(self.shot_position[0], self.shot_position[1], random.randint(2, 7), bullets)
                self.burst_count += 1
                self.shot_position = (random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT))
            else:
                self.random_burst_counter += 1
                self.burst_count = 0
                self.random_position = (random.randint(100, WINDOW_WIDTH - 100), random.randint(100, WINDOW_HEIGHT - 100))

        if self.random_burst_counter >= 10:
            del self.random_burst_counter
            del self.burst_count
            del self.random_position
            del self.shot_position
            del self.attack
            self.attacking = False
            return


    def choose_attack(self, bullets):
            
        if not hasattr(self, 'attack') and not self.attacking:
            self.attack = random.randint(1,3)
        
        if self.phase == 1:
            if self.attack == 1:
                self.bullet_rain(bullets)
            elif self.attack == 2:
                self.line_shot(bullets)
            elif self.attack == 3:
                self.pursuit_player(bullets)
        elif self.phase == 2:
            if self.attack == 1:
                self.array_shot(bullets)
            elif self.attack == 2:
                self.rotating_lasers(bullets)
            elif self.attack == 3:
                self.random_bursts(bullets)
        elif self.phase == 3:
            if self.attack == 1:
                self.omnidirectional_blast(bullets)
            elif self.attack == 2:
                self.downpour(bullets)
            elif self.attack == 3:
                self.chaos(bullets)

        

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

    def shoot(self, target_x, target_y, speed, bullets):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            bullet = Bullet(self.x, self.y, (dx / distance) * speed, (dy / distance) * speed, WINDOW_WIDTH, WINDOW_HEIGHT, bullet_type="enemy", sprite="Images/bullets.png")
            bullets.append(bullet)

        return None
    
    def defeat(self):
        # Game over text
        if self.isDefeated:
            return

    def get_rect(self):
        return self.image.get_rect(center=(self.x, self.y))

