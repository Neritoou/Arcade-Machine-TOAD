import os
import importlib.util
import sys
from arcade_machine_sdk import GameBase, GameMeta
from types import ModuleType
from dataclasses import dataclass
from meta import meta_replacements

GAMES_DIRECTORY = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "games"))

@dataclass
class GameEntry:
    sort_order: int
    metadata_path: str
    metadata_field: str
    game_path: str
    game_field: str
    root_subdir: str | None = ""
    # Hardcodeado aquí porque olvidé colocar esta field en el GameMeta :(
    group_day: str = ""

@dataclass
class LoadedGameEntry:
    name: str
    raw_entry: GameEntry
    full_root_path: str


class GameRegistry:
    def __init__(self) -> None:
        self.entries: dict[str, GameEntry] = {}

        self._register("tetris", "main.py", "metadata", "src/core/game.py", "Game", None, "Monday") # 1
        self._register("pacman", "main.py", "metadata", "game.py", "Game", None, "Monday") # 2
        self._register("street-fighter", "src/main.py", "metadata", "src/main.py", "StreetFighterGame", "src", "Monday") # 3
        self._register("tron", "game.py", "metadata", "game.py", "TronGame", None, "Monday") # 4
        self._register("snake", "main.py", "game_meta", "game.py", "SnakeGame", None, "Monday") # 5
        self._register("duck-hunt", "src/main.py", "meta", "src/main.py", "Juego", "src", "Monday") # 6
        self._register("bomberman", "main.py", "metadata", "src/core/bomberman_game.py", "BombermanGame", "src", "Monday") # 7
        self._register("space-invaders", "main.py", "metadata", "src/game.py", "Game", None, "Monday") # 8
        self._register("centipede", "Main.py", "metadata", "Game.py", "Game", None, "Monday") # 9

        self._register("donkey-kong", "main.py", "metadata", "game/game.py", "DonkeyKong", None, "Thursday") # 1
        self._register("galaga", "main.py", "metadata", "game.py", "GalagaGame", None, "Thursday") # 3
        self._register("jumper", "Jumper/main.py", "metadata", "Jumper/jumper.py", "Jumper", "Jumper", "Thursday") # 4
        self._register("arkanoid", "main.py", "metadata", "src/arkanoid/game.py", "ArkanoidGame", None, "Thursday") # 5
        self._register("flappy-bird", "main.py", "metadata", "game.py", "FlyingDuckGame", None, "Thursday") # 6
        self._register("breakout", "Breakout--master/main.py", "metadata", "Breakout--master/main.py", "BreakoutGame", "Breakout--master", "Thursday") # 6
        self._register("mario-bros", "main.py", "metadata", "mario_game.py", "Game", None, "Thursday") # 8
        self._register("frogger", "main.py", "metadata", "engine.py", "Game", None, "Thursday") # 9

        self.loaded_entries: list[tuple[type[GameBase], GameMeta, LoadedGameEntry]] = []

    def _register(self, game_name: str, metadata_path: str, metadata_field: str, game_path: str, game_field: str, root_subdir: str | None = "", group_day: str = ""):
        sort_order = len(self.entries)
        entry = GameEntry(sort_order, metadata_path, metadata_field, game_path, game_field, root_subdir, group_day)
        self.entries[game_name] = entry

    # Cargar todos los juegos de manera dinámica
    def perform_scan(self) -> None:
        
        # Únicamente leer directorios del nivel superficial del directorio
        directories: list[str] = []
        for (_, dirnames, _) in os.walk(GAMES_DIRECTORY):
            directories.extend(dirnames)
            break

        # Cargar la clase iniciadora y los metadatos del juego de manera dinámica
        games_to_load = len(directories)
        print(f"\nJuegos a cargar encontrados: {games_to_load}")
        current_index = 0
        working_directory = os.getcwd()

        for directory in directories:
            current_index += 1
            entry = self.entries.get(directory)
            
            if not entry:
                continue

            root_path = os.path.join(GAMES_DIRECTORY, directory)
            if entry.root_subdir:
                root_path = os.path.join(root_path, entry.root_subdir)

            try:
                game_class = self.__load_game_module(
                    f"game_class_{directory}",
                    os.path.join(GAMES_DIRECTORY, directory, os.path.normpath(entry.game_path)),
                    entry.game_field,
                    root_path
                )
            except Exception as ex:
                print(f"(Error - {current_index}/{games_to_load}) No se pudo cargar el juego de: {directory} -> {ex}")
                continue

            try:
                game_metadata = meta_replacements[directory] if directory in meta_replacements else self.__load_game_meta(
                    f"game_metadata_{directory}",
                    os.path.join(GAMES_DIRECTORY, directory, os.path.normpath(entry.metadata_path)),
                    entry.metadata_field,
                    root_path
                )
            except Exception as ex:
                print(f"(Error - {current_index}/{games_to_load}) No se pudieron cargar los metadatos del juego de: {directory} -> {ex}")
                continue

            self.loaded_entries.append((game_class, game_metadata, LoadedGameEntry(directory, entry, root_path)))
            print(f"(OK - {current_index}/{games_to_load}) Juego cargado satisfactoriamente: {game_metadata.title} de {", ".join(game_metadata.authors)}")

        self.loaded_entries.sort(key=lambda x: x[2].raw_entry.sort_order)
        os.chdir(working_directory)

    # Método para cargar un módulo genérico
    def __load_generic_module(self, module_name: str, module_file_path: str, root_path: str) -> ModuleType | None:
        if root_path not in sys.path:
            sys.path.insert(0, root_path)

        modules_before = set(sys.modules.keys())

        spec = importlib.util.spec_from_file_location(module_name, module_file_path)
        if not spec:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        if not spec.loader:
            return None

        spec.loader.exec_module(module)

        modules_added = set(sys.modules.keys()) - modules_before - {module_name}
        for mod in modules_added:
            del sys.modules[mod]

        sys.path.remove(root_path)
        return module

    # Método para cargar el tipo de la clase del juego de forma dinámica
    def __load_game_module(self, module_name: str, module_file_path: str, field: str, root_path: str) -> type[GameBase]:
        os.chdir(root_path)
        module = self.__load_generic_module(module_name, module_file_path, root_path)
        game_class = getattr(module, field)
        if not issubclass(game_class, GameBase):
            raise TypeError(f"Miembro \"{field}\" exportado no es hijo de la clase \"GameBase\"")
        return game_class
    
    # Método para cargar la instancia de los metadatos del juego de forma dinámica
    def __load_game_meta(self, module_name: str, module_file_path: str, field: str, root_path: str) -> GameMeta:
        os.chdir(root_path)
        module = self.__load_generic_module(module_name, module_file_path, root_path)
        metadata = getattr(module, field)
        if not isinstance(metadata, GameMeta):
            raise TypeError(f"Miembro \"{field}\" exportado no es una instancia de \"GameMeta\"")
        return metadata