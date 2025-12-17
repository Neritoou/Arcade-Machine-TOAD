import os
import importlib.util
import sys
from arcade_machine_sdk import GameBase, GameMeta
from types import ModuleType

GAMES_DIRECTORY = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "games"))

class GameRegistry:
    def __init__(self) -> None:
        self.entries: list[tuple[type[GameBase], GameMeta]] = []
        pass

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
        for directory in directories:
            current_index += 1
            game_path = os.path.join(GAMES_DIRECTORY, directory, "game.py")
            main_path = os.path.join(GAMES_DIRECTORY, directory, "main.py")
            
            if not os.path.isfile(game_path):
                print(f"(Error - {current_index}/{games_to_load}) No se encontró game.py en: {directory}")
                continue

            try:
                game_class = self.__load_game_module(f"game_{directory}", game_path)
            except Exception as ex:
                print(f"(Error - {current_index}/{games_to_load}) No se pudo cargar el juego de: {directory} -> {ex}")
                continue

            try:
                game_metadata = self.__load_game_meta(f"game_main_{directory}", main_path)
            except Exception as ex:
                print(f"(Error - {current_index}/{games_to_load}) No se pudieron cargar los metadatos del juego de: {directory} -> {ex}")
                continue

            self.entries.append((game_class, game_metadata))
            print(f"(OK - {current_index}/{games_to_load}) Juego cargado satisfactoriamente: {game_metadata.title} de {", ".join(game_metadata.authors)}")

    # Función para cargar un módulo genérico
    def __load_generic_module(self, module_name: str, module_file_path: str) -> ModuleType | None:
        module_dir = os.path.dirname(module_file_path)
        if os.path.dirname(module_file_path) not in sys.path:
            sys.path.insert(0, module_dir)

        spec = importlib.util.spec_from_file_location(module_name, module_file_path)
        if not spec:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        if not spec.loader:
            return None

        spec.loader.exec_module(module)
        sys.path.remove(module_dir)
        return module

    # Método para cargar el tipo de la clase del juego de forma dinámica
    def __load_game_module(self, module_name: str, module_file_path: str) -> type[GameBase]:
        module = self.__load_generic_module(module_name, module_file_path)
        game_class = getattr(module, "Game")
        if not issubclass(game_class, GameBase):
            raise TypeError("Miembro \"Game\" exportado no es hijo de la clase \"GameBase\"")
        return game_class
    
    # Método para cargar la instancia de los metadatos del juego de forma dinámica
    def __load_game_meta(self, module_name: str, module_file_path: str) -> GameMeta:
        module = self.__load_generic_module(module_name, module_file_path)
        metadata = getattr(module, "metadata")
        if not isinstance(metadata, GameMeta):
            raise TypeError("Miembro \"metadata\" exportado no es una instancia de \"GameMeta\"")
        return metadata