import pygame
import math

ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# lazer settings
LASER_W = 10
LASER_H = 30
laser_speed = 3
laser_life_frames = 220
cooldown_ms = 650
last_shot_time = 0
Lazer_color = ORANGE

#mob settings
Mob_color = PURPLE

class LaserMob:
    def __init__(self, x, y, w=40, h=50, speed=2, patrol_min_x=None, patrol_max_x=None):
        self.rect = pygame.Rect(x, y, w, h)

        self.speed = speed
        self.vx = speed

        if patrol_min_x is None:
            self.patrol_min_x = x - 200
        else:
            self.patrol_min_x = patrol_min_x

        if patrol_max_x is None:
            self.patrol_max_x = x + 200
        else:
            self.patrol_max_x = patrol_max_x

        self.locked_y = y

        self.lasers = []  # [x, y, vx, vy, life]
        self.laser_speed = laser_speed
        self.laser_life_frames = laser_life_frames
        self.cooldown_ms = cooldown_ms
        self.last_shot_time = last_shot_time

    def _in_camera(self, camera_x, width):
        # Horizontal-only camera in your game
        return (self.rect.right > camera_x) and (self.rect.left < camera_x + width)

    def _apply_horizontal(self, solids):
        #moving side to side
        self.rect.x += self.vx

        #solids collision
        for solid in solids:
            if self.rect.colliderect(solid):
                #stop when right collision with objects (vx is positive)
                if self.vx > 0:
                    self.rect.right = solid.left
                #stop when left colision with objets (vx is negative)
                else:
                    self.rect.left = solid.right
                self.vx *= -1
                break

        #keep mobs within every platform
        if self.rect.left <= self.patrol_min_x:
            self.rect.left = self.patrol_min_x
            self.vx = abs(self.speed)
        elif self.rect.right >= self.patrol_max_x:
            self.rect.right = self.patrol_max_x
            self.vx = -abs(self.speed)

    def _edge_turnaround(self, solids):
        if self.vx > 0:
            probe_x = self.rect.right + 6
        else:
            probe_x = self.rect.left - 6

        probe = pygame.Rect(probe_x, self.rect.bottom + 2, 6, 6)

        for solid in solids:
            if probe.colliderect(solid):
                return

        self.vx *= -1

    def _lock_to_floor(self, solids):
        # Small probe directly under the mob
        foot_probe = pygame.Rect(self.rect.centerx, self.rect.bottom + 1, 2, 6)

        floor = None
        floor_top = None

        for solid in solids:
            if foot_probe.colliderect(solid):
                if floor_top is None or solid.top < floor_top:
                    floor = solid
                    floor_top = solid.top

        if floor is not None:
            self.rect.bottom = floor.top
            self.locked_y = self.rect.y
        else:
            self.rect.y = self.locked_y

    def _shoot_if_visible(self, player_rect, camera_x, width):
        if not self._in_camera(camera_x, width):
            return

        now = pygame.time.get_ticks()
        if now - self.last_shot_time < self.cooldown_ms:
            return

        self.last_shot_time = now

        mob_x, mob_y = self.rect.centerx, self.rect.centery
        player_x, player_y = player_rect.centerx, player_rect.centery

        delta_x = player_x - mob_x
        delta_y = player_y - mob_y

        distance = math.hypot(delta_x, delta_y) or 1

        vx = (delta_x / distance) * self.laser_speed
        vy = (delta_y / distance) * self.laser_speed

        self.lasers.append([float(mob_x), float(mob_y), float(vx), float(vy), self.laser_life_frames])

    def _update_lasers(self, solids, player_rect):
        hit_player = False

        for laser in self.lasers[:]:
            laser[0] += laser[2]
            laser[1] += laser[3]
            laser[4] -= 1

            laser_rect = pygame.Rect(
                int(laser[0]) - LASER_W // 2,
                int(laser[1]) - LASER_H // 2,
                LASER_W,
                LASER_H
            )
            if laser_rect.colliderect(player_rect):
                hit_player = True

            for solid in solids:
                if laser_rect.colliderect(solid):
                    self.lasers.remove(laser)
                    break
            else:
                if laser[4] <= 0:
                    self.lasers.remove(laser)

        return hit_player

    def update(self, solids, player_rect, camera_x, width):
        self._lock_to_floor(solids)
        self._apply_horizontal(solids)
        self._edge_turnaround(solids)
        self._lock_to_floor(solids)

        self._shoot_if_visible(player_rect, camera_x, width)

        return self._update_lasers(solids, player_rect)

    def draw(self, screen, camera_x, mob_color=Mob_color, laser_color=Lazer_color):
        pygame.draw.rect(
            screen, mob_color,
            (self.rect.x - camera_x, self.rect.y, self.rect.w, self.rect.h)
        )

        for laser in self.lasers:
            pygame.draw.rect(
                screen, laser_color,
                (
                    int(laser[0]) - LASER_W // 2 - camera_x,
                    int(laser[1]) - LASER_H // 2,
                    LASER_W,
                    LASER_H
                )
            )

