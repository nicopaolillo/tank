from __future__ import annotations

import sys
import pygame

from config.Settings import (GameConfig,GREEN_TEXT,DARK_GREEN_TEXT)
from sences.Scene import Scene


class OptionsScene(Scene):

    AUDIO_ITEMS = ["general", "música", "efectos", "atrás"]
    MAIN_ITEMS = ["Video", "Sonido", "Atrás"]

    def __init__(self, config: GameConfig, scene_manager):
        super().__init__(config)
        self.scene_manager = scene_manager
        self._raw_background = pygame.image.load("assets/background_menu_options.png").convert()
        self._background_size = self.config.screen.get_size()
        self.background = self._build_cover_background(self._raw_background,self._background_size)
        self.selection_index = 0
        self._audio_mode = False

    @property
    def items(self) -> list[str]:
        return self.AUDIO_ITEMS if self._audio_mode else self.MAIN_ITEMS

    def on_activate(self) -> None:
        self.config.options_channel.play(self.config.get_sound('options'), loops=-1, fade_ms=100)

    def on_deactivate(self) -> None:
        self.config.options_channel.stop()

    def handle_events(self, events: list[pygame.event.EventType]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.config.get_sound('select').play()
                    if self._audio_mode:
                        self._audio_mode = False
                        self.selection_index = 0
                    else:
                        self._go_back()
                elif event.key == pygame.K_UP:
                    self.config.get_sound('select').play()
                    self.selection_index = (self.selection_index - 1) % len(self.items)
                elif event.key == pygame.K_DOWN:
                    self.config.get_sound('select').play()
                    self.selection_index = (self.selection_index + 1) % len(self.items)
                elif event.key == pygame.K_LEFT:
                    if self._audio_mode:
                        self._adjust_volume(-0.1)
                elif event.key == pygame.K_RIGHT:
                    if self._audio_mode:
                        self._adjust_volume(0.1)
                elif event.key == pygame.K_RETURN:
                    self.config.get_sound('select').play()
                    self._execute_selected()

    def _adjust_volume(self, delta: float) -> None:
        choice = self.items[self.selection_index]
        if choice == "general":
            self.config.master_volume = max(0.0, min(1.0, self.config.master_volume + delta))
        elif choice == "música":
            self.config.music_volume = max(0.0, min(1.0, self.config.music_volume + delta))
        elif choice == "efectos":
            self.config.effects_volume = max(0.0, min(1.0, self.config.effects_volume + delta))
        else:
            return
        self.config.apply_volumes()

    def _execute_selected(self) -> None:
        choice = self.items[self.selection_index]
        if self._audio_mode:
            if choice == "atrás":
                self._audio_mode = False
                self.selection_index = 0
        else:
            if choice == "Sonido":
                self._audio_mode = True
                self.selection_index = 0
            elif choice == "Atrás":
                self._go_back()

    def _go_back(self) -> None:
        from sences.MenuScene import MenuScene

        self.scene_manager.change_scene(MenuScene(self.config, self.scene_manager))

    def update(self, dt: float) -> None:
        pass

    def render(self) -> None:
        self._reload_background_if_needed()
        self.config.screen.blit(self.background, (0, 0))

        screen_w, screen_h = self.config.screen.get_size()

        center_x = screen_w // 2
        center_y = screen_h // 2
        spacing_y = 56

        for index, label in enumerate(self.items):
            item_y = center_y + (index - 1) * spacing_y

            color = GREEN_TEXT if index == self.selection_index else DARK_GREEN_TEXT

            text_surface = self.config.font_small.render(label, True, color)

            text_rect = text_surface.get_rect(center=(center_x, item_y))

            self.config.screen.blit(text_surface, text_rect)

            if index == self.selection_index:
                arrow_x = text_rect.left - 32
                arrow_y = text_rect.centery

                pygame.draw.polygon(
                    self.config.screen,
                    DARK_GREEN_TEXT,
                    [
                        (arrow_x, arrow_y),
                        (arrow_x - 16, arrow_y - 10),
                        (arrow_x - 16, arrow_y + 10),
                    ],
                )

            if self._audio_mode and label in ("general", "música", "efectos"):
                self._draw_slider(text_rect.right + 16, text_rect.centery, label)

        self.config.present()

    def _draw_slider(self, x: int, cy: int, label: str) -> None:
        if label == "general":
            value = self.config.master_volume
        elif label == "música":
            value = self.config.music_volume
        elif label == "efectos":
            value = self.config.effects_volume
        else:
            return

        bar_w = 160
        bar_h = 12
        bar_x = x
        bar_y = cy - bar_h // 2

        pygame.draw.rect(self.config.screen, DARK_GREEN_TEXT, (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * value)
        if fill_w > 0:
            pygame.draw.rect(self.config.screen, GREEN_TEXT, (bar_x, bar_y, fill_w, bar_h))
    
    def _build_cover_background(
    self, image: pygame.Surface, target_size: tuple[int, int]) -> pygame.Surface:

        src_w, src_h = image.get_size()
        dst_w, dst_h = target_size

        scale = max(dst_w / src_w, dst_h / src_h)

        scaled_w = max(1, int(src_w * scale))
        scaled_h = max(1, int(src_h * scale))

        scaled = pygame.transform.smoothscale(
            image,
            (scaled_w, scaled_h)
       )

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

        self.background = self._build_cover_background(
            self._raw_background,
            current_size)