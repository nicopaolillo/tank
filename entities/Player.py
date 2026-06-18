import pygame

from config.Settings import (
    WIDTH, HEIGHT, BLACK, 
    PLAYER_INITIAL_HP, PLAYER_INITIAL_LEVEL, 
    PLAYER_INITIAL_MISSILES, PLAYER_INITIAL_SUPPORT
)

class Player(pygame.sprite.Sprite):

    def __init__(self, config):
        super().__init__()
        self.config = config

        self.image = config.get_player_sprite('default')
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10

        self.speed_x = 0
        self.speed_y = 0

        self.hp = PLAYER_INITIAL_HP
        self.nivel = PLAYER_INITIAL_LEVEL
        self.misiles = PLAYER_INITIAL_MISSILES
        self.puntaje = 0
        self.apoyo = PLAYER_INITIAL_SUPPORT
        self.shield_inventory = 0
        self.shield_active = False
        self.shield_duration = 3.0
        self.shield_end_time = 0.0

    def activate_shield(self, current_time: float) -> None:
        if self.shield_inventory <= 0 or self.shield_active:
            return
        self.shield_inventory -= 1
        self.shield_active = True
        self.shield_end_time = current_time + self.shield_duration

    def update_shield(self, current_time: float) -> None:
        if self.shield_active and current_time >= self.shield_end_time:
            self.shield_active = False