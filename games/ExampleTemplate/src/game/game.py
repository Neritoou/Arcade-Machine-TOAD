import pygame
from typing import Any, Dict, List
try:
    from stub.screen import ScreenContext
    from stub.utils import load_json
    from stub.interfaces import GameModule
except ImportError:
    # En caso de que se ejecute dentro del Core
    from core.src.screen import ScreenContext
    from core.src.utils import load_json
    from core.src.interfaces import GameModule

# Clase de ejemplo que implementa GameModule
class MyGame(GameModule):
    """
    Ejemplo de implementación de GameModule para un juego simple.
    """
    def __init__(self, screen_context: ScreenContext, bg_color: tuple[int, int, int]) -> None:
        super().__init__(screen_context, bg_color)
        # Variables del juego
        self.player_pos = [self._screen_context.width // 2, self._screen_context.height // 2]
        self.player_speed = 200  # píxeles por segundo
        self.player_color = (255, 0, 0)
        self.player_size = 50
        self.jump_speed = 300  # pixeles por segundo
        self.gravity = 600  # pixeles por segundo^2
        self.is_jumping = False
        self.vertical_speed = 0
        self.start_y = self.player_pos[1]
        self._movement = [0, 0]  # Movimiento en x e y


    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Inicialización del juego. Se ejecuta una sola vez al cargar.
        """
        # Ejemplo: cargar datos de JSON si existe
        try:
            self._game_data = load_json("build/game_data.json")
        except FileNotFoundError:
            self._game_data = {
                "title": "Mi Juego Ejemplo",
                "description": "Demo",
                "release_date": "01/01/2025",
                "tags": ["Demo"],
                "group": "1",
                "authors": ["Desarrollador"]
            }
    def handle_input(self, events: List[pygame.event.Event]) -> None:
        keys = pygame.key.get_pressed()
        self._movement[0] = 0
        if keys[pygame.K_a]:
            self._movement[0] = -1
        if keys[pygame.K_d]:
            self._movement[0] = 1

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.is_jumping:
                    self.is_jumping = True
                    self.vertical_speed = -self.jump_speed
                elif event.key == pygame.K_e:
                    self.interact()

    def update(self, dt: float) -> None:
        # Movimiento horizontal
        self.player_pos[0] += self._movement[0] * 200 * dt  # 200 px/s velocidad horizontal

        # Movimiento vertical (salto y gravedad)
        if self.is_jumping:
            self.player_pos[1] += self.vertical_speed * dt
            self.vertical_speed += self.gravity * dt  # gravedad
            if self.player_pos[1] >= self.start_y:
                self.player_pos[1] = self.start_y
                self.is_jumping = False
                self.vertical_speed = 0


        # Mantener dentro de la pantalla
        self.player_pos[0] = max(0, min(self._screen_context.width - self.player_size, self.player_pos[0]))
        self.player_pos[1] = max(0, min(self._screen_context.height - self.player_size, self.player_pos[1]))


    def render(self) -> None:
        surface = self._screen_context.surface
        surface.fill((0, 0, 0))
        pygame.draw.rect(surface, self.player_color, (*self.player_pos, 50, 50))

    def interact(self) -> None:
        if self.player_color == (0, 255, 0):
            self.player_color = (255, 0, 0)
        else:
             self.player_color = (0, 255, 0)
