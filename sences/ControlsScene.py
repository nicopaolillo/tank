from __future__ import annotations

import sys
import pygame

from config.Settings import GameConfig, WIDTH, HEIGHT
from sences.Scene import Scene

BRIEFING_DURATION = 4.0


class ControlsScene(Scene):

    def __init__(self, config: GameConfig, scene_manager, pre_game_upgrade=None):
        super().__init__(config)
        self.scene_manager = scene_manager
        self._pre_game_upgrade = pre_game_upgrade
        self.blink_timer = 0.0
        self.show_text = True
        self.enter_font = pygame.font.SysFont(None, 36)

        raw = pygame.image.load("assets/instructions.png").convert_alpha()
        img_w, img_h = raw.get_size()
        max_w = WIDTH - 80
        max_h = HEIGHT - 120
        scale = min(max_w / img_w, max_h / img_h, 1.0)
        new_w = max(1, int(img_w * scale))
        new_h = max(1, int(img_h * scale))
        self.instructions = pygame.transform.smoothscale(raw, (new_w, new_h))
        self.instructions_rect = self.instructions.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))

        self.briefing_image = pygame.image.load("assets/background_mission_1.png").convert()
        self.briefing_image = pygame.transform.smoothscale(self.briefing_image, (WIDTH, HEIGHT))

        from GameContext import GameContext
        GameContext._preload_assets()

    def on_activate(self) -> None:
        self._state = "instructions"
        self.briefing_timer = 0.0

    def on_deactivate(self) -> None:
        pass

    def handle_events(self, events: list[pygame.event.EventType]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if self._state == "instructions":
                        self.config.get_sound("select").play()
                        self._state = "briefing"
                        self.briefing_timer = 0.0
                    elif self._state == "briefing":
                        self._start_game()

    def _start_game(self) -> None:
        from sences.GameScene import GameScene
        self.scene_manager.change_scene(
            GameScene(self.config, self.scene_manager, pre_game_upgrade=self._pre_game_upgrade)
        )

    def update(self, dt: float) -> None:
        if self._state == "instructions":
            self.blink_timer += dt
            if self.blink_timer >= 0.5:
                self.blink_timer = 0.0
                self.show_text = not self.show_text
        elif self._state == "briefing":
            self.briefing_timer += dt
            if self.briefing_timer >= BRIEFING_DURATION:
                self._start_game()

    def render(self) -> None:
        screen = self.config.screen
        screen.fill((0, 0, 0))

        if self._state == "instructions":
            screen.blit(self.instructions, self.instructions_rect)
            if self.show_text:
                enter_label = self.enter_font.render("press ENTER to continue", True, (100, 200, 100))
                er = enter_label.get_rect(center=(WIDTH // 2, HEIGHT - 50))
                screen.blit(enter_label, er)
        elif self._state == "briefing":
            screen.blit(self.briefing_image, (0, 0))

        self.config.present()
