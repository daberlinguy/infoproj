import pygame

from pygame_widgets.widget import OrderedSet

pygame.init()
screen = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)

def main():
    # WeakSet iteration expects OrderedSet.copy on Python 3.14.
    if not hasattr(OrderedSet, "copy"):
        def _ordered_set_copy(self):
            new_set = OrderedSet()
            new_set._od = self._od.copy()
            return new_set
        OrderedSet.copy = _ordered_set_copy

    from screens.TitleScreen import TitleScreen
    TitleScreen(screen, "Title Screen")

if __name__ == '__main__':
    main()

