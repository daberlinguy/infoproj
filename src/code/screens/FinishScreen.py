import pygame
import pygame
import pygame_widgets
from pygame_widgets.button import Button

from skeletons.screen import Screen
from assets.assets import getFont
from screens.SettingsScreen import SETTINGS


class FinishScreen(Screen):
    def __init__(
        self,
        screen,
        caption,
        attempts: int = 1,
        deaths: int = 0,
        total_time: float = 0.0,
        latest_run_time: float = 0.0,
        background: pygame.Surface | None = None,
    ):
        self.clear_widgets()
        self.attempts = attempts
        self.deaths = deaths
        self.total_time = total_time
        self.latest_run_time = latest_run_time
        self.background = background

        button_width = 220
        button_height = 60
        center_x = (screen.get_width() / 2) - (button_width / 2)
        start_y = (screen.get_height() / 2) + 110

        self.back_btn = Button(
            screen,
            center_x,
            start_y,
            button_width,
            button_height,
            False,
            text="Back to Levels",
            onClick=self.onBtnBack,
            font=getFont(24),
            radius=12,
        )

        self.title_text = "Level Complete"
        self.title_width = getFont(60).size(self.title_text)[0]

        self.overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 160))

        super().__init__(screen, caption)

    def onBtnBack(self):
        self.running = False
        from screens.LevelSelectScreen import LevelSelectScreen

        LevelSelectScreen(self.screen, "Levels", SETTINGS.get("selected_world"))

    def run(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return  # Exit immediately without drawing
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.onBtnBack()

        if self.background:
            self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.overlay, (0, 0))

        self.draw_text(
            self.title_text,
            getFont(60),
            255,
            255,
            255,
            (self.screen.get_width() / 2) - (self.title_width / 2),
            (self.screen.get_height() / 2) - 140,
        )

        stats_x = (self.screen.get_width() / 2) - 190
        stats_y = (self.screen.get_height() / 2) - 70
        self.draw_text(
            f"Attempts: {self.attempts}",
            getFont(24),
            255,
            255,
            255,
            stats_x,
            stats_y,
        )
        stats_y += 30
        self.draw_text(
            f"Deaths: {self.deaths}",
            getFont(24),
            255,
            255,
            255,
            stats_x,
            stats_y,
        )
        stats_y += 30
        self.draw_text(
            f"Total time: {self.total_time:.2f}s",
            getFont(24),
            255,
            255,
            255,
            stats_x,
            stats_y,
        )
        stats_y += 30
        self.draw_text(
            f"Latest run: {self.latest_run_time:.2f}s",
            getFont(24),
            255,
            255,
            255,
            stats_x,
            stats_y,
        )

        self.back_btn.draw()
        pygame_widgets.update(events)
        pygame.display.update()
