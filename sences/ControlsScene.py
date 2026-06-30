from __future__ import annotations

import sys
import pygame

from config.Settings import GameConfig, WIDTH, HEIGHT
from sences.Scene import Scene


class ControlsScene(Scene):

    def __init__(self, config: GameConfig, scene_manager):
        super().__init__(config)
        self.scene_manager = scene_manager
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

        from GameContext import GameContext
        GameContext._preload_assets()

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
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.config.get_sound("select").play()
                    from sences.GameScene import GameScene
                    self.scene_manager.change_scene(GameScene(self.config, self.scene_manager))
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    def update(self, dt: float) -> None:
        self.blink_timer += dt
        if self.blink_timer >= 0.5:
            self.blink_timer = 0.0
            self.show_text = not self.show_text

    def render(self) -> None:
        screen = self.config.screen
        screen.fill((0, 0, 0))

        screen.blit(self.instructions, self.instructions_rect)

        if self.show_text:
            enter_label = self.enter_font.render("press ENTER to continue", True, (100, 200, 100))
            er = enter_label.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            screen.blit(enter_label, er)

        self.config.present()
