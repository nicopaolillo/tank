import pygame

from config.Settings import WHITE, HEIGHT


class Shooting(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        self.image = pygame.image.load(
            "assets/bullet.png"
        ).convert()

        self.image.set_colorkey(WHITE)

        self.rect = self.image.get_rect()

    def destroy(self):
        if self.rect.y <= -50 or self.rect.y >= HEIGHT + 50:
            self.kill()

    def update(self):
        self.rect.y -= 3
        self.destroy()