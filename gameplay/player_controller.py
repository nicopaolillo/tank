from __future__ import annotations

import pygame

from config.Settings import (
    PLAYER_SPEED,
    PLAYER_BOUNDS_LEFT,
    PLAYER_BOUNDS_RIGHT,
    HEIGHT,
    MISSILE_FIRE_COOLDOWN,
)
from entities.AirSupport import AirSupport
from entities.Shooting import Shooting


class PlayerController:

    def __init__(self, config, player, all_sprites, shoot_list, apoyo_list):
        self.config = config
        self.player = player
        self.all_sprites = all_sprites
        self.shoot_list = shoot_list
        self.apoyo_list = apoyo_list
        self.last_fire_time = -MISSILE_FIRE_COOLDOWN
        self.min_top_bound = 0
        self._keys = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_UP: False,
            pygame.K_DOWN: False,
        }

    def _get_speed(self) -> int:
        speed = PLAYER_SPEED
        if self.player.tank_track_active:
            speed = int(speed * 1.5)
        return speed

    def set_top_limit(self, min_top: int) -> None:
        self.min_top_bound = max(0, min_top)

    def handle_keydown(self, event: pygame.event.EventType, elapsed_time: float) -> None:
        speed = self._get_speed()
        if event.key == pygame.K_LEFT:
            self._keys[pygame.K_LEFT] = True
            self.player.speed_x = -speed
            self.player.facing = "left"
            self.player.update_sprite()
        elif event.key == pygame.K_RIGHT:
            self._keys[pygame.K_RIGHT] = True
            self.player.speed_x = speed
            self.player.facing = "right"
            self.player.update_sprite()
        elif event.key == pygame.K_UP:
            self._keys[pygame.K_UP] = True
            self.player.speed_y = -speed
            self.player.facing = "up"
            self.player.update_sprite()
        elif event.key == pygame.K_DOWN:
            self._keys[pygame.K_DOWN] = True
            self.player.speed_y = speed
            self.player.facing = "down"
            self.player.update_sprite()
        elif event.key == pygame.K_q and self.player.apoyo > 0:
            self._spawn_support()
        elif event.key == pygame.K_w:
            self.player.activate_shield(elapsed_time)
        elif event.key == pygame.K_SPACE and self.player.misiles > 0:
            self._try_shoot(elapsed_time)

    def handle_keyup(self, event: pygame.event.EventType) -> None:
        speed = self._get_speed()
        if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            self._keys[event.key] = False
            if event.key == pygame.K_LEFT and self._keys[pygame.K_RIGHT]:
                self.player.speed_x = speed
            elif event.key == pygame.K_RIGHT and self._keys[pygame.K_LEFT]:
                self.player.speed_x = -speed
            else:
                self.player.speed_x = 0
        elif event.key in (pygame.K_UP, pygame.K_DOWN):
            self._keys[event.key] = False
            if event.key == pygame.K_UP and self._keys[pygame.K_DOWN]:
                self.player.speed_y = speed
            elif event.key == pygame.K_DOWN and self._keys[pygame.K_UP]:
                self.player.speed_y = -speed
            else:
                self.player.speed_y = 0

    def update(self) -> None:
        self.player.rect.x += self.player.speed_x
        self.player.rect.y += self.player.speed_y

    def clamp_bounds(self) -> None:
        if self.player.rect.right > PLAYER_BOUNDS_RIGHT:
            self.player.rect.right = PLAYER_BOUNDS_RIGHT
        if self.player.rect.left < PLAYER_BOUNDS_LEFT:
            self.player.rect.left = PLAYER_BOUNDS_LEFT
        if self.player.rect.top < self.min_top_bound:
            self.player.rect.top = self.min_top_bound
        if self.player.rect.bottom > HEIGHT:
            self.player.rect.bottom = HEIGHT

    def _spawn_support(self) -> None:
        apoyo = AirSupport()
        apoyo.rect.x = self.player.rect.x + 10
        apoyo.rect.y = HEIGHT
        self.all_sprites.add(apoyo)
        self.apoyo_list.add(apoyo)
        self.player.apoyo -= 1
        self.config.get_sound("plane").play()

    def _try_shoot(self, elapsed_time: float) -> None:
        time_since_last = elapsed_time - self.last_fire_time
        if time_since_last < MISSILE_FIRE_COOLDOWN:
            return

        direction = getattr(self.player, "facing", "up")
        shoot1 = Shooting(direction)

        if direction == "left":
            shoot1.rect.centery = self.player.rect.centery
            shoot1.rect.right = self.player.rect.left - 2
        elif direction == "right":
            shoot1.rect.centery = self.player.rect.centery
            shoot1.rect.left = self.player.rect.right + 2
        elif direction == "down":
            shoot1.rect.centerx = self.player.rect.centerx + 3
            shoot1.rect.top = self.player.rect.bottom - 2
        else:
            shoot1.rect.centerx = self.player.rect.centerx + 3
            shoot1.rect.bottom = self.player.rect.top + 2

        self.all_sprites.add(shoot1)
        self.shoot_list.add(shoot1)

        if self.player.double_barrel_active:
            shoot2 = Shooting(direction)
            offset = 10
            if direction == "left":
                shoot2.rect.centery = self.player.rect.centery + offset
                shoot2.rect.right = self.player.rect.left - 2
            elif direction == "right":
                shoot2.rect.centery = self.player.rect.centery + offset
                shoot2.rect.left = self.player.rect.right + 2
            elif direction == "down":
                shoot2.rect.centerx = self.player.rect.centerx + offset + 3
                shoot2.rect.top = self.player.rect.bottom - 2
            else:
                shoot2.rect.centerx = self.player.rect.centerx + offset + 3
                shoot2.rect.bottom = self.player.rect.top + 2
            self.all_sprites.add(shoot2)
            self.shoot_list.add(shoot2)

        self.config.get_sound("shoot").play()
        self.player.misiles -= 1
        self.last_fire_time = elapsed_time
