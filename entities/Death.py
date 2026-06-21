import pygame


class Death(pygame.sprite.Sprite):
    _cached_frames: list[pygame.Surface] | None = None

    def __init__(self, x, y):
        super().__init__()

        if Death._cached_frames is None:
            Death._cached_frames = [
                pygame.image.load(f"assets/TankExplosion/{i:04d}.png").convert_alpha()
                for i in range(1, 16)
            ]

        self.sprites = Death._cached_frames

        self.is_animating = False
        self.current_sprite = 0

        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()

        self.rect.x = x - 30
        self.rect.y = y - 30

        self.animationTime = 20
        self.time = pygame.time.get_ticks()

    def animate(self):
        self.is_animating = True

    def update(self):
        ahora = pygame.time.get_ticks()

        if ahora - self.time > self.animationTime:
            self.time = ahora

            if self.is_animating:
                self.current_sprite += 1

            if self.current_sprite >= len(self.sprites):
                self.kill()
                return

            self.image = self.sprites[self.current_sprite]