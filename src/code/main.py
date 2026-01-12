import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))

def main():
    from screens.TitleScreen import TitleScreen
    TitleScreen(screen, "Title Screen")

if __name__ == '__main__':
    main()
