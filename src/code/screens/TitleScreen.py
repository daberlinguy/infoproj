import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.widget import WidgetHandler
import sys

from skeletons.screen import Screen
from assets.assets import getFont
from screens.SettingsScreen import SETTINGS

class TitleScreen(Screen):
    def __init__(self, screen, caption):
        # Clear all previous widgets
        widgets = WidgetHandler.getWidgets()
        # Avoid WeakSet iteration issues on Python 3.14 by resetting the handler.
        WidgetHandler._widgets = widgets.__class__()

        # Define buttons
        button_width = 200
        button_height = 50
        button_spacing = 20
        start_y = (screen.get_height() / 2) - ((button_height + button_spacing) * 1.5)

        button_x = (screen.get_width() / 2) - (button_width / 2)
        
        self.texture = "button_background.png"
        
        self.worlds_btn = Button(screen, button_x, start_y,
                button_width, button_height, False, text="Worlds",
                onClick=self.onBtnOpenWorldsScreen, font=getFont(30), radius=10)
        self.character_btn = Button(screen, button_x, start_y + button_height + button_spacing,
                button_width, button_height, False, text="Characters", 
                onClick=self.onBtnOpenCharacterScreen, font=getFont(30), radius=10)
        self.settings_btn = Button(screen, button_x, start_y + 2 * (button_height + button_spacing),
                button_width, button_height, False, text="Settings", 
                onClick=self.onBtnOpenSettingsScreen, font=getFont(30), radius=10)
        self.exit_btn = Button(screen, button_x, start_y + 3 * (button_height + button_spacing),
                button_width, button_height, False, text="Exit",
                onClick=sys.exit, font=getFont(30), radius=10)

        # Set Title Text
        self.title_text = "Platformer"
        self.title_width = getFont(60).size(self.title_text)[0]
        

        
        super().__init__(screen, caption)

    def onBtnOpenGameScreen(self):
        self.running = False
        from screens.GameScreen import GameScreen
        if SETTINGS.get("selected_world") and SETTINGS.get("selected_level"):
            from data.storage import load_worlds
            worlds = load_worlds()
            world = worlds.get(SETTINGS["selected_world"])
            if world:
                for level in world["levels"]:
                    if level["id"] == SETTINGS["selected_level"]:
                        GameScreen(self.screen, "Game", level_path=level["path"])
                        return
        GameScreen(self.screen, "Game")
    
    def onBtnOpenCharacterScreen(self):
        self.running = False
        from screens.CharacterScreen import CharacterScreen
        CharacterScreen(self.screen, "Charaktere")
    
    def onBtnOpenSettingsScreen(self):
        self.running = False
        from screens.SettingsScreen import SettingsScreen
        SettingsScreen(self.screen, "Settings")
    
    def onBtnOpenWorldsScreen(self):
        self.running = False
        from screens.WorldSelectScreen import WorldSelectScreen
        WorldSelectScreen(self.screen, "Worlds")

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                exit()
                pygame.quit()
        
        # Fill screen with Background Image
        self.set_backgroundImage("title.jpg", scale_height=self.screen.get_height(), scale_width=self.screen.get_width())

        # Draw the Title with a rounded translucent badge
        badge_padding_x = 24
        badge_padding_y = 12
        badge_width = self.title_width + badge_padding_x * 2
        badge_height = 60 + badge_padding_y * 2
        badge_x = (self.screen.get_width() / 2) - (badge_width / 2)
        badge_y = (self.screen.get_height() / 2) - 230
        badge_surface = pygame.Surface((badge_width, badge_height), pygame.SRCALPHA)
        pygame.draw.rect(badge_surface, (255, 255, 255, 120), badge_surface.get_rect(), border_radius=16)
        pygame.draw.rect(badge_surface, (0, 0, 0, 200), badge_surface.get_rect(), 2, border_radius=16)
        self.screen.blit(badge_surface, (badge_x, badge_y))
        self.draw_text(self.title_text, getFont(60), 0, 0, 0,
                       (self.screen.get_width() / 2) - (self.title_width / 2),
                       badge_y + badge_padding_y)

        # Draw the buttons
        self.worlds_btn.draw()
        self.character_btn.draw()
        self.settings_btn.draw()
        self.exit_btn.draw()
        #self.set_btntexture()
        # Update widgets
        pygame_widgets.update(pygame.event.get())

        # Update Screen
        pygame.display.update()

