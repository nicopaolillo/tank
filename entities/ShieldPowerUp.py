import pygame
import random

from config.Settings import HEIGHT, WIDTH, WHITE


class ShieldPowerUp(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 150, 255, 200), (16, 16), 14)
        pygame.draw.circle(self.image, (255, 255, 255), (16, 16), 6)
        pygame.draw.polygon(
            self.image,
            (255, 255, 255),
            [(12, 16), (16, 10), (20, 16), (16, 22)],
        )
        self.image.set_colorkey(WHITE)

        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(220, WIDTH - 60)
        self.rect.y = -40

    def update(self):
        self.rect.y += 2
        if self.rect.y > HEIGHT:
            self.kill()
