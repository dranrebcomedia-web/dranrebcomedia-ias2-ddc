import pygame
import random
import sys
import json
import math

pygame.init()

# -------------------
# SCREEN
# -------------------
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minecraft Dino Runner - Safe Version")

clock = pygame.time.Clock()
FPS = 60

# -------------------
# COLORS
# -------------------
SKY_TOP = (175, 205, 220)
SKY_BOTTOM = (225, 230, 235)

GRASS = (90, 140, 90)
DIRT = (110, 85, 60)

BLACK = (30, 30, 30)
RED = (170, 60, 60)

# -------------------
# BACKGROUND IMAGE (sakura)
# -------------------
background_img = None
try:
    _bg = pygame.image.load("assets/background/sakura.png").convert()
    background_img = pygame.transform.scale(_bg, (WIDTH, HEIGHT))
except Exception:
    background_img = None

# -------------------
# PLAYER
# -------------------
player_img = pygame.image.load("assets/player/minecraft.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (70, 70))

PLAYER_W, PLAYER_H = 70, 70

player = pygame.Rect(120, 420, PLAYER_W, PLAYER_H)

velocity_y = 0
gravity = 1
on_ground = True

# jump control
jump_hold = 0
max_jump_hold = 11
jump_power = -16

# -------------------
# CACTUS OBSTACLE
# -------------------
cactus_img = pygame.image.load("assets/obstacles/cactus.png").convert_alpha()
ender_img = pygame.image.load("assets/obstacles/ender.png").convert_alpha()
# We'll scale the cactus per-obstacle so the same source image can be reused.
# Keep them visually larger than the original but not so tall they block reasonable jumps.
CACTUS_W = 60
CACTUS_H_BIG = 100
CACTUS_H_SMALL = 60
CACTUS_H_LOW = 40
DRAGON_W = 120
DRAGON_H = 45
DRAGON_SPEED_MULTIPLIER = 1.0
DRAGON_BASE_Y = 320
DRAGON_FLOAT_AMPLITUDE = 6

obstacles = []
obstacle_timer = 0
game_speed = 7

# -------------------
# SCORE
# -------------------
score = 0
font = pygame.font.SysFont(None, 40)

game_over = False
high_score = 0

def load_high_score():
    global high_score
    try:
        with open("save.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            high_score = int(data.get("highscore", 0))
    except Exception:
        high_score = 0


def save_high_score():
    try:
        with open("save.json", "w", encoding="utf-8") as f:
            json.dump({"highscore": high_score}, f)
    except Exception:
        pass

load_high_score()


def reset():
    global player, velocity_y, on_ground, obstacles, score, game_speed, game_over, jump_hold

    player.x = 120
    player.y = 420
    player.height = PLAYER_H

    velocity_y = 0
    on_ground = True
    jump_hold = 0

    obstacles = []
    score = 0
    game_speed = 7
    game_over = False

# -------------------
# SKY
# -------------------
def draw_sky():
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(SKY_TOP[0] * (1 - t) + SKY_BOTTOM[0] * t)
        g = int(SKY_TOP[1] * (1 - t) + SKY_BOTTOM[1] * t)
        b = int(SKY_TOP[2] * (1 - t) + SKY_BOTTOM[2] * t)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

# Mountains removed per user request

# -------------------
# FOG
# -------------------
def draw_fog():
    fog = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fog.fill((200, 200, 200, 25))
    screen.blit(fog, (0, 0))

# -------------------
# GAME LOOP
# -------------------
running = True

while running:

    clock.tick(FPS)

    keys = pygame.key.get_pressed()

    # -------------------
    # EVENTS
    # -------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if not game_over:
                if event.key == pygame.K_SPACE and on_ground:
                    velocity_y = jump_power
                    on_ground = False
                    jump_hold = 0

            if game_over and event.key == pygame.K_r:
                reset()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                jump_hold = max_jump_hold

    # -------------------
    # GAME LOGIC
    # -------------------
    if not game_over:

        # variable jump (hold space)
        if keys[pygame.K_SPACE] and not on_ground:
            if jump_hold < max_jump_hold:
                velocity_y -= 0.7
                jump_hold += 1

        # gravity
        velocity_y += gravity
        player.y += velocity_y

        if player.y >= 420:
            player.y = 420
            velocity_y = 0
            on_ground = True

        # -------------------
        # FAIR CACTUS OBSTACLES (DINO STYLE)
        # -------------------
        obstacle_timer += 1
        obstacle_bottom = 500

        if obstacle_timer > random.randint(60, 95):

            t = random.choices(
                ["single", "double", "low", "dragon"],
                weights=[4, 2, 3, 1],
                k=1,
            )[0]

            if t == "single":
                h = CACTUS_H_BIG
                y = obstacle_bottom - h
                obstacles.append({"rect": pygame.Rect(1000, y, CACTUS_W, h), "type": "cactus"})

            elif t == "double":
                h = CACTUS_H_BIG
                y = obstacle_bottom - h
                obstacles.append({"rect": pygame.Rect(1000, y, CACTUS_W, h), "type": "cactus"})
                obstacles.append({"rect": pygame.Rect(1045, y, CACTUS_W, h), "type": "cactus"})

            elif t == "low":
                h = CACTUS_H_LOW
                low_obstacle_bottom = 480
                y = low_obstacle_bottom - h
                obstacles.append({"rect": pygame.Rect(1000, y, CACTUS_W, h), "type": "cactus"})

            elif t == "dragon":
                y = DRAGON_BASE_Y
                rect = pygame.Rect(1000, y, DRAGON_W, DRAGON_H)
                obstacles.append({
                    "rect": rect,
                    "type": "dragon",
                    "base_y": y,
                    "phase": 0.0,
                })

            obstacle_timer = 0

        # move obstacles
        for o in obstacles:
            if o["type"] == "dragon":
                o["phase"] += 0.08
                o["rect"].y = o["base_y"] + int(math.sin(o["phase"]) * DRAGON_FLOAT_AMPLITUDE)
                o["rect"].x -= int(game_speed * DRAGON_SPEED_MULTIPLIER)
            else:
                o["rect"].x -= game_speed

        obstacles = [o for o in obstacles if o["rect"].x > -200]

        # collision
        for o in obstacles:
            if player.colliderect(o["rect"]):
                game_over = True
                if score > high_score:
                    high_score = score
                    save_high_score()

        # difficulty
        score += 1
        game_speed += 0.0012
        if game_speed > 12:
            game_speed = 12

    # -------------------
    # DRAW WORLD
    # -------------------
    # Use the sakura background image when available, otherwise draw the gradient sky.
    if background_img:
        screen.blit(background_img, (0, 0))
    else:
        draw_sky()
    draw_fog()

    # ground
    for x in range(0, WIDTH, 40):
        pygame.draw.rect(screen, GRASS, (x, 460, 40, 40))
        pygame.draw.rect(screen, DIRT, (x, 500, 40, 40))
        pygame.draw.rect(screen, DIRT, (x, 540, 40, 40))

    # player
    screen.blit(player_img, player)

    # obstacles
    for o in obstacles:
        if o["type"] == "dragon":
            img = pygame.transform.scale(ender_img, (DRAGON_W, DRAGON_H))
            screen.blit(img, o["rect"])
        else:
            img = pygame.transform.scale(cactus_img, (o["rect"].width, o["rect"].height))
            screen.blit(img, o["rect"])

    # score
    text = font.render(f"Score: {score}   High Score: {high_score}", True, BLACK)
    screen.blit(text, (20, 20))

    # game over
    if game_over:
        msg = font.render("GAME OVER - Press R", True, RED)
        screen.blit(msg, (330, 250))

    pygame.display.update()

pygame.quit()
sys.exit()