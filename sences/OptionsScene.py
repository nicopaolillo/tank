from __future__ import annotations

import sys
import pygame

from config.Settings import GameConfig, WIDTH, HEIGHT, RED_TEXT
from ui.hud import HudManager as Hud
from sences.Scene import Scene


class OptionsScene(Scene):

    def __init__(self, config: GameConfig, scene_manager):
        super().__init__(config)
        self.scene_manager = scene_manager
        self.background = pygame.image.load("assets/options.png").convert()
        self.selection_index = 0
        self.items = ["Video", "Sonido", "Atrás"]
        self.menu_positions = [
            (WIDTH / 2, (HEIGHT / 2) - 50),
            (WIDTH / 2, HEIGHT / 2),
            (WIDTH / 2, (HEIGHT / 2) + 50),
        ]

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
                    self._go_back()
                elif event.key == pygame.K_UP:
                    self.selection_index = (self.selection_index - 1) % len(self.items)
                elif event.key == pygame.K_DOWN:
                    self.selection_index = (self.selection_index + 1) % len(self.items)
                elif event.key == pygame.K_RETURN:
                    self._execute_selected()

    def _execute_selected(self) -> None:
        choice = self.items[self.selection_index]
        if choice == "Atrás":
            self._go_back()

    def _go_back(self) -> None:
        from sences.MenuScene import MenuScene

        self.scene_manager.change_scene(MenuScene(self.config, self.scene_manager))

    def update(self, dt: float) -> None:
        pass

    def render(self) -> None:
        self.config.screen.blit(self.background, (0, 0))

        for index, label in enumerate(self.items):
            x, y = self.menu_positions[index]
            Hud.simple_show_text(self.config.screen, self.config.font_small, label, x, y)
            if index == self.selection_index:
                pygame.draw.rect(self.config.screen, RED_TEXT, (x, y, 150, 30), 1)

        pygame.display.update()
