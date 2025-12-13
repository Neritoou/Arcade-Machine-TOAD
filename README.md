# Arcade Machine - INSTRUCTIONS

## 1. Propósito del Proyecto

Arcade Machine es un sistema centralizado que integra múltiples juegos arcade creados por diferentes grupos en un único Core. Permite seleccionar y ejecutar cualquier juego desde un menú principal, manteniendo una única ventana y cumpliendo los estándares de resolución, FPS y estructura de código definidos para el proyecto.

---

## 2. Uso de `build` en cada juego

Cada juego debe incluir la carpeta `build/` con los siguientes archivos:

* `cover_image.png`: Imagen de portada del juego.
* `gameplay_images/`: Mínimo 5 imágenes representando el gameplay.
* `gameplay_video.mp4`: Video de 15 segundos del gameplay.
* `game_data.json`: Archivo JSON con información obligatoria:

### Estructura requerida de `game_data.json`

```json
{
    "title": "Nombre Ejemplo",
    "description": "Juego arcade básico.",
    "release_date": "24/05/2006",
    "tags": ["Aventura", "Accion"],
    "group": "1",
    "authors": ["Pedrito", "Pablito"]
}
```

**Reglas importantes:**

* `description` máximo 30 caracteres.
* `game_data.json` es utilizado por el Core para mostrar información del juego en el menú.
* El Core importa este archivo para mostrar datos en la selección de juego.

---

## 3. Clase abstracta `GameModule`

Todos los juegos deben heredar de `GameModule` para integrarse al Core, el cual permite que el se ejecute cualquier juego sin modificar su código interno.

**Reglas Importantes:**

* La ventana/screen es única, proporcionada por el Core. **No crear nuevas ventanas**.
* `_running` indica si el juego está activo.
* Al sobrescribir métodos no abstractos, se debe implementar previamente `super().`.
* Solo existirá un Game Loop central del proyecto ejecutado en el Core.

---

## 4. Ejecución de los Juegos

Cada juego puede ejecutarse de **dos formas**, dependiendo de si se está desarrollando o si ya está integrado al Core.

### 4.1 Modo local (Desarrollo y pruebas)

- **Propósito:** Permite a los desarrolladores probar el juego de manera independiente, sin necesidad de abrir el Core.
- **Características:**
  - El juego **recibe** la `screen` creada por la clase `Screen` y no debe crear una ventana propia.
  - Ideal para desarrollo de lógica, animaciones, sonido y testeo de features específicas.
  - No depende del Core ni del menú centralizado.

  
  -  (?) Debe incluir temporalmente en el repositorio del juego las siguientes utilidades (tal cual está en la plantilla) para pruebas:
    - Archivo `screen` para manejar la ventana.
    - Archivo `constants` con resoluciones, FPS y demás configuraciones.
    - Archivo `interfaces` para herencia y cumplir la interfaz.
  - Una vez finalizadas las pruebas y el desarrollo del juego, estas clases/utilidades **deben eliminarse** del repositorio del juego, ya que en la integración con el Core no se necesitan.


**Ejemplo de `main.py` para ejecución local:**

```python
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
    game = MyGame()
    game.initialize(config={})  # Configuración específica si aplica
    game.start()

    running = True
    while running:
        dt = screen.tick() 
        events = pygame.event.get()

        # De esto se encargará el Core posteriormente
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        game.handle_input(events)
        game.update(dt)

        screen.clear(bg_color) # De esto se encargará el core posteriormente
        game.render()

        screen.update()  # Actualiza la pantalla y respeta el FPS

    game.stop()
    screen.close()

if __name__ == "__main__":
    main()
```
En general, la lógica del código debe centrarse en los 3 métodos principales: `game.handle_input`, `game_update(dt)` y `game.render(screen.surface)`
### 4.2. Modo Core (Integración al menú de Arcane Machine)

- **Propósito:** Ejecutar el juego desde el menú centralizado del Core, manteniendo una única ventana y un solo Game Loop.
- **Características:**
    - El Core controla el loop global (while running) y la ventana (screen.surface).
    - El juego no debe crear su propia ventana ni loop.
    - Todos los métodos obligatorios de GameModule (handle_input, update, render, etc.) son llamados por el Core cada frame.
    - La inicialización y el start() se manejan cuando el usuario selecciona el juego desde el menú.

- **Flujo en Core:**
    1. Usuario selecciona el juego desde el menú.
    2. El Core instancia MyGame().
    3. Se llama a initialize(config) y luego a start().
    4. Cada frame, el Core llama:
        - handle_input(events)
        - update(dt)
        - render()
    5. Cuando el juego termina o el usuario vuelve al menú, se llama a stop().


**Reglas importantes:**
* Se prohibe el uso de funciones que alteren el flujo del Game Loop forzosamente (ej. `time.sleep(), pygame.time.delay(), pygame.time.wait()`)
* Para esperar o temporizar animaciones, se debe usar el delta time del Core, timers o cálculos basados en FPS.
---


## 5. Convenciones de Código

* Clases: `CamelCase` (ej. `UiManager`, `HandleInput`)
* Variables y métodos: `snake_case` (ej. `get_info`, `save_json`)
* Constantes: `UPPER_CASE` (ej. `BASE_RESOLUTION`)
* Comentarios en español, código en inglés.
* Docstrings con tipo de argumentos y retorno:

```python
def load_json(file_path: str) -> Dict[str, Any]:
    """
    Carga un archivo JSON y devuelve un diccionario.

    args:
        **file_path**: str, ruta completa al archivo JSON.

    returns:
        Dict[str, Any]: diccionario con los datos del JSON.
    """
    # Implementación
```



## 6. Requisitos obligatorios

* Resolución estándar: 1280x1024 (SXGA).
* FPS mínimos: 30, máximos: 60.
* Documentación completa: `README.md` (detalles sobre los Archivos) y `requirements.txt` (Librerias utilizadas que requieran instalación).
* Código modular, organizado y siguiendo convenciones.

---

**Fin de INSTRUCTIONS.md**

