import pygame
import sys

from skeletons.platform import Platform

class Spieler:
    def __init__(self, player_pos, dt, radius=24):
        self.player_pos = player_pos
        self.dt = dt
        self.radius = radius
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 980
        self.jump_strength = -500
        self.acceleration = 1200  # Horizontal acceleration
        self.max_speed = 300  # Maximum horizontal speed
        self.friction = 0.8  # Default friction coefficient
        self.current_platform = None  # Track which platform we're on
        self.is_on_ground = False
        self.prev_y = player_pos.y
        self.prev_x = player_pos.x
        
    def move_left(self):
        # On slippery platforms, use acceleration. Otherwise, direct movement
        if self.is_on_ground and self.friction < 0.1:  # Slippery
            self.velocity_x -= self.acceleration * self.dt
            self.velocity_x = max(self.velocity_x, -self.max_speed)
        else:
            self.player_pos.x -= 300 * self.dt
            self.velocity_x = -300

    def move_right(self):
        # On slippery platforms, use acceleration. Otherwise, direct movement
        if self.is_on_ground and self.friction < 0.1:  # Slippery
            self.velocity_x += self.acceleration * self.dt
            self.velocity_x = min(self.velocity_x, self.max_speed)
        else:
            self.player_pos.x += 300 * self.dt
            self.velocity_x = 300

    def jump(self):
        if self.is_on_ground:
            self.velocity_y = self.jump_strength
            self.is_on_ground = False
    
    def on_ground(self):
        return self.is_on_ground


    def apply_physics(self, dt):
        # prev_x and prev_y are now set in GameScreen before movement
        
        # Apply gravity
        if not self.is_on_ground:
            self.velocity_y += self.gravity * dt
            self.velocity_x = 0  # Stop horizontal movement in air if not on slippery surface
        else:
            self.velocity_y = 0
            # Only apply friction on slippery platforms
            if self.friction < 0.1 and abs(self.velocity_x) > 0:
                # Calculate deceleration based on friction for slippery surfaces
                deceleration = self.friction * 1000 * dt
                if abs(self.velocity_x) <= deceleration:
                    self.velocity_x = 0
                else:
                    self.velocity_x -= deceleration * (1 if self.velocity_x > 0 else -1)
            elif self.friction >= 0.1:
                # On normal platforms, stop immediately when not pressing keys
                self.velocity_x = 0
        
        # Apply velocities to position (only for slippery or air movement)
        if self.friction < 0.1 or not self.is_on_ground:
            self.player_pos.x += self.velocity_x * dt
        self.player_pos.y += self.velocity_y * dt

    def get_rect(self):
        return pygame.Rect(self.player_pos.x - self.radius, 
                          self.player_pos.y - self.radius, 
                          self.radius * 2, self.radius * 2)

    def check_platform_collision(self, platforms: list[Platform]):
        self.is_on_ground = False
        player_rect = self.get_rect()
        feet_rect = player_rect.copy()
        feet_rect.y += 1

        # previous / current edges for more reliable axis resolution
        prev_top = self.prev_y - self.radius
        prev_bottom = self.prev_y + self.radius
        prev_left = self.prev_x - self.radius
        prev_right = self.prev_x + self.radius

        curr_top = self.player_pos.y - self.radius
        curr_bottom = self.player_pos.y + self.radius
        curr_left = self.player_pos.x - self.radius
        curr_right = self.player_pos.x + self.radius

        # First pass: check for ground collision (highest priority)
        self.current_platform = None
        for platform in platforms:
            if feet_rect.colliderect(platform.rect) and self.velocity_y >= 0 and prev_bottom <= platform.rect.top and curr_bottom >= platform.rect.top:
                self.player_pos.y = platform.rect.top - self.radius
                self.velocity_y = 0
                self.is_on_ground = True
                self.current_platform = platform
                self.friction = platform.get_friction()
                
                # Inherit platform velocity if it's moving
                if hasattr(platform, 'velocity_x') and platform.velocity_x != 0:
                    self.player_pos.x += platform.velocity_x * self.dt
                break

        # Second pass: check for ceiling and wall collisions (only if not grounded or different platforms)
        player_rect = self.get_rect()  # Update rect after potential ground correction
        for platform in platforms:
            if player_rect.colliderect(platform.rect):
                # Skip if this is the platform we're standing on
                if self.is_on_ground and abs(self.player_pos.y + self.radius - platform.rect.top) < 2:
                    continue

                # Head (bottom of platform) collision when moving up
                if self.velocity_y < 0 and prev_top >= platform.rect.bottom and curr_top < platform.rect.bottom:
                    self.player_pos.y = platform.rect.bottom + self.radius
                    self.velocity_y = 0
                    continue

                # Side collisions: detect approach side using previous X edges
                # Only apply if there's clear horizontal movement into the platform
                if prev_right <= platform.rect.left and curr_right > platform.rect.left:
                    # collided from left -> push player to left side of platform
                    self.player_pos.x = platform.rect.left - self.radius
                    continue

                if prev_left >= platform.rect.right and curr_left < platform.rect.right:
                    # collided from right -> push player to right side of platform
                    self.player_pos.x = platform.rect.right + self.radius
                    continue

                platform_type = getattr(platform, 'platform_type', None)
                if platform_type == Platform.SLIPPERY:
                    self.prev_x = self.player_pos.x
                    self.player_pos.x += (self.player_pos.x - self.prev_x) * 0.2
                    pass  # This would be integrated with player movement logic
                elif platform_type == Platform.DEATH:
                    print("Player hit death platform")
                    pass  # Death handled in special interactions
    
    def check_special_platform_interactions(self, platforms, current_checkpoint):
        """
        Check for special platform interactions (death, checkpoint, finish)
        Returns: tuple (new_checkpoint, should_respawn)
        """
        # Use the same rect as get_rect() for consistency, plus a small buffer for touching
        player_rect = self.get_rect()
        player_rect.inflate_ip(0, 2)  # Slightly extend vertically to detect touching platforms
        
        for platform in platforms:
            if player_rect.colliderect(platform.rect):
                # Death platform - trigger respawn (check any collision)
                if platform.is_deadly():
                    self.player_pos.x = current_checkpoint.x
                    self.player_pos.y = current_checkpoint.y
                    self.velocity_x = 0
                    self.velocity_y = 0
                    self.is_on_ground = False
                    return (current_checkpoint.copy(), True)
                
                # Checkpoint platform - save position (only when standing on top)
                elif platform.is_checkpoint():
                    # Only activate if player is on top of the checkpoint
                    if self.is_on_ground and abs(self.player_pos.y + 24 - platform.rect.top) < 5:
                        if not platform.checkpoint_activated:
                            platform.activate_checkpoint()
                        new_checkpoint = pygame.Vector2(platform.rect.centerx, platform.rect.top - 30)
                        return (new_checkpoint, False)
                
                # Finish platform is handled in GameScreen for level completion
        
        return (current_checkpoint, False)
    
    def check_fell_off_screen(self, screen_height, current_checkpoint):
        """
        Check if player fell off screen and respawn if needed
        Returns: True if respawned
        """
        if self.player_pos.y > screen_height:
            self.player_pos = current_checkpoint.copy()
            self.velocity_x = 0
            self.velocity_y = 0
            return True
        return False