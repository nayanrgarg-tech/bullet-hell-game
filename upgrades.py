from upgrade import Upgrade
import random
import player
import pygame
from PIL import Image, ImageDraw

import upgrade

UPGRADES = [
    Upgrade(
        "Quick Hands",
        "Decreases the cooldown between shots, allowing the player to shoot more frequently.",
        "Common", 10,
        lambda player: setattr(player, "shot_speed", getattr(player, "shot_speed", 50) * 0.95)
    ),
    
    Upgrade(
        "Light Frame",
        "Increases the player's movement speed, allowing for quicker dodging of enemy bullets.",
        "Common", 10,
        lambda player: setattr(player, "speed", getattr(player, "speed", 5) + 2)
    ),

    Upgrade(
        "Immunity Boost",
        "Allow the player to briefly become immune to damage after being hit.",
        "Common", 10, 
        lambda player: setattr(player, "immunity_duration", getattr(player, "immunity_duration") + 10)
    ),

    Upgrade(
        "High-Velocity Rounds",
        "Increases the speed of the player's bullets, making it easier to hit fast-moving enemies.",
        "Common", 10,
        lambda player: setattr(player, "bullet_speed", getattr(player, "bullet_speed") + 2)
    ),

    Upgrade(
        "Large Caliber",
        "Increases the size of the player's bullets, making them easier to hit enemies with.",
        "Uncommon", 5,
        lambda player: setattr(player, "bullet_size", getattr(player, "bullet_size") + 2)
    ),

    Upgrade(
        "Lucky Day",
        "Increases the player's luck, improving the chances of getting better upgrades in the future.",
        "Uncommon", 5,
        lambda player: setattr(player, "min_luck", getattr(player, "min_luck") + 5)
    ),

    Upgrade(
        "Advanced Medkit",
        "Increases the amount of health restored when the player heals.",
        "Uncommon", 5, 
        lambda player: setattr(player, "healing_amount", getattr(player, "healing_amount") + 1)
    ),

    Upgrade(
        "Another Shot",
        "Grants the player the ability to shoot an additional bullet with each shot.",
        "Uncommon", 5,
        lambda player: setattr(player, "bullet_count", getattr(player, "bullet_count") + 1)
    ),

    Upgrade(
        "Focused Fire",
        "Reduces the spread angle between bullets when using multishot, increasing accuracy.",
        "Uncommon", 5,
        lambda player: setattr(player, "multishot_spread_deg", getattr(player, "multishot_spread_deg") - 5)
    ),

    Upgrade(
        "Piercing Rounds",
        "Allows bullets to pierce through enemies, dealing damage to all enemies in their path.",
        "Uncommon", 5,
        lambda player: setattr(player, "pierce_count", getattr(player, "pierce_count") + 1)
    ),

    Upgrade(
        "Micro Targeting System",
        "Decreases bullet size, but increases bullet count significantly.",
        "Rare", 3,
        lambda player: (setattr(player, "bullet_size", max(1, getattr(player, "bullet_size") - 3)),
                        setattr(player, "bullet_count", getattr(player, "bullet_count") + 2))
    ),

    Upgrade(
        "Extra Choice",
        "Increases the number of upgrade choices presented to the player.",
        "Rare", 3,
        lambda player: setattr(player, "upgrade_choices", getattr(player, "upgrade_choices") + 1)
    ),

    Upgrade(
        "Heavy Artillery",
        "Greatly increases bullet size, but decreases bullet speed.",
        "Rare", 3,
        lambda player: (setattr(player, "bullet_size", getattr(player, "bullet_size") + 5),
                        setattr(player, "bullet_speed", max(1, getattr(player, "bullet_speed") - 2)))
    ),

    Upgrade(
        "Homing Missiles",
        "Occasionally fires homing bullets that track enemies.",
        "Rare", 3,
        lambda player: setattr(player, "homing_count", getattr(player, "homing_count", 0) + 1)
    ),

    Upgrade(
        "Damage Retaliation Shield",
        "Grants a chance to reflect bullets back to enemies when hit.",
        "Rare", 3,
        lambda player: setattr(player, "retaliation_chance", getattr(player, "retaliation_chance", 0) + 10)
    ),

    Upgrade(
        "Vampireism",
        "Heals a player every 15 hits.",
        "Legendary", 1,
        lambda player: setattr(player, "vampireism", True)
    ),

    Upgrade(
        "Overdrive",
        "Increases all stats slightly.",
        "Legendary", 1,
        lambda player: (setattr(player, "speed", getattr(player, "speed") + 1),
                        setattr(player, "bullet_speed", getattr(player, "bullet_speed") + 1),
                        setattr(player, "bullet_count", getattr(player, "bullet_count") + 1),
                        setattr(player, "pierce_count", getattr(player, "pierce_count") + 1),
                        setattr(player, "shot_speed", getattr(player, "shot_speed") * 0.98))
    ),

    Upgrade(
        "Orbital Protection",
        "Grants a rotating saw that damages enemies on contact",
        "Legendary", 1,
        lambda player: setattr(player, "orbital_saw", True)
    ),

    Upgrade(
        "Rigged Ships",
        "Riggs all basic enemy ships, reducing their spawn rate.",
        "Legendary", 1,
        lambda player: setattr(player, "rigged_ships", True)
    ),

    Upgrade(
        "Last Stand",
        "When at 1 health, greatly boosts all stats",
        "Mythic", 1,
        lambda player: setattr(player, "last_stand", True)
    ),

    Upgrade(
        "Turbo Gun",
        "Never stop shooting",
        "Mythic", 1,
        lambda player: setattr(player, "shot_speed", 10)
    ),

]

def get_random_upgrades(num_choices, player):
    useable_upgrades = [u for u in UPGRADES if u.current_stack < u.get_max_stack()]
    chosen_upgrades = []

    if not useable_upgrades:
        return chosen_upgrades

    for _ in range(num_choices):
        if not useable_upgrades:
            break
        attempts = 0
        while True:
            if not useable_upgrades:
                break
            luck = random.randint(player.min_luck, 100)
            tempUpgrade = random.choice(useable_upgrades)
            tempRarity = tempUpgrade.get_rarity()

            # Check if the current stack is below the max stack
            if tempUpgrade.current_stack < tempUpgrade.get_max_stack():
                # Apply the upgrade only if its current stack is below the max stack
                if tempRarity == "Common" and tempUpgrade.current_stack < tempUpgrade.get_max_stack():
                    chosen_upgrades.append(tempUpgrade)
                    tempUpgrade.current_stack += 1  # Increment the stack after choosing
                    useable_upgrades.remove(tempUpgrade)
                    break
                elif tempRarity == "Uncommon" and luck >= 30 and tempUpgrade.current_stack < tempUpgrade.get_max_stack():
                    chosen_upgrades.append(tempUpgrade)
                    tempUpgrade.current_stack += 1  # Increment the stack after choosing
                    useable_upgrades.remove(tempUpgrade)
                    break
                elif tempRarity == "Rare" and luck >= 60 and tempUpgrade.current_stack < tempUpgrade.get_max_stack():
                    chosen_upgrades.append(tempUpgrade)
                    tempUpgrade.current_stack += 1  # Increment the stack after choosing
                    useable_upgrades.remove(tempUpgrade)
                    break
                elif tempRarity == "Legendary" and luck >= 85 and tempUpgrade.current_stack < tempUpgrade.get_max_stack():
                    chosen_upgrades.append(tempUpgrade)
                    tempUpgrade.current_stack += 1  # Increment the stack after choosing
                    useable_upgrades.remove(tempUpgrade)
                    break
                elif tempRarity == "Mythic" and luck >= 95 and tempUpgrade.current_stack < tempUpgrade.get_max_stack():
                    chosen_upgrades.append(tempUpgrade)
                    tempUpgrade.current_stack += 1  # Increment the stack after choosing
                    useable_upgrades.remove(tempUpgrade)
                    break
                else:
                    attempts += 1
                    if attempts > 200:
                        break
                    continue
            else:
                # If upgrade has reached max stack, skip it
                attempts += 1
                if attempts > 200:
                    break
                continue

    return chosen_upgrades


def show_upgrade_choices(player, screen, pil_font):
    """
    Displays a centered upgrade menu using a PIL font, waits for player to choose an upgrade,
    then applies the selected upgrade to the player.
    """
    # Clear screen
    screen.fill((0, 0, 0))
    
    # Dynamically get number of upgrades
    num_choices = getattr(player, "upgrade_choices", 3)
    upgrade_choice = get_random_upgrades(num_choices, player)
    if not upgrade_choice:
        return None

    screen_width, screen_height = screen.get_size()
    choice_height = 100  # vertical space per upgrade
    total_height = choice_height * len(upgrade_choice)
    start_y = (screen_height - total_height) // 2  # center vertically

    selected = None
    while selected is None:
        # Create a blank PIL image to render text
        menu_img = Image.new("RGB", (screen_width, screen_height), (0, 0, 0))
        draw = ImageDraw.Draw(menu_img)

        for i, upgrade in enumerate(upgrade_choice):
            y_offset = start_y + i * choice_height

            # Measure text size for horizontal centering
            # For name
            name_bbox = pil_font.getbbox(upgrade.get_name())
            name_w = name_bbox[2] - name_bbox[0]
            name_h = name_bbox[3] - name_bbox[1]

            # For description
            desc_bbox = pil_font.getbbox(upgrade.get_description())
            desc_w = desc_bbox[2] - desc_bbox[0]
            desc_h = desc_bbox[3] - desc_bbox[1]
            name_x = (screen_width - name_w) // 2
            desc_x = (screen_width - desc_w) // 2

            # Draw text
            draw.text((name_x, y_offset), upgrade.get_name(), font=pil_font, fill=upgrade.get_rarity_color())
            draw.text((desc_x, y_offset + 40), upgrade.get_description(), font=pil_font, fill=(200, 200, 200))

        # Convert PIL image to Pygame surface and draw
        menu_surface = pygame.image.fromstring(menu_img.tobytes(), menu_img.size, "RGB")
        screen.blit(menu_surface, (0, 0))
        pygame.display.flip()

        # Handle input for selection
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and len(upgrade_choice) >= 1:
                    selected = 0
                elif event.key == pygame.K_2 and len(upgrade_choice) >= 2:
                    selected = 1
                elif event.key == pygame.K_3 and len(upgrade_choice) >= 3:
                    selected = 2
                elif event.key == pygame.K_4 and len(upgrade_choice) >= 4:
                    selected = 3
                elif event.key == pygame.K_5 and len(upgrade_choice) >= 5:
                    selected = 4

    # Apply the chosen upgrade
    upgrade_choice[selected].apply_effect(player)
    return upgrade_choice[selected]