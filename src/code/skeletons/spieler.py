import pygame
import sys

path=sys.argv[0].replace("main.py","")

class Spieler:
    def __init__(this, player_pos, dt, radius=24):
        this.player_pos = player_pos
        this.dt = dt
        this.radius = radius
        this.velocity_y = 0
        this.gravity = 980
        this.jump_strength = -500
        this.is_on_ground = False
        this.prev_y = player_pos.y
        this.prev_x = player_pos.x
        
    def move_left(this):
        this.prev_x = this.player_pos.x  # Store position before moving
        this.player_pos.x -= 300 * this.dt

    def move_right(this):
        this.prev_x = this.player_pos.x  # Store position before moving
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

        # previous / current edges for more reliable axis resolution
        prev_top = this.prev_y - this.radius
        prev_bottom = this.prev_y + this.radius
        prev_left = this.prev_x - this.radius
        prev_right = this.prev_x + this.radius

        curr_top = this.player_pos.y - this.radius
        curr_bottom = this.player_pos.y + this.radius
        curr_left = this.player_pos.x - this.radius
        curr_right = this.player_pos.x + this.radius

        for platform in platforms:
            # Ground landing: use a small feet rect to allow stable landing from above
            if feet_rect.colliderect(platform.rect) and this.velocity_y >= 0 and prev_bottom <= platform.rect.top and curr_bottom >= platform.rect.top:
                this.player_pos.y = platform.rect.top - this.radius
                this.velocity_y = 0
                this.is_on_ground = True
                break

            # For side/head collisions check the full player rect
            if player_rect.colliderect(platform.rect):
                # Head (bottom of platform) collision when moving up
                if this.velocity_y < 0 and prev_top >= platform.rect.bottom and curr_top < platform.rect.bottom:
                    this.player_pos.y = platform.rect.bottom + this.radius
                    this.velocity_y = 0
                    break

                # Side collisions: detect approach side using previous X edges
                if prev_right <= platform.rect.left and curr_right > platform.rect.left:
                    # collided from left -> push player to left side of platform
                    this.player_pos.x = platform.rect.left - this.radius
                    break

                if prev_left >= platform.rect.right and curr_left < platform.rect.right:
                    # collided from right -> push player to right side of platform
                    this.player_pos.x = platform.rect.right + this.radius
                    break