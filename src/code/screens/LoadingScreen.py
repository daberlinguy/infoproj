"""Loading screen displayed while initializing game assets.

Shows a simple loading animation and progress bar while loading
textures and other assets.
"""

import pygame
from assets.assets import getFont


class LoadingScreen:
    """Simple loading screen with progress bar."""

    def __init__(self, screen: pygame.Surface):
        """Initialize the loading screen.

        Args:
            screen: The pygame display surface to draw on.
        """
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

        # Colors
        self.bg_color = (20, 20, 30)
        self.text_color = (200, 200, 220)
        self.bar_bg_color = (50, 50, 70)
        self.bar_fill_color = (100, 150, 255)

        # Fonts
        self.title_font = getFont(60)
        self.subtitle_font = getFont(30)

    def show(self, message: str = "Loading...", progress: float = 0.0):
        """Display the loading screen with current progress.

        Args:
            message: Loading message to display.
            progress: Loading progress from 0.0 to 1.0.
        """
        self.screen.fill(self.bg_color)

        # Draw title
        title_text = self.title_font.render("Loading", True, self.text_color)
        title_rect = title_text.get_rect(
            center=(self.width // 2, self.height // 2 - 100)
        )
        self.screen.blit(title_text, title_rect)

        # Draw message
        message_text = self.subtitle_font.render(message, True, self.text_color)
        message_rect = message_text.get_rect(
            center=(self.width // 2, self.height // 2 - 30)
        )
        self.screen.blit(message_text, message_rect)

        # Draw progress bar
        bar_width = 400
        bar_height = 30
        bar_x = self.width // 2 - bar_width // 2
        bar_y = self.height // 2 + 30

        # Background bar
        pygame.draw.rect(
            self.screen,
            self.bar_bg_color,
            (bar_x, bar_y, bar_width, bar_height),
            border_radius=5,
        )

        # Fill bar
        fill_width = int(bar_width * min(1.0, max(0.0, progress)))
        if fill_width > 0:
            pygame.draw.rect(
                self.screen,
                self.bar_fill_color,
                (bar_x, bar_y, fill_width, bar_height),
                border_radius=5,
            )

        # Draw percentage
        percent_text = self.subtitle_font.render(
            f"{int(progress * 100)}%", True, self.text_color
        )
        percent_rect = percent_text.get_rect(
            center=(self.width // 2, bar_y + bar_height + 30)
        )
        self.screen.blit(percent_text, percent_rect)

        pygame.display.flip()
