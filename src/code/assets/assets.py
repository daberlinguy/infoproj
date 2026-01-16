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

def getMinecraftTexture(location_x: int, location_y: int, width: int, height: int, top_left: tuple = (0, 0)) -> pygame.Surface:
    texture_path = path+'../resources/assets/sprites/texture_atlas.png'
    minecraft_texture = pygame.image.load(texture_path).convert_alpha()
    texture_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    texture_surface.blit(minecraft_texture, top_left, pygame.Rect(location_x, location_y, width, height))
    return texture_surface

class Texture:
    GRASS = getMinecraftTexture(352, 576, 16, 16)
    ICE = getMinecraftTexture(112, 576, 16, 16)
    ICEBROKEN = getMinecraftTexture(128, 576, 16, 16)
    ICEBROKEN2 = getMinecraftTexture(144, 576, 16, 16)
    ICEBROKEN3 = getMinecraftTexture(160, 576, 16, 16)
    STONE = getMinecraftTexture(640, 640, 16, 16)
    GOLD_BLOCK = getMinecraftTexture(288, 576, 16, 16)
    LAVA = getMinecraftTexture(400, 592, 16, 16)
    FLETCHINGTABLE = getMinecraftTexture(48, 576, 16, 16)
    FLETCHINGTABLE2 = getMinecraftTexture(64, 576, 16, 16)
    FLETCHINGTABLE3 = getMinecraftTexture(80, 576, 16, 16)
    OVENOFF = getMinecraftTexture(176, 576, 16, 16)
    OVENON = getMinecraftTexture(192, 576, 16, 16)
    OVENBEHIND = getMinecraftTexture(208, 576, 16, 16)
    OVENTOP = getMinecraftTexture(224, 576, 16, 16)