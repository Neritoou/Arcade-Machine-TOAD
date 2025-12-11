from abc import ABC, abstractmethod
from typing import Any, Dict, List
from arcade_machine_sdk.screen import ScreenContext
import pygame

class GameModule(ABC):
    """
    Clase base que todo juego debe implementar para integrarse al Core.

    Arquitectura pensada para un loop único del Core:
      - El Core mantiene la ventana y el loop global.
      - Los juegos nunca crean su propio loop ni su propia ventana.
      - Cada juego expone métodos que el Core llama por frame.

    Flags importantes:
      - running: True cuando el juego está activo.
      - game_data: Diccionario con información del juego leída desde game_data.json del build
      - screen_context: Contexto de pantalla compartida entre el Core y el juego.
    """
    def __init__(self, screen_context: ScreenContext, bg_color: tuple[int, int, int]) -> None:
        # Flag para saber si el juego está activo
        self._running: bool = False
        self._screen_context = screen_context # Contexto de pantalla compartida
        self._bg_color = bg_color

    # (?) Verificar si se implementará de manera genérica
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Carga recursos pesados (sprites, sonidos, niveles) y configura variables fijas.
        Se llama **una sola vez** cuando el juego es cargado por primera vez.
        """
        pass

    def start(self) -> None:
        """
        Marca el juego como activo.
        - Su uso en clases concretas debe llamar a **super()**.
        - Se llama cada vez que el usuario inicia el juego desde el menú del Core.
        """
        self._running = True

    def stop(self) -> None:
        """
        Detiene el juego, libera recursos dinámicos si es necesario.
        - Su uso en clases concretas debe llamar a **super()**.
        - Se llama cuando el usuario vuelve al menú o cierra el juego.
        """
        self._running = False

    @abstractmethod
    def handle_input(self, events: List[pygame.event.Event]) -> None:
        """
        Recibe los eventos que pasan por el Core (teclado, mouse, joystick)
        y los procesa para la lógica del juego.
        - Nunca debe llamar a `pygame.event.get()` por sí mismo.

        args:
            **events**: lista de eventos de pygame capturados en el frame actual
        """
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Actualización de la lógica del juego por frame.
        - Se llama solo si `_running=True`.

        args:
            **dt**: tiempo en segundos desde el último frame (para movimientos independientes del FPS)
        """
        pass
    
    @abstractmethod
    def render(self) -> None:
        """
        Dibuja todo el estado del juego en la superficie que pasa el Core.
        - Nunca crea su propia ventana.
        - Se llama solo si `_running=True`.
        """
        pass

    @property
    def get_state(self) -> bool:
        """
        Devuelve el estado actual del juego (activo o no).
        Útil para el Core para saber si debe llamar a update() y render().
        """
        return self._running

    @property
    def get_bg_color(self) -> tuple[int, int, int]:
        """
        Devuelve el color de fondo compartido entre el Core y el juego.
        Útil para que el juego pueda acceder al color de fondo actual.

        returns:
        - Tupla con el color de fondo (R, G, B)
        """
        return self._bg_color