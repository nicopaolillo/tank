from __future__ import annotations

import math
import random
import pygame

from config.Settings import HEIGHT, WIDTH, HELICOPTER_MAX_HP, HELICOPTER_SHOOT_COOLDOWN
from entities.Death import Death

HELICOPTER_SPRITE_PATH = "assets/helicopter.png"


class HelicopterProjectile(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, velocity: pygame.Vector2):
        super().__init__()
        self.image = pygame.Surface((8, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (255, 200, 50, 255), (0, 0, 8, 20))
        self.rect = self.image.get_rect(center=(x, y))

        if velocity.length() == 0:
            velocity = pygame.Vector2(0, 1)
        self.velocity = velocity.normalize() * 6.0
        self.damage = 15

    def update(self) -> None:
        self.rect.x += int(self.velocity.x)
        self.rect.y += int(self.velocity.y)

        if (
            self.rect.right < -40
            or self.rect.left > WIDTH + 40
            or self.rect.bottom < -40
            or self.rect.top > HEIGHT + 40
        ):
            self.kill()


class Helicopter(pygame.sprite.Sprite):
    _base_image_cache: pygame.Surface | None = None

    def __init__(
        self,
        enemy_shoot_list: pygame.sprite.Group,
        all_sprites: pygame.sprite.Group,
        target,
        left_bound: int,
        right_bound: int,
        y_position: int,
    ):
        super().__init__()
        self._rotor_frames = self._get_rotor_frames()
        self.image = self._rotor_frames[0].copy()
        self.rect = self.image.get_rect(center=((left_bound + right_bound) // 2, -120))

        self.enemy_shoot_list = enemy_shoot_list
        self.all_sprites = all_sprites
        self.target = target

        self.left_bound = left_bound
        self.right_bound = right_bound
        self._target_y = y_position
        self._entrance_speed = 1.5
        self.speed_x = 3.2
        self.direction = 1
        self.max_hp = HELICOPTER_MAX_HP
        self.hp = self.max_hp

        self._entering = True
        self.is_destroyed = False
        self.death_sequence_started = False
        self.explosions_remaining = 0
        self.next_explosion_ms = 0
        self.explosion_interval_ms = 85
        self.final_center = self.rect.center

        now = pygame.time.get_ticks()
        self.next_shot_ms = now + random.randint(600, 1000)
        self._barrel_side = -1

        self._bob_offset = 0.0
        self._bob_timer = 0.0
        self._shield_active = False

    @classmethod
    def _get_base_image(cls) -> pygame.Surface:
        if cls._base_image_cache is not None:
            return cls._base_image_cache
        raw = pygame.image.load(HELICOPTER_SPRITE_PATH).convert_alpha()
        rect = raw.get_bounding_rect(min_alpha=1)
        if rect.width > 0 and rect.height > 0:
            raw = raw.subsurface(rect).copy()
        cls._base_image_cache = pygame.transform.smoothscale(raw, (160, 120))
        return cls._base_image_cache

    @classmethod
    def _get_rotor_frames(cls) -> list[pygame.Surface]:
        base = cls._get_base_image()
        return [base.copy()]

    def update(self) -> None:
        if self.death_sequence_started:
            self._run_death_sequence()
            return

        if self._entering:
            self._enter_from_top()
            return

        self._move_horizontally()
        self._bob()
        self._animate_rotor()
        self._try_shoot()

    def _enter_from_top(self) -> None:
        self.rect.y += int(self._entrance_speed)
        if self.rect.y >= self._target_y:
            self.rect.y = self._target_y
            self._entering = False
            self.final_center = self.rect.center
            self.next_shot_ms = pygame.time.get_ticks() + random.randint(600, 1000)

    def take_damage(self, amount: int) -> bool:
        if self.is_destroyed:
            return False
        if self._entering or self._shield_active:
            return False

        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self._begin_destruction()
            return True
        return False

    def _begin_destruction(self) -> None:
        self.is_destroyed = True
        self.death_sequence_started = True
        self.final_center = self.rect.center
        self.speed_x = 0.0
        self.next_shot_ms = 2**31 - 1
        self.explosions_remaining = 8
        self.next_explosion_ms = pygame.time.get_ticks()
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)

    def _run_death_sequence(self) -> None:
        now = pygame.time.get_ticks()
        if self.explosions_remaining > 0 and now >= self.next_explosion_ms:
            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-20, 20)
            explosion = Death(self.final_center[0] + offset_x, self.final_center[1] + offset_y)
            explosion.animate()
            self.all_sprites.add(explosion)

            self.explosions_remaining -= 1
            self.next_explosion_ms = now + self.explosion_interval_ms

        if self.explosions_remaining <= 0:
            self.kill()

    def _move_horizontally(self) -> None:
        self.rect.x += int(self.speed_x * self.direction)

        if self.rect.left <= self.left_bound:
            self.rect.left = self.left_bound
            self.direction = 1
        elif self.rect.right >= self.right_bound:
            self.rect.right = self.right_bound
            self.direction = -1

    def _bob(self) -> None:
        self._bob_timer += 0.08
        new_offset = math.sin(self._bob_timer) * 4
        dy = new_offset - self._bob_offset
        self._bob_offset = new_offset
        self.rect.y += int(dy)

    def _animate_rotor(self) -> None:
        center = self.rect.center
        frame = self._rotor_frames[0]

        if self.direction < 0:
            frame = pygame.transform.flip(frame, True, False)

        self.image = frame
        self.rect = self.image.get_rect(center=center)

    def _try_shoot(self) -> None:
        now = pygame.time.get_ticks()
        if now < self.next_shot_ms:
            return

        self._barrel_side *= -1
        muzzle_x = self.rect.centerx + (15 * self._barrel_side)
        muzzle_y = self.rect.bottom - 5

        origin = pygame.Vector2(muzzle_x, muzzle_y)
        target_center = pygame.Vector2(self.target.rect.centerx, self.target.rect.centery)
        velocity = target_center - origin

        projectile = HelicopterProjectile(int(origin.x), int(origin.y), velocity)
        self.all_sprites.add(projectile)
        self.enemy_shoot_list.add(projectile)

        self.next_shot_ms = now + random.randint(
            int(HELICOPTER_SHOOT_COOLDOWN * 700),
            int(HELICOPTER_SHOOT_COOLDOWN * 1200),
        )
