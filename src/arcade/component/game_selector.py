from math import ceil
class GameSelector:
    """
    Modelo de navegación para el grid de juegos.

    Conceptos clave:
      - El grid tiene N columnas absolutas (calculadas a partir del total de juegos).
      - Solo `visible_columns` columnas se muestran a la vez (ventana deslizante).
      - `scroll_offset` indica qué columna absoluta ocupa la posición visual 0.
      - `current_col` y `current_row` son índices ABSOLUTOS.

    No tiene conocimiento de Pygame ni de la vista.
    """

    def __init__(self, total_games: int, rows_per_col: int = 4, visible_columns: int = 2) -> None:
        self._total = total_games
        self._rows_per_col = rows_per_col
        self._visible_columns = visible_columns
        self._total_columns = max(1, ceil(self._total / self._rows_per_col))

        self._current_col = 0
        self._current_row = 0
        self._scroll_offset = 0

    # --- PROPIEDADES ---
    @property
    def rows_per_col(self) -> int:
        return self._rows_per_col

    @property
    def visible_columns(self) -> int:
        return self._visible_columns

    @property
    def total_columns(self) -> int:
        return self._total_columns

    @property
    def current_col(self) -> int:
        """Columna absoluta seleccionada actualmente."""
        return self._current_col

    @property
    def current_row(self) -> int:
        return self._current_row

    @property
    def scroll_offset(self) -> int:
        """Columna absoluta que ocupa la posición visual 0."""
        return self._scroll_offset

    @property
    def selected_index(self) -> int:
        """Índice absoluto del juego seleccionado."""
        return self._current_col * self._rows_per_col + self._current_row

    # --- OPERACIONES ---
    def abs_index(self, abs_col: int, row: int) -> int:
        return abs_col * self._rows_per_col + row

    def rows_in_col(self, abs_col: int) -> int:
        """Cantidad de filas válidas en una columna absoluta."""
        remaining = self._total - abs_col * self._rows_per_col
        return max(0, min(self._rows_per_col, remaining))

    def is_valid(self, abs_col: int, row: int) -> bool:
        return 0 <= abs_col < self.total_columns and row < self.rows_in_col(abs_col)

    def visible_col_to_abs(self, visible_col: int) -> int:
        """Convierte índice visual de columna -> índice absoluto."""
        return self._scroll_offset + visible_col

    def abs_col_to_visible(self, abs_col: int) -> int | None:
        """
        Convierte índice absoluto -> índice visual de columna.
        Retorna None si la columna no está en la ventana visible actual.
        """
        vis = abs_col - self._scroll_offset
        if 0 <= vis < self._visible_columns:
            return vis
        return None
    
    # --- NAVEGACIÓN ---
    def set_current_col(self, col: int) -> None:
        """
        Mueve la selección a una columna absoluta y actualiza el scroll.
        Clampea la fila para que siempre apunte a un juego válido.
        """
        if not 0 <= col < self.total_columns:
            raise ValueError(
                f"GameGridModel: columna {col} fuera de rango [0, {self.total_columns - 1}]"
            )
        self._current_col = col
        self._clamp_row()
        self._update_scroll()

    def move_right(self) -> bool:
        prev = self._current_col
        self.set_current_col((self._current_col + 1) % self.total_columns)
        return self._current_col != prev

    def move_left(self) -> bool:
        prev = self._current_col
        self.set_current_col((self._current_col - 1) % self.total_columns)
        return self._current_col != prev

    def move_down(self) -> bool:
        prev = self._current_row
        self._current_row = (self._current_row + 1) % self.rows_in_col(self._current_col)
        return self._current_row != prev

    def move_up(self) -> bool:
        prev = self._current_row
        self._current_row = (self._current_row - 1) % self.rows_in_col(self._current_col)
        return self._current_row != prev

    def _clamp_row(self) -> None:
        """Ajusta la fila para que siempre apunte a un juego válido."""
        max_row = self.rows_in_col(self._current_col) - 1
        self._current_row = min(self._current_row, max(0, max_row))

    def _update_scroll(self) -> None:
        if self.total_columns <= self._visible_columns:
            self._scroll_offset = 0
            return

        page = self._current_col // self._visible_columns
        self._scroll_offset = page * self._visible_columns