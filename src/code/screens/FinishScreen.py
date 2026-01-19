import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.widget import WidgetHandler

from skeletons.screen import Screen
from assets.assets import getFont
from screens.SettingsScreen import SETTINGS


class FinishScreen(Screen):
    def __init__(self, screen, caption):
        widgets = WidgetHandler.getWidgets()
        WidgetHandler._widgets = widgets.__class__()

        button_width = 220
        button_height = 60
        center_x = (screen.get_width() / 2) - (button_width / 2)
        start_y = (screen.get_height() / 2) + 40

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
                exit()
                pygame.quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.onBtnBack()

        self.set_backgroundImage("title.jpg")

        self.draw_text(self.title_text, getFont(60), 255, 255, 255,
                       (self.screen.get_width() / 2) - (self.title_width / 2),
                       (self.screen.get_height() / 2) - 140)

        self.draw_text("All checkpoints reached!", getFont(24), 255, 255, 255,
                       (self.screen.get_width() / 2) - 150,
                       (self.screen.get_height() / 2) - 40)

        self.back_btn.draw()
        pygame_widgets.update(events)
        pygame.display.update()
