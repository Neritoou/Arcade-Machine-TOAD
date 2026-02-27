import os
import importlib.util
import sys
from arcade_machine_sdk import GameBase, GameMeta
from types import ModuleType
from dataclasses import dataclass

GAMES_DIRECTORY = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "games"))

@dataclass
class GameEntry:
    metadata_path: str
    metadata_field: str
    game_path: str
    game_field: str
    root_subdir: str = ""

class GameRegistry:
    def __init__(self) -> None:
        self.entries = {
            "centipede": GameEntry("Main.py", "metadata", "Game.py", "Game"),
            "donkey-kong": GameEntry("main.py", "metadata", "game/game.py", "DonkeyKong"),
            "frogger": GameEntry("main.py", "metadata", "engine.py", "Game"),
            "galaga": GameEntry("main.py", "metadata", "game.py", "GalagaGame"),
            "space-invaders": GameEntry("main.py", "metadata", "src/game.py", "Game"),
            "street-fighter": GameEntry("src/main.py", "metadata", "src/main.py", "StreetFighterGame", "src"), # modified to work
            "tetris": GameEntry("main.py", "metadata", "src/core/game.py", "Game"),
            "tron": GameEntry("main.py", "metadata", "tron_game/game.py", "TronGame"),
        }
        self.loaded_entries: list[tuple[type[GameBase], GameMeta, str]] = []

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
                game_metadata = self.__load_game_meta(
                    f"game_metadata_{directory}",
                    os.path.join(GAMES_DIRECTORY, directory, os.path.normpath(entry.metadata_path)),
                    entry.metadata_field,
                    root_path
                )
            except Exception as ex:
                print(f"(Error - {current_index}/{games_to_load}) No se pudieron cargar los metadatos del juego de: {directory} -> {ex}")
                continue

            self.loaded_entries.append((game_class, game_metadata, root_path))
            print(f"(OK - {current_index}/{games_to_load}) Juego cargado satisfactoriamente: {game_metadata.title} de {", ".join(game_metadata.authors)}")

        os.chdir(working_directory)

    # Método para cargar un módulo genérico
    def __load_generic_module(self, module_name: str, module_file_path: str, root_path: str) -> ModuleType | None:
        print(root_path)
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
        print(module)
        game_class = getattr(module, field)
        if not issubclass(game_class, GameBase):
            raise TypeError(f"Miembro \"{field}\" exportado no es hijo de la clase \"GameBase\"")
        return game_class
    
    # Método para cargar la instancia de los metadatos del juego de forma dinámica
    def __load_game_meta(self, module_name: str, module_file_path: str, field: str, root_path: str) -> GameMeta:
        os.chdir(root_path)
        module = self.__load_generic_module(module_name, module_file_path, root_path)
        print(module)
        metadata = getattr(module, field)
        if not isinstance(metadata, GameMeta):
            raise TypeError(f"Miembro \"{field}\" exportado no es una instancia de \"GameMeta\"")
        return metadata