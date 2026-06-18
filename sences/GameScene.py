from __future__ import annotations

import sys
import pygame

from config.Settings import GameConfig, BACKGROUND_IMAGE
from GameContext import GameContext
from sences.Scene import Scene
from ui.hud import Hud
from gameplay.player_controller import PlayerController
from gameplay.enemy_manager import EnemyManager
from gameplay.collision_manager import CollisionManager
from gameplay.progression_manager import ProgressionManager
from config.Settings import (
    WIDTH,
    HEIGHT,
    GREEN_TEXT,
    DARK_GREEN_TEXT,
    RED_TEXT,
)


class GameScene(Scene):

    def __init__(self, config: GameConfig, scene_manager):
        super().__init__(config)
        self.scene_manager = scene_manager
        self.context = GameContext(config)
        self.player = self.context.player
        self.all_sprites = self.context.all_sprites
        self.tank_red_list = self.context.tank_red_list
        self.tank_green_list = self.context.tank_green_list
        self.shoot_list = self.context.shoot_list
        self.apoyo_list = self.context.apoyo_list
        self.crash_list = self.context.crash_list
        self.context.reset_player_state()
        self.background = pygame.image.load(BACKGROUND_IMAGE).convert()
        self.player_controller = PlayerController(config, self.player, self.all_sprites, self.shoot_list, self.apoyo_list)
        self.enemy_manager = EnemyManager(self.all_sprites, self.tank_red_list, self.tank_green_list)
        self.collision_manager = CollisionManager(config, self.player, self.all_sprites, self.shoot_list, self.tank_red_list, self.tank_green_list, self.apoyo_list)
        self.progression_manager = ProgressionManager(self.player)
        self.y = 700
        self.game_over = False
        self.pause = False
        self._game_over_shown = False
        # normalize timing to seconds
        self.tiempo_inicio = pygame.time.get_ticks() / 1000.0
        self.show_debug = False

    def on_activate(self) -> None:
        self.config.game_channel.play(self.config.get_sound('game'), loops=-1, fade_ms=100)

    def on_deactivate(self) -> None:
        self.config.game_channel.stop()

    def handle_events(self, events: list[pygame.event.EventType]) -> None:
        tiempoTranscurrido = pygame.time.get_ticks() / 1000.0 - self.tiempo_inicio
        for event in events:
            # toggle debug overlay
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                self.show_debug = not self.show_debug
                continue

            if event.type == pygame.KEYDOWN:
                # allow restarting the scene after game over
                if self.game_over and event.key == pygame.K_r:
                    new_scene = GameScene(self.config, self.scene_manager)
                    self.scene_manager.change_scene(new_scene)
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_p:
                    self.pause = not self.pause
                    if self.pause:
                        self._pause_screen()
                        pygame.display.flip()
                    continue

                self.player_controller.handle_keydown(event, tiempoTranscurrido)
            elif event.type == pygame.KEYUP:
                self.player_controller.handle_keyup(event)

    def _pause_screen(self) -> None:
        Hud.draw_pause_overlay(self.config.screen, self.config.font_small, self.config.font_large, WIDTH, HEIGHT)

    def update(self, dt: float) -> None:
        if self.pause or self.game_over:
            return

        self.player_controller.update()
        self.player_controller.clamp_bounds()
        self.enemy_manager.update()
        self.y = self._render_background(self.y)

        self.collision_manager.handle_red_tank_shots()
        self.collision_manager.handle_air_support_collisions()
        self.collision_manager.handle_green_tank_shots()
        self.game_over = self.collision_manager.handle_player_collisions()

        self.progression_manager.update(pygame.time.get_ticks() / 1000.0 - self.tiempo_inicio, self.enemy_manager, self.tank_red_list, self.tank_green_list)

    def _render_background(self, y: float) -> float:
        y_relativa = y % self.background.get_rect().height
        self.config.screen.blit(self.background, (0, y_relativa - self.background.get_rect().height))
        if y_relativa < HEIGHT:
            self.config.screen.blit(self.background, (0, y_relativa))
        return y + 1 * 2.8

    def _game_over_screen(self) -> None:
        # Play game over sound and stop game music (only once)
        if not self._game_over_shown:
            self.config.gameover_channel.play(self.config.get_sound('gameover'), loops=0, fade_ms=0)
            self.config.game_channel.stop()
            self._game_over_shown = True

    def _draw_game_over_overlay(self) -> None:
        # Dim background
        shape_surf = pygame.Surface(pygame.Rect((0, 0, WIDTH, HEIGHT)).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (0, 0, 0, 180), shape_surf.get_rect())
        self.config.screen.blit(shape_surf, (0, 0))
        # Main text
        text1 = self.config.font_large.render("GAME OVER", True, RED_TEXT)
        text_rect = text1.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 20))
        self.config.screen.blit(text1, text_rect)
        # Secondary text
        text2 = self.config.font_small.render("Pulsa R para reiniciar o ESC para salir", True, RED_TEXT)
        text_rect2 = text2.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 60))
        self.config.screen.blit(text2, text_rect2)

    def _handle_game_progression(self, tiempoTranscurrido: float):
        if tiempoTranscurrido - self.misilNuevo > MISSILE_RECHARGE_TIME:
            self.player.misiles += 1
            self.misilNuevo = tiempoTranscurrido

        if len(self.tank_green_list) == 0 and len(self.tank_red_list) == 0:
            self.player.nivel += 1
            # heal player on level-up but cap maximum HP at 200
            self.player.hp = min(self.player.hp + 100, 200)
            self.player.misiles += 3
            self.player.apoyo += 1
            self.completado = True

        if self.player.nivel > 1 and self.completado:
            self.completado = False
            # spawn new tanks from above the screen, staggered so they enter gradually
            import math
            num_green = self.player.nivel + 2
            num_red = self.player.nivel + 4

            for i in range(num_green):
                offset = 50 * i
                tank_green = Tank_green(spawn_from_top=True, max_start_offset=200 + offset)
                # stagger further by pushing some higher
                tank_green.rect.y -= offset
                self.tank_green_list.add(tank_green)
                self.all_sprites.add(tank_green)

            for i in range(num_red):
                offset = 50 * i
                tank_red = Tank(spawn_from_top=True, max_start_offset=200 + offset)
                tank_red.rect.y -= offset
                self.tank_red_list.add(tank_red)
                self.all_sprites.add(tank_red)

        return self.misilNuevo, self.completado

    def render(self) -> None:
        if not self.game_over:
            self.all_sprites.update()
            self.all_sprites.draw(self.config.screen)

            Hud.draw_game_hud(self.config.screen, self.config.font_small, self.player)

            # Debug overlay: show FPS and player position only when toggled
            if self.show_debug:
                fps = self.config.clock.get_fps()
                debug_text = f"pos={self.player.rect.x},{self.player.rect.y} spd={self.player.speed_x},{self.player.speed_y}"
                fps_surf = self.config.font_small.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
                debug_surf = self.config.font_small.render(debug_text, True, (255, 255, 255))
                self.config.screen.blit(fps_surf, (10, 10))
                self.config.screen.blit(debug_surf, (10, 30))

        else:
            # Ensure game over actions happen once
            self._game_over_screen()
            self._draw_game_over_overlay()

        pygame.display.flip()
