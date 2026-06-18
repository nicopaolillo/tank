from __future__ import annotations

from config.Settings import MISSILE_RECHARGE_TIME


class ProgressionManager:

    def __init__(self, player):
        self.player = player
        self.completed = False
        self.last_recharge_time = 0.0

    def update(self, current_time: float, enemy_manager, tank_red_list, tank_green_list) -> None:
        self._recharge_missiles(current_time)
        self._handle_level_complete(enemy_manager, tank_red_list, tank_green_list)

    def _recharge_missiles(self, current_time: float) -> None:
        if current_time - self.last_recharge_time > MISSILE_RECHARGE_TIME:
            self.player.misiles += 1
            self.last_recharge_time = current_time

    def _handle_level_complete(self, enemy_manager, tank_red_list, tank_green_list) -> None:
        if len(tank_red_list) == 0 and len(tank_green_list) == 0:
            self.player.nivel += 1
            self.player.hp = min(self.player.hp + 100, 200)
            self.player.misiles += 3
            self.player.apoyo += 1
            self.completed = True

        if self.player.nivel > 1 and self.completed:
            self.completed = False
            enemy_manager.spawn_level(self.player.nivel)
