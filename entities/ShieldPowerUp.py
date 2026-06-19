import pygame
import random

from config.Settings import HEIGHT, WIDTH


class ShieldPowerUp(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        shield_image = pygame.image.load('assets/shieldArmy.png').convert_alpha()
        self.image = pygame.transform.smoothscale(shield_image, (48, 48))

        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(220, WIDTH - 60)
        self.rect.y = -48

    def update(self):
        self.rect.y += 2
        if self.rect.y > HEIGHT:
            self.kill()
