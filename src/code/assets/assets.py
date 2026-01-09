import pygame
import sys

path=sys.argv[0].replace("main.py","")

font_path = path+'../resources/assets/fonts/font.ttf'
font_size = 40
custom_font = pygame.font.Font(font_path, font_size)

cfont = {}
for i in range(1, 100):
    cfont[i] = pygame.font.Font(font_path, i)  # Use : to create key-value pairs

def getFont(size: int) -> pygame.font.Font:
    if size > 100:
        raise RuntimeError("Out of Range above 100")
    elif size < 0:
        raise RuntimeError("Out of Range below 0")
    else:
        return cfont[size]
