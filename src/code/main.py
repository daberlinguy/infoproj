import pygame

from pygame_widgets.widget import OrderedSet

pygame.init()

WIDTH = 1920
HEIGHT = 1080

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.SCALED | pygame.FULLSCREEN
)


def main():
    # WeakSet iteration expects OrderedSet.copy on Python 3.14.
    if not hasattr(OrderedSet, "copy"):

        def _ordered_set_copy(self):
            new_set = OrderedSet()
            new_set._od = self._od.copy()
            return new_set

        OrderedSet.copy = _ordered_set_copy

    # Show loading screen and preload assets
    from screens.LoadingScreen import LoadingScreen
    from assets.assets import Texture

    loading_screen = LoadingScreen(screen)

    # Show initial loading
    loading_screen.show("Initializing...", 0.1)
    pygame.time.delay(100)  # Brief delay to ensure screen displays

    # Preload all textures
    loading_screen.show("Loading textures...", 0.3)
    Texture.preload()

    # Loading complete
    loading_screen.show("Starting game...", 1.0)
    pygame.time.delay(300)

    # Start the game
    from screens.TitleScreen import TitleScreen

    TitleScreen(screen, "Title Screen")


if __name__ == "__main__":
    main()
