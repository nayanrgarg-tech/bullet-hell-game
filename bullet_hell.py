import pygame
import random
import math
from PIL import Image
import level
from player import Player
from bullet import Bullet
from enemy import Enemy
import upgrades
from boss import Boss
from PIL import ImageFont 
from io import BytesIO
import os

# Get the parent directory to find MelonPop.ttf
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
font_path = os.path.join(parent_dir, "MelonPop.ttf")

# Initialize Pygame
pygame.init()

# add fonts
pil_font_large = ImageFont.truetype(font_path, 48)  # For GAME OVER
pil_font_medium = ImageFont.truetype(font_path, 36) # For score
pil_font_small = ImageFont.truetype(font_path, 28)  # For instructions / upgrade descriptions


# Constants
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
FPS = 60


# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Bullet Hell")
    clock = pygame.time.Clock()
    
    NUM_STARS = 150

    stars = [
        (random.randint(0, WINDOW_WIDTH),
        random.randint(0, WINDOW_HEIGHT),
        random.randint(1, 2))   # size
        for _ in range(NUM_STARS)
    ]
    

    running = True
    while running:
        # Initialize game
        player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)
        bullets = []
        enemies = []
        score = 0
        enemy_spawn_timer = 0
        level.Level.reset_level()
        game_over = False
        boss_spawned = False
        boss = None

        # Game loop
        while running and not game_over:
            clock.tick(FPS)
            
            # Get mouse position for shooting
            mouse_x, mouse_y = pygame.mouse.get_pos()
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    game_over = True

            # Continuous shooting - hold mouse or space
            new_bullets = player.shoot(mouse_x, mouse_y, enemies)
            bullets.extend(new_bullets)

            player.handle_input(WINDOW_WIDTH, WINDOW_HEIGHT)

            # Spawn enemies
            if player.rigged_ships:
                timer = 450
            else:
                timer = 300
            enemy_spawn_timer += level.Level.get_level()  # Increase spawn rate with level
            if (enemy_spawn_timer > timer) and level.Level.get_level() != 10:
                enemy_x = random.randint(0, WINDOW_WIDTH - 30)
                enemies.append(Enemy(enemy_x, -30, WINDOW_WIDTH, WINDOW_HEIGHT))
                enemy_spawn_timer = 0

            # Update enemies and their bullets
            for enemy in enemies[:]:
                enemy.update(player.x, player.y)
                
                # Shoot bullets
                bullet = enemy.shoot(player.x, player.y)
                if bullet:
                    bullets.append(bullet)

                # Remove off-screen enemies
                if enemy.y > WINDOW_HEIGHT:
                    enemies.remove(enemy)

            # Update bullets
            for bullet in bullets[:]:
                bullet.update()
                if bullet.is_offscreen():
                    bullets.remove(bullet)

            # Check collisions: bullets hit player
            player_rect = player.get_rect()
            player.immunity = max(0, player.immunity - 1)  # Decrease immunity timer
            for bullet in bullets[:]:
                if bullet.bullet_type == "enemy" and player_rect.colliderect(bullet.get_rect()) and player.immunity == 0:
                    # Check for retaliation chance
                    if random.randint(1, 100) <= player.retaliation_chance:
                        # Reflect bullet back towards enemies
                        dx = bullet.vx
                        dy = bullet.vy
                        distance = math.sqrt(dx**2 + dy**2)
                        if distance > 0:
                            reflected_bullet = Bullet(bullet.x, bullet.y, - (dx / distance) * 6, - (dy / distance) * 6, WINDOW_WIDTH, WINDOW_HEIGHT, bullet_type="player")
                            bullets.append(reflected_bullet)
                    else:
                        player.health -= 1            
                        player.immunity = player.immunity_duration  # Set immunity timer
                    if bullet in bullets:
                        bullets.remove(bullet)
                    if player.health <= 0:
                        game_over = True
            #check collisions: orbital saw hits bullets
            if player.orbital_saw:
                saw_x = player.x + player.width // 2 + math.cos(math.radians(player.orbital_saw_angle)) * player.orbital_saw_radius
                saw_y = player.y + player.height // 2 + math.sin(math.radians(player.orbital_saw_angle)) * player.orbital_saw_radius
                saw_rect = pygame.Rect(saw_x - player.orbital_saw_size // 2, saw_y - player.orbital_saw_size // 2, player.orbital_saw_size, player.orbital_saw_size)
                for bullet in bullets[:]:
                    if bullet.bullet_type == "enemy" and saw_rect.colliderect(bullet.get_rect()):
                        bullets.remove(bullet)
                        bullets.append(Bullet(saw_x, saw_y, -bullet.vx, -bullet.vy, WINDOW_WIDTH, WINDOW_HEIGHT, bullet_type="player"))

            # Check collisions: player bullets hit enemies
            for bullet in bullets[:]:
                if bullet.bullet_type == "player":
                    for enemy in enemies[:]:
                        if bullet.get_rect().colliderect(enemy.get_rect()):
                            if enemy in enemies:
                                enemies.remove(enemy)
                                player.kill_count += 1
                                # Vampireism heal every 15 kills
                                if player.vampireism and player.kill_count % 15 == 0:
                                    player.health += 1
                            if bullet in bullets:
                                bullets.remove(bullet)
                            score += 1
                            break

            # Check collisions: enemies hit player
            for enemy in enemies[:]:
                if player_rect.colliderect(enemy.get_rect()) and player.immunity == 0:
                    player.health -= 1
                    player.immunity = player.immunity_duration  # Set immunity timer
                    if enemy in enemies:
                        enemies.remove(enemy)
                    if player.health <= 0:
                        game_over = True

            #Check collisions: player bullets hit boss
            for bullet in bullets[:]:
                if bullet.bullet_type == "player" and boss_spawned:
                    if bullet.get_rect().colliderect(boss.get_rect()):
                        boss.take_damage(1)
                        if bullet in bullets:
                            bullets.remove(bullet)


            # Increase level based on scored
            if score > level.Level.get_level() ** 2:
                level.Level.increase_level()
                player.health += player.healing_amount  # Heal player on level up

                # Show upgrade choices
                upgrades.show_upgrade_choices(player, screen, pil_font_small)

        

            # Draw everything
            screen.fill(BLACK)
            # Draw stars
            for x, y, size in stars:
                pygame.draw.circle(screen, (255, 255, 255), (x, y), size)

            # Draw scoreboard with white background and larger text
            try:
                from PIL import ImageDraw, ImageFont
                score_img = Image.new("RGBA", (600, 80), (255, 255, 255, 0))
                draw = ImageDraw.Draw(score_img)
                text = f"Score: {score}  Health: {player.health} Level: {level.Level.get_level()}"
                # Draw text in large font with black color for contrast
                draw.text((20, 20), text, fill=WHITE, font=pil_font_medium)
                score_surface = pygame.image.fromstring(score_img.tobytes(), score_img.size, "RGBA")
                screen.blit(score_surface, (10, 10))
            except Exception:
                pass

            player.draw(screen)
            for bullet in bullets:
                bullet.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)

            # Spawn boss at level 10
            if level.Level.get_level() == 10 and not boss_spawned:
                enemies.clear()  # Clear existing enemies
                boss = Boss(WINDOW_WIDTH // 2, 100, 300, "Images/boss1.png", 1, player, bullets)    
                boss_spawned = True
            
            # Update boss
            if boss_spawned:
                boss.draw(screen)
                boss.choose_attack(bullets)

            if boss_spawned and boss.health <= 0:
                boss.defeat()
                level.Level.increase_level()
                score += 50  # Bonus for defeating boss
                del boss
                boss_spawned = False
                

            pygame.display.flip()

        # Game Over screen
        if running:  # Only show if not quitting entirely
            game_over_screen = True
            while game_over_screen and running:
                clock.tick(FPS)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        game_over_screen = False
                    if event.type == pygame.KEYDOWN:
                        game_over_screen = False

                # Draw game over screen
                screen.fill(BLACK)

                for x, y, size in stars:
                    pygame.draw.circle(screen, (255, 255, 255), (x, y), size)


                
                try:
                    from PIL import ImageDraw
                    # Game over text
                    game_over_img = Image.new("RGB", (600, 400), WHITE)
                    draw = ImageDraw.Draw(game_over_img)
                    
                    draw.text((150, 80), "GAME OVER", fill=BLACK, font=pil_font_large)
                    draw.text((100, 180), f"Final Score: {score}", fill=BLACK, font=pil_font_medium)
                    draw.text((50, 280), "Press any key to play again", fill=BLACK, font=pil_font_medium)
                    
                    game_over_surface = pygame.image.fromstring(game_over_img.tobytes(), game_over_img.size, "RGB")
                    screen.blit(game_over_surface, (WINDOW_WIDTH // 2 - 300, WINDOW_HEIGHT // 2 - 200))
                except Exception:
                    pass
                
                pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
