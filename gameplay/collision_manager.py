from __future__ import annotations

import pygame

from config.Settings import (
    TANK_RED_HIT_DAMAGE,
    TANK_GREEN_HIT_DAMAGE,
    TANK_RED_KILL_POINTS,
    TANK_GREEN_KILL_POINTS,
    AIR_SUPPORT_RED_POINTS,
    AIR_SUPPORT_GREEN_POINTS,
)
from entities.Death import Death


class CollisionManager:

    def __init__(self, config, player, all_sprites, shoot_list, tank_red_list, tank_green_list, apoyo_list):
        self.config = config
        self.player = player
        self.all_sprites = all_sprites
        self.shoot_list = shoot_list
        self.tank_red_list = tank_red_list
        self.tank_green_list = tank_green_list
        self.apoyo_list = apoyo_list

    def handle_red_tank_shots(self) -> None:
        for shoot in list(self.shoot_list):
            shoot_hits = pygame.sprite.spritecollide(shoot, self.tank_red_list, True)
            if shoot_hits:
                self._remove_shoot(shoot)
                self.config.get_sound("explosion").play()
                for tank in shoot_hits:
                    death = Death(tank.rect.x, tank.rect.y)
                    death.animate()
                    self.all_sprites.add(death)
                    self.player.puntaje += TANK_RED_KILL_POINTS
            elif shoot.rect.y < -10:
                self._remove_shoot(shoot)

    def handle_air_support_collisions(self) -> None:
        for apoyo in list(self.apoyo_list):
            hits_red = pygame.sprite.spritecollide(apoyo, self.tank_red_list, True)
            hits_green = pygame.sprite.spritecollide(apoyo, self.tank_green_list, True)
            for tank in hits_red:
                self.config.get_sound("explosion").play()
                death = Death(tank.rect.x, tank.rect.y)
                death.animate()
                self.all_sprites.add(death)
                self.player.puntaje += AIR_SUPPORT_RED_POINTS
            for tank in hits_green:
                self.config.get_sound("explosion").play()
                death = Death(tank.rect.x, tank.rect.y)
                death.animate()
                self.all_sprites.add(death)
                self.player.puntaje += AIR_SUPPORT_GREEN_POINTS
            if apoyo.rect.y < -200:
                if apoyo in self.all_sprites:
                    self.all_sprites.remove(apoyo)
                if apoyo in self.apoyo_list:
                    self.apoyo_list.remove(apoyo)

    def handle_green_tank_shots(self) -> None:
        for shoot in list(self.shoot_list):
            shoot_hits = pygame.sprite.spritecollide(shoot, self.tank_green_list, len(self.tank_red_list) == 0)
            for tank in shoot_hits:
                self._remove_shoot(shoot)
                if len(self.tank_red_list) > 0:
                    self.config.get_sound("iron").play()
                else:
                    self.player.puntaje += TANK_GREEN_KILL_POINTS
                    death = Death(tank.rect.x, tank.rect.y)
                    death.animate()
                    self.all_sprites.add(death)
                    self.config.get_sound("explosion").play()

    def handle_player_collisions(self) -> bool:
        if self._handle_red_tank_crash():
            return True
        if self._handle_green_tank_collision():
            return True
        return False

    def _remove_shoot(self, shoot) -> None:
        if shoot in self.all_sprites:
            self.all_sprites.remove(shoot)
        if shoot in self.shoot_list:
            self.shoot_list.remove(shoot)

    def _handle_red_tank_crash(self) -> bool:
        crash_list = pygame.sprite.spritecollide(self.player, self.tank_red_list, True)
        if crash_list:
            self.config.get_sound("explosion").play()
        for tank in crash_list:
            self.player.hp -= TANK_RED_HIT_DAMAGE
            death = Death(self.player.rect.x, self.player.rect.y)
            death.animate()
            self.all_sprites.add(death)
        if self.player.hp <= 0 and self.player in self.all_sprites:
            self.all_sprites.remove(self.player)
            return True
        return False

    def _handle_green_tank_collision(self) -> bool:
        crash_list = pygame.sprite.spritecollide(self.player, self.tank_green_list, True)
        if crash_list:
            self.config.get_sound("explosion").play()
        for tank in crash_list:
            self.player.hp -= TANK_GREEN_HIT_DAMAGE
            death = Death(self.player.rect.x, self.player.rect.y)
            death.animate()
            self.all_sprites.add(death)
            if self.player.hp <= 0:
                if self.player in self.all_sprites:
                    self.all_sprites.remove(self.player)
                return True
        return False
