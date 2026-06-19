import pygame

from config.Settings import WHITE, HEIGHT


class AirSupport(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        plane = pygame.image.load(
            "assets/avion.png"
        ).convert_alpha()
        self.image = plane

        self.image.set_colorkey(WHITE)

        self.rect = self.image.get_rect()

    def update(self):
        self.rect.y -= 9

        if self.rect.y <= -200 or self.rect.y >= HEIGHT + 50:
            self.kill()