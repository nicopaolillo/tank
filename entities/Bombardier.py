from __future__ import annotations

from pathlib import Path
import math
import random
import pygame

from config.Settings import HEIGHT, WIDTH, BOMBARDIER_MAX_HP
from entities.Death import Death

BOAT_COMPOSITE_PATH = "assets/bombardier_lvl1/bombardier.jpg"
SHEET_PATH = "assets/bombardier_lvl1/bombardier_sheet.jpg"
DEATH_SHEET_PATH = Path("assets/bombardier_lvl1/BombardierDeathAnimation/BombardierDeath.jpg")
SHEET_REF_WIDTH = 1800
SHEET_REF_HEIGHT = 1200

# Fire/shot sprites from the package sheet.
CANNON_FIRE_RECTS = [
    pygame.Rect(1498, 1086, 96, 110),
    pygame.Rect(1602, 1086, 96, 110),
    pygame.Rect(1706, 1086, 96, 110),
]

PROJECTILE_CORE_RECTS = [
    pygame.Rect(1071, 1077, 34, 117),
    pygame.Rect(1438, 1077, 29, 117),
    pygame.Rect(1676, 1077, 18, 117),
]

PROJECTILE_TRAIL_RECTS = [
    pygame.Rect(1131, 1084, 98, 112),
    pygame.Rect(1313, 1084, 98, 112),
    pygame.Rect(1496, 1084, 98, 112),
]

# Ordered sprite sequence for the boss projectile animation.
# Put your new frames in one of these folders and keep their order in the list.
PROJECTILE_SEQUENCE_DIRS = [
    Path("assets/bombardier_lvl1/BoatShot"),
    Path("assets/bombardier_lvl1/BoatProjectile"),
]
PROJECTILE_SEQUENCE_FILES = [
    "shot_01.png",
    "shot_02.png",
    "shot_03.png",
    "shot_04.png",
    "shot_05.png",
]


def _load_sheet() -> pygame.Surface:
    return pygame.image.load(SHEET_PATH).convert()


def _scaled_rect(sheet: pygame.Surface, ref_rect: pygame.Rect) -> pygame.Rect:
    sheet_width, sheet_height = sheet.get_size()
    scale_x = sheet_width / SHEET_REF_WIDTH
    scale_y = sheet_height / SHEET_REF_HEIGHT

    x = int(ref_rect.x * scale_x)
    y = int(ref_rect.y * scale_y)
    w = max(1, int(ref_rect.width * scale_x))
    h = max(1, int(ref_rect.height * scale_y))

    x = max(0, min(x, sheet_width - 1))
    y = max(0, min(y, sheet_height - 1))

    if x + w > sheet_width:
        w = sheet_width - x
    if y + h > sheet_height:
        h = sheet_height - y

    return pygame.Rect(x, y, max(1, w), max(1, h))


def _trim_transparent_borders(surface: pygame.Surface) -> pygame.Surface:
    rect = surface.get_bounding_rect(min_alpha=1)
    if rect.width <= 0 or rect.height <= 0:
        return surface
    return surface.subsurface(rect).copy()


def _remove_checker_background(surface: pygame.Surface) -> pygame.Surface:
    """Remove editor checkerboard background from Bombardier.jpg via border flood-fill."""
    result = surface.convert_alpha()
    width, height = result.get_size()

    rgb = pygame.surfarray.pixels3d(result)
    alpha = pygame.surfarray.pixels_alpha(result)
    visited = [[False] * width for _ in range(height)]
    stack: list[tuple[int, int]] = []

    for x in range(width):
        stack.append((x, 0))
        stack.append((x, height - 1))
    for y in range(height):
        stack.append((0, y))
        stack.append((width - 1, y))

    while stack:
        x, y = stack.pop()
        if visited[y][x]:
            continue
        visited[y][x] = True

        r, g, b = rgb[x, y]
        # checkerboard tones are near-gray and relatively bright
        is_checker = abs(int(r) - int(g)) <= 14 and abs(int(g) - int(b)) <= 14 and int(r) >= 145
        if not is_checker:
            continue

        alpha[x, y] = 0
        if x > 0:
            stack.append((x - 1, y))
        if x < width - 1:
            stack.append((x + 1, y))
        if y > 0:
            stack.append((x, y - 1))
        if y < height - 1:
            stack.append((x, y + 1))

    del rgb
    del alpha
    return result


def _remove_sheet_gray_background(surface: pygame.Surface, tolerance: int = 24) -> pygame.Surface:
    """Remove connected gray background from sprites extracted from bombardier_lvl1.jpg."""
    result = surface.convert_alpha()
    width, height = result.get_size()
    rgb = pygame.surfarray.pixels3d(result)
    alpha = pygame.surfarray.pixels_alpha(result)
    visited = [[False] * width for _ in range(height)]
    stack: list[tuple[int, int]] = []

    for x in range(width):
        stack.append((x, 0))
        stack.append((x, height - 1))
    for y in range(height):
        stack.append((0, y))
        stack.append((width - 1, y))

    while stack:
        x, y = stack.pop()
        if visited[y][x]:
            continue
        visited[y][x] = True

        r, g, b = rgb[x, y]
        is_gray = abs(int(r) - int(g)) <= tolerance and abs(int(g) - int(b)) <= tolerance
        is_mid = 70 <= int(r) <= 200
        if not (is_gray and is_mid):
            continue

        alpha[x, y] = 0
        if x > 0:
            stack.append((x - 1, y))
        if x < width - 1:
            stack.append((x + 1, y))
        if y > 0:
            stack.append((x, y - 1))
        if y < height - 1:
            stack.append((x, y + 1))

    del rgb
    del alpha
    return result


def _extract_frames(
    crop_rects: list[pygame.Rect],
    layer_size: tuple[int, int],
    canvas_size: tuple[int, int],
    anchor_center: tuple[int, int],
) -> list[pygame.Surface]:
    sheet = _load_sheet()
    frames: list[pygame.Surface] = []

    for ref_rect in crop_rects:
        safe_rect = _scaled_rect(sheet, ref_rect)
        frame = sheet.subsurface(safe_rect).copy().convert_alpha()
        frame = _remove_sheet_gray_background(frame)
        frame = _trim_transparent_borders(frame)
        frame = pygame.transform.smoothscale(frame, layer_size)

        canvas = pygame.Surface(canvas_size, pygame.SRCALPHA)
        frame_rect = frame.get_rect(center=anchor_center)
        canvas.blit(frame, frame_rect)
        frames.append(canvas)

    return frames


def _load_projectile_sequence_frames() -> list[pygame.Surface]:
    canvas_size = (26, 44)

    for frame_dir in PROJECTILE_SEQUENCE_DIRS:
        if not frame_dir.exists() or not frame_dir.is_dir():
            continue

        # Try exact filenames first
        ordered_paths = [frame_dir / name for name in PROJECTILE_SEQUENCE_FILES]
        if all(path.exists() for path in ordered_paths):
            frame_paths = ordered_paths
        else:
            # Fall back to all PNGs sorted alphabetically
            frame_paths = sorted(frame_dir.glob("*.png"))

        if len(frame_paths) < 1:
            continue

        frames: list[pygame.Surface] = []
        for path in frame_paths:
            try:
                frame = pygame.image.load(str(path)).convert_alpha()
                frame = _trim_transparent_borders(frame)
                frame = pygame.transform.smoothscale(frame, canvas_size)
                frames.append(frame)
            except Exception:
                continue

        if len(frames) > 0:
            return frames

    return []


def _remove_dark_checker_background(surface: pygame.Surface, tolerance: int = 18) -> pygame.Surface:
    """Remove dark checkerboard background via border flood-fill."""
    result = surface.convert_alpha()
    width, height = result.get_size()

    rgb = pygame.surfarray.pixels3d(result)
    alpha = pygame.surfarray.pixels_alpha(result)
    visited = [[False] * width for _ in range(height)]
    stack: list[tuple[int, int]] = []

    for x in range(width):
        stack.append((x, 0))
        stack.append((x, height - 1))
    for y in range(height):
        stack.append((0, y))
        stack.append((width - 1, y))

    while stack:
        x, y = stack.pop()
        if visited[y][x]:
            continue
        visited[y][x] = True

        r, g, b = rgb[x, y]
        avg = (int(r) + int(g) + int(b)) // 3
        is_checker = (
            abs(int(r) - int(g)) <= tolerance
            and abs(int(g) - int(b)) <= tolerance
            and 25 <= avg <= 130
        )
        if not is_checker:
            continue

        alpha[x, y] = 0
        if x > 0:
            stack.append((x - 1, y))
        if x < width - 1:
            stack.append((x + 1, y))
        if y > 0:
            stack.append((x, y - 1))
        if y < height - 1:
            stack.append((x, y + 1))

    del rgb
    del alpha
    return result


def _extract_connected_frames(
    surface: pygame.Surface,
    min_pixels: int,
    max_frames: int,
    canvas_size: tuple[int, int],
) -> list[pygame.Surface]:
    width, height = surface.get_size()
    alpha = pygame.surfarray.pixels_alpha(surface)
    visited = [[False] * width for _ in range(height)]
    components: list[tuple[int, pygame.Rect]] = []

    for y in range(height):
        for x in range(width):
            if visited[y][x] or alpha[x, y] == 0:
                continue

            stack = [(x, y)]
            visited[y][x] = True
            pixels_count = 0
            min_x = max_x = x
            min_y = max_y = y

            while stack:
                cx, cy = stack.pop()
                if alpha[cx, cy] == 0:
                    continue

                pixels_count += 1
                min_x = min(min_x, cx)
                max_x = max(max_x, cx)
                min_y = min(min_y, cy)
                max_y = max(max_y, cy)

                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < width and 0 <= ny < height and not visited[ny][nx]:
                        visited[ny][nx] = True
                        if alpha[nx, ny] > 0:
                            stack.append((nx, ny))

            if pixels_count < min_pixels:
                continue

            rect = pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
            components.append((pixels_count, rect))

    del alpha

    selected = sorted(components, key=lambda item: item[0], reverse=True)[:max_frames]
    ordered_rects = [rect for _, rect in sorted(selected, key=lambda item: (item[1].top, item[1].left))]

    frames: list[pygame.Surface] = []
    for rect in ordered_rects:
        frame = surface.subsurface(rect).copy()
        frame = _trim_transparent_borders(frame)
        frame = pygame.transform.smoothscale(frame, (150, 150))

        canvas = pygame.Surface(canvas_size, pygame.SRCALPHA)
        canvas.blit(frame, frame.get_rect(center=(canvas_size[0] // 2, canvas_size[1] // 2)))
        frames.append(canvas)

    return frames


def _load_bombardier_sinking_frames() -> list[pygame.Surface]:
    if not DEATH_SHEET_PATH.exists():
        return []

    raw = pygame.image.load(str(DEATH_SHEET_PATH)).convert_alpha()
    cleaned = _remove_dark_checker_background(raw)
    return _extract_connected_frames(cleaned, min_pixels=5000, max_frames=6, canvas_size=(180, 180))


class BoatProjectile(pygame.sprite.Sprite):
    _frames_cache: list[pygame.Surface] | None = None

    def __init__(self, x: int, y: int, velocity: pygame.Vector2):
        super().__init__()
        self.frames = self._get_frames()
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))

        if velocity.length() == 0:
            velocity = pygame.Vector2(0, 1)
        self.velocity = velocity.normalize() * 5.2
        self.animation_interval = 70
        self.last_frame_ms = pygame.time.get_ticks()

    @classmethod
    def _get_frames(cls) -> list[pygame.Surface]:
        if cls._frames_cache is not None:
            return cls._frames_cache

        sequence_frames = _load_projectile_sequence_frames()
        if sequence_frames:
            cls._frames_cache = sequence_frames
            return cls._frames_cache

        core_frames = _extract_frames(PROJECTILE_CORE_RECTS, (20, 34), (26, 44), (13, 18))
        trail_frames = _extract_frames(PROJECTILE_TRAIL_RECTS, (24, 42), (26, 44), (13, 24))

        frames: list[pygame.Surface] = []
        total = max(len(core_frames), len(trail_frames))
        for index in range(total):
            composite = pygame.Surface((26, 44), pygame.SRCALPHA)
            composite.blit(trail_frames[index % len(trail_frames)], (0, 0))
            composite.blit(core_frames[index % len(core_frames)], (0, 0))
            frames.append(composite)

        cls._frames_cache = frames
        return frames

    def update(self) -> None:
        now = pygame.time.get_ticks()
        if now - self.last_frame_ms >= self.animation_interval:
            self.last_frame_ms = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            center = self.rect.center
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=center)

        self.rect.x += int(self.velocity.x)
        self.rect.y += int(self.velocity.y)

        if (
            self.rect.right < -40
            or self.rect.left > WIDTH + 40
            or self.rect.bottom < -40
            or self.rect.top > HEIGHT + 40
        ):
            self.kill()


class BombardierSinkingEffect(pygame.sprite.Sprite):
    _frames_cache: list[pygame.Surface] | None = None

    def __init__(self, center: tuple[int, int]):
        super().__init__()
        self.frames = self._get_frames()
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=center)
        self.animation_interval_ms = 95
        self.last_frame_ms = pygame.time.get_ticks()
        self.loop_count = 3
        self.completed_loops = 0

    @classmethod
    def _get_frames(cls) -> list[pygame.Surface]:
        if cls._frames_cache is not None:
            return cls._frames_cache

        frames = _load_bombardier_sinking_frames()
        if not frames:
            fallback = pygame.Surface((180, 180), pygame.SRCALPHA)
            pygame.draw.circle(fallback, (160, 230, 240, 70), (90, 90), 56, 6)
            pygame.draw.circle(fallback, (220, 250, 255, 90), (90, 90), 30, 4)
            frames = [fallback]

        cls._frames_cache = frames
        return cls._frames_cache

    def update(self) -> None:
        now = pygame.time.get_ticks()
        if now - self.last_frame_ms < self.animation_interval_ms:
            return

        self.last_frame_ms = now
        self.frame_index += 1
        if self.frame_index >= len(self.frames):
            self.completed_loops += 1
            if self.completed_loops >= self.loop_count:
                self.kill()
                return
            self.frame_index = 0

        center = self.rect.center
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=center)


class Bombardier(pygame.sprite.Sprite):
    _base_frames_cache: list[pygame.Surface] | None = None
    _water_frames_cache: list[pygame.Surface] | None = None
    _fire_frames_cache: list[pygame.Surface] | None = None
    _destroyed_surface_cache: pygame.Surface | None = None

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
        self.base_frames = self._get_base_frames()
        self.water_frames = self._get_water_frames()
        self.fire_frames = self._get_fire_frames()
        self.frame_index = 0
        self.image = self.base_frames[self.frame_index]
        self.rect = self.image.get_rect(center=((left_bound + right_bound) // 2, y_position))

        self.enemy_shoot_list = enemy_shoot_list
        self.all_sprites = all_sprites
        self.target = target

        self.left_bound = left_bound
        self.right_bound = right_bound
        self.speed_x = 2.2
        self.direction = 1
        self.max_hp = BOMBARDIER_MAX_HP
        self.hp = self.max_hp

        self.wave_interval_ms = 95
        self.last_wave_ms = pygame.time.get_ticks()

        self.next_shot_ms = self.last_wave_ms + random.randint(900, 1400)
        self.shoot_fx_start_ms = 0
        self.shoot_fx_until_ms = 0
        self.shoot_fx_duration_ms = 230
        self.water_anim_interval_ms = 90
        self.fire_anim_interval_ms = 65
        self._cannon_side = -1
        self.is_destroyed = False
        self.death_sequence_started = False
        self.explosions_remaining = 0
        self.next_explosion_ms = 0
        self.explosion_interval_ms = 85
        self.final_center = self.rect.center
        self.sinking_effect_spawned = False

    @classmethod
    def _get_base_frames(cls) -> list[pygame.Surface]:
        if cls._base_frames_cache is not None:
            return cls._base_frames_cache

        raw = pygame.image.load(BOAT_COMPOSITE_PATH).convert()
        raw = _remove_checker_background(raw)
        raw = _trim_transparent_borders(raw)
        boat = pygame.transform.smoothscale(raw, (108, 150))

        # Small wave movement by subtle ripple sway while moving.
        frames: list[pygame.Surface] = []
        for dx in (0, 1, 0, -1):
            frame = pygame.Surface((108, 300), pygame.SRCALPHA)
            frame.blit(boat, (dx, 50))
            frames.append(frame)

        cls._base_frames_cache = frames
        return frames

    @classmethod
    def _get_fire_frames(cls) -> list[pygame.Surface]:
        if cls._fire_frames_cache is not None:
            return cls._fire_frames_cache

        canvas_size = (108, 300)
        # Centered at cannon tips from Bombardier.jpg composite.
        cls._fire_frames_cache = _extract_frames(CANNON_FIRE_RECTS, (40, 46), canvas_size, (54, 220))
        return cls._fire_frames_cache

    @classmethod
    def _get_water_frames(cls) -> list[pygame.Surface]:
        if cls._water_frames_cache is not None:
            return cls._water_frames_cache

        canvas_size = (108, 300)
        center_x = 54
        center_y = 126
        base_w = 78
        base_h = 150
        frame_count = 8

        frames: list[pygame.Surface] = []
        for phase in range(frame_count):
            frame = pygame.Surface(canvas_size, pygame.SRCALPHA)
        
            # Draw multiple animated rings to fake water ripples around hull.
            for ring in range(3):
                t = ((phase + ring * 2) % frame_count) / frame_count
                pulse = math.sin(t * math.pi * 2.0)

                grow = 8 + ring * 8 + int(3 * pulse)
                rect = pygame.Rect(0, 0, base_w + grow * 2, base_h + grow * 2)
                rect.center = (center_x, center_y)

                alpha = max(18, 70 - ring * 18)
                color = (82, 136, 198, alpha)
                pygame.draw.ellipse(frame, color, rect, 1 + ring)

            # Small wake accents at bow and stern to make motion feel watery.
            bow = pygame.Rect(0, 0, 34, 10)
            bow.center = (center_x, center_y - 70)
            stern = pygame.Rect(0, 0, 28, 8)
            stern.center = (center_x, center_y + 76)
            pygame.draw.ellipse(frame, (98, 160, 225, 44), bow, 1)
            pygame.draw.ellipse(frame, (90, 150, 215, 36), stern, 1)

            frames.append(frame)

        cls._water_frames_cache = frames
        return frames

    def update(self) -> None:
        if self.death_sequence_started:
            self._run_death_sequence()
            return

        self._move_horizontally()
        self._animate()
        self._try_shoot()

    def take_damage(self, amount: int) -> bool:
        if self.is_destroyed:
            return False

        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self._begin_destruction()
            return True

        return False

    @classmethod
    def _get_destroyed_surface(cls, size: tuple[int, int]) -> pygame.Surface:
        cached = cls._destroyed_surface_cache
        if cached is None or cached.get_size() != size:
            cls._destroyed_surface_cache = pygame.Surface(size, pygame.SRCALPHA)
        return cls._destroyed_surface_cache.copy()

    def _begin_destruction(self) -> None:
        self.is_destroyed = True
        self.death_sequence_started = True
        self.final_center = self.rect.center
        self.speed_x = 0.0
        self.shoot_fx_start_ms = 0
        self.shoot_fx_until_ms = 0
        self.next_shot_ms = 2**31 - 1
        self.explosions_remaining = 10
        self.next_explosion_ms = pygame.time.get_ticks()

        # Release instance references to large animation assets and hide the hull immediately.
        self.base_frames = []
        self.water_frames = []
        self.fire_frames = []
        self.image = self._get_destroyed_surface(self.rect.size)
        self.rect = self.image.get_rect(center=self.final_center)

    def _run_death_sequence(self) -> None:
        now = pygame.time.get_ticks()
        if self.explosions_remaining > 0 and now >= self.next_explosion_ms:
            offset_x = random.randint(-28, 28)
            offset_y = random.randint(-44, 44)
            explosion = Death(self.final_center[0] + offset_x, self.final_center[1] + offset_y)
            explosion.animate()
            self.all_sprites.add(explosion)

            self.explosions_remaining -= 1
            self.next_explosion_ms = now + self.explosion_interval_ms

        if self.explosions_remaining <= 0 and not self.sinking_effect_spawned:
            self.sinking_effect_spawned = True
            sinking = BombardierSinkingEffect(self.final_center)
            self.all_sprites.add(sinking)
            self.kill()

    def _animate(self) -> None:
        now = pygame.time.get_ticks()

        if abs(self.speed_x) > 0 and now - self.last_wave_ms >= self.wave_interval_ms:
            self.last_wave_ms = now
            self.frame_index = (self.frame_index + 1) % len(self.base_frames)

        center = self.rect.center
        boat_frame = self.base_frames[self.frame_index]
        water_index = (now // self.water_anim_interval_ms) % len(self.water_frames)
        frame = self.water_frames[int(water_index)].copy()
        frame.blit(boat_frame, (0, 0))

        if self.shoot_fx_start_ms and now < self.shoot_fx_until_ms:
            elapsed = now - self.shoot_fx_start_ms
            fire_index = (elapsed // self.fire_anim_interval_ms) % len(self.fire_frames)
            fire_frame = self.fire_frames[int(fire_index)]
            frame.blit(fire_frame, (0, 0))

        if self.direction < 0:
            frame = pygame.transform.flip(frame, True, False)

        self.image = frame
        self.rect = self.image.get_rect(center=center)

    def _move_horizontally(self) -> None:
        self.rect.x += int(self.speed_x * self.direction)

        if self.rect.left <= self.left_bound:
            self.rect.left = self.left_bound
            self.direction = 1
        elif self.rect.right >= self.right_bound:
            self.rect.right = self.right_bound
            self.direction = -1

    def _try_shoot(self) -> None:
        now = pygame.time.get_ticks()
        if now < self.next_shot_ms:
            return

        # Alternate left/right cannon tips from the composite sprite.
        self._cannon_side *= -1
        muzzle_x = self.rect.centerx + (7 * self._cannon_side)
        muzzle_y = self.rect.centery + 70

        origin = pygame.Vector2(muzzle_x, muzzle_y)
        target_center = pygame.Vector2(self.target.rect.centerx, self.target.rect.centery)
        velocity = target_center - origin

        projectile = BoatProjectile(int(origin.x), int(origin.y), velocity)
        self.all_sprites.add(projectile)
        self.enemy_shoot_list.add(projectile)

        self.shoot_fx_start_ms = now
        self.shoot_fx_until_ms = now + self.shoot_fx_duration_ms
        self.next_shot_ms = now + random.randint(700, 1200)
