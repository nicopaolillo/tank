import pygame
from pathlib import Path


class SmokeTrail(pygame.sprite.Sprite):
    _frames: list[pygame.Surface] | None = None

    def __init__(self, x: int, y: int):
        super().__init__()

        self.frames = self._load_frames()
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))

        self.frame_delay_ms = 32
        self.frame_step = 2
        self.last_tick = pygame.time.get_ticks()

    @classmethod
    def _load_frames(cls) -> list[pygame.Surface]:
        if cls._frames is not None:
            return cls._frames

        frames: list[pygame.Surface] = []
        frame_dir = Path("assets/SmokeFrames")
        for frame_path in sorted(frame_dir.glob("*.png")):
            frame = pygame.image.load(frame_path.as_posix()).convert_alpha()
            frame = pygame.transform.smoothscale(frame, (42, 42))
            frames.append(frame)

        if not frames:
            fallback = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(fallback, (120, 120, 120, 160), (12, 12), 10)
            frames = [fallback]

        cls._frames = frames
        return cls._frames

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_tick < self.frame_delay_ms:
            return

        self.last_tick = now
        self.frame_index += self.frame_step
        if self.frame_index >= len(self.frames):
            self.kill()
            return

        center = self.rect.center
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=center)
