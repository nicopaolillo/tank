from __future__ import annotations

import random

from config.Settings import HEIGHT, ENEMY_SHOOT_COOLDOWN, ENEMY_SHOOT_LEVEL_START
from entities.Tank import Tank, Tank_green
from entities.Shooting import Shooting

_MIN_SEPARATION = 130
_X_MIN = 150
_X_MAX = 750
_MAX_ATTEMPTS = 30


class EnemyManager:

    def __init__(self, config, all_sprites, tank_red_list, tank_green_list, enemy_shoot_list):
        self.config = config
        self.all_sprites = all_sprites
        self.tank_red_list = tank_red_list
        self.tank_green_list = tank_green_list
        self.enemy_shoot_list = enemy_shoot_list
        self._last_enemy_fire = -ENEMY_SHOOT_COOLDOWN

    def _occupied_x_positions(self) -> list[int]:
        positions = [t.rect.centerx for t in self.tank_red_list]
        positions += [t.rect.centerx for t in self.tank_green_list]
        return positions

    def _find_non_overlapping_x(self, occupied: list[int]) -> int:
        if not occupied:
            return random.randrange(_X_MIN, _X_MAX)

        for _ in range(_MAX_ATTEMPTS):
            candidate = random.randrange(_X_MIN, _X_MAX)
            if all(abs(candidate - ox) >= _MIN_SEPARATION for ox in occupied):
                return candidate

        best = occupied[0]
        best_dist = 0
        for pos in range(_X_MIN, _X_MAX, 10):
            min_dist = min(abs(pos - ox) for ox in occupied)
            if min_dist > best_dist:
                best_dist = min_dist
                best = pos
        return best

    def update(self) -> None:
        all_tanks = list(self.tank_red_list) + list(self.tank_green_list)
        occupied = [t.rect.centerx for t in all_tanks]

        for tank in self.tank_red_list:
            tank.rect.y += tank.speed_y * 2.0
            if tank.rect.y > HEIGHT:
                tank.rect.y = -10
                tank.rect.centerx = self._find_non_overlapping_x(occupied)
                occupied.append(tank.rect.centerx)

        for tank in self.tank_green_list:
            tank.rect.y += tank.speed_y * 2.0
            if tank.rect.y > HEIGHT:
                tank.rect.y = -10
                tank.rect.centerx = self._find_non_overlapping_x(occupied)
                occupied.append(tank.rect.centerx)

    def try_enemy_shoot(self, current_time: float, level: int) -> None:
        if level < ENEMY_SHOOT_LEVEL_START:
            return

        max_bullets = 2 if level >= 6 else 1
        if len(self.enemy_shoot_list) >= max_bullets:
            return
        if current_time - self._last_enemy_fire < ENEMY_SHOOT_COOLDOWN:
            return

        all_tanks = list(self.tank_red_list) + list(self.tank_green_list)
        if not all_tanks:
            return

        num_shooters = min(max_bullets, len(all_tanks))
        shooters = random.sample(all_tanks, num_shooters)
        for tank in shooters:
            bullet = Shooting("down", damage=tank.shoot_damage)
            bullet.rect.centerx = tank.rect.centerx
            bullet.rect.top = tank.rect.bottom
            self.all_sprites.add(bullet)
            self.enemy_shoot_list.add(bullet)

        self.config.get_sound("shoot").play()
        self._last_enemy_fire = current_time

    def clear_all_enemies(self) -> None:
        for tank in list(self.tank_red_list):
            self.tank_red_list.remove(tank)
            self.all_sprites.remove(tank)
        for tank in list(self.tank_green_list):
            self.tank_green_list.remove(tank)
            self.all_sprites.remove(tank)

    def spawn_level(self, level: int) -> None:
        self.clear_all_enemies()
        capped_level = min(level, 3)
        num_green = capped_level
        num_red = capped_level

        occupied = self._occupied_x_positions()

        for i in range(num_green):
            offset = 50 * i
            tank_green = Tank_green(spawn_from_top=True, max_start_offset=200 + offset)
            tank_green.rect.y -= offset
            tank_green.rect.centerx = self._find_non_overlapping_x(occupied)
            occupied.append(tank_green.rect.centerx)
            self.tank_green_list.add(tank_green)
            self.all_sprites.add(tank_green)

        for i in range(num_red):
            offset = 50 * i
            tank_red = Tank(spawn_from_top=True, max_start_offset=200 + offset)
            tank_red.rect.y -= offset
            tank_red.rect.centerx = self._find_non_overlapping_x(occupied)
            occupied.append(tank_red.rect.centerx)
            self.tank_red_list.add(tank_red)
            self.all_sprites.add(tank_red)

    def all_enemies_cleared(self) -> bool:
        return len(self.tank_red_list) == 0 and len(self.tank_green_list) == 0
