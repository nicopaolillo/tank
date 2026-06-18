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