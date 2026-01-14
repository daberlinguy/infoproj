import pygame
import sys

path = sys.argv[0].replace("main.py", "")

class Grid:
    def __init__(this, cell_size=50, color=(50, 50, 50), line_width=1):
        this.cell_size = cell_size
        this.color = color
        this.line_width = line_width
        this.visible = False
    
    def toggle(this):
        this.visible = not this.visible
    
    def set_cell_size(this, size):
        this.cell_size = max(10, min(200, size))  # Begrenzt zwischen 10 und 200
    
    def draw(this, screen):
        if not this.visible:
            return
        
        width, height = screen.get_size()
        
        # Vertikale Linien - eine extra Linie am rechten Rand
        for x in range(0, width + 1, this.cell_size):
            pygame.draw.line(screen, this.color, (x, 0), (x, height), this.line_width)
        
        # Horizontale Linien - eine extra Linie am unteren Rand
        for y in range(0, height + 1, this.cell_size):
            pygame.draw.line(screen, this.color, (0, y), (width, y), this.line_width)
    
    def snap_to_grid(this, x, y):
        """Schnapp Koordinaten zum nächsten Grid-Punkt"""
        return (x // this.cell_size) * this.cell_size, (y // this.cell_size) * this.cell_size

class Platform:
    def __init__(this, x, y, width, height, color=(100, 100, 100)):
        this.rect = pygame.Rect(x, y, width, height)
        this.color = color
    
    def draw(this, screen):
        pygame.draw.rect(screen, this.color, this.rect)
