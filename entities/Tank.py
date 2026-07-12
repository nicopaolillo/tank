import pygame
import random

from config.Settings import HEIGHT, TANK_RED_SHOOT_DAMAGE, TANK_GREEN_SHOOT_DAMAGE

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
        self.last_fire_time = 0.0
        self.shoot_damage = TANK_RED_SHOOT_DAMAGE

    def update(self):
        pass


class Tank_green(Tank):
    damaged_image = None

    def __init__(self, spawn_from_top: bool = False, max_start_offset: int = 300):
        super().__init__(spawn_from_top=spawn_from_top, max_start_offset=max_start_offset)
        self.image = pygame.image.load("assets/tank_green.png").convert_alpha()
        self.hits = 0
        self.shoot_damage = TANK_GREEN_SHOOT_DAMAGE
        if Tank_green.damaged_image is None:
            Tank_green.damaged_image = pygame.image.load("assets/tank_green_damaged.png").convert_alpha()