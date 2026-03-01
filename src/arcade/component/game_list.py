import pygame
from typing import TYPE_CHECKING
from .game_selector import GameSelector
from ..util.paths import get_asset
from enum import Enum
from .progress_bar import ProgressBar

# Esto es para evitar la dependencia circular
if TYPE_CHECKING:
    from ..engine import ArcadeEngine

# Layout provisional
_MARGIN_X = 20
_MARGIN_Y = 15
_START_X  = 354
_START_Y  = 305
_PANEL_START_X = 35
_PANEL_WIDTH = 255
_PANEL_START_Y = 512
_PANEL_LINE_X_MARGIN = 15
_PANEL_TITLE_Y_MARGIN = 20
_PANEL_LINE_Y_MARGIN = 9
_PANEL_HEIGHT = 164
_SCROLL_DELAY= 0.4

class TextAlignment(Enum):
    LEFT = 0
    CENTER = 1

class GameList:
    def __init__(self, engine: "ArcadeEngine") -> None:
        self.font_meta = pygame.font.SysFont(pygame.font.get_default_font(), 30)
        self._engine = engine
        self._selector = GameSelector(len(engine.games.loaded_entries))

        self._button_normal = pygame.image.load(str(get_asset("images","button_normal.png"))).convert_alpha()
        self._button_hover = pygame.image.load(str(get_asset("images","button_hover.png"))).convert_alpha()

        self._label_unassigned = self._engine.font_arcade.render("UNASSIGNED", True, (100, 100, 100))
        self._labels_normal:   list[pygame.Surface] = []
        self._labels_selected: list[pygame.Surface] = []
        self._panel_surfs: list[list[tuple[pygame.Surface, TextAlignment]]] = []
        self._load_game_text()
        
        self._marquee_offset = 0.0   # posición X actual del scroll
        self._marquee_speed  = 90    # píxeles por segundo
        self._timer_scroll = 0.0     # Timer para el tiempo tarda en empezar a moverse al seleccionar
        self.progress_bar = ProgressBar(self._engine)

    def update(self, dt: float) -> None:
        if self.progress_bar.shown:
            self.progress_bar.update(dt)
        else:
            self._timer_scroll += dt
            if self._timer_scroll < _SCROLL_DELAY:
                return

            self._marquee_offset += self._marquee_speed * dt

            btn_w   = self._button_normal.get_width()
            sel_abs = self._selector.selected_index
            title   = self._engine.games.loaded_entries[sel_abs][1].title
            label_w = self._engine.font_arcade.size(title)[0]

            center = (btn_w - label_w) // 2

            # Cuando sale por la derecha, reaparece desde la izquierda
            if center + self._marquee_offset >= btn_w:
                self._marquee_offset = -label_w - center

    def render(self) -> None:
        if self.progress_bar.shown:
            self.progress_bar.render()
        else:
            self._render_panel()
            self._render_buttons()
        
    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_UP | pygame.K_w:
                        self._on_move(self._selector.move_up())
                    case pygame.K_DOWN | pygame.K_s:
                        self._on_move(self._selector.move_down())
                    case pygame.K_LEFT | pygame.K_a:
                        self._on_move(self._selector.move_left())
                    case pygame.K_RIGHT | pygame.K_d:
                        self._on_move(self._selector.move_right())
                    case pygame.K_RETURN | pygame.K_SPACE:
                        self._engine.snd_select_game.play()
                        self._launch_selected()
                    case _:
                        pass

    def _render_buttons(self):
        btn_w, btn_h = self._button_normal.get_size()

        for visible_col in range(self._selector.visible_columns):
            abs_col = self._selector.visible_col_to_abs(visible_col)

            for row in range(self._selector.rows_per_col):
                x = _START_X + visible_col * (btn_w + _MARGIN_X)
                y = _START_Y + row         * (btn_h + _MARGIN_Y)

                is_selected = (abs_col == self._selector.current_col and row == self._selector.current_row)
                self._engine.screen.blit(self._button_hover if is_selected else self._button_normal, (x, y))

                if not self._selector.is_valid(abs_col, row):
                    lw = self._label_unassigned.get_width()
                    lh = self._label_unassigned.get_height()
                    self._engine.screen.blit(self._label_unassigned, (x + (btn_w - lw) // 2, y + (btn_h - lh) // 2))
                    continue

                abs_idx = self._selector.abs_index(abs_col, row)
                label   = self._labels_selected[abs_idx] if is_selected else self._labels_normal[abs_idx]
                label_w = label.get_width()
                label_y = y + (btn_h - label.get_height()) // 2
                center  = (btn_w - label_w) // 2

                if is_selected:
                    self._engine.screen.set_clip(pygame.Rect(x + 10, y, btn_w - 20, btn_h))
                    self._engine.screen.blit(label, (x + center + int(self._marquee_offset), label_y))
                    self._engine.screen.set_clip(None)
                else:
                    self._engine.screen.set_clip(pygame.Rect(x + 10, y, btn_w - 20, btn_h))
                    self._engine.screen.blit(label, (x + center, label_y))
                    self._engine.screen.set_clip(None)

    def _render_panel(self) -> None:
        surfs = self._panel_surfs[self._selector.selected_index]    
        combined_height = sum(surf[0].get_height() for surf in surfs) + ((len(surfs) - 2) * _PANEL_LINE_Y_MARGIN) + _PANEL_TITLE_Y_MARGIN
        y = _PANEL_START_Y + (_PANEL_HEIGHT - combined_height) // 2 
        for index, (surf, alignment) in enumerate(surfs):
            self._engine.screen.blit(
                surf,
                (
                    _PANEL_START_X + _PANEL_LINE_X_MARGIN if alignment == TextAlignment.LEFT else _PANEL_START_X + (_PANEL_WIDTH - surf.get_width()) // 2,
                    y
                )
            )
            y += surf.get_height() + (_PANEL_TITLE_Y_MARGIN if index == 0 else _PANEL_LINE_Y_MARGIN)

    def _launch_selected(self) -> None:
        idx = self._selector.selected_index
        if idx < len(self._engine.games.loaded_entries):
            pygame.mixer.music.stop()
            self.progress_bar.shown = True
            self.progress_bar.target_game = idx

    def _on_move(self, moved: bool) -> None:
        if moved:
            self._timer_scroll = 0.0
            self._marquee_offset = 0.0
            self._engine.snd_navigate.play()
        else:
            self._engine.snd_cancel.play()

    def _render_panel_text(self, text: str) -> pygame.Surface:
        return self._engine.font_meta.render(text, True, (255, 255, 255))

    def _load_game_text(self) -> None:
        for _, meta, entry in self._engine.games.loaded_entries:
            title = meta.title.replace(" ", "   ").upper()
            self._labels_normal.append(self._engine.font_arcade.render(title, True, (255, 255, 255)))
            self._labels_selected.append(self._engine.font_arcade.render(title, True, (225, 168, 240)))
            
            game_panel_lines: list[tuple[pygame.Surface, TextAlignment]] = []
            game_panel_lines.extend([
                (self._render_panel_text(f"Group #{meta.group_number} - " + entry.raw_entry.group_day), TextAlignment.CENTER),
                (self._render_panel_text("Members:"), TextAlignment.LEFT)
            ])
            for author in meta.authors:
                game_panel_lines.append((self._render_panel_text(f"- {author}"), TextAlignment.LEFT))
            self._panel_surfs.append(game_panel_lines)