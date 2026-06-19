import pygame


class HudManager:
    _shield_icon_small: pygame.Surface | None = None
    _bullet_icon_small: pygame.Surface | None = None
    _health_icon_small: pygame.Surface | None = None
    _support_icon_small: pygame.Surface | None = None

    @staticmethod
    def _get_shield_icon_small() -> pygame.Surface | None:
        if HudManager._shield_icon_small is not None:
            return HudManager._shield_icon_small

        try:
            icon = pygame.image.load('assets/shieldArmy.png').convert_alpha()
            HudManager._shield_icon_small = pygame.transform.smoothscale(icon, (48, 48))
        except pygame.error:
            fallback = pygame.Surface((48, 48), pygame.SRCALPHA)
            pygame.draw.circle(fallback, (0, 150, 255, 220), (24, 24), 22)
            pygame.draw.circle(fallback, (255, 255, 255), (24, 24), 8)
            HudManager._shield_icon_small = fallback

        return HudManager._shield_icon_small

    @staticmethod
    def _get_bullet_icon_small() -> pygame.Surface | None:
        if HudManager._bullet_icon_small is not None:
            return HudManager._bullet_icon_small

        try:
            icon = pygame.image.load('assets/bullet.png').convert()
            icon.set_colorkey((255, 255, 255))
            HudManager._bullet_icon_small = pygame.transform.smoothscale(icon, (34, 34))
        except pygame.error:
            fallback = pygame.Surface((34, 34), pygame.SRCALPHA)
            pygame.draw.ellipse(fallback, (255, 240, 120), (11, 5, 12, 22))
            pygame.draw.polygon(fallback, (255, 130, 40), [(17, 27), (12, 33), (22, 33)])
            HudManager._bullet_icon_small = fallback

        return HudManager._bullet_icon_small

    @staticmethod
    def _get_health_icon_small() -> pygame.Surface | None:
        if HudManager._health_icon_small is not None:
            return HudManager._health_icon_small

        try:
            icon = pygame.image.load('assets/player_main.png').convert_alpha()
            bounds = icon.get_bounding_rect(min_alpha=1)
            if bounds.width > 0 and bounds.height > 0:
                icon = icon.subsurface(bounds).copy()
            HudManager._health_icon_small = pygame.transform.smoothscale(icon, (34, 34))
        except pygame.error:
            fallback = pygame.Surface((34, 34), pygame.SRCALPHA)
            pygame.draw.rect(fallback, (120, 200, 120), (6, 10, 22, 16), border_radius=4)
            pygame.draw.rect(fallback, (180, 240, 180), (13, 4, 8, 10), border_radius=2)
            HudManager._health_icon_small = fallback

        return HudManager._health_icon_small

    @staticmethod
    def _get_support_icon_small() -> pygame.Surface | None:
        if HudManager._support_icon_small is not None:
            return HudManager._support_icon_small

        try:
            icon = pygame.image.load('assets/avion.png').convert_alpha()
            bounds = icon.get_bounding_rect(min_alpha=1)
            if bounds.width > 0 and bounds.height > 0:
                icon = icon.subsurface(bounds).copy()
            HudManager._support_icon_small = pygame.transform.smoothscale(icon, (40, 28))
        except pygame.error:
            fallback = pygame.Surface((40, 28), pygame.SRCALPHA)
            pygame.draw.polygon(fallback, (170, 210, 220), [(4, 16), (18, 10), (36, 14), (18, 18)])
            pygame.draw.rect(fallback, (130, 170, 190), (16, 8, 8, 12), border_radius=2)
            HudManager._support_icon_small = fallback

        return HudManager._support_icon_small

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
        health_icon = HudManager._get_health_icon_small()
        if health_icon is not None:
            screen.blit(health_icon, (0, 58))
        HudManager.simple_show_text(screen, font, str(player.hp), 42, 60)
        bullet_icon = HudManager._get_bullet_icon_small()
        if bullet_icon is not None:
            screen.blit(bullet_icon, (0, 118))
        HudManager.simple_show_text(screen, font, str(player.misiles), 46, 120)
        support_icon = HudManager._get_support_icon_small()
        if support_icon is not None:
            screen.blit(support_icon, (0, 306))
        HudManager.simple_show_text(screen, font, "Q", 46, 300)
        HudManager.simple_show_text(screen, font, str(player.apoyo), 84, 300)

        shield_icon = HudManager._get_shield_icon_small()
        if shield_icon is not None:
            screen.blit(shield_icon, (0, 352))
        HudManager.simple_show_text(screen, font, "W", 54, 360)
        HudManager.simple_show_text(screen, font, str(player.shield_inventory), 92, 360)

        if player.shield_active:
            HudManager.simple_show_text(screen, font, "Escudo activo", 0, 420)

        HudManager.show_text(screen, font, "Puntaje: ", player.puntaje, 0, 480, 140, 480)

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
