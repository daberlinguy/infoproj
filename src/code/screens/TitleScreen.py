import pygame
import pygame_widgets
from pygame_widgets.button import Button

from skeletons.screen import Screen
from assets.assets import getFont
from utils.paths import assets_path
from screens.SettingsScreen import SETTINGS


class TitleScreen(Screen):
    def quit_game(self):
        """Properly quit the game."""
        self.running = False
        self.should_quit = True

    def __init__(
        self, screen, caption, allow_escape_quit=True, block_escape_until_release=False
    ):
        self.should_quit = False
        self.allow_escape_quit = allow_escape_quit
        self._escape_blocked = block_escape_until_release
        # Clear all previous widgets
        # Avoid WeakSet iteration issues on Python 3.14 by resetting the handler.
        self.clear_widgets()

        # Define buttons
        button_width = 200
        button_height = 50
        button_spacing = 20
        start_y = (screen.get_height() / 2) - ((button_height + button_spacing) * 1.5)

        button_x = (screen.get_width() / 2) - (button_width / 2)

        self.button_texture = pygame.image.load(
            assets_path("backgrounds/button_background.png")
        ).convert_alpha()
        self.button_texture = pygame.transform.scale(
            self.button_texture, (button_width, button_height)
        )

        self.button_hover_texture = self.button_texture.copy()
        # Create a white overlay with alpha to brighten the image for hover effect
        brighten_surface = pygame.Surface(
            self.button_hover_texture.get_size(), pygame.SRCALPHA
        )
        brighten_surface.fill((255, 255, 255, 50))
        self.button_hover_texture.blit(brighten_surface, (0, 0))

        self.worlds_btn = Button(
            screen,
            button_x,
            start_y,
            button_width,
            button_height,
            False,
            text="Worlds",
            onClick=self.onBtnOpenWorldsScreen,
            font=getFont(30),
            radius=10,
            image=self.button_texture,
        )
        self.character_btn = Button(
            screen,
            button_x,
            start_y + button_height + button_spacing,
            button_width,
            button_height,
            False,
            text="Characters",
            onClick=self.onBtnOpenCharacterScreen,
            font=getFont(30),
            radius=10,
            image=self.button_texture,
        )
        self.settings_btn = Button(
            screen,
            button_x,
            start_y + 2 * (button_height + button_spacing),
            button_width,
            button_height,
            False,
            text="Settings",
            onClick=self.onBtnOpenSettingsScreen,
            font=getFont(30),
            radius=10,
            image=self.button_texture,
        )
        self.exit_btn = Button(
            screen,
            button_x,
            start_y + 3 * (button_height + button_spacing),
            button_width,
            button_height,
            False,
            text="Exit",
            onClick=self.quit_game,
            font=getFont(30),
            radius=10,
            image=self.button_texture,
        )

        buttons = [
            self.worlds_btn,
            self.character_btn,
            self.settings_btn,
            self.exit_btn,
        ]
        for btn in buttons:
            btn.onHover = lambda b=btn: b.setImage(self.button_hover_texture)
            btn.onHoverRelease = lambda b=btn: b.setImage(self.button_texture)

        # Set Title Text
        self.title_text = "Parkuhr"
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
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.quit_game()
                return
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self._escape_blocked = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.allow_escape_quit and not self._escape_blocked:
                        self.quit_game()
                        return

        # Fill screen with Background Image
        self.set_backgroundImage(
            "plains.png",
            scale_height=self.screen.get_height(),
            scale_width=self.screen.get_width(),
        )

        # Draw the Title with a rounded translucent badge
        badge_padding_x = 24
        badge_padding_y = 12
        badge_width = self.title_width + badge_padding_x * 2
        badge_height = 60 + badge_padding_y * 2
        badge_x = (self.screen.get_width() / 2) - (badge_width / 2)
        badge_y = (self.screen.get_height() / 2) - 230
        badge_surface = pygame.Surface((badge_width, badge_height), pygame.SRCALPHA)
        pygame.draw.rect(
            badge_surface,
            (255, 255, 255, 120),
            badge_surface.get_rect(),
            border_radius=16,
        )
        pygame.draw.rect(
            badge_surface, (0, 0, 0, 200), badge_surface.get_rect(), 2, border_radius=16
        )
        self.screen.blit(badge_surface, (badge_x, badge_y))
        self.draw_text(
            self.title_text,
            getFont(60),
            0,
            0,
            0,
            (self.screen.get_width() / 2) - (self.title_width / 2),
            badge_y + badge_padding_y,
        )

        # Draw the buttons
        self.worlds_btn.draw()
        self.character_btn.draw()
        self.settings_btn.draw()
        self.exit_btn.draw()
        # self.set_btntexture()
        # Update widgets
        pygame_widgets.update(events)

        # Update Screen
        pygame.display.update()
