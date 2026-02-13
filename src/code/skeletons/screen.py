"""Base screen module for the Parkour Game.

This module provides the base `Screen` class that all game screens inherit from.
It handles the main game loop, rendering utilities, and common screen operations.

Example:
    Creating a custom screen::

        from skeletons.screen import Screen

        class MyScreen(Screen):
            def __init__(self, screen, caption):
                # Initialize your widgets/state here BEFORE calling super().__init__
                self.my_button = Button(...)
                super().__init__(screen, caption)

            def run(self):
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        pygame.quit()
                        exit()

                # Draw your screen
                self.set_backgroundImage("my_background.jpg")
                self.my_button.draw()

                # Update display
                pygame.display.update()
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

import pygame

from utils.paths import assets_path


class Screen:
    _background_cache: Dict[Tuple[str, int, int], pygame.Surface] = {}
    _sprite_cache: Dict[Tuple[str, Optional[int], Optional[int]], pygame.Surface] = {}
    """Base class for all game screens.

    This class provides the fundamental structure for screens in the game.
    It manages the main loop, rendering utilities, and screen lifecycle.

    Important:
        When subclassing, initialize all widgets and state variables BEFORE
        calling ``super().__init__()``, as the parent constructor immediately
        starts the game loop.

    Attributes:
        screen: The pygame Surface to render to.
        caption: The window title for this screen.
        running: Controls the main loop. Set to False to exit the screen.

    Args:
        screen: The pygame display Surface.
        caption: The window title to display.
    """

    def __init__(self, screen: pygame.Surface, caption: str) -> None:
        self.screen: pygame.Surface = screen
        self.caption: str = caption
        self.running: bool = True

        pygame.display.set_caption(self.caption)

        # Main game loop - runs until self.running is set to False
        while self.running:
            self.run()

    def set_background(self, r: int, g: int, b: int) -> None:
        """Fill the screen with a solid color.

        Args:
            r: Red component (0-255).
            g: Green component (0-255).
            b: Blue component (0-255).
        """
        self.screen.fill((r, g, b))

    def set_backgroundImage(
        self,
        name: str,
        scale_width: int = pygame.display.Info().current_w,
        scale_height: int = pygame.display.Info().current_h,
    ) -> None:
        """Set a background image from the assets/backgrounds folder.

        The image is loaded, scaled to the specified dimensions, and drawn
        at position (0, 0).

        Args:
            name: Filename of the background image (e.g., "title.jpg").
            scale_width: Target width in pixels. Defaults to 1280.
            scale_height: Target height in pixels. Defaults to 720.

        Raises:
            FileNotFoundError: If the background image doesn't exist.
        """
        cache_key = (name, scale_width, scale_height)
        image = self._background_cache.get(cache_key)
        if image is None:
            image = pygame.image.load(assets_path("backgrounds", name)).convert()
            image = pygame.transform.scale(image, (scale_width, scale_height))
            self._background_cache[cache_key] = image
        self.screen.blit(image, (0, 0))

    @staticmethod
    def clear_widgets(mode: str = "reset") -> None:
        """Clear pygame_widgets from previous screens.

        Args:
            mode: "reset" to replace handler storage, "remove" to detach widgets.
        """
        try:
            from pygame_widgets.widget import WidgetHandler
        except ImportError:
            return

        widgets = WidgetHandler.getWidgets()
        if mode == "remove":
            for widget in list(widgets):
                WidgetHandler.removeWidget(widget)
        else:
            WidgetHandler._widgets = widgets.__class__()

    """def set_btntexture(
            self,
            name: str,
            scale_width: int = 128
            scale_height: int = 64
    ) -> None:
        image = pygame.image.load(assetees_path("button_textures", name)).convert()
        image = pygame.transform.scale(image, (scale_width, scale_height))
        self.screen.blit(image, (20,20))"""

    def draw_text(
        self,
        text: str,
        font: pygame.font.Font,
        r: int,
        g: int,
        b: int,
        x: float,
        y: float,
    ) -> None:
        """Render text to the screen.

        Args:
            text: The text string to display.
            font: A pygame Font object to use for rendering.
            r: Red component of text color (0-255).
            g: Green component of text color (0-255).
            b: Blue component of text color (0-255).
            x: X position in pixels.
            y: Y position in pixels.
        """
        text_surface = font.render(str(text), True, (r, g, b))
        self.screen.blit(text_surface, (x, y))

    def draw_sprite(
        self,
        name: str,
        x: float,
        y: float,
        scale_width: Optional[int] = None,
        scale_height: Optional[int] = None,
    ) -> None:
        """Draw a sprite from the assets/sprites folder.

        Args:
            name: Filename of the sprite image.
            x: X position in pixels.
            y: Y position in pixels.
            scale_width: Optional target width. If provided with scale_height,
                the sprite will be scaled.
            scale_height: Optional target height. If provided with scale_width,
                the sprite will be scaled.
        """
        cache_key = (name, scale_width, scale_height)
        image = self._sprite_cache.get(cache_key)
        if image is None:
            image = pygame.image.load(assets_path("sprites", name)).convert_alpha()
            if scale_width is not None and scale_height is not None:
                image = pygame.transform.scale(image, (scale_width, scale_height))
            self._sprite_cache[cache_key] = image
        self.screen.blit(image, (x, y))

    def drawBar(self, pos, size, borderC, barC, progress):
        """Draw a progress bar on the screen.
        
        Args:
            pos: Tuple of (x, y) position for the bar.
            size: Tuple of (width, height) for the bar.
            borderC: Color tuple (r, g, b) for the border.
            barC: Color tuple (r, g, b) for the progress fill.
            progress: Float between 0.0 and 1.0 representing completion.
        """
        pygame.draw.rect(self.screen, borderC, (*pos, *size), 1)
        innerPos  = (pos[0]+3, pos[1]+3)
        innerSize = ((size[0]-6) * progress, size[1]-6)
        pygame.draw.rect(self.screen, barC, (*innerPos, *innerSize))

    def run(self) -> None:
        """Main update method called every frame.

        Override this method in subclasses to implement screen-specific logic.
        This method should:

        1. Handle pygame events (especially QUIT)
        2. Process input
        3. Update game state
        4. Render the screen
        5. Call ``pygame.display.update()`` or ``flip()``

        Note:
            Remember to handle the quit event to allow clean exit::

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        pygame.quit()
                        exit()
        """
        pass
