import pygame


class HudManager:

    @staticmethod
    def simple_show_text(screen: pygame.Surface, font: pygame.font.Font, text: str, x: float, y: float) -> None:
        rendered = font.render(text, True, (173, 255, 47))
        screen.blit(rendered, (x, y))

    @staticmethod
    def show_text(screen: pygame.Surface, font: pygame.font.Font, label: str, value: int, x1: float, y1: float, x2: float, y2: float) -> None:
        text1 = font.render(label, True, (173, 255, 47))
        screen.blit(text1, (x1, y1))

        text2 = font.render(str(value), True, (173, 255, 47))
        screen.blit(text2, (x2, y2))

    @staticmethod
    def draw_game_hud(screen: pygame.Surface, font: pygame.font.Font, player) -> None:
        HudManager.show_text(screen, font, "Energía: ", player.hp, 0, 60, 140, 60)
        HudManager.show_text(screen, font, "Misiles: ", player.misiles, 0, 120, 140, 120)
        HudManager.show_text(screen, font, "Nivel: ", player.nivel, 0, 180, 140, 180)
        HudManager.show_text(screen, font, "Puntaje: ", player.puntaje, 0, 240, 140, 240)
        HudManager.show_text(screen, font, "Q - Apoyos: ", player.apoyo, 0, 300, 260, 300)
        HudManager.show_text(screen, font, "W - Escudos: ", player.shield_inventory, 0, 360, 260, 360)
        if player.shield_active:
            HudManager.simple_show_text(screen, font, "Escudo activo", 0, 420)

    @staticmethod
    def draw_pause_overlay(screen: pygame.Surface, font_small: pygame.font.Font, font_large: pygame.font.Font, width: int, height: int) -> None:
        shape_surf = pygame.Surface(pygame.Rect((0, 0, width, height)).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (0, 0, 0, 127), shape_surf.get_rect())
        shape_surf.set_alpha(128)
        screen.blit(shape_surf, (0, 0, width, height))

        text1 = font_large.render("PAUSA", True, (0, 143, 57))
        text2 = font_small.render("Pulse p para continuar", True, (0, 143, 57))

        text_rect = text1.get_rect(center=(width / 2, height / 2))
        text_rect2 = text2.get_rect(center=(width / 2, height / 2 + 50))

        screen.blit(text1, text_rect)
        screen.blit(text2, text_rect2)
