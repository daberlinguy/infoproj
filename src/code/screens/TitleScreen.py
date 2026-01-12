import pygame
import pygame_widgets
from pygame_widgets.button import Button
import sys

from skeletons.screen import Screen
from assets.assets import getFont

class TitleScreen(Screen):
    def __init__(this, screen, caption):

        # Define buttons
        this.play_btn = Button(screen, (screen.get_width() / 2) - 100, (screen.get_height() / 2) - 50, 
                    200, 100, False, text="Play", 
                    onClick=this.onBtnOpenGameScreen, font=getFont(40), radius=20)
        this.settings_btn = Button(screen, (screen.get_width() / 2) - 100, (screen.get_height() / 2) + 70, 
                    200, 100, False, text="Settings", 
                    onClick=this.onBtnOpenGameScreen, font=getFont(40), radius=20)
        this.exit_btn = Button(screen, (screen.get_width() / 2) - 100, (screen.get_height() / 2) + 190, 
                    200, 100, False, text="Exit", onClick=sys.exit, font=getFont(40), radius=20)

        # Set Title Text
        this.title_text = "Platformer"
        this.title_width = getFont(60).size(this.title_text)[0]

        
        super().__init__(screen, caption)

    def onBtnOpenGameScreen(this):
        from screens.GameScreen import GameScreen
        GameScreen(this.screen, "Game")  # Add your game screen transition here

    def run(this):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                this.running = False
                exit()
                pygame.quit()
        
        # Fill screen with Background Image
        this.set_backgroundImage("title.jpg")

        # Draw the Title
        this.draw_text(this.title_text, getFont(60), 255, 255, 255,
                       (this.screen.get_width() / 2) - (this.title_width / 2), 
                       (this.screen.get_height() / 2) - 200)

        # Draw the buttons
        this.play_btn.draw()
        this.settings_btn.draw()
        this.exit_btn.draw()

        # Update widgets
        pygame_widgets.update(pygame.event.get())

        # Update Screen
        pygame.display.update()
