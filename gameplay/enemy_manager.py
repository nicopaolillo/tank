from __future__ import annotations

from entities.Tank import Tank, Tank_green

class EnemyManager:

    def __init__(self, all_sprites, tank_red_list, tank_green_list):
        self.all_sprites = all_sprites
        self.tank_red_list = tank_red_list
        self.tank_green_list = tank_green_list

    def update(self) -> None:
        for tank in self.tank_red_list:
            tank.rect.y += tank.speed_y * 2.0
        for tank in self.tank_green_list:
            tank.rect.y += tank.speed_y * 2.0

    def spawn_level(self, level: int) -> None:
        capped_level = min(level, 5)
        num_green = capped_level
        num_red = capped_level

        for i in range(num_green):
            offset = 50 * i
            tank_green = Tank_green(spawn_from_top=True, max_start_offset=200 + offset)
            tank_green.rect.y -= offset
            self.tank_green_list.add(tank_green)
            self.all_sprites.add(tank_green)

        for i in range(num_red):
            offset = 50 * i
            tank_red = Tank(spawn_from_top=True, max_start_offset=200 + offset)
            tank_red.rect.y -= offset
            self.tank_red_list.add(tank_red)
            self.all_sprites.add(tank_red)

    def all_enemies_cleared(self) -> bool:
        return len(self.tank_red_list) == 0 and len(self.tank_green_list) == 0
