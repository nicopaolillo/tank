from __future__ import annotations

import sys
import pygame

from config.Settings import GameConfig, BACKGROUND_IMAGES, BACKGROUND_IMAGES_LVL2
from GameContext import GameContext
from entities.SmokeTrail import SmokeTrail
from entities.ShieldPowerUp import ShieldPowerUp
from entities.AirSupportPickup import AirSupportPickup
from entities.UpgradePickup import UpgradePickup
from entities.HealthPickup import HealthPickup
from entities.Bombardier import Bombardier
from entities.Helicopter import Helicopter
from entities.Tank import Tank, Tank_green, Tank_blue
from sences.Scene import Scene
from ui.hud import HudManager as Hud
from gameplay.player_controller import PlayerController
from gameplay.enemy_manager import EnemyManager
from gameplay.collision_manager import CollisionManager
from gameplay.progression_manager import ProgressionManager
from config.Settings import (
    WIDTH,
    HEIGHT,
    MISSILE_RECHARGE_TIME,
    GREEN_TEXT,
    DARK_GREEN_TEXT,
    RED_TEXT,
    BOMBARDIER_WATER_TOP,
    BOMBARDIER_WATER_BOTTOM,
    BOMBARDIER_LEFT_BOUND,
    BOMBARDIER_RIGHT_BOUND,
    HELICOPTER_LEFT_BOUND,
    HELICOPTER_RIGHT_BOUND,
    HELICOPTER_Y_POSITION,
    HELICOPTER_SCROLL_DECEL_RATE,
)


class GameScene(Scene):

    def __init__(self, config: GameConfig, scene_manager, pre_game_upgrade=None, mission=1, persistent_player=None):
        super().__init__(config)
        self.scene_manager = scene_manager
        self.mission = mission
        self.context = GameContext(config)
        self.player = persistent_player if persistent_player is not None else self.context.player
        self.all_sprites = self.context.all_sprites
        self.tank_red_list = self.context.tank_red_list
        self.tank_green_list = self.context.tank_green_list
        self.shoot_list = self.context.shoot_list
        self.enemy_shoot_list = self.context.enemy_shoot_list
        self.apoyo_list = self.context.apoyo_list
        self.crash_list = self.context.crash_list
        self.smoke_list = self.context.smoke_list
        self.bombardier_list = self.context.bombardier_list
        self.helicopter_list = self.context.helicopter_list
        self.tank_blue_list = self.context.tank_blue_list
        if persistent_player is not None:
            self.context.player.kill()
            self.all_sprites.add(self.player)
            self.player.nivel = 1
            self.player.misiles = 3
            self.player.puntaje = 0
            self.player.update_sprite()
        else:
            self.context.reset_player_state()
            if pre_game_upgrade is not None:
                setattr(self.player, pre_game_upgrade, True)
                if pre_game_upgrade == "armor_active":
                    self.player.max_hp += 200
                    self.player.hp += 200
                self.player.update_sprite()

        bg_images = BACKGROUND_IMAGES_LVL2 if self.mission >= 2 else BACKGROUND_IMAGES
        self.background_images = [self._prepare_background(pygame.image.load(path).convert()) for path in bg_images]
        self.background_loop_count = max(1, len(self.background_images) - 1)
        self.final_background_index = len(self.background_images) - 1
        self.final_background_trigger_level = 7 if self.mission < 2 else 999
        self.final_background_transition_started = False
        self.final_background_active = False
        self.bombardier_defeated = False
        self.helicopter_defeated = False
        self._scroll_deceleration_started = False
        self._scroll_deceleration_complete = False
        self._mission_complete_timer = None
        self.current_background_index = 0
        self.next_background_index = 1 % self.background_loop_count
        self.current_background = self.background_images[self.current_background_index]
        self.next_background = self.background_images[self.next_background_index]
        self.background_offset = 0.0
        self.background_scroll_speed = 80.0
        self.player_controller = PlayerController(config, self.player, self.all_sprites, self.shoot_list, self.apoyo_list)
        self.enemy_manager = EnemyManager(self.config, self.all_sprites, self.tank_red_list, self.tank_green_list, self.tank_blue_list, self.enemy_shoot_list)
        self.collision_manager = CollisionManager(
            config,
            self.player,
            self.all_sprites,
            self.shoot_list,
            self.tank_red_list,
            self.tank_green_list,
            self.tank_blue_list,
            self.apoyo_list,
            self.context.powerup_list,
            self.bombardier_list,
            self.enemy_shoot_list,
            self.helicopter_list,
        )
        self.progression_manager = ProgressionManager(self.player)
        self.game_over = False
        self.pause = False
        self._game_over_shown = False
        self._last_smoke_spawn_ms = 0
        self._smoke_spawn_interval_ms = 90
        self._enemy_smoke_spawn_interval_ms = 140
        self._enemy_last_smoke_spawn_ms: dict[int, int] = {}
        # normalize timing to seconds
        self.tiempo_inicio = pygame.time.get_ticks() / 1000.0
        self.show_debug = False
        self._current_engine = None
        self._initial_spawn_timer = 2.0

    def on_activate(self) -> None:
        self.config.game_channel.play(self.config.get_sound('game'), loops=-1, fade_ms=100)

    def on_deactivate(self) -> None:
        self.config.game_channel.stop()
        self.config.engine_channel.stop()
        self._current_engine = None

    def handle_events(self, events: list[pygame.event.EventType]) -> None:
        tiempoTranscurrido = pygame.time.get_ticks() / 1000.0 - self.tiempo_inicio
        for event in events:
            # toggle debug overlay
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                self.show_debug = not self.show_debug
                continue

            if event.type == pygame.KEYDOWN:
                if self.pause:
                    if event.key == pygame.K_p:
                        self.pause = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_r:
                        new_scene = GameScene(self.config, self.scene_manager)
                        self.scene_manager.change_scene(new_scene)
                        return
                    continue

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
                        self.config.present()
                    continue

                self.player_controller.handle_keydown(event, tiempoTranscurrido)
            elif event.type == pygame.KEYUP:
                self.player_controller.handle_keyup(event)

    def _pause_screen(self) -> None:
        Hud.draw_pause_overlay(self.config.screen, self.config.font_small, self.config.font_large, WIDTH, HEIGHT)

    def update(self, dt: float) -> None:
        if self.pause or self.game_over:
            return

        if self._mission_complete_timer is not None:
            self._mission_complete_timer += dt
            self.player_controller.update()
            self.player_controller.clamp_bounds()
            self._update_engine_sound()
            self._update_smoke_trail()
            self.smoke_list.update()
            if self._mission_complete_timer >= 5.0:
                self._go_to_shop()
            return

        current_time = pygame.time.get_ticks() / 1000.0 - self.tiempo_inicio
        self.player.update_shield(current_time)
        self._check_final_background_transition()
        self._update_background(dt)

        if self._initial_spawn_timer > 0:
            self._initial_spawn_timer -= dt
            if self._initial_spawn_timer <= 0:
                self._initial_spawn_timer = 0
                self.enemy_manager.spawn_level(1, self.mission)

        self.player_controller.update()
        self.player_controller.clamp_bounds()
        self._update_engine_sound()
        self.enemy_manager.update()
        self.enemy_manager.try_enemy_shoot(current_time, self.player.nivel, self.mission)
        self._update_blue_tank_bursts(dt)
        self._update_smoke_trail()
        self._update_enemy_smoke_trails()
        self.smoke_list.update()

        self.collision_manager.handle_red_tank_shots()
        self.collision_manager.handle_air_support_collisions()
        self.collision_manager.handle_green_tank_shots()
        self.collision_manager.handle_blue_tank_shots()
        self.collision_manager.handle_bombardier_shots()
        self.collision_manager.handle_helicopter_shots()
        self.collision_manager.handle_powerup_collisions()
        self.game_over = self.collision_manager.handle_player_collisions()

        if not self.bombardier_defeated:
            self.bombardier_defeated = any(
                getattr(bombardier, "is_destroyed", False)
                for bombardier in self.bombardier_list
            )

        if not self.helicopter_defeated:
            self.helicopter_defeated = any(
                getattr(helicopter, "is_destroyed", False)
                for helicopter in self.helicopter_list
            )

        if self.bombardier_defeated and len(self.bombardier_list) == 0 and self._mission_complete_timer is None:
            self._mission_complete_timer = 0.0

        if self.helicopter_defeated and len(self.helicopter_list) == 0 and self._mission_complete_timer is None:
            self._mission_complete_timer = 0.0

        self._handle_scroll_deceleration(dt)

        level_up = self.progression_manager.update(
            current_time,
            self.enemy_manager,
            self.tank_red_list,
            self.tank_green_list,
            tank_blue_list=self.tank_blue_list,
            mission=self.mission,
            allow_enemy_spawn=not (
                self.final_background_transition_started
                or self._scroll_deceleration_started
                or self.player.nivel >= self.final_background_trigger_level - 1
            ),
            allow_level_progression=(
                not self.final_background_transition_started
                and not self._scroll_deceleration_started
                and self._initial_spawn_timer <= 0
            ),
        )
        if level_up and self.player.nivel % 3 == 0:
            self._spawn_shield_powerup()
        if level_up and self.player.nivel in (3, 5, 7):
            self._spawn_air_support_pickup()
        if level_up and self.player.nivel in (4, 7):
            self._spawn_health_pickup()
        if self.final_background_active:
            if self.mission < 2:
                self._ensure_bombardier()
            else:
                self._ensure_helicopter()

    def _handle_scroll_deceleration(self, dt: float) -> None:
        if self.mission < 2:
            return
        if self._scroll_deceleration_complete:
            return
        if self._scroll_deceleration_started:
            self.background_scroll_speed = max(
                0.0, self.background_scroll_speed - HELICOPTER_SCROLL_DECEL_RATE * dt
            )
            if self.background_scroll_speed <= 0.0:
                self.background_scroll_speed = 0.0
                self._scroll_deceleration_complete = True
                self.final_background_active = True
                self.background_offset = 0.0
                self.current_background = self.background_images[self.final_background_index]
                self.next_background = self.current_background
            return
        if (
            self.mission >= 2
            and self.player.nivel >= 7
            and not self.final_background_active
        ):
            self._scroll_deceleration_started = True
            self.enemy_manager.clear_all_enemies()

    def _ensure_helicopter(self) -> None:
        if self.helicopter_defeated:
            return
        if len(self.helicopter_list) > 0:
            return
        if self.mission < 2:
            return

        y_position = max(60, min(HELICOPTER_Y_POSITION, HEIGHT // 2 - 40))
        helicopter = Helicopter(
            enemy_shoot_list=self.enemy_shoot_list,
            all_sprites=self.all_sprites,
            target=self.player,
            left_bound=HELICOPTER_LEFT_BOUND,
            right_bound=HELICOPTER_RIGHT_BOUND,
            y_position=y_position,
        )
        self.helicopter_list.add(helicopter)
        self.all_sprites.add(helicopter)

    def _check_final_background_transition(self) -> None:
        if self.final_background_transition_started:
            return

        if self.player.nivel < self.final_background_trigger_level:
            return

        self.final_background_transition_started = True
        self.next_background_index = self.final_background_index
        self.next_background = self.background_images[self.next_background_index]
        self.player_controller.set_top_limit(HEIGHT // 2)

    def _update_smoke_trail(self) -> None:
        vx = self.player.speed_x
        vy = self.player.speed_y
        if vx == 0 and vy == 0:
            return

        now = pygame.time.get_ticks()
        if now - self._last_smoke_spawn_ms < self._smoke_spawn_interval_ms:
            return

        self._last_smoke_spawn_ms = now

        direction = pygame.Vector2(vx, vy)
        if direction.length() == 0:
            return
        direction = direction.normalize()

        behind = -direction
        distance = max(self.player.rect.width, self.player.rect.height) * 0.45
        smoke_x = int(self.player.rect.centerx + behind.x * distance)
        smoke_y = int(self.player.rect.centery + behind.y * distance)

        smoke = SmokeTrail(smoke_x, smoke_y)
        self.smoke_list.add(smoke)

    def _update_enemy_smoke_trails(self) -> None:
        now = pygame.time.get_ticks()
        active_ids: set[int] = set()

        enemies = [*self.tank_red_list.sprites(), *self.tank_green_list.sprites(), *self.tank_blue_list.sprites()]
        for tank in enemies:
            tank_id = id(tank)
            active_ids.add(tank_id)

            last_spawn = self._enemy_last_smoke_spawn_ms.get(tank_id, 0)
            if now - last_spawn < self._enemy_smoke_spawn_interval_ms:
                continue

            move = pygame.Vector2(0, tank.speed_y * 3.5)
            if move.length() == 0:
                continue

            self._enemy_last_smoke_spawn_ms[tank_id] = now
            direction = move.normalize()
            behind = -direction

            distance = max(tank.rect.width, tank.rect.height) * 0.35
            smoke_x = int(tank.rect.centerx + behind.x * distance)
            smoke_y = int(tank.rect.centery + behind.y * distance)

            smoke = SmokeTrail(smoke_x, smoke_y)
            self.smoke_list.add(smoke)

        # Remove timers for enemies that no longer exist.
        stale_ids = [tid for tid in self._enemy_last_smoke_spawn_ms if tid not in active_ids]
        for tid in stale_ids:
            del self._enemy_last_smoke_spawn_ms[tid]

    def _update_blue_tank_bursts(self, dt: float) -> None:
        self.enemy_manager.try_trigger_blue_burst(dt)
        for blue in self.tank_blue_list:
            if blue.update_burst(dt):
                self.enemy_manager.try_blue_burst()

    def _update_engine_sound(self) -> None:
        moving = self.player.speed_x != 0 or self.player.speed_y != 0
        if moving and self._current_engine != 'engine_2':
            self.config.engine_channel.stop()
            self.config.engine_channel.play(self.config.get_sound('engine_2'), loops=-1)
            self._current_engine = 'engine_2'
        elif not moving and self._current_engine != 'engine':
            self.config.engine_channel.stop()
            self.config.engine_channel.play(self.config.get_sound('engine'), loops=-1)
            self._current_engine = 'engine'

    def _render_background(self, y: float) -> float:
        current_y = self.background_offset
        next_y = current_y - HEIGHT
        self.config.screen.blit(self.current_background, (0, current_y))
        self.config.screen.blit(self.next_background, (0, next_y))

        return y

    def _prepare_background(self, background: pygame.Surface) -> pygame.Surface:
        return pygame.transform.smoothscale(background, (WIDTH, HEIGHT))

    def _update_background(self, dt: float) -> None:
        if self.final_background_active:
            return

        self.background_offset += self.background_scroll_speed * dt

        if self.background_offset < HEIGHT:
            return

        self.background_offset -= HEIGHT
        self.current_background_index = self.next_background_index
        if self.final_background_transition_started and self.current_background_index == self.final_background_index:
            self.final_background_active = True
            self.background_offset = 0.0
            self.current_background = self.background_images[self.final_background_index]
            self.next_background = self.current_background
            return

        if self.final_background_transition_started:
            self.next_background_index = self.final_background_index
        else:
            self.next_background_index = (self.current_background_index + 1) % self.background_loop_count

        self.current_background = self.background_images[self.current_background_index]
        self.next_background = self.background_images[self.next_background_index]

    def _ensure_bombardier(self) -> None:
        if self.bombardier_defeated:
            return

        if len(self.bombardier_list) > 0:
            return

        water_top = max(0, BOMBARDIER_WATER_TOP)
        water_bottom = min(HEIGHT // 2, BOMBARDIER_WATER_BOTTOM)
        y_position = max(water_top + 30, min((water_top + water_bottom) // 2, HEIGHT // 2 - 30))
        y_position = max(water_top + 30, y_position - 70)

        bombardier = Bombardier(
            enemy_shoot_list=self.enemy_shoot_list,
            all_sprites=self.all_sprites,
            target=self.player,
            left_bound=max(0, BOMBARDIER_LEFT_BOUND),
            right_bound=min(WIDTH, BOMBARDIER_RIGHT_BOUND),
            y_position=y_position,
        )
        self.bombardier_list.add(bombardier)
        self.all_sprites.add(bombardier)

    def _spawn_shield_powerup(self) -> None:
        powerup = ShieldPowerUp()
        self.all_sprites.add(powerup)
        self.context.powerup_list.add(powerup)

    def _spawn_air_support_pickup(self) -> None:
        pickup = AirSupportPickup()
        self.all_sprites.add(pickup)
        self.context.powerup_list.add(pickup)

    def _spawn_upgrade_pickup(self) -> None:
        pickup = UpgradePickup()
        self.all_sprites.add(pickup)
        self.context.powerup_list.add(pickup)

    def _spawn_health_pickup(self) -> None:
        pickup = HealthPickup()
        self.all_sprites.add(pickup)
        self.context.powerup_list.add(pickup)

    def _go_to_shop(self) -> None:
        from sences.ShopScene import ShopScene
        self.config.game_channel.stop()
        self.config.engine_channel.stop()
        self._current_engine = None
        self.scene_manager.change_scene(ShopScene(self.config, self.scene_manager, self.player))

    def _game_over_screen(self) -> None:
        # Play game over sound and stop game music (only once)
        if not self._game_over_shown:
            self.config.gameover_channel.play(self.config.get_sound('gameover'), loops=0, fade_ms=0)
            self.config.game_channel.stop()
            self.config.engine_channel.stop()
            self._current_engine = None
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
            self.player.misiles = min(self.player.misiles + 3, 3)
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
            self._render_background(0)
            if not self.pause:
                self.all_sprites.update()
            self.smoke_list.draw(self.config.screen)
            self.all_sprites.draw(self.config.screen)

            if self.player.shield_active:
                shield_surf = pygame.Surface((self.player.rect.width + 24, self.player.rect.height + 24), pygame.SRCALPHA)
                pygame.draw.ellipse(shield_surf, (0, 150, 255, 100), shield_surf.get_rect(), 4)
                self.config.screen.blit(shield_surf, (self.player.rect.x - 12, self.player.rect.y - 12))

            active_bombardier = self.bombardier_list.sprites()[0] if len(self.bombardier_list) > 0 else None
            if active_bombardier is not None and getattr(active_bombardier, "is_destroyed", False):
                active_bombardier = None

            if active_bombardier is not None and getattr(active_bombardier, "_shield_active", False):
                r = active_bombardier.rect
                shield_surf = pygame.Surface((r.width + 24, r.height + 24), pygame.SRCALPHA)
                pygame.draw.ellipse(shield_surf, (255, 180, 0, 90), shield_surf.get_rect(), 4)
                self.config.screen.blit(shield_surf, (r.x - 12, r.y - 12))

            active_helicopter = self.helicopter_list.sprites()[0] if len(self.helicopter_list) > 0 else None
            if active_helicopter is not None and getattr(active_helicopter, "is_destroyed", False):
                active_helicopter = None

            Hud.draw_game_hud(self.config.screen, self.config.font_small, self.player, active_bombardier, active_helicopter)

            if self._mission_complete_timer is not None:
                remaining = max(0, 5.0 - self._mission_complete_timer)
                complete_text = self.config.font_small.render(
                    f"Misi\u00f3n 1 completada", True, DARK_GREEN_TEXT
                )
                complete_rect = complete_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
                self.config.screen.blit(complete_text, complete_rect)
                timer_text = self.config.font_small.render(
                    f"Transfiriendo a la tienda en {remaining:.0f}s...", True, GREEN_TEXT
                )
                timer_rect = timer_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
                self.config.screen.blit(timer_text, timer_rect)

            # Debug overlay: show FPS and player position only when toggled
            if self.show_debug:
                fps = self.config.clock.get_fps()
                debug_text = f"pos={self.player.rect.x},{self.player.rect.y} spd={self.player.speed_x},{self.player.speed_y}"
                fps_surf = self.config.font_small.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
                debug_surf = self.config.font_small.render(debug_text, True, (255, 255, 255))
                self.config.screen.blit(fps_surf, (10, 10))
                self.config.screen.blit(debug_surf, (10, 30))

            if self.pause:
                self._pause_screen()

        else:
            # Ensure game over actions happen once
            self._game_over_screen()
            self._draw_game_over_overlay()

        self.config.present()
