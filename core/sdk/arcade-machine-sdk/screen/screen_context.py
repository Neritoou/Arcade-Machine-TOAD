import pygame

class ScreenContext:
    """Contiene solo los datos esenciales de la pantalla"""
    def __init__(self, width: int, height: int, surface: 'pygame.Surface', clock: pygame.time.Clock, fps: int):
        self._width = width
        self._height = height
        self._surface = surface 
        self._clock = clock
        self._fps = fps

    @property
    def center(self) -> tuple: 
        """Devuelve el centro de la pantalla"""
        return (self._width // 2, self._height // 2)
    
    @property
    def size(self) -> tuple:
        """Devuelve el tamaño de la pantalla"""
        return (self._width, self._height)
    
    @property
    def width(self) -> int:
        """Devuelve el ancho de la pantalla"""
        return self._width
    
    @property
    def height(self) -> int:
        """Devuelve el alto de la pantalla"""
        return self._height
    
    @property
    def limit_fps(self) -> int:
        """Devuelve el límite de FPS actuales."""
        return self._fps
    
    @property
    def actual_fps(self) -> float:
        """Devuelve los FPS actuales medidos."""
        return self._clock.get_fps()
    
    @property
    def surface(self) -> 'pygame.Surface':
        """Devuelve la superficie de la pantalla"""
        return self._surface
