import math
import pygame

from config.Settings import WHITE, HEIGHT, WIDTH


class Shooting(pygame.sprite.Sprite):

    def __init__(self, direction: str = "up", damage: int = 0):
        super().__init__()
        self.direction = direction
        self.speed = 6
        self.damage = damage

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
        elif self.direction == "up_left":
            self.image = pygame.transform.rotate(self.image, 45)
        elif self.direction == "up_right":
            self.image = pygame.transform.rotate(self.image, -45)
        elif self.direction == "down_left":
            self.image = pygame.transform.rotate(self.image, 135)
        elif self.direction == "down_right":
            self.image = pygame.transform.rotate(self.image, -135)

        self.image.set_colorkey(WHITE)

        self.rect = self.image.get_rect()

        self._velocity = self._calc_velocity()

    def _calc_velocity(self) -> tuple[float, float]:
        s = self.speed
        d = self.direction
        diag = s / math.sqrt(2)
        velocities = {
            "up": (0, -s),
            "down": (0, s),
            "left": (-s, 0),
            "right": (s, 0),
            "up_left": (-diag, -diag),
            "up_right": (diag, -diag),
            "down_left": (-diag, diag),
            "down_right": (diag, diag),
        }
        return velocities.get(d, (0, -s))

    def destroy(self):
        if (
            self.rect.y <= -50
            or self.rect.y >= HEIGHT + 50
            or self.rect.x <= -50
            or self.rect.x >= WIDTH + 50
        ):
            self.kill()

    def update(self):
        vx, vy = self._velocity
        self.rect.x += vx
        self.rect.y += vy
        self.destroy()