import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.toggle import Toggle

from skeletons.screen import Screen
from assets.assets import getFont
from data.storage import load_settings, save_settings

# Global settings dictionary
SETTINGS = load_settings()


class SettingsScreen(Screen):
    def __init__(self, screen, caption):
        # Clear all previous widgets
        self.clear_widgets(mode="remove")

        button_width = 200
        button_height = 50
        button_spacing = 20
        start_y = int((screen.get_height() / 2) - 100)

        # Debug mode toggle
        self.debug_toggle = Toggle(
            screen,
            int((screen.get_width() / 2) + 100),
            int((screen.get_height() / 2) - 200),
            100,
            40,
            startOn=SETTINGS["debug_mode"],
        )

        # Back button
        self.back_btn = Button(
            screen,
            int((screen.get_width() / 2) - (button_width / 2)),
            start_y + 120,
            button_width,
            button_height,
            False,
            text="Back",
            onClick=self.onBtnBack,
            font=getFont(30),
            radius=10,
        )

        # Set Title Text
        self.title_text = "Settings"
        self.title_width = getFont(60).size(self.title_text)[0]

        super().__init__(screen, caption)

    def onBtnBack(self):
        # Save settings before going back
        SETTINGS["debug_mode"] = self.debug_toggle.getValue()
        save_settings(SETTINGS)
        self.running = False
        from screens.TitleScreen import TitleScreen

        TitleScreen(self.screen, "Title Screen")

    def run(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return  # Exit immediately without drawing

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.onBtnBack()

        # Fill screen with Background Image
        self.set_backgroundImage("title.jpg")

        # Draw the Title
        self.draw_text(
            self.title_text,
            getFont(60),
            255,
            255,
            255,
            (self.screen.get_width() / 2) - (self.title_width / 2),
            (self.screen.get_height() / 2) - 300,
        )

        # Draw debug mode label
        self.draw_text(
            "Debug Mode:",
            getFont(30),
            255,
            255,
            255,
            (self.screen.get_width() / 2) - 180,
            (self.screen.get_height() / 2) - 200,
        )

        self.draw_text(
            "Jump:",
            getFont(30),
            255,
            255,
            255,
            (self.screen.get_width() / 2) - 180,
            (self.screen.get_height() / 2) - 150,
        )

        self.draw_text(
            "Left:",
            getFont(30),
            255,
            255,
            255,
            (self.screen.get_width() / 2) - 180,
            (self.screen.get_height() / 2) - 100,
        )

        self.draw_text(
            "Right:",
            getFont(30),
            255,
            255,
            255,
            (self.screen.get_width() / 2) - 180,
            (self.screen.get_height() / 2) - 50,
        )

        self.draw_text(
            "Attack:",
            getFont(30),
            255,
            255,
            255,
            (self.screen.get_width() / 2) - 180,
            (self.screen.get_height() / 2),
        )

        # Draw the buttons and toggle
        self.debug_toggle.draw()
        self.back_btn.draw()

        # Update widgets
        pygame_widgets.update(events)

        # Update Screen
        pygame.display.update()
