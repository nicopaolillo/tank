import pygame
import random

from config.Settings import HEIGHT

class Tank(pygame.sprite.Sprite):
    def __init__(self, spawn_from_top: bool = False, max_start_offset: int = 300):
        super().__init__()
        self.image = pygame.image.load("assets/tank_red.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(200 , 700)
        # by default place tank somewhere on screen; if spawn_from_top, start above viewport
        if spawn_from_top:
            self.rect.y = -random.randrange(20, max(50, max_start_offset))
        else:
            self.rect.y = random.randrange(max(0, HEIGHT - 350))
        self.speed_y = 1

    def update(self):
        if self.rect.y > HEIGHT:
            self.rect.y = -10
            self.rect.x = random.randrange(150,750)


class Tank_green(Tank):
    def __init__(self, spawn_from_top: bool = False, max_start_offset: int = 300):
        super().__init__(spawn_from_top=spawn_from_top, max_start_offset=max_start_offset)
        self.image = pygame.image.load("assets/tank_green.png").convert_alpha()