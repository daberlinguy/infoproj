import pygame
import sys
from pathlib import Path

# Calculate path relative to this file's location
# This works whether running main.py or editor.py
current_file = Path(__file__).resolve()
code_dir = current_file.parent.parent  # Go up to 'code' directory
resources_dir = code_dir.parent / 'resources'

font_path = str(resources_dir / 'assets' / 'fonts' / 'font.ttf')
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

def getMinecraftTexture(location_x: int, location_y: int, width: int, height: int, top_left: tuple = (0, 0)) -> pygame.Surface:
    texture_path = str(resources_dir / 'assets' / 'sprites' / 'texture_atlas.png')
    minecraft_texture = pygame.image.load(texture_path).convert_alpha()
    texture_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    texture_surface.blit(minecraft_texture, top_left, pygame.Rect(location_x, location_y, width, height))
    return texture_surface

class Texture:
    """Texture cache - call init_textures() after pygame display is set"""
    GRASS = None
    DIRT = None
    ICE = None
    STONE = None
    GOLD_BLOCK = None
    LAVA = None
    
    @classmethod
    def init_textures(cls):
        """Initialize textures after pygame display mode is set"""
        if cls.GRASS is None:  # Only load once
            cls.GRASS = getMinecraftTexture(352, 576, 16, 16)
            cls.DIRT = getMinecraftTexture(1024, 176, 16, 16)
            cls.ICE = getMinecraftTexture(112, 576, 16, 16)
            cls.STONE = getMinecraftTexture(640, 640, 16, 16)
            cls.GOLD_BLOCK = getMinecraftTexture(288, 576, 16, 16)
            cls.LAVA = getMinecraftTexture(400, 592, 16, 16)
            

# For backward compatibility, try to init textures immediately if display is already set
# This will fail silently if no display mode is set yet
try:
    if pygame.display.get_surface() is not None:
        Texture.init_textures()
except:
    pass  # Will be initialized later when display is set