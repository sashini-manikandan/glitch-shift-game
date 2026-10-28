
import pygame
import random
import math

pygame.init()

# ---------- SETUP ----------
W, H = 900, 650
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("GLITCH // SHIFT")
clock = pygame.time.Clock()

BG = (7, 10, 25)
CYAN = (45, 245, 255)
PURPLE = (180, 80, 255)
PINK = (255, 65, 155)
WHITE = (235, 245, 255)

font = pygame.font.SysFont("consolas", 22, bold=True)
big_font = pygame.font.SysFont("consolas", 52, bold=True)

def text(msg, x, y, color=WHITE, font_obj=font):
    img = font_obj.render(msg, True, color)
    screen.blit(img, (x, y))

def glow(pos, radius, color):
    x, y = int(pos[0]), int(pos[1])
    for r, alpha in [(radius * 2.5, 18),
                     (radius * 1.7, 35)]:
        layer = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.circle(
            layer, (*color, alpha), (x, y), int(r)
        )
        screen.blit(layer, (0, 0))
    pygame.draw.circle(screen, color, (x, y), radius)

def new_shard():
    return pygame.Vector2(
        random.randint(35, W - 35),
        random.randint(90, H - 35)
    )

def reset():
    global player, hunter, shards, particles
    global score, lives, start_time, last_glitch
    global glitch, dash_ready, game_over

    player = pygame.Vector2(W / 2, H / 2)
    hunter = pygame.Vector2(100, 100)
    shards = [new_shard() for _ in range(7)]
    particles = []
    score = 0
    lives = 3
    start_time = pygame.time.get_ticks()
    last_glitch = 0
    glitch = "NORMAL"
    dash_ready = 0
    game_over = False

reset()
running = True

# ---------- MAIN LOOP ----------
while running:
    dt = min(clock.tick(60) / 1000, 0.03)
    now = pygame.time.get_ticks() / 1000
    elapsed = now - start_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if game_over and event.key == pygame.K_r:
                reset()

            if (not game_over and event.key == pygame.K_SPACE
                    and now >= dash_ready):
                keys = pygame.key.get_pressed()
                direction = pygame.Vector2(
                    keys[pygame.K_d] - keys[pygame.K_a],
                    keys[pygame.K_s] - keys[pygame.K_w]
                )
                if direction.length_squared() == 0:
                    direction = player - hunter
                if direction.length_squared():
                    player += direction.normalize() * 95
                player.x = max(15, min(W - 15, player.x))
                player.y = max(75, min(H - 15, player.y))
                dash_ready = now + 2.0

    if not game_over:
        # Change the rules every 10 seconds
        if now - last_glitch >= 10:
            last_glitch = now
            glitch = random.choice([
                "REVERSED", "SPEED SURGE", "LOW GRAVITY", "NORMAL"
            ])

        keys = pygame.key.get_pressed()
        move = pygame.Vector2(
            keys[pygame.K_d] - keys[pygame.K_a],
            keys[pygame.K_s] - keys[pygame.K_w]
        )

        if glitch == "REVERSED":
            move *= -1

        speed = 235
        if glitch == "SPEED SURGE":
            speed = 340
        if glitch == "LOW GRAVITY":
            speed = 150

        if move.length_squared():
            player += move.normalize() * speed * dt

        player.x = max(15, min(W - 15, player.x))
        player.y = max(75, min(H - 15, player.y))

        # Hunter learns by becoming faster over time
        direction = player - hunter
        if direction.length_squared():
            hunter += direction.normalize() * min(
                105 + score * 1.5 + elapsed * 0.8, 210
            ) * dt

        # Collect energy
        for shard in shards[:]:
            if player.distance_to(shard) < 24:
                shards.remove(shard)
                score += 10

                for _ in range(15):
                    particles.append([
                        list(shard),
                        [random.uniform(-150, 150),
                         random.uniform(-150, 150)],
                        0.5
                    ])

        while len(shards) < 7:
            shards.append(new_shard())

        # Hunter collision
        if player.distance_to(hunter) < 27:
            lives -= 1
            hunter = pygame.Vector2(
                random.choice([40, W - 40]),
                random.choice([90, H - 40])
            )
            player = pygame.Vector2(W / 2, H / 2)

            if lives <= 0:
                game_over = True

        # Particle effects
        for p in particles[:]:
            p[0][0] += p[1][0] * dt
            p[0][1] += p[1][1] * dt
            p[2] -= dt
            if p[2] <= 0:
                particles.remove(p)

    # ---------- DRAW WORLD ----------
    screen.fill(BG)

    # Animated grid
    offset = int(now * 12) % 40
    for x in range(-40 + offset, W, 40):
        pygame.draw.line(screen, (17, 29, 52),
                         (x, 70), (x, H))
    for y in range(70, H, 40):
        pygame.draw.line(screen, (17, 29, 52),
                         (0, y), (W, y))

    pygame.draw.line(screen, PURPLE, (0, 65), (W, 65), 2)

    text("GLITCH // SHIFT", 20, 20, CYAN)
    text(f"SCORE {score:04}", 350, 20)
    text(f"LIVES {'♥ ' * lives}", 650, 20, PINK)
    text(f"GLITCH: {glitch}", 20, 80, PURPLE)
    text("WASD: MOVE   SPACE: DASH   ESC: EXIT",
         20, H - 30, (130, 160, 195))

    # Energy shards
    for shard in shards:
        pulse = 9 + int(3 * math.sin(now * 5 + shard.x))
        glow(shard, pulse, CYAN)
        pygame.draw.circle(screen, WHITE,
                           (int(shard.x), int(shard.y)), 3)

    # Hunter
    glow(hunter, 13, PINK)
    pygame.draw.circle(screen, PINK,
                       (int(hunter.x), int(hunter.y)), 12, 2)

    # Player
    glow(player, 11, PURPLE)
    pygame.draw.circle(screen, WHITE,
                       (int(player.x), int(player.y)), 9)
    pygame.draw.circle(screen, CYAN,
                       (int(player.x), int(player.y)), 15, 2)

    # Particles
    for p in particles:
        pygame.draw.circle(
            screen, CYAN,
            (int(p[0][0]), int(p[0][1])),
            max(1, int(p[2] * 5))
        )

    if now < dash_ready and not game_over:
        text(f"DASH RECHARGING: {dash_ready - now:.1f}s",
             W - 290, 80, (140, 160, 190))
    elif not game_over:
        text("DASH READY", W - 190, 80, CYAN)

    if game_over:
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((3, 5, 18, 210))
        screen.blit(overlay, (0, 0))

        title = big_font.render("SYSTEM CRASHED", True, PINK)
        screen.blit(title, title.get_rect(center=(W/2, H/2 - 55)))
        text(f"FINAL SCORE: {score}",
             W//2 - 100, H//2 + 5, CYAN)
        text("PRESS R TO REBOOT",
             W//2 - 125, H//2 + 55)

    pygame.display.flip()

pygame.quit()
