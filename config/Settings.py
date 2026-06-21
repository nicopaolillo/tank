import pygame
from enum import Enum

# Screen dimensions
WIDTH = 1000
HEIGHT = 700
FULLSCREEN = True

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SAND_COLOR = (195, 169, 139)
GREEN_TEXT = (173, 255, 47)
DARK_GREEN_TEXT = (0, 143, 57)
RED_TEXT = (255, 0, 0)

# Game mechanics
PLAYER_INITIAL_HP = 200
PLAYER_INITIAL_LEVEL = 1
PLAYER_INITIAL_MISSILES = 3
PLAYER_INITIAL_SUPPORT = 1
PLAYER_MAX_SUPPORT = 2
PLAYER_MAX_SHIELDS = 2
PLAYER_SPEED = 3
PLAYER_BOUNDS_LEFT = 150
PLAYER_BOUNDS_RIGHT = 850

TANK_RED_SPAWN_COUNT = 2
TANK_GREEN_SPAWN_COUNT = 1

MISSILE_RECHARGE_TIME = 3.0  # seconds
MISSILE_SCORE_PENALTY_PER_SECOND = 300
# cooldown in seconds (was described as deciseconds before)
MISSILE_FIRE_COOLDOWN = 1.5  # seconds

TANK_RED_HIT_DAMAGE = 20
TANK_GREEN_HIT_DAMAGE = 40
TANK_RED_KILL_POINTS = 200
TANK_GREEN_KILL_POINTS = 300
TANK_GREEN_KILL_POINTS_ALONE = 500
AIR_SUPPORT_RED_POINTS = 200
AIR_SUPPORT_GREEN_POINTS = 300

# Sound paths
SOUNDS = {
    'game': 'sound/song.ogg',
    'options': 'sound/options.ogg',
    'menu': 'sound/main.ogg',
    'gameover': 'sound/gameover.ogg',
    'engine': 'sound/engine.ogg',
    'explosion': 'sound/explosion.ogg',
    'shoot': 'sound/shoot.ogg',
    'iron': 'sound/iron_sound.ogg',
    'select': 'sound/selection.ogg',
}

# Asset paths
BACKGROUND_IMAGE = 'assets/background_2.png'
BACKGROUND_IMAGES = [
    'assets/background_lvl1_A.png',
    'assets/background_lvl1_B.png',
    'assets/background_lvl1_C.png',
    'assets/background_lvl1_D.png',
]
PLAYER_SPRITES = {
    'default': 'assets/player_main.png',
    'left': 'assets/player_main.png',
    'right': 'assets/player_main.png',
    'down': 'assets/player_main.png',
}

PLAYER_SPRITE_SIZE = (75, 75)

# UI
FONT_SIZE_SMALL = 40
FONT_SIZE_LARGE = 100

# Game speed
TARGET_FPS = 60
GAME_LOOP_DELAY = 3200  # milliseconds before first game


class GameConfig:
    """Centralizes all pygame initialization and game configuration."""
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Display window and virtual render surface
        if FULLSCREEN:
            display_info = pygame.display.Info()
            display_size = (display_info.current_w, display_info.current_h)
            self.window = pygame.display.set_mode(display_size, pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode((WIDTH, HEIGHT))

        self.screen = pygame.Surface((WIDTH, HEIGHT)).convert()
        self._last_window_size = self.window.get_size()
        self._display_rect = self._compute_display_rect(self._last_window_size)
        pygame.display.set_caption("Tank Game")
        
        # Clock
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_small = pygame.font.SysFont(None, FONT_SIZE_SMALL)
        self.font_large = pygame.font.SysFont(None, FONT_SIZE_LARGE)
        
        # Sound channels
        self.game_channel = pygame.mixer.Channel(0)
        self.options_channel = pygame.mixer.Channel(1)
        self.main_channel = pygame.mixer.Channel(2)
        self.gameover_channel = pygame.mixer.Channel(3)
        
        # Sounds (loaded on demand to avoid blocking)
        self._sounds = {}
        self._player_sprite_cache = {}

    def _compute_display_rect(self, window_size: tuple[int, int]) -> pygame.Rect:
        window_width, window_height = window_size
        scale = min(window_width / WIDTH, window_height / HEIGHT)
        render_width = max(1, int(WIDTH * scale))
        render_height = max(1, int(HEIGHT * scale))
        offset_x = (window_width - render_width) // 2
        offset_y = (window_height - render_height) // 2
        return pygame.Rect(offset_x, offset_y, render_width, render_height)

    def present(self) -> None:
        window_size = self.window.get_size()
        if window_size != self._last_window_size:
            self._last_window_size = window_size
            self._display_rect = self._compute_display_rect(window_size)

        scaled_frame = pygame.transform.smoothscale(self.screen, self._display_rect.size)
        self.window.fill(BLACK)
        self.window.blit(scaled_frame, self._display_rect.topleft)
        pygame.display.flip()
    
    def get_sound(self, key: str) -> pygame.mixer.Sound:
        """Load and cache sounds on demand."""
        if key not in self._sounds:
            if key in SOUNDS:
                self._sounds[key] = pygame.mixer.Sound(SOUNDS[key])
        return self._sounds.get(key)
    
    def get_player_sprite(self, direction: str = 'default') -> pygame.Surface:
        """Load player sprite images."""
        cached = self._player_sprite_cache.get(direction)
        if cached is not None:
            return cached.copy()

        sprite_path = PLAYER_SPRITES.get(direction, PLAYER_SPRITES['default'])
        image = pygame.image.load(sprite_path).convert_alpha()

        # Remove transparent margins so no boxed look remains after scaling.
        crop_rect = image.get_bounding_rect(min_alpha=1)
        if crop_rect.width > 0 and crop_rect.height > 0:
            image = image.subsurface(crop_rect).copy()

        image = pygame.transform.smoothscale(image, PLAYER_SPRITE_SIZE)

        if direction == 'left':
            image = pygame.transform.rotate(image, 90)
        elif direction == 'right':
            image = pygame.transform.rotate(image, -90)
        elif direction == 'down':
            image = pygame.transform.rotate(image, 180)

        self._player_sprite_cache[direction] = image
        return image.copy()