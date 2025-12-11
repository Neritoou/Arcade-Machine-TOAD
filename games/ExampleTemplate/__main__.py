import pygame
from src.game import MyGame
try:
    from stub.screen import Screen
except ImportError:
    # En caso de que se ejecute dentro del Core
    from core.src.screen import Screen


def main():
    # Creamos la screen con título e icono
    screen = Screen(title="Mi Juego", icon_path="build/cover_image.png")
    bg_color = (0,0,0)

    # Instanciamos el juego
    game = MyGame(screen.get_context, bg_color)
    game.initialize(config={})  # Configuración específica si aplica
    game.start()

    running = True

    """
    Esta misma lógica la manejará el Core posteriormente
    Se debe tener en cuenta el flujo principal del juego bajo los 3 métodos establecidos (y no bajo este main)
    Este main es solo para pruebas locales independientes del juego
    """
    while running:
        dt = screen.tick() 
        events = pygame.event.get()

        # De esto se encargará el Core posteriormente
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        game.handle_input(events)
        game.update(dt)

        screen.clear(game.get_bg_color) # De esto se encargará el core posteriormente
        game.render()

        screen.update()  # Actualiza la pantalla y respeta el FPS

    game.stop()
    screen.close()

if __name__ == "__main__":
    main()