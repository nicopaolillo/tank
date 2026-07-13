from __future__ import annotations

from config.Settings import MISSILE_RECHARGE_TIME


class ProgressionManager:

    def __init__(self, player):
        self.player = player
        self.completed = False
        self.last_recharge_time = 0.0

    def update(
        self,
        current_time: float,
        enemy_manager,
        tank_red_list,
        tank_green_list,
        tank_blue_list=None,
        mission: int = 1,
        allow_enemy_spawn: bool = True,
        allow_level_progression: bool = True,
    ) -> bool:
        self._recharge_missiles(current_time)
        if not allow_level_progression:
            return False
        return self._handle_level_complete(enemy_manager, tank_red_list, tank_green_list, tank_blue_list, mission, allow_enemy_spawn)

    def _recharge_missiles(self, current_time: float) -> None:
        if current_time - self.last_recharge_time > MISSILE_RECHARGE_TIME:
            self.player.misiles = min(self.player.misiles + 1, 3)
            self.last_recharge_time = current_time

    def _handle_level_complete(self, enemy_manager, tank_red_list, tank_green_list, tank_blue_list, mission: int, allow_enemy_spawn: bool) -> bool:
        all_red_dead = len(tank_red_list) == 0
        all_green_dead = len(tank_green_list) == 0
        all_blue_dead = tank_blue_list is None or len(tank_blue_list) == 0

        if all_red_dead and all_green_dead and all_blue_dead:
            self.player.nivel += 1
            self.player.misiles += 3

            self.completed = True

        if self.player.nivel > 1 and self.completed:
            level_up = True
            self.completed = False
            if allow_enemy_spawn:
                enemy_manager.spawn_level(self.player.nivel, mission)
            return level_up

        return False
