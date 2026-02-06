import pygame
import math

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
speed = 7          # faster movement
jump_power = 12
gravity = 0.5
on_ground = False

# VERY LONG FLOOR (world space)
ground_rect = pygame.Rect(0, HEIGHT - 50, 10000, 50)

# Blocks
block = pygame.Rect(300, HEIGHT - 100, 100, mario_height)
block2 = pygame.Rect(600, 400, 100, 150)

# Quicksand
quicksand = pygame.Rect(500, 450, 100, 100)

solids = (ground_rect, block, quicksand, block2)

# Camera
camera_x = 0
camera_y = 0

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

    for _ in range(pixels):
        mario_y += direction
        mario_rect.topleft = (mario_x, mario_y)

        for solid in solids:
            if mario_rect.colliderect(solid):
                mario_y -= direction
                mario_vel_y = 0
                on_ground = True
                mario_rect.topleft = (mario_x, mario_y)
                break
        if on_ground:
            break

    # ---------- CAMERA FOLLOW ----------
    camera_x = mario_x - math.floor(WIDTH / 2)
    camera_y = 0  # keep vertical locked (Mario-style)

    # ---------- DRAW ----------
    screen.fill(SKY_BLUE)

    #Draw based on camera
    """
    Since World is not moving and only camera, we only see blocks in terms of camera.
    Thus: World position − Camera position = Screen position
    
    Test with this:
    print(mario_x, block.x)

    See how this logic works
    """

    pygame.draw.rect(
        screen, GREEN,
        (ground_rect.x - camera_x, ground_rect.y - camera_y,
         ground_rect.width, ground_rect.height)
    )

    #-----DRAWING SOLIDS-------

    #Cant draw these individually because each is cannot have the same color

    pygame.draw.rect(screen, BLACK,(block.x - camera_x, block.y - camera_y, block.width, block.height))
    pygame.draw.rect(screen, BLACK,(block2.x - camera_x, block2.y - camera_y, block2.width, block2.height))
    pygame.draw.rect(screen, SAND,(quicksand.x - camera_x, quicksand.y - camera_y, quicksand.width, quicksand.height))

    pygame.draw.rect(screen, RED,(mario_x - camera_x, mario_y - camera_y, mario_width, mario_height))

    pygame.display.flip()

pygame.quit()
