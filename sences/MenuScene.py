from __future__ import annotations

import sys
import pygame

from config.Settings import GameConfig, WIDTH, HEIGHT, RED_TEXT
from ui.hud import HudManager as Hud
from sences.Scene import Scene


class MenuScene(Scene):

    def __init__(self, config: GameConfig, scene_manager):
        super().__init__(config)
        self.scene_manager = scene_manager
        self._raw_background = pygame.image.load("assets/background_menu.png").convert()
        self._background_size = self.config.screen.get_size()
        self.background = self._build_cover_background(self._raw_background, self._background_size)
        self.selection_index = 0
        self.items = ["Jugar", "Opciones", "Salir"]
        self.menu_positions = [
            (WIDTH / 2, (HEIGHT / 2) - 50),
            (WIDTH / 2, HEIGHT / 2),
            (WIDTH / 2, (HEIGHT / 2) + 50),
        ]

    def _build_cover_background(self, image: pygame.Surface, target_size: tuple[int, int]) -> pygame.Surface:
        """Scale image to fully cover the render area without distortion."""
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
        self.config.main_channel.play(self.config.get_sound('menu'), loops=-1, fade_ms=100)

    def on_deactivate(self) -> None:
        self.config.main_channel.stop()

    def handle_events(self, events: list[pygame.event.EventType]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.config.get_sound('select').play()
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_UP:
                    self.config.get_sound('select').play()
                    self.selection_index = (self.selection_index - 1) % len(self.items)
                elif event.key == pygame.K_DOWN:
                    self.config.get_sound('select').play()
                    self.selection_index = (self.selection_index + 1) % len(self.items)
                elif event.key == pygame.K_RETURN:
                    self.config.get_sound('select').play()
                    self._execute_selected()

    def _execute_selected(self) -> None:
        choice = self.items[self.selection_index]
        if choice == "Jugar":
            self.config.main_channel.stop()
            self.config.game_channel.play(self.config.get_sound('game'), loops=-1, fade_ms=100)
            from sences.GameScene import GameScene

            self.scene_manager.change_scene(GameScene(self.config, self.scene_manager))
        elif choice == "Opciones":
            from sences.OptionsScene import OptionsScene

            self.scene_manager.change_scene(OptionsScene(self.config, self.scene_manager))
        elif choice == "Salir":
            pygame.quit()
            sys.exit()

    def update(self, dt: float) -> None:
        pass

    def render(self) -> None:
        self._reload_background_if_needed()
        self.config.screen.blit(self.background, (0, 0))

        for index, label in enumerate(self.items):
            x, y = self.menu_positions[index]
            Hud.simple_show_text(self.config.screen, self.config.font_small, label, x, y)
            if index == self.selection_index:
                pygame.draw.rect(self.config.screen, RED_TEXT, (x, y, 150, 30), 1)

        self.config.present()
