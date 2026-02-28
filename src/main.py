from registry import GameRegistry
from arcade import ArcadeEngine
import pygame

try:
    if not pygame.get_init():
        pygame.init()

    game_registry = GameRegistry()
    game_registry.perform_scan()

    engine = ArcadeEngine("Arcade Machine", game_registry)
    engine.run()
except KeyboardInterrupt:
    pass