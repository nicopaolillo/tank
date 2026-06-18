from __future__ import annotations

import sys
import pygame

from config.Settings import GameConfig, TARGET_FPS, BACKGROUND_IMAGE
from GameContext import GameContext
from sences.Scene import Scene
from resources.Hud import Hud
from entities.AirSupport import AirSupport
from entities.Death import Death
from entities.Shooting import Shooting
from entities.Tank import Tank, Tank_green
from config.Settings import (
    WIDTH,
    HEIGHT,
    GREEN_TEXT,
    DARK_GREEN_TEXT,
    RED_TEXT,
    PLAYER_SPEED,
    PLAYER_BOUNDS_LEFT,
    PLAYER_BOUNDS_RIGHT,
    MISSILE_RECHARGE_TIME,
    MISSILE_SCORE_PENALTY_PER_SECOND,
    MISSILE_FIRE_COOLDOWN,
    TANK_RED_HIT_DAMAGE,
    TANK_GREEN_HIT_DAMAGE,
    TANK_RED_KILL_POINTS,
    TANK_GREEN_KILL_POINTS,
    AIR_SUPPORT_RED_POINTS,
    AIR_SUPPORT_GREEN_POINTS,
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
        self.misilNuevo = 0
        self.ultimoMisil = 0
        self.y = 700
        self.game_over = False
        self.completado = False
        self.pause = False
        self._game_over_shown = False
        # normalize timing to seconds
        self.tiempo_inicio = pygame.time.get_ticks() / 1000.0
        self.ultimoMisil = 0.0
        self.misilNuevo = 0.0
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
                elif event.key == pygame.K_LEFT:
                    self.player.speed_x = -PLAYER_SPEED
                    self.player.image = self.config.get_player_sprite('left')
                elif event.key == pygame.K_RIGHT:
                    self.player.speed_x = PLAYER_SPEED
                    self.player.image = self.config.get_player_sprite('right')
                elif event.key == pygame.K_UP:
                    self.player.speed_y = -PLAYER_SPEED
                    self.player.image = self.config.get_player_sprite('default')
                elif event.key == pygame.K_DOWN:
                    self.player.speed_y = PLAYER_SPEED
                    self.player.image = self.config.get_player_sprite('down')
                elif event.key == pygame.K_q:
                    if self.player.apoyo > 0:
                        apoyo = AirSupport()
                        apoyo.rect.x = self.player.rect.x + 10
                        apoyo.rect.y = HEIGHT
                        self.all_sprites.add(apoyo)
                        self.apoyo_list.add(apoyo)
                        self.player.apoyo -= 1
                elif event.key == pygame.K_SPACE:
                    if self.player.misiles > 0:
                        # enforce cooldown between missile shots but do not penalize score
                        tiempo_desde_ultimo = tiempoTranscurrido - self.ultimoMisil
                        if tiempo_desde_ultimo < MISSILE_FIRE_COOLDOWN:
                            # Too soon to fire another missile; ignore input
                            continue
                        shoot = Shooting()
                        shoot.rect.x = self.player.rect.x + 10
                        shoot.rect.y = self.player.rect.y - 20
                        self.all_sprites.add(shoot)
                        self.shoot_list.add(shoot)
                        self.config.get_sound('shoot').play()
                        self.player.misiles -= 1
                        self.misilNuevo = tiempoTranscurrido
                        self.ultimoMisil = tiempoTranscurrido
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    self.player.speed_x = 0
                elif event.key in (pygame.K_UP, pygame.K_DOWN):
                    self.player.speed_y = 0

    def _pause_screen(self) -> None:
        shape_surf = pygame.Surface(pygame.Rect((0, 0, WIDTH, HEIGHT)).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (0, 0, 0, 127), shape_surf.get_rect())
        shape_surf.set_alpha(128)
        self.config.screen.blit(shape_surf, (0, 0, WIDTH, HEIGHT))
        text1 = self.config.font_large.render("PAUSA", True, DARK_GREEN_TEXT)
        text2 = self.config.font_small.render("Pulse p para continuar", True, DARK_GREEN_TEXT)
        text_rect = text1.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        text_rect2 = text2.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
        self.config.screen.blit(text1, text_rect)
        self.config.screen.blit(text2, text_rect2)

    def update(self, dt: float) -> None:
        if self.pause or self.game_over:
            return

        # apply player movement then clamp to bounds
        self._update_player_movement()
        self._handle_player_bounds()

        self._update_enemy_movement()
        self.y = self._render_background(self.y)
        self._handle_red_tank_shots()
        self._handle_air_support_collisions()
        self._handle_green_tank_shots()
        self.game_over = self._handle_player_collisions()
        self.misilNuevo, self.completado = self._handle_game_progression(pygame.time.get_ticks() / 1000.0 - self.tiempo_inicio)

    def _handle_player_bounds(self) -> None:
        if self.player.rect.right > PLAYER_BOUNDS_RIGHT:
            self.player.rect.right = PLAYER_BOUNDS_RIGHT
        if self.player.rect.left < PLAYER_BOUNDS_LEFT:
            self.player.rect.left = PLAYER_BOUNDS_LEFT
        if self.player.rect.top < 0:
            self.player.rect.top = 0
        if self.player.rect.bottom > HEIGHT:
            self.player.rect.bottom = HEIGHT

    def _update_enemy_movement(self) -> None:
        for tank in self.tank_red_list:
            tank.rect.y += tank.speed_y * 3.8
        for tank in self.tank_green_list:
            tank.rect.y += tank.speed_y * 3.8

    def _update_player_movement(self) -> None:
        # move player according to current speed
        self.player.rect.x += self.player.speed_x
        self.player.rect.y += self.player.speed_y

    def _render_background(self, y: float) -> float:
        y_relativa = y % self.background.get_rect().height
        self.config.screen.blit(self.background, (0, y_relativa - self.background.get_rect().height))
        if y_relativa < HEIGHT:
            self.config.screen.blit(self.background, (0, y_relativa))
        return y + 1 * 2.8

    def _handle_red_tank_shots(self) -> None:
        for shoot in list(self.shoot_list):
            shoot_hits_list = pygame.sprite.spritecollide(shoot, self.tank_red_list, True)
            for tank in shoot_hits_list:
                if shoot in self.all_sprites:
                    self.all_sprites.remove(shoot)
                if shoot in self.shoot_list:
                    self.shoot_list.remove(shoot)
                self.config.get_sound('explosion').play()
                death = Death(tank.rect.x, tank.rect.y)
                death.animate()
                self.all_sprites.add(death)
                self.player.puntaje += TANK_RED_KILL_POINTS
            if shoot.rect.y < -10:
                if shoot in self.all_sprites:
                    self.all_sprites.remove(shoot)
                if shoot in self.shoot_list:
                    self.shoot_list.remove(shoot)

    def _handle_air_support_collisions(self) -> None:
        for apoyo in list(self.apoyo_list):
            apoyo_hits_list = pygame.sprite.spritecollide(apoyo, self.tank_red_list, True)
            apoyo_hits_list2 = pygame.sprite.spritecollide(apoyo, self.tank_green_list, True)
            for tank in apoyo_hits_list:
                self.config.get_sound('explosion').play()
                death = Death(tank.rect.x, tank.rect.y)
                death.animate()
                self.all_sprites.add(death)
                self.player.puntaje += AIR_SUPPORT_RED_POINTS
            for tank in apoyo_hits_list2:
                self.config.get_sound('explosion').play()
                death = Death(tank.rect.x, tank.rect.y)
                death.animate()
                self.all_sprites.add(death)
                self.player.puntaje += AIR_SUPPORT_GREEN_POINTS
            if apoyo.rect.y < -200:
                if apoyo in self.all_sprites:
                    self.all_sprites.remove(apoyo)
                if apoyo in self.apoyo_list:
                    self.apoyo_list.remove(apoyo)

    def _handle_green_tank_shots(self) -> None:
        for shoot in list(self.shoot_list):
            shoot_hits_list = pygame.sprite.spritecollide(shoot, self.tank_green_list, len(self.tank_red_list) == 0)
            for tank in shoot_hits_list:
                if shoot in self.all_sprites:
                    self.all_sprites.remove(shoot)
                if shoot in self.shoot_list:
                    self.shoot_list.remove(shoot)
                if len(self.tank_red_list) > 0:
                    self.config.get_sound('iron').play()
                else:
                    self.player.puntaje += TANK_GREEN_KILL_POINTS
                    death = Death(tank.rect.x, tank.rect.y)
                    death.animate()
                    self.all_sprites.add(death)
                    self.config.get_sound('explosion').play()

    def _handle_red_tank_crash(self) -> bool:
        crash_list = pygame.sprite.spritecollide(self.player, self.tank_red_list, True)
        if len(crash_list) == 1:
            self.config.get_sound('explosion').play()
        for tank in crash_list:
            self.player.hp -= TANK_RED_HIT_DAMAGE
            death = Death(self.player.rect.x, self.player.rect.y)
            death.animate()
            self.all_sprites.add(death)
        return self.player.hp <= 0

    def _handle_green_tank_collision(self) -> bool:
        game_over = False
        crash_list = pygame.sprite.spritecollide(self.player, self.tank_green_list, True)
        if len(crash_list) == 1:
            self.config.get_sound('explosion').play()
        for tank in crash_list:
            self.player.hp -= TANK_GREEN_HIT_DAMAGE
            death = Death(self.player.rect.x, self.player.rect.y)
            death.animate()
            self.all_sprites.add(death)
            if self.player.hp <= 0:
                self.all_sprites.remove(self.player)
                game_over = True
        return game_over

    def _handle_player_collisions(self) -> bool:
        if self._handle_red_tank_crash():
            self.all_sprites.remove(self.player)
            self._game_over_screen()
            return True
        if self._handle_green_tank_collision():
            return True
        return False

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

            Hud.showText(self.config.screen, self.config.font_small, "Energía: ", self.player.hp, 0, 60, 140, 60)
            Hud.showText(self.config.screen, self.config.font_small, "Misiles: ", self.player.misiles, 0, 120, 140, 120)
            Hud.showText(self.config.screen, self.config.font_small, "Nivel: ", self.player.nivel, 0, 180, 140, 180)
            Hud.showText(self.config.screen, self.config.font_small, "Puntaje: ", self.player.puntaje, 0, 240, 140, 240)
            Hud.showText(self.config.screen, self.config.font_small, "Apoyos: ", self.player.apoyo, 0, 300, 140, 300)

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
