import pygame
import random

from config.Settings import HEIGHT, PLAYER_BOUNDS_LEFT, PLAYER_BOUNDS_RIGHT

POWERUP_SIZE = 58

class AirSupportPickup(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        plane_image = pygame.image.load('assets/avion.png').convert_alpha()
        bounds = plane_image.get_bounding_rect(min_alpha=1)
        if bounds.width > 0 and bounds.height > 0:
            plane_image = plane_image.subsurface(bounds).copy()
        self.image = pygame.transform.smoothscale(plane_image, (POWERUP_SIZE, POWERUP_SIZE))
        self.rect = self.image.get_rect()
        spawn_left = PLAYER_BOUNDS_LEFT
        spawn_right = PLAYER_BOUNDS_RIGHT - self.rect.width
        self.rect.x = random.randrange(spawn_left, spawn_right + 1)
        self.rect.y = -self.rect.height

    def update(self):
        self.rect.y += 2
        if self.rect.y > HEIGHT:
            self.kill()
