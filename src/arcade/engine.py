from .component import GameList
from registry import GameRegistry
from arcade_machine_sdk import BASE_RESOLUTION, DEFAULT_FPS, GameBase
from .util.paths import get_asset
import pygame

class ArcadeEngine:
    def __init__(self, launcher_title: str, game_registry: GameRegistry) -> None:
        self.games = game_registry
        self.launcher_title = launcher_title
        self.__running = True
        self.__current_game: None | GameBase = None
        self._muted = False

        self.screen = pygame.display.set_mode(BASE_RESOLUTION)
        pygame.display.set_caption(self.launcher_title)
        self.clock = pygame.time.Clock()

        self._background = pygame.image.load(str(get_asset("images","background.png"))).convert()
        self._button_mute = pygame.image.load(str(get_asset("images","mute.png"))).convert_alpha()
        self._button_unmute = pygame.image.load(str(get_asset("images","unmute.png"))).convert_alpha()

        self._background_rect = self._background.get_rect(topleft=(0,0))
        self._button_mute_rect     = self._button_mute.get_rect(topleft=(950, 715))
        self._button_unmute_rect   = self._button_unmute.get_rect(topleft=(950, 715))

        self.font_arcade = pygame.font.Font(str(get_asset("fonts","arcade.ttf")),40)
        self.font_meta = pygame.font.Font(str(get_asset("fonts","pixelmix.ttf")),15)

        self.snd_navigate = pygame.mixer.Sound(str(get_asset("sounds", "navigate.ogg")))
        self.snd_cancel   = pygame.mixer.Sound(str(get_asset("sounds", "cancel.ogg")))
        self.snd_select_game   = pygame.mixer.Sound(str(get_asset("sounds", "start.ogg")))

        self.game_list = GameList(self)

        pygame.mixer.music.load(str(get_asset("sounds", "music.ogg")))
        pygame.mixer.music.play(-1)  # -1 = loop infinito

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
            self.game_list.handle_events(events)
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                    self.toggle_mute()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.stop()


    def update(self, dt: float) -> None:
        if self.__current_game:
            self.__current_game.update(dt)
        else:
            self.game_list.update(dt)
    
    def render(self) -> None:
        if self.__current_game:
            if self.__current_game.running:
                self.__current_game.render()
            else:
                pygame.display.set_caption(self.launcher_title)
                self.__current_game = None
                pygame.mixer.music.load(str(get_asset("sounds", "music.ogg")))
                pygame.mixer.music.play(-1)  # -1 = loop infinito
        else:
            self.screen.blit(self._background,self._background_rect)
            self.game_list.render()
            mute_img = self._button_unmute if self._muted else self._button_mute
            self.screen.blit(mute_img, self._button_mute_rect)


    def stop(self) -> None:
        self.__running = False
        if self.__current_game and self.__current_game.running:
            self.__current_game.stop()

    def run_game(self, index: int) -> None:
        if self._muted:
            self._muted = False
            pygame.mixer.music.set_volume(1)
            pygame.mixer.set_num_channels(8)
        (game_class, game_metadata) = self.games.entries[index]
        self.__current_game = game_class(game_metadata)
        self.__current_game.start(self.screen)
        pygame.display.set_caption(game_metadata.title)

    def toggle_mute(self) -> None:
        self._muted = not self._muted
        pygame.mixer.music.set_volume(0 if self._muted else 1)
        pygame.mixer.set_num_channels(0 if self._muted else 8)