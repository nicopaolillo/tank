import pygame
import random

from config.Settings import HEIGHT

class Tank(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/tank_red.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(200 , 700)
        self.rect.y = random.randrange(HEIGHT - 350)
        self.speed_y = 1

    def update(self):
        if self.rect.y > HEIGHT:
            self.rect.y = -10
            self.rect.x = random.randrange(150,750)


class Tank_green(Tank):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/tank_green.png").convert_alpha()