import pygame
import pygame_widgets
from pygame_widgets.button import Button
import sys

from skeletons.screen import Screen
from assets.assets import getFont

class CharacterScreen(Screen):
    def __init__(self, screen, caption):
        # Clear all existing widgets from previous screens
        pygame_widgets.WidgetHandler.getWidgets().clear()
        
        button_width = 150
        button_height = 50
        button_spacing = 20
        start_y = (screen.get_height() / 2) - ((button_height + button_spacing) * 2)

        # Define buttons
        self.character1_btn = Button(screen, (screen.get_width() / 2) - 100, (screen.get_height() / 2) - 50, 
                    200, 100, False, text="Charakter 1", 
                    onClick=self.selectCharacter, font=getFont(40), radius=20)
        self.character2_btn = Button(screen, (screen.get_width() / 2) - 100, (screen.get_height() / 2) + 70, 
                    200, 100, False, text="Charakter 2", 
                    onClick=self.selectCharacter, font=getFont(40), radius=20)
        self.character3_btn = Button(screen, (screen.get_width() / 2) - 100, (screen.get_height() / 2) + 190, 
                    200, 100, False, text="Charakter 3", 
                    onClick=self.selectCharacter, font=getFont(40), radius=20)

        # Set Title Text
        self.title_text = "Platformer"
        self.title_width = getFont(60).size(self.title_text)[0]

       
       super().__init__(screen, caption)

    def selectCharacter(self):
        from screens.GameScreen import GameScreen
        GameScreen(self.screen, "Game")

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                exit()
                pygame.quit()
        
        # Fill screen with Background Image
        self.set_backgroundImage("characters.jpg")

        # Draw the Title
        self.draw_text(self.title_text, getFont(60), 255, 255, 255,
                       (self.screen.get_width() / 2) - (self.title_width / 2), 
                       (self.screen.get_height() / 2) - 200)

        # Draw the buttons
        self.play_btn.draw()
        self.settings_btn.draw()
        self.exit_btn.draw()

        # Update widgets
        pygame_widgets.update(pygame.event.get())

        # Update Screen
        pygame.display.update()
