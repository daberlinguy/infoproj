import pygame
import sys

path=sys.argv[0].replace("main.py","")

class Spieler:
    def __init__(this, player_pos, dt, radius=40):
        this.player_pos = player_pos
        this.dt = dt
        this.radius = radius
        this.velocity_y = 0
        this.gravity = 980
        this.jump_strength = -500
        this.is_on_ground = False
        this.prev_y = player_pos.y  # Track previous Y position
        
    def move_left(this):
        this.player_pos.x -= 300 * this.dt

    def move_right(this):
        this.player_pos.x += 300 * this.dt

    def jump(this):
        if this.is_on_ground:
            this.velocity_y = this.jump_strength
            this.is_on_ground = False
    
    def on_ground(this):
        return this.is_on_ground


    def apply_gravity(this, dt):
        this.prev_y = this.player_pos.y  # Store position before applying gravity
        if not this.is_on_ground:
            this.velocity_y += this.gravity * dt
            this.player_pos.y += this.velocity_y * dt
        else:
            this.velocity_y = 0

    def get_rect(this):
        return pygame.Rect(this.player_pos.x - this.radius, 
                          this.player_pos.y - this.radius, 
                          this.radius * 2, this.radius * 2)

    def check_platform_collision(this, platforms):
        this.is_on_ground = False
        player_rect = this.get_rect()
        feet_rect = player_rect.copy()
        feet_rect.y += 1
        
        for platform in platforms:
            rect_to_check = feet_rect if this.velocity_y >= 0 else player_rect

            if rect_to_check.colliderect(platform.rect):
                prev_bottom = this.prev_y + this.radius
                current_bottom = this.player_pos.y + this.radius
                
                if this.velocity_y >= 0 and prev_bottom <= platform.rect.top + 5:
                    this.player_pos.y = platform.rect.top - this.radius
                    this.velocity_y = 0
                    this.is_on_ground = True
                    break
                elif this.velocity_y >= 0 and abs(current_bottom - platform.rect.top) < 3:
                    this.player_pos.y = platform.rect.top - this.radius
                    this.velocity_y = 0
                    this.is_on_ground = True
                    break
                elif this.velocity_y < 0 and prev_bottom > platform.rect.top:
                    this.player_pos.y = platform.rect.bottom + this.radius
                    this.velocity_y = 0