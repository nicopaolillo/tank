import pygame

from config.Settings import WHITE, HEIGHT, WIDTH


class Shooting(pygame.sprite.Sprite):

    def __init__(self, direction: str = "up"):
        super().__init__()
        self.direction = direction
        self.speed = 6

        bullet = pygame.image.load(
            "assets/bullet.png"
        ).convert()
        self.image = bullet
        if self.direction == "left":
            self.image = pygame.transform.rotate(self.image, 90)
        elif self.direction == "right":
            self.image = pygame.transform.rotate(self.image, -90)
        elif self.direction == "down":
            self.image = pygame.transform.rotate(self.image, 180)

        self.image.set_colorkey(WHITE)

        self.rect = self.image.get_rect()

    def destroy(self):
        if (
            self.rect.y <= -50
            or self.rect.y >= HEIGHT + 50
            or self.rect.x <= -50
            or self.rect.x >= WIDTH + 50
        ):
            self.kill()

    def update(self):
        if self.direction == "left":
            self.rect.x -= self.speed
        elif self.direction == "right":
            self.rect.x += self.speed
        elif self.direction == "down":
            self.rect.y += self.speed
        else:
            self.rect.y -= self.speed
        self.destroy()