from arcade_machine_sdk import GameBase, GameMeta
import pygame
from random import randrange

def random_color():
    return [randrange(255) for _ in range(3)]

class Game(GameBase):
    def __init__(self, metadata: GameMeta) -> None:
        super().__init__(metadata);
        self.current_color = random_color()
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 25)
        self.text_surfaces = [
            self.font.render("Presiona Escape para salir del juego y regresar al lanzador", True, (255, 255, 255)),
            self.font.render("Presiona Espacio para cambiar el color del fondo", True, (255, 255, 255))
        ]

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_ESCAPE:
                        self.stop()
                    case pygame.K_SPACE:
                        self.current_color = random_color()
                    case _:
                        pass
        
    def update(self, dt: float) -> None:
        pass
        
    def render(self) -> None:
        self.surface.fill(self.current_color)
        offset_y = 20
        for text_surface in self.text_surfaces:
            self.surface.blit(text_surface, (20, offset_y))
            offset_y += 20