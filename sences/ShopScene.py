from __future__ import annotations

import sys
import pygame

from config.Settings import GameConfig, WIDTH, HEIGHT, DARK_GREEN_TEXT, GREEN_TEXT, PLAYER_SPRITE_SIZE
from sences.Scene import Scene
from entities.SmokeTrail import SmokeTrail


UPGRADE_ICON_SIZE = 80
TANK_PREVIEW_SIZE = (120, 120)

UPGRADE_ITEMS = [
    {"name": "Armadura", "key": "armor", "icon": "assets/armor.png",
     "desc": "+200 HP", "attr": "armor_active"},
    {"name": "Doble Ca\u00f1\u00f3n", "key": "double_barrel", "icon": "assets/double_barrel.png",
     "desc": "Dos proyectiles", "attr": "double_barrel_active"},
    {"name": "Orugas", "key": "tank_track", "icon": "assets/tank_track.png",
     "desc": "M\u00e1s velocidad", "attr": "tank_track_active"},
]

TANK_SPRITE_KEYS = ["armor", "double_barrel", "tank_track"]

BACK_LABEL = "Atr\u00e1s"


class ShopScene(Scene):

    def __init__(self, config: GameConfig, scene_manager, player):
        super().__init__(config)
        self.scene_manager = scene_manager
        self.player = player

        self._raw_background = pygame.image.load("assets/menu_shop.png").convert()
        self._background_size = self.config.screen.get_size()
        self.background = self._build_cover_background(self._raw_background, self._background_size)

        self.selection_index = 0
        self._pre_game_upgrade = None
        self._back_selected = False
        self._up_held = False
        self._smoke_list = pygame.sprite.Group()
        self._last_smoke_ms = 0
        self._smoke_interval_ms = 90

        self.icons = []
        for item in UPGRADE_ITEMS:
            try:
                icon = pygame.image.load(item["icon"]).convert_alpha()
                icon = pygame.transform.smoothscale(icon, (UPGRADE_ICON_SIZE, UPGRADE_ICON_SIZE))
            except pygame.error:
                icon = pygame.Surface((UPGRADE_ICON_SIZE, UPGRADE_ICON_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(icon, DARK_GREEN_TEXT, icon.get_rect(), 2)
            self.icons.append(icon)

        self.tank_previews = []
        for key in TANK_SPRITE_KEYS:
            path = f"assets/player_{key}.png"
            try:
                img = pygame.image.load(path).convert_alpha()
            except (pygame.error, FileNotFoundError):
                img = pygame.Surface(PLAYER_SPRITE_SIZE, pygame.SRCALPHA)
                img.fill((80, 80, 80, 200))
            img = pygame.transform.smoothscale(img, TANK_PREVIEW_SIZE)
            self.tank_previews.append(img)

        self._selected = False
        self._applied_upgrade = None

    def _build_cover_background(self, image: pygame.Surface, target_size: tuple[int, int]) -> pygame.Surface:
        src_w, src_h = image.get_size()
        dst_w, dst_h = target_size
        if src_w == 0 or src_h == 0:
            return pygame.Surface((dst_w, dst_h)).convert()
        scale = max(dst_w / src_w, dst_h / src_h)
        scaled_w = max(1, int(src_w * scale))
        scaled_h = max(1, int(src_h * scale))
        scaled = pygame.transform.smoothscale(image, (scaled_w, scaled_h))
        offset_x = (scaled_w - dst_w) // 2
        offset_y = (scaled_h - dst_h) // 2
        cropped = pygame.Surface((dst_w, dst_h)).convert()
        cropped.blit(scaled, (-offset_x, -offset_y))
        return cropped

    def _reload_background_if_needed(self) -> None:
        current_size = self.config.screen.get_size()
        if current_size == self._background_size:
            return
        self._background_size = current_size
        self.background = self._build_cover_background(self._raw_background, current_size)

    def on_activate(self) -> None:
        self.config.engine_channel.play(self.config.get_sound('engine'), loops=-1, fade_ms=100)

    def on_deactivate(self) -> None:
        self.config.engine_channel.stop()

    def handle_events(self, events: list[pygame.event.EventType]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self._selected:
                    self._return_to_menu()
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_DOWN:
                    if not self._back_selected:
                        self.config.get_sound("select").play()
                        self._back_selected = True
                elif event.key == pygame.K_UP:
                    if self._back_selected:
                        self._back_selected = False
                    else:
                        self._up_held = True
                        self.config.engine_channel.stop()
                        self.config.engine_channel.play(self.config.get_sound('engine_2'), loops=-1)
                        self._spawn_smoke_now()
                elif self._back_selected:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        self._back_selected = False
                    elif event.key == pygame.K_RETURN:
                        self.config.get_sound("select").play()
                        self._return_to_menu()
                else:
                    if event.key == pygame.K_LEFT:
                        self.config.get_sound("select").play()
                        self.selection_index = (self.selection_index - 1) % len(UPGRADE_ITEMS)
                    elif event.key == pygame.K_RIGHT:
                        self.config.get_sound("select").play()
                        self.selection_index = (self.selection_index + 1) % len(UPGRADE_ITEMS)
                    elif event.key == pygame.K_RETURN:
                        self.config.get_sound("select").play()
                        self._apply_upgrade()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self._up_held = False
                    self.config.engine_channel.stop()
                    self.config.engine_channel.play(self.config.get_sound('engine'), loops=-1)

    def _spawn_smoke_now(self) -> None:
        smoke = SmokeTrail(WIDTH // 2, HEIGHT - 70)
        self._smoke_list.add(smoke)

    def _apply_upgrade(self) -> None:
        item = UPGRADE_ITEMS[self.selection_index]
        attr = item["attr"]
        if self.player is not None:
            setattr(self.player, attr, True)
            if attr == "armor_active":
                self.player.max_hp += 200
                self.player.hp += 200
            self.player.update_sprite()
            self._applied_upgrade = item["name"]
            self._selected = True
        else:
            self._pre_game_upgrade = attr
            from sences.ControlsScene import ControlsScene
            self.scene_manager.change_scene(
                ControlsScene(self.config, self.scene_manager, pre_game_upgrade=attr)
            )

    def _return_to_menu(self) -> None:
        if self.player is not None:
            from sences.GameScene import GameScene
            self.scene_manager.change_scene(
                GameScene(self.config, self.scene_manager, mission=2, persistent_player=self.player)
            )
        else:
            from sences.MenuScene import MenuScene
            self.scene_manager.change_scene(MenuScene(self.config, self.scene_manager))

    def update(self, dt: float) -> None:
        self._smoke_list.update()
        if self._up_held:
            now = pygame.time.get_ticks()
            if now - self._last_smoke_ms >= self._smoke_interval_ms:
                self._last_smoke_ms = now
                self._spawn_smoke_now()

    def render(self) -> None:
        self._reload_background_if_needed()
        self.config.screen.blit(self.background, (0, 0))

        if self._selected:
            self._render_selected()
        else:
            self._render_shop()

        self.config.present()

    def _render_shop(self) -> None:
        title = self.config.font_large.render("MEJORAS", True, DARK_GREEN_TEXT)
        title_rect = title.get_rect(center=(WIDTH // 2, 60))
        self.config.screen.blit(title, title_rect)

        slot_w = 220
        total_width = len(UPGRADE_ITEMS) * slot_w
        start_x = (WIDTH - total_width) // 2
        y_center = HEIGHT // 2 - 20

        for i, item in enumerate(UPGRADE_ITEMS):
            cx = start_x + i * slot_w + slot_w // 2

            icon_rect = self.icons[i].get_rect(center=(cx, y_center - 30))
            self.config.screen.blit(self.icons[i], icon_rect)

            name_surf = self.config.font_small.render(item["name"], True, GREEN_TEXT)
            name_rect = name_surf.get_rect(center=(cx, y_center + 45))
            self.config.screen.blit(name_surf, name_rect)

            desc_surf = self.config.font_small.render(item["desc"], True, DARK_GREEN_TEXT)
            desc_rect = desc_surf.get_rect(center=(cx, y_center + 85))
            self.config.screen.blit(desc_surf, desc_rect)

            if i == self.selection_index and not self._back_selected:
                rect_x = start_x + i * slot_w
                rect_y = y_center - 80
                pygame.draw.rect(
                    self.config.screen, DARK_GREEN_TEXT,
                    (rect_x, rect_y, slot_w, 200), 4, border_radius=4,
                )

        tank_img = self.tank_previews[self.selection_index]
        tank_rect = tank_img.get_rect(center=(WIDTH // 2, HEIGHT - 140))
        self.config.screen.blit(tank_img, tank_rect)
        self._smoke_list.draw(self.config.screen)

        back_surf = self.config.font_small.render(BACK_LABEL, True, GREEN_TEXT)
        back_rect = back_surf.get_rect()
        back_rect.bottom = HEIGHT - 20
        back_rect.right = WIDTH - 30
        self.config.screen.blit(back_surf, back_rect)

        if self._back_selected:
            px = back_rect.left - 10
            py = back_rect.top - 6
            pw = back_rect.width + 20
            ph = back_rect.height + 12
            pygame.draw.rect(
                self.config.screen, DARK_GREEN_TEXT,
                (px, py, pw, ph), 4, border_radius=4,
            )

    def _render_selected(self) -> None:
        text = self.config.font_large.render(
            f"\u00a1{self._applied_upgrade} equipada!", True, GREEN_TEXT
        )
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        self.config.screen.blit(text, text_rect)

        sub = self.config.font_small.render("Preparando misi\u00f3n 2...", True, DARK_GREEN_TEXT)
        sub_rect = sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        self.config.screen.blit(sub, sub_rect)

        prompt = self.config.font_small.render(
            "Presiona cualquier tecla para continuar", True, DARK_GREEN_TEXT
        )
        prompt_rect = prompt.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.config.screen.blit(prompt, prompt_rect)
