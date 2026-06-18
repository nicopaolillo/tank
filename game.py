from __future__ import annotations

import pygame

from config.Settings import GameConfig, TARGET_FPS
from sences.SceneManager import SceneManager
from sences.MenuScene import MenuScene


def main() -> None:
    config = GameConfig()
    scene_manager = SceneManager(config)
    menu_scene = MenuScene(config, scene_manager)
    scene_manager.change_scene(menu_scene)

    while True:
        events = pygame.event.get()
        scene_manager.handle_events(events)
        scene_manager.update(config.clock.get_time() / 1000.0)
        scene_manager.render()
        config.clock.tick(TARGET_FPS)


if __name__ == "__main__":
    main()
