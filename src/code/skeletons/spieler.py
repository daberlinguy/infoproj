import pygame
import sys

path=sys.argv[0].replace("main.py","")

class Spieler:
    def __init__(self, player_pos):
        player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
        
        
    def move_left(player_pos,dt):
        if  keys[pygame.K_a]:
            player_pos.x -= 300 * dt
    
    def move_right(player_pos,dt):
        if keys[pygame.K_d]:
            player_pos.x -= 300 * dt

    def move_fwd(player_pos,dt):
        if keys[pygame.K_w]:
            player_pos.y += 300 * dt

    def move_bck(player_pos,dt):
        if keys[pygame.K_s]:
            player_pos.y -= 300 * dt
