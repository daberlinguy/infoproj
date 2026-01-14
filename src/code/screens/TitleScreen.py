import pygame
import pygame_widgets
from pygame_widgets.button import Button
import sys

from skeletons.screen import Screen
from assets.assets import getFont

class TitleScreen(Screen):
    def __init__(self, screen, caption):

        # Define buttons
        button_width = 150
        button_height = 50
        button_spacing = 20
        start_y = (screen.get_height() / 2) - ((button_height + button_spacing) * 2)

        self.play_btn = Button(screen, (screen.get_width() / 2) - (button_width / 2), start_y, 
                button_width, button_height, False, text="Play", 
                onClick=self.onBtnOpenGameScreen, font=getFont(30), radius=10)
        self.character_btn = Button(screen, (screen.get_width() / 2) - (button_width / 2), start_y + button_height + button_spacing, 
                button_width, button_height, False, text="Character", 
                onClick=self.onBtnOpenCharacterScreen, font=getFont(30), radius=10)
        self.settings_btn = Button(screen, (screen.get_width() / 2) - (button_width / 2), start_y + 2 * (button_height + button_spacing), 
                button_width, button_height, False, text="Settings", 
                onClick=self.onBtnOpenGameScreen, font=getFont(30), radius=10)
        self.exit_btn = Button(screen, (screen.get_width() / 2) - (button_width / 2), start_y + 3 * (button_height + button_spacing), 
                button_width, button_height, False, text="Exit", 
                onClick=sys.exit, font=getFont(30), radius=10)

        # Set Title Text
        self.title_text = "Platformer"
        self.title_width = getFont(60).size(self.title_text)[0]

        
        super().__init__(screen, caption)

    def onBtnOpenGameScreen(self):
        from screens.GameScreen import GameScreen
        GameScreen(self.screen, "Game")  # Add your game screen transition here
    
    def onBtnOpenCharacterScreen(self):
        from screens.CharacterScreen import CharacterScreen
        CharacterScreen(self.screen, "Charaktere")

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                exit()
                pygame.quit()
        
        # Fill screen with Background Image
        self.set_backgroundImage("title.jpg")

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

