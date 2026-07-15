from __future__ import annotations

import math
import random
import pygame

from config.Settings import HEIGHT, WIDTH, HELICOPTER_MAX_HP, HELICOPTER_SHOOT_COOLDOWN
from entities.Death import Death

HELICOPTER_FUSELAJE_PATH = "assets/helicopter_fuselaje.png"
HELICOPTER_ASPAS_PATH = "assets/helicopter_aspas.png"


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
    _fuselaje_cache: pygame.Surface | None = None
    _aspas_cache: pygame.Surface | None = None
    _fuselaje_size: tuple[int, int] = (100, 170)
    _aspas_size: tuple[int, int] = (195, 59)

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
        self._fuselaje = self._get_fuselaje()
        self._aspas_original = self._get_aspas()
        self._rotor_angle = 0.0
        self._rotor_speed = 25.0
        self.image = self._compose_helicopter()
        self.rect = self.image.get_rect(center=((left_bound + right_bound) // 2, -120))

        self.enemy_shoot_list = enemy_shoot_list
        self.all_sprites = all_sprites
        self.target = target

        self.left_bound = left_bound
        self.right_bound = right_bound
        self._target_y = y_position
        self._entrance_speed = 1.5
        self.speed = 2.5
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

        self._patrol_side = 0
        self._facing_angle = 0.0

    @classmethod
    def _get_fuselaje(cls) -> pygame.Surface:
        if cls._fuselaje_cache is not None:
            return cls._fuselaje_cache
        raw = pygame.image.load(HELICOPTER_FUSELAJE_PATH).convert_alpha()
        rect = raw.get_bounding_rect(min_alpha=1)
        if rect.width > 0 and rect.height > 0:
            raw = raw.subsurface(rect).copy()
        cls._fuselaje_cache = pygame.transform.smoothscale(raw, cls._fuselaje_size)
        return cls._fuselaje_cache

    @classmethod
    def _get_aspas(cls) -> pygame.Surface:
        if cls._aspas_cache is not None:
            return cls._aspas_cache
        raw = pygame.image.load(HELICOPTER_ASPAS_PATH).convert_alpha()
        rect = raw.get_bounding_rect(min_alpha=1)
        if rect.width > 0 and rect.height > 0:
            raw = raw.subsurface(rect).copy()
        cls._aspas_cache = pygame.transform.smoothscale(raw, cls._aspas_size)
        return cls._aspas_cache

    def _compose_helicopter(self) -> pygame.Surface:
        fw, fh = self._fuselaje_size
        aw, ah = self._aspas_size

        diag = int(math.sqrt(aw * aw + ah * ah))
        pad_x = (diag - fw) // 2 + 4
        pad_y = (diag - fh) // 2 + 4
        pad_x = max(0, pad_x)
        pad_y = max(0, pad_y)

        comp_w = fw + pad_x * 2
        comp_h = fh + pad_y * 2
        composite = pygame.Surface((comp_w, comp_h), pygame.SRCALPHA)

        composite.blit(self._fuselaje, (pad_x, pad_y))

        aspas_center_x = comp_w // 2
        aspas_center_y = comp_h // 2 + 15

        rotated_aspas = pygame.transform.rotate(self._aspas_original, self._rotor_angle)
        aspas_rect = rotated_aspas.get_rect(center=(aspas_center_x, aspas_center_y))

        composite.blit(rotated_aspas, aspas_rect)
        return composite

    def update(self) -> None:
        if self.death_sequence_started:
            self._run_death_sequence()
            return

        if self._entering:
            self._enter_from_top()
            self._animate_rotor()
            return

        self._patrol_square()
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
        self.speed = 0.0
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

    def _patrol_square(self) -> None:
        cx, cy = self.rect.center
        half_w = self.rect.width // 2
        half_h = self.rect.height // 2

        top = self._target_y
        bottom = min(HEIGHT - 80, top + 200)
        left = self.left_bound + half_w
        right = self.right_bound - half_w

        corners = [
            (left, top),
            (right, top),
            (right, bottom),
            (left, bottom),
        ]

        target_x, target_y = corners[self._patrol_side]
        dx = target_x - cx
        dy = target_y - cy
        dist = math.hypot(dx, dy)

        if dist < self.speed * 2:
            self._patrol_side = (self._patrol_side + 1) % 4
        else:
            self.rect.x += int(self.speed * dx / dist)
            self.rect.y += int(self.speed * dy / dist)

    def _animate_rotor(self) -> None:
        center = self.rect.center
        self._rotor_angle = (self._rotor_angle + self._rotor_speed) % 360
        self.image = self._compose_helicopter()

        if self.target is not None:
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            self._facing_angle = math.degrees(math.atan2(-dx, -dy)) + 180
            self.image = pygame.transform.rotate(self.image, self._facing_angle)

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
