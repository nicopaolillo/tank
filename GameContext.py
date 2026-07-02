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
        self.enemy_shoot_list = pygame.sprite.Group()
        self.crash_list = pygame.sprite.Group()
        self.apoyo_list = pygame.sprite.Group()
        self.powerup_list = pygame.sprite.Group()
        self.smoke_list = pygame.sprite.Group()
        self.bombardier_list = pygame.sprite.Group()

        self.all_sprites = pygame.sprite.Group()

        self.player = Player(config)

        self.game_over = False
        self.pause = False

        self._preload_assets()
        self._create_tanks()

        self.all_sprites.add(self.player)

    @staticmethod
    def _preload_assets() -> None:
        """Preload heavy assets so they don't cause hitches during gameplay."""
        from entities.Bombardier import Bombardier, BombardierSinkingEffect, BoatProjectile
        from entities.Death import Death
        from entities.SmokeTrail import SmokeTrail

        Bombardier._get_base_frames()
        Bombardier._get_fire_frames()
        Bombardier._get_water_frames()
        BombardierSinkingEffect._get_frames()
        BoatProjectile._get_frames()
        Death._load_cache()
        SmokeTrail._load_frames()

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
        self.player.max_hp = PLAYER_INITIAL_HP
        self.player.double_barrel_active = False
        self.player.armor_active = False
        self.player.tank_track_active = False
        self.player.nivel = PLAYER_INITIAL_LEVEL
        self.player.misiles = PLAYER_INITIAL_MISSILES
        self.player.apoyo = PLAYER_INITIAL_SUPPORT
        self.player.puntaje = 0
        self.player.update_sprite()