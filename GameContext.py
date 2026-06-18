import pygame

from entities.Player import Player
from entities.Tank import Tank, Tank_green
from config.Settings import GameConfig, TANK_GREEN_SPAWN_COUNT, TANK_RED_SPAWN_COUNT


class GameContext:
    """Manages game state and sprite groups."""

    def __init__(self, config: GameConfig):
        self.config = config
        
        self.tank_red_list = pygame.sprite.Group()
        self.tank_green_list = pygame.sprite.Group()
        self.shoot_list = pygame.sprite.Group()
        self.crash_list = pygame.sprite.Group()
        self.apoyo_list = pygame.sprite.Group()

        self.all_sprites = pygame.sprite.Group()

        self.player = Player(config)

        self.game_over = False
        self.pause = False

        self._create_tanks()

        self.all_sprites.add(self.player)

    def _create_tanks(self):
        """Spawn initial tanks for the level."""
        for _ in range(TANK_GREEN_SPAWN_COUNT):
            tank_green = Tank_green()
            self.tank_green_list.add(tank_green)
            self.all_sprites.add(tank_green)

        for _ in range(TANK_RED_SPAWN_COUNT):
            tank_red = Tank()
            self.tank_red_list.add(tank_red)
            self.all_sprites.add(tank_red)
    
    def reset_player_state(self):
        """Reset player to initial state."""
        from config.Settings import (
            PLAYER_INITIAL_HP, PLAYER_INITIAL_LEVEL, 
            PLAYER_INITIAL_MISSILES, PLAYER_INITIAL_SUPPORT
        )
        self.player.hp = PLAYER_INITIAL_HP
        self.player.nivel = PLAYER_INITIAL_LEVEL
        self.player.misiles = PLAYER_INITIAL_MISSILES
        self.player.apoyo = PLAYER_INITIAL_SUPPORT
        self.player.puntaje = 0