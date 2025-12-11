import pygame
from arcade_machine_sdk.constants import BASE_RESOLUTION, DEFAULT_FPS
from screen_context import ScreenContext

class Screen:
    def __init__(self,title: str, icon_path: str) -> None:
        # --- Tamaño principal de la ventana ---
        self._width = BASE_RESOLUTION[0]
        self._height = BASE_RESOLUTION[1]

        # --- Configuración de modo ---
        self.surface = pygame.display.set_mode((self._width, self._height), pygame.RESIZABLE | pygame.SCALED)
        # --- Propiedades generales ---
        self._clock = pygame.time.Clock()
        self._fps = DEFAULT_FPS
        pygame.display.set_caption(title)

        # --- Contexto ---
        self._context = ScreenContext(self._width, self._height, self.surface, self._clock, self._fps)

        # --- Icono de la Aplicacion ---
        try:
            window_Icon = pygame.image.load(icon_path)  
            pygame.display.set_icon(window_Icon)
        except:
            # Si falla, crear uno automáticamente
            window_Icon = pygame.Surface((32, 32))
            window_Icon.fill((100, 200, 50))
            pygame.display.set_icon(window_Icon)

    def clear(self,color: tuple[int, int, int]) -> None:
        """Limpia la pantalla con el color base."""
        self.surface.fill(color)

    def update(self) -> None:
        """Actualiza sola la pantalla.
        - Solo se puede llamar una vez por frame."""
        pygame.display.flip()

    def tick(self) -> float:
        """Calcula dt REAL del frame actual.
        - Solo se puede llamar una vez por frame.

        returns:
            Delta time en segundos.
        """
        return self._clock.tick(self._fps) / 1000.0

    @property
    def get_context(self) -> ScreenContext:
        """Obtiene el contexto de la pantalla actual.

        returns:
            ScreenContext: Contexto de la pantalla.
        """
        return self._context
    
# (?) Modificar para solo usarse en el Menu del Juego
    def close(self) -> None:
        """Cierra pygame y libera recursos."""
        pygame.quit()

