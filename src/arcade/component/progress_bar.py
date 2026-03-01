from ..util import ease_in_out_cubic
from typing import TYPE_CHECKING
import pygame
from arcade_machine_sdk import BASE_WIDTH, BASE_HEIGHT

if TYPE_CHECKING:
    from ..engine import ArcadeEngine

PROGRESS_DURATION = 1
BAR_WIDTH = 340
BAR_HEIGHT = 50
BORDER = 3
GAP = 20

class ProgressBar:
    def __init__(self, engine: "ArcadeEngine"):
        self._engine = engine
        self.shown = False
        self.progress = 0
        self.target_game = 0
        self._elapsed = 0
        self.loading_surf = self._engine.font_arcade.render("NOW  LOADING", True, (255, 255, 255))
        self.please_wait_surf = self._engine.font_arcade.render("PLEASE  WAIT", True, (255, 255, 255))

    def render(self):
        self._engine.screen.fill((0, 0, 0))
        filled_width = int(self.progress * BAR_WIDTH)

        percent_text = f"{int(self.progress * 100)}"
        percent_surf_dark = self._engine.font_arcade.render(percent_text, True, (255, 255, 255))
        percent_surf_light = self._engine.font_arcade.render(percent_text, True, (0, 0, 0))

        combined_height = (
            self.loading_surf.get_height() +
            GAP +
            BAR_HEIGHT +
            GAP +
            self.please_wait_surf.get_height()
        )
        x = (BASE_WIDTH - BAR_WIDTH) // 2
        y = (BASE_HEIGHT - combined_height) // 2

        self._engine.screen.blit(self.loading_surf, ((BASE_WIDTH - self.loading_surf.get_width()) // 2, y))
        y += self.loading_surf.get_height() + GAP

        pygame.draw.rect(self._engine.screen, (255, 255, 255), (x - BORDER, y - BORDER, BAR_WIDTH + BORDER * 2, BAR_HEIGHT + BORDER * 2), BORDER)
        pygame.draw.rect(self._engine.screen, (30, 30, 30), (x, y, BAR_WIDTH, BAR_HEIGHT))
        if filled_width > 0:
            pygame.draw.rect(self._engine.screen, (255, 255, 255), (x, y, filled_width, BAR_HEIGHT))

        text_x = x + (BAR_WIDTH - percent_surf_dark.get_width()) // 2
        text_y = y + (BAR_HEIGHT - percent_surf_dark.get_height()) // 2

        self._engine.screen.set_clip((x + filled_width, y, BAR_WIDTH - filled_width, BAR_HEIGHT))
        self._engine.screen.blit(percent_surf_dark, (text_x, text_y))

        self._engine.screen.set_clip((x, y, filled_width, BAR_HEIGHT))
        self._engine.screen.blit(percent_surf_light, (text_x, text_y))

        self._engine.screen.set_clip(None)

        self._engine.screen.blit(self.please_wait_surf, ((BASE_WIDTH - self.please_wait_surf.get_width()) // 2, y + BAR_HEIGHT + GAP))

    def update(self, dt: float):
        if not self.shown:
            return
        if self.progress >= 1:
            self._engine.run_game(self.target_game)

        self._elapsed = min(self._elapsed + dt, PROGRESS_DURATION)
        self.progress = ease_in_out_cubic(self._elapsed / PROGRESS_DURATION)

    def reset(self):
        self.shown = False
        self.progress = 0
        self._elapsed = 0