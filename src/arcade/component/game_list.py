import pygame
from typing import TYPE_CHECKING

# TODO: esto evidentemente será cambiado después, pero por ahora para que sea algo funcional

# Esto es para evitar la dependencia circular
if TYPE_CHECKING:
    from ..engine import ArcadeEngine

class GameList:
    def __init__(self, engine: "ArcadeEngine") -> None:
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 25)
        self.engine = engine

        self.text_surfaces: list[tuple[pygame.Surface, pygame.Rect]] = []
        offset_y = 20
        for entry in self.engine.games.entries:
            text_surface = self.font.render(f"Click aquí para jugar {entry[1].title}", True, (255, 255, 255))
            self.text_surfaces.append(
                (
                    text_surface,
                    pygame.Rect(20, offset_y, text_surface.get_width(), text_surface.get_height())
                )
            )
            offset_y += 40

    def render(self) -> None:
        for (text_surface, text_rect) in self.text_surfaces:
            self.engine.screen.blit(text_surface, (text_rect.left, text_rect.top))

    def on_screen_click(self) -> None:
        index = 0
        for (_, text_rect) in self.text_surfaces:
            if text_rect.collidepoint(pygame.mouse.get_pos()):
                self.on_click(index)
                continue
            index += 1

    def on_click(self, index: int) -> None:
        self.engine.run_game(index)