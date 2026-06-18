import pygame
from enum import Enum

# Screen dimensions
WIDTH = 1000
HEIGHT = 700

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
PLAYER_SPEED = 3
PLAYER_BOUNDS_LEFT = 200
PLAYER_BOUNDS_RIGHT = 800

TANK_RED_SPAWN_COUNT = 5
TANK_GREEN_SPAWN_COUNT = 3

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
PLAYER_SPRITES = {
    'default': 'assets/player.png',
    'left': 'assets/player_left.png',
    'right': 'assets/player_right.png',
    'down': 'assets/player_down.png',
}

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
        
        # Screen
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
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
    
    def get_sound(self, key: str) -> pygame.mixer.Sound:
        """Load and cache sounds on demand."""
        if key not in self._sounds:
            if key in SOUNDS:
                self._sounds[key] = pygame.mixer.Sound(SOUNDS[key])
        return self._sounds.get(key)
    
    def get_player_sprite(self, direction: str = 'default') -> pygame.Surface:
        """Load player sprite images."""
        sprite_path = PLAYER_SPRITES.get(direction, PLAYER_SPRITES['default'])
        image = pygame.image.load(sprite_path).convert()
        image.set_colorkey(BLACK)
        return image