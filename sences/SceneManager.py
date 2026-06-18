from __future__ import annotations

from config.Settings import GameConfig
from sences.Scene import Scene


class SceneManager:

    def __init__(self, config: GameConfig, initial_scene: Scene | None = None):
        self.config = config
        self.current_scene = initial_scene
        if self.current_scene is not None:
            self.current_scene.on_activate()

    def change_scene(self, scene: Scene) -> None:
        if self.current_scene is not None:
            self.current_scene.on_deactivate()

        self.current_scene = scene
        self.current_scene.on_activate()

    def handle_events(self, events: list[object]) -> None:
        self.current_scene.handle_events(events)

    def update(self, dt: float) -> None:
        self.current_scene.update(dt)

    def render(self) -> None:
        self.current_scene.render()
