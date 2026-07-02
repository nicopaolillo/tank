import pygame
import random

from config.Settings import HEIGHT, PLAYER_BOUNDS_LEFT, PLAYER_BOUNDS_RIGHT

POWERUP_SIZE = 58


class HealthPickup(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        tool_image = pygame.image.load('assets/tool.png').convert_alpha()
        self.image = pygame.transform.smoothscale(tool_image, (POWERUP_SIZE, POWERUP_SIZE))
        self.rect = self.image.get_rect()
        spawn_left = PLAYER_BOUNDS_LEFT
        spawn_right = PLAYER_BOUNDS_RIGHT - self.rect.width
        self.rect.x = random.randrange(spawn_left, spawn_right + 1)
        self.rect.y = -self.rect.height

    def update(self):
        self.rect.y += 2
        if self.rect.y > HEIGHT:
            self.kill()
