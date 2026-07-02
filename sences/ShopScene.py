from __future__ import annotations

import sys
import pygame

from config.Settings import GameConfig, WIDTH, HEIGHT, DARK_GREEN_TEXT, GREEN_TEXT
from sences.Scene import Scene


UPGRADE_ICON_SIZE = 80

UPGRADE_ITEMS = [
    {"name": "Armadura", "key": "armor", "icon": "assets/armor.png",
     "desc": "+200 HP", "attr": "armor_active"},
    {"name": "Doble Ca\u00f1\u00f3n", "key": "double_barrel", "icon": "assets/double_barrel.png",
     "desc": "Dos proyectiles", "attr": "double_barrel_active"},
    {"name": "Orugas", "key": "tank_track", "icon": "assets/tank_track.png",
     "desc": "M\u00e1s velocidad", "attr": "tank_track_active"},
]


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

        self.icons = []
        for item in UPGRADE_ITEMS:
            try:
                icon = pygame.image.load(item["icon"]).convert_alpha()
                icon = pygame.transform.smoothscale(icon, (UPGRADE_ICON_SIZE, UPGRADE_ICON_SIZE))
            except pygame.error:
                icon = pygame.Surface((UPGRADE_ICON_SIZE, UPGRADE_ICON_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(icon, DARK_GREEN_TEXT, icon.get_rect(), 2)
            self.icons.append(icon)

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
        pass

    def on_deactivate(self) -> None:
        pass

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
                elif event.key == pygame.K_LEFT:
                    self.config.get_sound("select").play()
                    self.selection_index = (self.selection_index - 1) % len(UPGRADE_ITEMS)
                elif event.key == pygame.K_RIGHT:
                    self.config.get_sound("select").play()
                    self.selection_index = (self.selection_index + 1) % len(UPGRADE_ITEMS)
                elif event.key == pygame.K_RETURN:
                    self.config.get_sound("select").play()
                    self._apply_upgrade()

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
        from sences.MenuScene import MenuScene
        self.scene_manager.change_scene(MenuScene(self.config, self.scene_manager))

    def update(self, dt: float) -> None:
        pass

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
            name_rect = name_surf.get_rect(center=(cx, y_center + 50))
            self.config.screen.blit(name_surf, name_rect)

            desc_surf = self.config.font_small.render(item["desc"], True, DARK_GREEN_TEXT)
            desc_rect = desc_surf.get_rect(center=(cx, y_center + 90))
            self.config.screen.blit(desc_surf, desc_rect)

            if i == self.selection_index:
                rect_x = start_x + i * slot_w
                rect_y = y_center - 80
                pygame.draw.rect(
                    self.config.screen, DARK_GREEN_TEXT,
                    (rect_x, rect_y, slot_w, 210), 4, border_radius=4,
                )

        instr = self.config.font_small.render(
            "Usa FLECHAS IZQUIERDA/DERECHA para navegar, ENTER para elegir", True, DARK_GREEN_TEXT
        )
        instr_rect = instr.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.config.screen.blit(instr, instr_rect)

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
