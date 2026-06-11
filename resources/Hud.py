import pygame

class Hud:

    @staticmethod
    def simpleShowText(screen, font, text, x, y):
        rendered = font.render(text, True, (173, 255, 47))
        screen.blit(rendered, (x, y))

    @staticmethod
    def showText(screen, font, label, value, x1, y1, x2, y2):
        text1 = font.render(label, True, (173, 255, 47))
        screen.blit(text1, (x1, y1))

        text2 = font.render(str(value), True, (173, 255, 47))
        screen.blit(text2, (x2, y2))

    @staticmethod
    def pause(screen, font, font2, width, height):
        shape_surf = pygame.Surface(
            pygame.Rect((0, 0, width, height)).size,
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            shape_surf,
            (0, 0, 0, 127),
            shape_surf.get_rect()
        )

        shape_surf.set_alpha(128)
        screen.blit(shape_surf, (0, 0, width, height))

        text1 = font2.render("PAUSA", True, (0, 143, 57))
        text2 = font.render("Pulse p para continuar", True, (0, 143, 57))

        text_rect = text1.get_rect(center=(width / 2, height / 2))
        text_rect2 = text2.get_rect(center=(width / 2, height / 2 + 50))

        screen.blit(text1, text_rect)
        screen.blit(text2, text_rect2)