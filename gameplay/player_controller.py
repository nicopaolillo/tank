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
        self.last_fire_time = 0.0

    def handle_keydown(self, event: pygame.event.EventType, elapsed_time: float) -> None:
        if event.key == pygame.K_LEFT:
            self.player.speed_x = -PLAYER_SPEED
            self.player.image = self.config.get_player_sprite("left")
        elif event.key == pygame.K_RIGHT:
            self.player.speed_x = PLAYER_SPEED
            self.player.image = self.config.get_player_sprite("right")
        elif event.key == pygame.K_UP:
            self.player.speed_y = -PLAYER_SPEED
            self.player.image = self.config.get_player_sprite("default")
        elif event.key == pygame.K_DOWN:
            self.player.speed_y = PLAYER_SPEED
            self.player.image = self.config.get_player_sprite("down")
        elif event.key == pygame.K_q and self.player.apoyo > 0:
            self._spawn_support()
        elif event.key == pygame.K_w:
            self.player.activate_shield(elapsed_time)
        elif event.key == pygame.K_SPACE and self.player.misiles > 0:
            self._try_shoot(elapsed_time)

    def handle_keyup(self, event: pygame.event.EventType) -> None:
        if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            self.player.speed_x = 0
        elif event.key in (pygame.K_UP, pygame.K_DOWN):
            self.player.speed_y = 0

    def update(self) -> None:
        self.player.rect.x += self.player.speed_x
        self.player.rect.y += self.player.speed_y

    def clamp_bounds(self) -> None:
        if self.player.rect.right > PLAYER_BOUNDS_RIGHT:
            self.player.rect.right = PLAYER_BOUNDS_RIGHT
        if self.player.rect.left < PLAYER_BOUNDS_LEFT:
            self.player.rect.left = PLAYER_BOUNDS_LEFT
        if self.player.rect.top < 0:
            self.player.rect.top = 0
        if self.player.rect.bottom > HEIGHT:
            self.player.rect.bottom = HEIGHT

    def _spawn_support(self) -> None:
        apoyo = AirSupport()
        apoyo.rect.x = self.player.rect.x + 10
        apoyo.rect.y = HEIGHT
        self.all_sprites.add(apoyo)
        self.apoyo_list.add(apoyo)
        self.player.apoyo -= 1

    def _try_shoot(self, elapsed_time: float) -> None:
        time_since_last = elapsed_time - self.last_fire_time
        if time_since_last < MISSILE_FIRE_COOLDOWN:
            return

        shoot = Shooting()
        shoot.rect.x = self.player.rect.x + 10
        shoot.rect.y = self.player.rect.y - 20
        self.all_sprites.add(shoot)
        self.shoot_list.add(shoot)
        self.config.get_sound("shoot").play()
        self.player.misiles -= 1
        self.last_fire_time = elapsed_time
