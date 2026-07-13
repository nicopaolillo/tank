import pygame
import random
import math
import numpy as np


class DebrisPiece(pygame.sprite.Sprite):
    _caches: dict[str, list[pygame.Surface]] = {}

    @classmethod
    def _load_parts(cls, prefix: str) -> list[pygame.Surface]:
        if prefix in cls._caches:
            return cls._caches[prefix]

        images = []
        for i in range(1, 8):
            path = f"assets/parts/{prefix}{i}.png"
            img = pygame.image.load(path).convert_alpha()

            arr = pygame.surfarray.pixels3d(img)
            alpha = pygame.surfarray.pixels_alpha(img)
            max_ch = np.max(arr, axis=2)
            min_ch = np.min(arr, axis=2)
            bg_mask = ((max_ch - min_ch) <= 15) & (min_ch >= 180)
            alpha[bg_mask] = 0
            del alpha
            del arr

            images.append(img)

        cls._caches[prefix] = images
        return images

    def __init__(self, x: int, y: int, prefix: str, part_index: int):
        super().__init__()

        images = self._load_parts(prefix)
        self.original_image = images[part_index].copy()
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))

        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(120, 350)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 80

        self.gravity = 350.0
        self.rotation_speed = random.uniform(-540, 540)
        self.current_angle = 0.0

        self.spawn_time = pygame.time.get_ticks()
        self.lifetime_ms = 1000
        self.last_update = self.spawn_time

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.spawn_time > self.lifetime_ms:
            self.kill()
            return

        dt = (now - self.last_update) / 1000.0
        self.last_update = now

        self.vy += self.gravity * dt
        self.rect.x += self.vx * dt
        self.rect.y += self.vy * dt

        self.current_angle += self.rotation_speed * dt
        self.image = pygame.transform.rotate(self.original_image, self.current_angle)
        self.rect = self.image.get_rect(center=self.rect.center)
