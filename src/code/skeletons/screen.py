import pygame
import sys

path=sys.argv[0].replace("main.py","")

class Screen:
    def __init__(this, screen:pygame.Surface, caption:str):
        this.screen=screen
        this.caption=caption
        this.running=True

        pygame.display.set_caption(this.caption)

        while this.running:
            this.run()

    def set_background(this, r:int,g:int,b:int):
        this.screen.fill(r,g,b)

    def set_backgroundImage(this, name:str,scale_width:int=1280,scale_height:int=720):
        imp = pygame.image.load(path+"../resources/assets/backgrounds/"+name).convert()
        imp = pygame.transform.scale(imp, (scale_width, scale_height))
        this.screen.blit(imp, (0,0))

    def draw_text(this, text:int, font:pygame.font.Font, r:int,g:int,b:int, x:float, y:float):
        text_surface = font.render(text, True, (r,g,b))
        this.screen.blit(text_surface, (x, y))
    
    def draw_sprite(this, name:str, x:float, y:float, scale_width:int=None, scale_height:int=None):
        image = pygame.image.load(path+"../resources/assets/sprites/"+name).convert_alpha()
        if scale_width is not None and scale_height is not None:
            image = pygame.transform.scale(image, (scale_width, scale_height))
        this.screen.blit(image, (x, y))

    def run():
        pass