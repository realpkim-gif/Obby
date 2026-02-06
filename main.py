import pygame
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
SAND = (194, 178, 128)

# Mario
mario_width = 40
mario_height = 50
mario_x = 100
mario_y = HEIGHT - mario_height - 50
mario_vel_x = 0
mario_vel_y = 0
speed = 5
jump_power = 12
gravity = 0.5
on_ground = False

# Ground
ground_rect = pygame.Rect(0, HEIGHT - 50, WIDTH, 50)

# Block (Mario height)
block = pygame.Rect(300, HEIGHT - 100, 100, mario_height)

# Quicksand
quicksand = pygame.Rect(500, 450, 100, 100)

block2 = pygame.Rect(600, 400, 100, 150)

solids = (ground_rect, block, quicksand, block2)

running = True
while running:
    clock.tick(120)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    mario_vel_x = 0

    if keys[pygame.K_LEFT]:
        mario_vel_x = -speed
    if keys[pygame.K_RIGHT]:
        mario_vel_x = speed
    if keys[pygame.K_SPACE] and on_ground:
        mario_vel_y = -jump_power

    # Save previous pos
    prev_mario_x = mario_x
    prev_mario_y = mario_y

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


    # ---------- VERTICAL----------
    mario_vel_y += gravity
    on_ground = False

    direction = 0
    if mario_vel_y > 0:
        direction = 1
    else:
        direction=-1

    pixels = abs(int(mario_vel_y))

    #calculating gravity
    for i in range(pixels):
        mario_y += direction*gravity

        #update position
        mario_rect.topleft = (mario_x, mario_y)

        #quitting gravity once in collision with solid
        for solid in solids:
            if mario_rect.colliderect(solid):
                #keep mario one pixel up
                mario_y -= 1
                #QUIT GRAVITY HERE:
                mario_vel_y = 0
                on_ground = True
                #update pos
                mario_rect.topleft = (mario_x, mario_y)
                break
        if on_ground:
            break

    # ---------- DRAW ----------
    screen.fill(SKY_BLUE)

    pygame.draw.rect(screen, GREEN, ground_rect)
    pygame.draw.rect(screen, BLACK, block)
    pygame.draw.rect(screen, SAND, quicksand)
    pygame.draw.rect(screen, BLACK, block2)

    pygame.draw.rect(screen, RED, mario_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
