import pygame
import sys

path=sys.argv[0].replace("main.py","")

class Spieler:
    def __init__(this, player_pos):
        player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
        
        
    def move_left(this,player_pos,dt):
            player_pos.x += 300 * dt
    
    def move_right(this,player_pos,dt):
            player_pos.x -= 300 * dt

    def move_fwd(this,player_pos,dt):
            player_pos.y += 300 * dt

    def move_bck(this,player_pos,dt):
            player_pos.y -= 300 * dt
