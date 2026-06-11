import pygame

from entities.Player import Player
from entities.Tank import Tank
from entities.Tank import Tank_green


class GameContext:

    def __init__(self):

        self.tank_red_list = pygame.sprite.Group()
        self.tank_green_list = pygame.sprite.Group()
        self.shoot_list = pygame.sprite.Group()
        self.crash_list = pygame.sprite.Group()
        self.apoyo_list = pygame.sprite.Group()

        self.all_sprites = pygame.sprite.Group()

        self.player = Player()

        self.game_over = False
        self.pause = False

        self._create_tanks()

        self.all_sprites.add(self.player)

    def _create_tanks(self):

        for _ in range(3):
            tank_green = Tank_green()
            self.tank_green_list.add(tank_green)
            self.all_sprites.add(tank_green)

        for _ in range(5):
            tank_red = Tank()
            self.tank_red_list.add(tank_red)
            self.all_sprites.add(tank_red)