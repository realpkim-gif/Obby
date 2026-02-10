import pygame
import math
from Lazer_mob import LaserMob
import os
import sys


pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Colors
SKY_BLUE = (135, 206, 235)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)

# Mario
mario_width = 40
mario_height = 50
mario_x = 100
mario_y = HEIGHT - mario_height - 50
mario_vel_x = 0
mario_vel_y = 0
speed = 4
jump_power = 12
gravity = 0.5
on_ground = False
facing = 1


# ---------------- WORLD 1 ----------------
# (Rectangles)  -- ONLY CHANGED/EXTENDED THIS SECTION

# Original segments
ground_rect = pygame.Rect(0, HEIGHT - 50, 420, 50)
ground_rect2 = pygame.Rect(580, HEIGHT - 50, 520, 50)

block = pygame.Rect(720, HEIGHT - 140, 120, 30)
block2 = pygame.Rect(900, HEIGHT - 220, 120, 30)
block3 = pygame.Rect(1040, HEIGHT - 160, 120, 30)

ground_rect3 = pygame.Rect(1260, HEIGHT - 50, 620, 50)

block4 = pygame.Rect(1340, HEIGHT - 170, 140, 30)
block5 = pygame.Rect(1520, HEIGHT - 250, 160, 30)
block6 = pygame.Rect(1740, HEIGHT - 200, 140, 30)

ground_rect4 = pygame.Rect(2040, HEIGHT - 50, 520, 50)

block7 = pygame.Rect(2190, HEIGHT - 150, 220, 30)

ground_rect5 = pygame.Rect(2740, HEIGHT - 50, 760, 50)
block8 = pygame.Rect(2920, HEIGHT - 140, 120, 30)
block9 = pygame.Rect(3100, HEIGHT - 200, 140, 30)

# -------- EXTENSION (substantially longer world) --------
# more floor segments with gaps (death pits) + more platforms

ground_rect6 = pygame.Rect(3600, HEIGHT - 50, 700, 50)  # gap from 3500 to 3600
block10 = pygame.Rect(3720, HEIGHT - 160, 140, 30)
block11 = pygame.Rect(3920, HEIGHT - 230, 160, 30)
block12 = pygame.Rect(4140, HEIGHT - 180, 140, 30)

ground_rect7 = pygame.Rect(4500, HEIGHT - 50, 620, 50)  # gap from 4300 to 4500
block13 = pygame.Rect(4580, HEIGHT - 140, 120, 30)
block14 = pygame.Rect(4760, HEIGHT - 210, 140, 30)
block15 = pygame.Rect(4960, HEIGHT - 260, 160, 30)

ground_rect8 = pygame.Rect(5320, HEIGHT - 50, 680, 50)  # continues (5120 to 5320 is the gap)
block16 = pygame.Rect(5450, HEIGHT - 170, 150, 30)
block17 = pygame.Rect(5660, HEIGHT - 240, 160, 30)
block18 = pygame.Rect(5900, HEIGHT - 190, 140, 30)

ground_rect9 = pygame.Rect(6200, HEIGHT - 50, 760, 50)  # gap from 6000 to 6200
block19 = pygame.Rect(6320, HEIGHT - 140, 120, 30)
block20 = pygame.Rect(6520, HEIGHT - 200, 140, 30)
block21 = pygame.Rect(6740, HEIGHT - 260, 160, 30)
block22 = pygame.Rect(6960, HEIGHT - 200, 140, 30)

ground_rect10 = pygame.Rect(7200, HEIGHT - 50, 900, 50)  # small gap from 6960 to 7200
block23 = pygame.Rect(7420, HEIGHT - 160, 140, 30)
block24 = pygame.Rect(7640, HEIGHT - 230, 160, 30)
block25 = pygame.Rect(7900, HEIGHT - 180, 140, 30)

ground_rect11 = pygame.Rect(8200, HEIGHT - 50, 1100, 50)  # gap from 8100 to 8200, long end run
block26 = pygame.Rect(8500, HEIGHT - 140, 120, 30)
block27 = pygame.Rect(8720, HEIGHT - 200, 140, 30)
block28 = pygame.Rect(8960, HEIGHT - 260, 160, 30)

# Solids tuple (extended)
solids = (
    ground_rect, ground_rect2, ground_rect3, ground_rect4, ground_rect5,
    ground_rect6, ground_rect7, ground_rect8, ground_rect9, ground_rect10, ground_rect11,
    block, block2, block3, block4, block5, block6, block7, block8, block9,
    block10, block11, block12, block13, block14, block15, block16, block17, block18,
    block19, block20, block21, block22, block23, block24, block25, block26, block27, block28
)

# ---------- SPAWN LASER MOBS ON EVERY GROUND PLATFORM ----------
MOB_W, MOB_H = 38, 46

ground_platforms = (
    ground_rect3, ground_rect4, ground_rect5,
    ground_rect6, ground_rect7, ground_rect8, ground_rect9, ground_rect10, ground_rect11
)

mobs = []
# adding how many mobs there are (1 per platform, except the first two)
for i, gr in enumerate(ground_platforms):
    spawn_x = gr.x + gr.w // 2 - MOB_W // 2
    spawn_y = gr.top - MOB_H
    patrol_min = gr.left
    patrol_max = gr.right

    mobs.append(LaserMob(
        spawn_x, spawn_y,
        w=MOB_W, h=MOB_H,
        speed=2,
        patrol_min_x=patrol_min,
        patrol_max_x=patrol_max,
    ))

    # print(ground_platforms)

# fireball shooting mechanism
last_shot_time = 0
cooldown_ms = 650
shot_cooldown_ms = 360
last_shot_time_ms = 0
fireball_width = 10
fireball_height = 10
fireballs = []
FIREBALL_SPEED = 10

# Gamestate
gamestate = True


class Fireball:
    def __init__(self, x, y, dir=1):
        self.rect = pygame.Rect(x, y, fireball_width, fireball_height)
        self.dir = dir

    def update(self):
        self.rect.x += FIREBALL_SPEED * self.dir

    def draw(self, screen, camera_x):
        pygame.draw.rect(
            screen,
            ORANGE,
            (self.rect.x - camera_x, self.rect.y, self.rect.w, self.rect.h)
        )


large_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 36)
deathtime=0

def draw_game_over(screen, final_time_ms, WIDTH, HEIGHT):
    # Fill entire screen with black
    screen.fill(BLACK)

    # Calculate final time
    final_seconds = round(deathtime / 1000, 2)

    # GAME OVER text
    game_over_text = large_font.render("GAME OVER", True, (255, 0, 0))
    go_x = WIDTH // 2 - game_over_text.get_width() // 2
    go_y = HEIGHT // 3
    screen.blit(game_over_text, (go_x, go_y))

    # Time survived
    time_text = small_font.render(f"Time: {final_seconds}s", True, (255, 255, 255))
    time_x = WIDTH // 2 - time_text.get_width() // 2
    time_y = go_y + 100
    screen.blit(time_text, (time_x, time_y))

    # Restart
    restart_text = small_font.render("Press R to Restart", True, (200, 200, 200))
    restart_x = WIDTH // 2 - restart_text.get_width() // 2
    restart_y = time_y + 60
    screen.blit(restart_text, (restart_x, restart_y))

    pygame.display.flip()


# Camera
camera_x = 0
camera_y = 0

start_time = 0

running = True

while running:
    clock.tick(120)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # RESTART FUNCTIONALITY
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and gamestate==False:
            """
            Copy all initializing code here
            """

            # Reset game
            mario_x = 100
            mario_y = HEIGHT - mario_height - 50
            mario_vel_x = 0
            mario_vel_y = 0
            gamestate = True
            start_time = pygame.time.get_ticks()
            fireballs.clear()
            facing=1
            deathtime=0

            # Respawn mobs
            mobs.clear()
            for gr in ground_platforms:
                spawn_x = gr.x + gr.w // 2 - MOB_W // 2
                spawn_y = gr.top - MOB_H
                mobs.append(LaserMob(
                    spawn_x, spawn_y,
                    w=MOB_W, h=MOB_H,
                    speed=2,
                    patrol_min_x=gr.left,
                    patrol_max_x=gr.right,
                ))

    keys = pygame.key.get_pressed()
    mario_vel_x = 0

    if keys[pygame.K_a]:
        mario_vel_x = -speed
        facing = -1
    if keys[pygame.K_d]:
        mario_vel_x = speed
        facing = 1
    if keys[pygame.K_w] and on_ground:
        mario_vel_y = -jump_power

    if gamestate == True:
        current_time = pygame.time.get_ticks() - start_time
        #print(start_time, current_time)
    else:
        current_time = 0


    if keys[pygame.K_SPACE] and current_time - last_shot_time >= shot_cooldown_ms:
        if facing == 1:
            spawn_x = mario_x + mario_width
        else:
            # fireball x pixels wide
            spawn_x = mario_x - fireball_width

        fb = Fireball(
            spawn_x,
            mario_y + mario_height // 2 - 5,
            dir=facing
        )
        fireballs.append(fb)
        last_shot_time = current_time

    # colliding with mobs
    for fb in fireballs[:]:
        if fb.rect.x < camera_x + 100 or fb.rect.x > camera_x + WIDTH - 100:
            fireballs.remove(fb)
            continue
        for mob in mobs[:]:
            if fb.rect.colliderect(mob.rect):
                fireballs.remove(fb)
                mobs.remove(mob)
                break  # fireball is gone, stop checking mobs

    # ---------- HORIZONTAL ----------
    mario_x += mario_vel_x
    mario_rect = pygame.Rect(mario_x, mario_y, mario_width, mario_height)

    for solid in solids:
        if mario_rect.colliderect(solid):
            if mario_vel_x > 0:
                mario_x = solid.left - mario_width
            elif mario_vel_x < 0:
                mario_x = solid.right
            mario_rect.topleft = (mario_x, mario_y)

    # ---------- VERTICAL ----------
    mario_vel_y += gravity
    on_ground = False

    direction = 1 if mario_vel_y > 0 else -1
    pixels = abs(int(mario_vel_y))

    for i in range(pixels):
        mario_y += direction
        mario_rect.topleft = (mario_x, mario_y)

        for solid in solids:
            if mario_rect.colliderect(solid):
                mario_y -= direction
                mario_rect.topleft = (mario_x, mario_y)

                if direction == 1:
                    mario_vel_y = 0
                    on_ground = True

                else:
                    mario_vel_y = 0
                    on_ground = False
                break

        if on_ground:
            break

    # ---------- DEATH PIT / FALL DEATH ----------
    if mario_y > HEIGHT + 100:
        deathtime += current_time
        gamestate = False
        draw_game_over(screen, current_time, WIDTH, HEIGHT)

    # ---------- CAMERA FOLLOW ----------
    camera_x = mario_x - math.floor(WIDTH / 2)
    camera_y = 0

    # ---------- UPDATE MOBS (BEFORE DRAW) ----------
    for mob in mobs:
        hit = mob.update(solids, mario_rect, camera_x, WIDTH)
        if hit:
            deathtime += current_time
            gamestate = False
            draw_game_over(screen, current_time, WIDTH, HEIGHT)

    # ---------- UPDATE FIREBALLS ----------
    for fb in fireballs[:]:
        fb.update()
        # remove if too far off screen

    # ============ FIX: SKIP DRAWING IF GAME OVER ============
    if gamestate == False:
        continue  # Skip all the drawing below and go to next frame
    # ---------- DRAW ----------
    else:
        screen.fill(SKY_BLUE)

    if gamestate == True:

        # Grounds (draw all)
        pygame.draw.rect(screen, GREEN, (mario_x - (camera_x + 390), 10, 230, 30))
        timer_surface = small_font.render(
            f"Time: {round(current_time / 1000, 2)} seconds",
            True,
            (0, 0, 0)
        )
        screen.blit(timer_surface, (mario_x - (camera_x + 390), 10))

        pygame.draw.rect(screen, GREEN,
                         (ground_rect.x - camera_x, ground_rect.y, ground_rect.width, ground_rect.height))
        pygame.draw.rect(screen, GREEN,
                         (ground_rect2.x - camera_x, ground_rect2.y, ground_rect2.width, ground_rect2.height))
        pygame.draw.rect(screen, GREEN,
                         (ground_rect3.x - camera_x, ground_rect3.y, ground_rect3.width, ground_rect3.height))
        pygame.draw.rect(screen, GREEN,
                         (ground_rect4.x - camera_x, ground_rect4.y, ground_rect4.width, ground_rect4.height))
        pygame.draw.rect(screen, GREEN,
                         (ground_rect5.x - camera_x, ground_rect5.y, ground_rect5.width, ground_rect5.height))
        pygame.draw.rect(screen, GREEN,
                         (ground_rect6.x - camera_x, ground_rect6.y, ground_rect6.width, ground_rect6.height))
        pygame.draw.rect(screen, GREEN,
                         (ground_rect7.x - camera_x, ground_rect7.y, ground_rect7.width, ground_rect7.height))
        pygame.draw.rect(screen, GREEN,
                         (ground_rect8.x - camera_x, ground_rect8.y, ground_rect8.width, ground_rect8.height))
        pygame.draw.rect(screen, GREEN,
                         (ground_rect9.x - camera_x, ground_rect9.y, ground_rect9.width, ground_rect9.height))
        pygame.draw.rect(screen, GREEN,
                         (ground_rect10.x - camera_x, ground_rect10.y, ground_rect10.width, ground_rect10.height))
        pygame.draw.rect(screen, GREEN,
                         (ground_rect11.x - camera_x, ground_rect11.y, ground_rect11.width, ground_rect11.height))

        # Platforms (draw all)
        pygame.draw.rect(screen, BLACK, (block.x - camera_x, block.y, block.width, block.height))
        pygame.draw.rect(screen, BLACK, (block2.x - camera_x, block2.y, block2.width, block2.height))
        pygame.draw.rect(screen, BLACK, (block3.x - camera_x, block3.y, block3.width, block3.height))
        pygame.draw.rect(screen, BLACK, (block4.x - camera_x, block4.y, block4.width, block4.height))
        pygame.draw.rect(screen, BLACK, (block5.x - camera_x, block5.y, block5.width, block5.height))
        pygame.draw.rect(screen, BLACK, (block6.x - camera_x, block6.y, block6.width, block6.height))
        pygame.draw.rect(screen, BLACK, (block7.x - camera_x, block7.y, block7.width, block7.height))
        pygame.draw.rect(screen, BLACK, (block8.x - camera_x, block8.y, block8.width, block8.height))
        pygame.draw.rect(screen, BLACK, (block9.x - camera_x, block9.y, block9.width, block9.height))
        pygame.draw.rect(screen, BLACK, (block10.x - camera_x, block10.y, block10.width, block10.height))
        pygame.draw.rect(screen, BLACK, (block11.x - camera_x, block11.y, block11.width, block11.height))
        pygame.draw.rect(screen, BLACK, (block12.x - camera_x, block12.y, block12.width, block12.height))
        pygame.draw.rect(screen, BLACK, (block13.x - camera_x, block13.y, block13.width, block13.height))
        pygame.draw.rect(screen, BLACK, (block14.x - camera_x, block14.y, block14.width, block14.height))
        pygame.draw.rect(screen, BLACK, (block15.x - camera_x, block15.y, block15.width, block15.height))
        pygame.draw.rect(screen, BLACK, (block16.x - camera_x, block16.y, block16.width, block16.height))
        pygame.draw.rect(screen, BLACK, (block17.x - camera_x, block17.y, block17.width, block17.height))
        pygame.draw.rect(screen, BLACK, (block18.x - camera_x, block18.y, block18.width, block18.height))
        pygame.draw.rect(screen, BLACK, (block19.x - camera_x, block19.y, block19.width, block19.height))
        pygame.draw.rect(screen, BLACK, (block20.x - camera_x, block20.y, block20.width, block20.height))
        pygame.draw.rect(screen, BLACK, (block21.x - camera_x, block21.y, block21.width, block21.height))
        pygame.draw.rect(screen, BLACK, (block22.x - camera_x, block22.y, block22.width, block22.height))
        pygame.draw.rect(screen, BLACK, (block23.x - camera_x, block23.y, block23.width, block23.height))
        pygame.draw.rect(screen, BLACK, (block24.x - camera_x, block24.y, block24.width, block24.height))
        pygame.draw.rect(screen, BLACK, (block25.x - camera_x, block25.y, block25.width, block25.height))
        pygame.draw.rect(screen, BLACK, (block26.x - camera_x, block26.y, block26.width, block26.height))
        pygame.draw.rect(screen, BLACK, (block27.x - camera_x, block27.y, block27.width, block27.height))
        pygame.draw.rect(screen, BLACK, (block28.x - camera_x, block28.y, block28.width, block28.height))

        # Draw mobs (after platforms)
        for mob in mobs:
            mob.draw(screen, camera_x)

        # Draw fireballs
        for fb in fireballs:
            fb.draw(screen, camera_x)

    # Mario
    mario = pygame.draw.rect(screen, RED, (mario_x - camera_x, mario_y, mario_width, mario_height))

    pygame.display.flip()

pygame.quit()

