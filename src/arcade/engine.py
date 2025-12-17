from .component import GameList
from registry import GameRegistry
from arcade_machine_sdk import BASE_RESOLUTION, DEFAULT_FPS, GameBase
import pygame

class ArcadeEngine:
    def __init__(self, launcher_title: str, game_registry: GameRegistry) -> None:
        self.games = game_registry
        self.launcher_title = launcher_title
        self.__running = True
        self.__current_game: None | GameBase = None

        self.screen = pygame.display.set_mode(BASE_RESOLUTION)
        pygame.display.set_caption(self.launcher_title)
        self.clock = pygame.time.Clock()
        self.game_list = GameList(self)

    def run(self):
        try:
            while self.__running:
                events = pygame.event.get()

                for event in events:
                    if event.type == pygame.QUIT:
                        self.stop()
                        break

                if self.__running:
                    self.handle_events(events)

                if self.__running:
                    dt = self.clock.get_time() / 1000.0
                    self.update(dt)

                if self.__running:
                    self.render()
                    pygame.display.flip()

                self.clock.tick(DEFAULT_FPS)
        except KeyboardInterrupt:
            pass
        
        finally:
            self.stop()
            pygame.quit()
            
    def handle_events(self, events: list[pygame.event.Event]) -> None:
        if self.__current_game:
            self.__current_game.handle_events(events)
        else:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.game_list.on_screen_click()

    def update(self, dt: float) -> None:
        if self.__current_game:
            self.__current_game.update(dt)
    
    def render(self) -> None:
        if self.__current_game:
            if self.__current_game.running:
                self.__current_game.render()
            else:
                pygame.display.set_caption(self.launcher_title)
                self.__current_game = None
        else:
            self.screen.fill((0, 0, 0))
            self.game_list.render()

    def stop(self) -> None:
        self.__running = False
        if self.__current_game and self.__current_game.running:
            self.__current_game.stop()

    def run_game(self, index: int) -> None:
        (game_class, game_metadata) = self.games.entries[index]
        self.__current_game = game_class(game_metadata)
        self.__current_game.start(self.screen)
        pygame.display.set_caption(game_metadata.title)