from __future__ import annotations

import pygame
from abc import ABC, abstractmethod
from config.Settings import GameConfig


class Scene(ABC):

    def __init__(self, config: GameConfig):
        self.config = config

    @abstractmethod
    def handle_events(self, events: list[pygame.event.EventType]) -> None:
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @abstractmethod
    def render(self) -> None:
        pass

    def on_activate(self) -> None:
        pass

    def on_deactivate(self) -> None:
        pass
