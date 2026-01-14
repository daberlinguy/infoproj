import pygame
import sys

path=sys.argv[0].replace("main.py","")

class Screen:
    def __init__(self, screen:pygame.Surface, caption:str):
        self.screen=screen
        self.caption=caption
        self.running=True

        pygame.display.set_caption(self.caption)

        while self.running:
            self.run()

    def set_background(self, r:int,g:int,b:int):
        self.screen.fill(r,g,b)

    def set_backgroundImage(self, name:str,scale_width:int=1280,scale_height:int=720):
        imp = pygame.image.load(path+"../resources/assets/backgrounds/"+name).convert()
        imp = pygame.transform.scale(imp, (scale_width, scale_height))
        self.screen.blit(imp, (0,0))

    def draw_text(self, text:int, font:pygame.font.Font, r:int,g:int,b:int, x:float, y:float):
        text_surface = font.render(text, True, (r,g,b))
        self.screen.blit(text_surface, (x, y))
    
    def draw_sprite(self, name:str, x:float, y:float, scale_width:int=None, scale_height:int=None):
        image = pygame.image.load(path+"../resources/assets/sprites/"+name).convert_alpha()
        if scale_width is not None and scale_height is not None:
            image = pygame.transform.scale(image, (scale_width, scale_height))
        self.screen.blit(image, (x, y))

    def run():
        pass
