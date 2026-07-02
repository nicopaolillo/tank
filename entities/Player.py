import pygame

from config.Settings import (
    WIDTH, HEIGHT, BLACK, 
    PLAYER_INITIAL_HP, PLAYER_INITIAL_LEVEL, 
    PLAYER_INITIAL_MISSILES, PLAYER_INITIAL_SUPPORT,
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
        self.facing = "up"

        self.hp = PLAYER_INITIAL_HP
        self.max_hp = PLAYER_INITIAL_HP
        self.nivel = PLAYER_INITIAL_LEVEL
        self.double_barrel_active = False
        self.armor_active = False
        self.tank_track_active = False
        self.update_sprite()
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

    def update_sprite(self) -> None:
        if self.double_barrel_active:
            state = 'double_barrel'
        elif self.armor_active:
            state = 'armor'
        elif self.tank_track_active:
            state = 'tank_track'
        elif self.hp <= 50:
            state = 'damaged_2'
        elif self.hp <= 100:
            state = 'damaged'
        else:
            state = ''
        self.image = self.config.get_player_sprite(self.facing, damage_state=state)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update_shield(self, current_time: float) -> None:
        if self.shield_active and current_time >= self.shield_end_time:
            self.shield_active = False