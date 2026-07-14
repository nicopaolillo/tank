from __future__ import annotations

import pygame

from config.Settings import (
    TANK_RED_HIT_DAMAGE,
    TANK_GREEN_HIT_DAMAGE,
    TANK_BLUE_HIT_DAMAGE,
    TANK_RED_KILL_POINTS,
    TANK_GREEN_KILL_POINTS,
    TANK_BLUE_KILL_POINTS,
    AIR_SUPPORT_RED_POINTS,
    AIR_SUPPORT_GREEN_POINTS,
    PLAYER_MAX_SHIELDS,
    PLAYER_MAX_SUPPORT,
    PLAYER_INITIAL_HP,
    BOMBARDIER_PLAYER_SHOT_DAMAGE,
    BOMBARDIER_KILL_POINTS,
    BOMBARDIER_PROJECTILE_DAMAGE,
    HELICOPTER_PLAYER_SHOT_DAMAGE,
    HELICOPTER_KILL_POINTS,
)
from entities.Death import Death
from entities.DebrisPiece import DebrisPiece
from entities.Tank import Tank_green


class CollisionManager:

    def __init__(
        self,
        config,
        player,
        all_sprites,
        shoot_list,
        tank_red_list,
        tank_green_list,
        tank_blue_list,
        apoyo_list,
        powerup_list,
        bombardier_list,
        enemy_shoot_list,
        helicopter_list,
    ):
        self.config = config
        self.player = player
        self.all_sprites = all_sprites
        self.shoot_list = shoot_list
        self.tank_red_list = tank_red_list
        self.tank_green_list = tank_green_list
        self.tank_blue_list = tank_blue_list
        self.apoyo_list = apoyo_list
        self.powerup_list = powerup_list
        self.bombardier_list = bombardier_list
        self.enemy_shoot_list = enemy_shoot_list
        self.helicopter_list = helicopter_list

    def _spawn_debris(self, x: int, y: int, prefix: str) -> None:
        for i in range(7):
            piece = DebrisPiece(x, y, prefix, i)
            self.all_sprites.add(piece)

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
                    self._spawn_debris(tank.rect.centerx, tank.rect.centery, "partsRed")
                    self.player.puntaje += TANK_RED_KILL_POINTS
            elif shoot.rect.y < -10:
                self._remove_shoot(shoot)

    def handle_blue_tank_shots(self) -> None:
        for shoot in list(self.shoot_list):
            shoot_hits = pygame.sprite.spritecollide(shoot, self.tank_blue_list, False)
            for tank in shoot_hits:
                self._remove_shoot(shoot)
                self.config.get_sound("explosion").play()
                self.tank_blue_list.remove(tank)
                self.all_sprites.remove(tank)
                self.player.puntaje += TANK_BLUE_KILL_POINTS
                death = Death(tank.rect.x, tank.rect.y)
                death.animate()
                self.all_sprites.add(death)
                self._spawn_debris(tank.rect.centerx, tank.rect.centery, "partsRed")

    def handle_air_support_collisions(self) -> None:
        for apoyo in list(self.apoyo_list):
            hits_red = pygame.sprite.spritecollide(apoyo, self.tank_red_list, True)
            hits_green = pygame.sprite.spritecollide(apoyo, self.tank_green_list, True)
            hits_blue = pygame.sprite.spritecollide(apoyo, self.tank_blue_list, True)
            for tank in hits_red:
                self.config.get_sound("explosion").play()
                death = Death(tank.rect.x, tank.rect.y)
                death.animate()
                self.all_sprites.add(death)
                self._spawn_debris(tank.rect.centerx, tank.rect.centery, "partsRed")
                self.player.puntaje += AIR_SUPPORT_RED_POINTS
            for tank in hits_green:
                self.config.get_sound("explosion").play()
                death = Death(tank.rect.x, tank.rect.y)
                death.animate()
                self.all_sprites.add(death)
                self._spawn_debris(tank.rect.centerx, tank.rect.centery, "partsGreen")
                self.player.puntaje += AIR_SUPPORT_GREEN_POINTS
            for tank in hits_blue:
                self.config.get_sound("explosion").play()
                death = Death(tank.rect.x, tank.rect.y)
                death.animate()
                self.all_sprites.add(death)
                self._spawn_debris(tank.rect.centerx, tank.rect.centery, "partsRed")
                self.player.puntaje += TANK_BLUE_KILL_POINTS
            if apoyo.rect.y < -200:
                if apoyo in self.all_sprites:
                    self.all_sprites.remove(apoyo)
                if apoyo in self.apoyo_list:
                    self.apoyo_list.remove(apoyo)

    def handle_green_tank_shots(self) -> None:
        for shoot in list(self.shoot_list):
            shoot_hits = pygame.sprite.spritecollide(shoot, self.tank_green_list, False)
            for tank in shoot_hits:
                self._remove_shoot(shoot)
                if tank.hits == 0:
                    tank.hits += 1
                    tank.image = Tank_green.damaged_image
                    self.config.get_sound("iron").play()
                else:
                    self.tank_green_list.remove(tank)
                    self.all_sprites.remove(tank)
                    self.player.puntaje += TANK_GREEN_KILL_POINTS
                    death = Death(tank.rect.x, tank.rect.y)
                    death.animate()
                    self.all_sprites.add(death)
                    self._spawn_debris(tank.rect.centerx, tank.rect.centery, "partsGreen")
                    self.config.get_sound("explosion").play()

    def handle_player_collisions(self) -> bool:
        if self._handle_red_tank_crash():
            return True
        if self._handle_green_tank_collision():
            return True
        if self._handle_blue_tank_collision():
            return True
        if self._handle_enemy_projectile_collision():
            return True
        return False

    def handle_bombardier_shots(self) -> None:
        for shoot in list(self.shoot_list):
            hits = pygame.sprite.spritecollide(shoot, self.bombardier_list, False)
            if not hits:
                continue

            self._remove_shoot(shoot)
            for boat in hits:
                if getattr(boat, "is_destroyed", False):
                    continue

                # Spawn damage feedback each time a player shot lands on Bombardier.
                hit_fx = Death(boat.rect.centerx, boat.rect.centery)
                hit_fx.animate()
                self.all_sprites.add(hit_fx)

                if getattr(boat, "_shield_active", False):
                    self.config.get_sound("iron").play()
                    continue

                if boat.take_damage(BOMBARDIER_PLAYER_SHOT_DAMAGE):
                    self.player.puntaje += BOMBARDIER_KILL_POINTS
                    self.config.get_sound("explosion").play()
                else:
                    self.config.get_sound("explosion").play()

    def handle_helicopter_shots(self) -> None:
        for shoot in list(self.shoot_list):
            hits = pygame.sprite.spritecollide(shoot, self.helicopter_list, False)
            if not hits:
                continue

            self._remove_shoot(shoot)
            for heli in hits:
                if getattr(heli, "is_destroyed", False):
                    continue

                hit_fx = Death(heli.rect.centerx, heli.rect.centery)
                hit_fx.animate()
                self.all_sprites.add(hit_fx)

                if getattr(heli, "_shield_active", False) or getattr(heli, "_entering", False):
                    self.config.get_sound("iron").play()
                    continue

                if heli.take_damage(HELICOPTER_PLAYER_SHOT_DAMAGE):
                    self.player.puntaje += HELICOPTER_KILL_POINTS
                    self.config.get_sound("explosion").play()
                else:
                    self.config.get_sound("explosion").play()

    def handle_powerup_collisions(self) -> None:
        for powerup in list(self.powerup_list):
            if pygame.sprite.collide_rect(self.player, powerup):
                if powerup in self.all_sprites:
                    self.all_sprites.remove(powerup)
                if powerup in self.powerup_list:
                    self.powerup_list.remove(powerup)
                from entities.ShieldPowerUp import ShieldPowerUp
                from entities.AirSupportPickup import AirSupportPickup
                from entities.UpgradePickup import UpgradePickup
                from entities.HealthPickup import HealthPickup
                if isinstance(powerup, ShieldPowerUp):
                    self.player.shield_inventory = min(self.player.shield_inventory + 1, PLAYER_MAX_SHIELDS)
                elif isinstance(powerup, AirSupportPickup):
                    self.player.apoyo = min(self.player.apoyo + 1, PLAYER_MAX_SUPPORT)
                elif isinstance(powerup, UpgradePickup):
                    self.player.double_barrel_active = True
                    self.player.hp = PLAYER_INITIAL_HP
                    self.player.update_sprite()
                elif isinstance(powerup, HealthPickup):
                    self.player.hp = min(self.player.hp + 50, PLAYER_INITIAL_HP)
                self.config.get_sound("select").play()

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
            if self.player.shield_active:
                continue
            dmg = TANK_RED_HIT_DAMAGE
            if self.player.armor_active:
                dmg //= 2
            self.player.hp -= dmg
            self.player.update_sprite()
            death = Death(self.player.rect.x, self.player.rect.y)
            death.animate()
            self.all_sprites.add(death)
            self._spawn_debris(tank.rect.centerx, tank.rect.centery, "partsRed")
        if self.player.hp <= 0 and self.player in self.all_sprites:
            self.all_sprites.remove(self.player)
            return True
        return False

    def _handle_green_tank_collision(self) -> bool:
        crash_list = pygame.sprite.spritecollide(self.player, self.tank_green_list, True)
        if crash_list:
            self.config.get_sound("explosion").play()
        for tank in crash_list:
            if self.player.shield_active:
                continue
            dmg = TANK_GREEN_HIT_DAMAGE
            if self.player.armor_active:
                dmg //= 2
            self.player.hp -= dmg
            self.player.update_sprite()
            death = Death(self.player.rect.x, self.player.rect.y)
            death.animate()
            self.all_sprites.add(death)
            self._spawn_debris(tank.rect.centerx, tank.rect.centery, "partsGreen")
            if self.player.hp <= 0:
                if self.player in self.all_sprites:
                    self.all_sprites.remove(self.player)
                return True
        return False

    def _handle_blue_tank_collision(self) -> bool:
        crash_list = pygame.sprite.spritecollide(self.player, self.tank_blue_list, True)
        if crash_list:
            self.config.get_sound("explosion").play()
        for tank in crash_list:
            if self.player.shield_active:
                continue
            dmg = TANK_BLUE_HIT_DAMAGE
            if self.player.armor_active:
                dmg //= 2
            self.player.hp -= dmg
            self.player.update_sprite()
            death = Death(self.player.rect.x, self.player.rect.y)
            death.animate()
            self.all_sprites.add(death)
            self._spawn_debris(tank.rect.centerx, tank.rect.centery, "partsRed")
            if self.player.hp <= 0:
                if self.player in self.all_sprites:
                    self.all_sprites.remove(self.player)
                return True
        return False

    def _handle_enemy_projectile_collision(self) -> bool:
        hits = pygame.sprite.spritecollide(self.player, self.enemy_shoot_list, True)
        if not hits:
            return False

        if self.player.shield_active:
            return False

        dmg = sum(getattr(bullet, 'damage', BOMBARDIER_PROJECTILE_DAMAGE) for bullet in hits)
        if self.player.armor_active:
            dmg //= 2
        self.player.hp -= dmg
        self.player.update_sprite()
        death = Death(self.player.rect.x, self.player.rect.y)
        death.animate()
        self.all_sprites.add(death)
        self.config.get_sound("explosion").play()

        if self.player.hp <= 0 and self.player in self.all_sprites:
            self.all_sprites.remove(self.player)
            return True

        return False
