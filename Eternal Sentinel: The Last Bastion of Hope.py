import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (200, 200, 200)
DARK_GRAY = (169, 169, 169)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense")

# Set background color to green
screen.fill(GREEN)

# Clock to control frame rate
clock = pygame.time.Clock()

# Base properties
base_radius = 50
base_x = SCREEN_WIDTH // 2
base_y = SCREEN_HEIGHT - 60
base_health = 100

# Tower properties
tower_radius = 40
towers = []

# Tower types
tower_types = {
    "arrow": {"cost": 50, "color": BLUE, "shoot_interval": 60, "bullet_speed": 10, "bullet_count": 1},
    "laser": {"cost": 100, "color": ORANGE, "shoot_interval": 0, "bullet_speed": 0, "bullet_count": 1},  # Laser shoots beams
    "fire": {"cost": 75, "color": RED, "damage_per_second":25}  # Fire tower
}

# Enemy properties
enemy_width = 30
enemy_height = 30
enemy_speed = 2
enemies = []

# Enemy health
enemy_health = []  # Each enemy will have a corresponding health value

# Enemy image
enemy_image = pygame.image.load("spider.png")
enemy_image = pygame.transform.scale(enemy_image, (enemy_width, enemy_height))

# Bullet properties
bullets = []

# Fire tower beams
fire_beams = []

# Laser beams
beams = []

# Score and money
score = 0
money = 100

# Paths for enemies
paths = [
    [(50, 0), (100, 150), (200, 300), (base_x, base_y)],
    [(SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2 + 50, 200), (SCREEN_WIDTH // 2 - 50, 400), (base_x, base_y)],
    [(SCREEN_WIDTH - 50, 0), (SCREEN_WIDTH - 100, 150), (SCREEN_WIDTH - 200, 300), (base_x, base_y)]
]

# Font for UI
font = pygame.font.Font(None, 36)

def draw_base():
    home_image = pygame.image.load("home.png")
    home_image = pygame.transform.scale(home_image, (int(base_radius * 2.64), int(base_radius * 2.64)))
    screen.blit(home_image, (base_x - base_radius, base_y - base_radius))
    health_text = font.render(f"Health: {base_health}", True, BLACK)
    screen.blit(health_text, (10, 10))

def draw_paths():
    for path in paths:
        for i in range(len(path) - 1):
            start = path[i]
            end = path[i + 1]
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            length = (dx ** 2 + dy ** 2) ** 0.5
            unit_dx = dx / length
            unit_dy = dy / length

            # Calculate offsets for path edges
            half_width = enemy_width * 1.8
            offset_x = -unit_dy * half_width
            offset_y = unit_dx * half_width

            # Draw path edges
            pygame.draw.line(screen, GRAY, (start[0] + offset_x, start[1] + offset_y),
                             (end[0] + offset_x, end[1] + offset_y), 2)
            pygame.draw.line(screen, GRAY, (start[0] - offset_x, start[1] - offset_y),
                             (end[0] - offset_x, end[1] - offset_y), 2)

def draw_towers():
    for tower in towers:
        if tower["type"] == tower_types["fire"]:
            # Draw a rectangular shape for the fire tower
            tower_width = 20
            tower_height = 40
            top_x, top_y = tower["x"], tower["y"] - tower_height - 10
            pygame.draw.rect(screen, tower["type"]["color"], (tower["x"] - tower_width // 2, tower["y"] - tower_height, tower_width, tower_height))
            pygame.draw.polygon(screen, YELLOW, [(tower["x"] - tower_width // 2, tower["y"] - tower_height),
                                                (tower["x"] + tower_width // 2, tower["y"] - tower_height),
                                                (top_x, top_y)])
            # Adjust fire beam to originate from the tip of the tower
            tower["top_x"] = top_x
            tower["top_y"] = top_y
        else:
            pygame.draw.circle(screen, tower["type"]["color"], (tower["x"], tower["y"]), tower_radius)

def draw_enemies():
    for i, enemy in enumerate(enemies):
        screen.blit(enemy_image, (enemy["pos"][0] - enemy_width // 2, enemy["pos"][1] - enemy_height // 2))

def draw_fire_beams():
    for beam in fire_beams:
        pygame.draw.line(screen, RED, (beam["x"], beam["y"]), (beam["target_x"], beam["target_y"]), 2)

def draw_bullets():
    for bullet in bullets:
        pygame.draw.circle(screen, BLACK, (bullet["x"], bullet["y"]), 5)

def spawn_enemy():
    global score
    if score == 100:
        # Spawn the boss enemy
        path = random.choice(paths)
        enemies.append({"path": path, "index": 0, "pos": list(path[0]), "health": 1000 * 1.9, "is_boss": True})
    else:
        # Spawn regular enemies
        path = random.choice(paths)
        enemies.append({"path": path, "index": 0, "pos": list(path[0]), "health": 100})

def move_enemies():
    for enemy in enemies:
        if enemy["index"] < len(enemy["path"]):
            target = enemy["path"][enemy["index"] + 1]
            dx = target[0] - enemy["pos"][0]
            dy = target[1] - enemy["pos"][1]
            dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
            enemy["pos"][0] += int(enemy_speed * dx / dist)
            enemy["pos"][1] += int(enemy_speed * dy / dist)

            if abs(dx) < 5 and abs(dy) < 5:
                enemy["index"] += 1

def apply_fire_tower_damage():
    fire_beams.clear()
    for tower in towers:
        if tower["type"] == tower_types["fire"]:
            beam_count = 0  # عداد للأشعة النشطة لكل برج
            for enemy in enemies:
                if beam_count >= 2:
                    break  # لا تضيف المزيد من الأشعة إذا كان العدد قد وصل إلى 2
                if abs(tower["x"] - enemy["pos"][0]) <= 150 and abs(tower["y"] - enemy["pos"][1]) <= 150:
                    enemy["health"] -= tower["type"]["damage_per_second"] / 30  # Damage applied per frame
                    if "top_x" in tower and "top_y" in tower:
                        fire_beams.append({"x": tower["top_x"], "y": tower["top_y"], "target_x": enemy["pos"][0], "target_y": enemy["pos"][1]})
                    beam_count += 1

def shoot_bullets():
    for tower in towers:
        if tower["type"] == tower_types["arrow"]:
            tower["shoot_timer"] += 1
            if tower["shoot_timer"] >= tower["type"]["shoot_interval"]:
                tower["shoot_timer"] = 0
                for _ in range(tower["type"]["bullet_count"]):
                    bullets.append({"x": tower["x"], "y": tower["y"] - tower_radius, "speed": tower["type"]["bullet_speed"]})

def shoot_beams():
    beams.clear()
    for tower in towers:
        if tower["type"] == tower_types["laser"]:
            for i, enemy in enumerate(enemies):
                if abs(tower["x"] - enemy["pos"][0]) <= 100 and abs(tower["y"] - enemy["pos"][1]) <= 100:
                    beams.append({"x": tower["x"], "y": tower["y"], "target_x": enemy["pos"][0], "target_y": enemy["pos"][1]})
                    enemy["health"] -= 50  # Laser reduces health by 50 every 0.5 seconds

    for i in range(len(enemies) - 1, -1, -1):
        if enemies[i]["health"] <= 0:
            enemies.pop(i)
            global score, money
            score += 10
            money += 20

def show_score_and_money():
    score_text = font.render(f"Score: {score}", True, BLACK)
    money_text = font.render(f"Money: {money}", True, BLACK)
    screen.blit(score_text, (10, 50))
    screen.blit(money_text, (10, 90))

# Store screen
store_screen = False
selected_tower = None

def draw_store():
    global selected_tower
    screen.fill(WHITE)
    title_text = font.render("Tower Store", True, BLACK)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - 80, 50))

    arrow_text = font.render(f"1: Arrow Tower - Cost: {tower_types['arrow']['cost']}", True, BLUE)
    laser_text = font.render(f"2: Laser Tower - Cost: {tower_types['laser']['cost']}", True, ORANGE)
    fire_text = font.render(f"3: Fire Tower - Cost: {tower_types['fire']['cost']}", True, RED)
    back_text = font.render("Press B to go back", True, BLACK)
    selected_text = font.render(f"Selected: {selected_tower if selected_tower else 'None'}", True, GREEN)

    screen.blit(arrow_text, (50, 150))
    screen.blit(laser_text, (50, 200))
    screen.blit(fire_text, (50, 250))
    screen.blit(back_text, (50, 300))
    screen.blit(selected_text, (50, 350))

# Main game loop
running = True
enemy_spawn_timer = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                store_screen = True
            if event.key == pygame.K_b:
                store_screen = False
            if store_screen:
                if event.key == pygame.K_1:
                    selected_tower = "arrow"
                if event.key == pygame.K_2:
                    selected_tower = "laser"
                if event.key == pygame.K_3:
                    selected_tower = "fire"
        if event.type == pygame.MOUSEBUTTONDOWN and not store_screen:
            x, y = pygame.mouse.get_pos()
            if y < base_y - base_radius and selected_tower:
                tower_type = tower_types[selected_tower]
                if money >= tower_type["cost"]:
                    towers.append({"x": x, "y": y, "type": tower_type, "shoot_timer": 0})
                    money -= tower_type["cost"]

    if store_screen:
        draw_store()
    else:
        screen.fill(GRAY)  # Set background color to green

        # Enemy spawn logic
        enemy_spawn_timer += 1
        if enemy_spawn_timer > 60:
            spawn_enemy()
            enemy_spawn_timer = 0

        # Move enemies along paths
        move_enemies()

        # Apply fire tower damage
        apply_fire_tower_damage()

        # Bullet shooting logic
        shoot_bullets()

        # Beam shooting logic
        shoot_beams()

        # Update enemy positions
        for i in range(len(enemies) - 1, -1, -1):
            if ((enemies[i]["pos"][0] - base_x) ** 2 + (enemies[i]["pos"][1] - base_y) ** 2) ** 0.5 <= base_radius:
                enemies.pop(i)
                base_health -= 10

        # Update bullet positions
        for bullet in bullets[:]:
            bullet["y"] -= bullet["speed"]
            if bullet["y"] < 0:
                bullets.remove(bullet)

        # Check collisions
        for bullet in bullets[:]:
            for i in range(len(enemies) - 1, -1, -1):
                if (bullet["x"] > enemies[i]["pos"][0] - enemy_width // 2 and bullet["x"] < enemies[i]["pos"][0] + enemy_width // 2 and
                    bullet["y"] > enemies[i]["pos"][1] - enemy_height // 2 and bullet["y"] < enemies[i]["pos"][1] + enemy_height // 2):
                    bullets.remove(bullet)
                    enemies[i]["health"] -= 25  # Arrow reduces health by 25
                    if enemies[i]["health"] <= 0:
                        enemies.pop(i)
                        score += 10
                        money += 20

        # Draw everything
        draw_base()
        draw_paths()
        draw_towers()
        draw_fire_beams()
        draw_enemies()
        draw_bullets()
        show_score_and_money()

        # Game over condition
        if base_health <= 0:
            game_over_text = font.render("Game Over!", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(30)

# Quit pygame
pygame.quit()
sys.exit()
