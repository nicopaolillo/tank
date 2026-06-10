import pygame

from config.Settings import WIDTH, HEIGHT, BLACK

class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("assets/player.png").convert()
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10

        self.speed_x = 0
        self.speed_y = 0

        self.hp = 200
        self.nivel = 1
        self.misiles = 0
        self.puntaje = 0
        self.apoyo = 1