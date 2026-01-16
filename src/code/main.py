import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))

# Initialize textures after display mode is set
from assets.assets import Texture
Texture.init_textures()

def main():
    from screens.TitleScreen import TitleScreen
    TitleScreen(screen, "Title Screen")

if __name__ == '__main__':
    main()

