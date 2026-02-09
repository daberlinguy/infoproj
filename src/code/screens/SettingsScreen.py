import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.toggle import Toggle

from skeletons.screen import Screen
from assets.assets import getFont
from data.storage import load_settings, save_settings

# Global settings dictionary
SETTINGS = load_settings()

import pygame as pg
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
FONT = pg.font.Font(None, 32)


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)


"""
def main():
    clock = pg.time.Clock()
    input_box1 = InputBox(100, 100, 140, 32)
    input_box2 = InputBox(100, 300, 140, 32)
    input_boxes = [input_box1, input_box2]
    done = False

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            for box in input_boxes:
                box.handle_event(event)

        for box in input_boxes:
            box.update()

        screen.fill((30, 30, 30))
        for box in input_boxes:
            box.draw(screen)

        pg.display.flip()
        clock.tick(30)
"""

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
            50,
            20,
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

        self.input_boxes = [
            InputBox(
            int((screen.get_width() / 2) + 100),
            int((screen.get_height() / 2)),
            50,
            20,
            text=",".join(SETTINGS["controls"]["attack"]),
        ),
            InputBox(
            int((screen.get_width() / 2) + 100),
            int((screen.get_height() / 2) - 150),
            50,
            20,
            text=",".join(SETTINGS["controls"]["jump"]),
        ),
            InputBox(
            int((screen.get_width() / 2) + 100),
            int((screen.get_height() / 2) - 100),
            50,
            20,
            text=",".join(SETTINGS["controls"]["move_left"]),
        ),
            InputBox(
            int((screen.get_width() / 2) + 100),
            int((screen.get_height() / 2) - 50),
            50,
            20,
            text=",".join(SETTINGS["controls"]["move_right"]),
        )   
        ]

        # Set Title Text
        self.title_text = "Settings"
        self.title_width = getFont(60).size(self.title_text)[0]

        super().__init__(screen, caption)

    def onBtnBack(self):
        # Save settings before going back
        SETTINGS["debug_mode"] = self.debug_toggle.getValue()
        
        # Save input box values to controls
        SETTINGS["controls"]["attack"] = self.input_boxes[0].text.split(",")
        SETTINGS["controls"]["jump"] = self.input_boxes[1].text.split(",")
        SETTINGS["controls"]["move_left"] = self.input_boxes[2].text.split(",")
        SETTINGS["controls"]["move_right"] = self.input_boxes[3].text.split(",")
        
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
            
            # Handle events for all input boxes
            for box in self.input_boxes:
                box.handle_event(event)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.onBtnBack()

        # Update all input boxes
        for box in self.input_boxes:
            box.update()

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
        
        # Draw all input boxes
        for box in self.input_boxes:
            box.draw(self.screen)

        # Update widgets
        pygame_widgets.update(events)

        # Update Screen
        pygame.display.update()
