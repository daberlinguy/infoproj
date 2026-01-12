import pygame
import sys

path = sys.argv[0].replace("main.py", "")

class Platform:
    def __init__(this, x, y, width, height, color=(100, 100, 100)):
        this.rect = pygame.Rect(x, y, width, height)
        this.color = color
    
    def draw(this, screen):
        pygame.draw.rect(screen, this.color, this.rect)
