import pygame

from skeletons.platform import Platform


class Spieler:
    def __init__(self, player_pos, dt, radius=24):
        self.player_pos = player_pos
        self.dt = dt
        self.radius = radius  # Keep for backward compatibility
        # Sprite-based collision box (matching the sprite dimensions)
        self.sprite_width = int(182 * 0.2)  # 36 pixels
        self.sprite_height = int(243 * 0.2)  # 48 pixels
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 980
        self.jump_strength = -450
        self.acceleration = 1200  # Horizontal acceleration
        self.max_speed = 300  # Maximum horizontal speed
        self.max_fall_speed = 1000  # Maximum falling speed to prevent tunneling
        self.friction = 0.8  # Default friction coefficient
        self.current_platform = None  # Track which platform we're on
        self.is_on_ground = False
        self.prev_y = player_pos.y
        self.prev_x = player_pos.x

    def set_sprite_size(self, width, height):
        self.sprite_width = int(width)
        self.sprite_height = int(height)

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
            # Clamp falling speed to prevent tunneling
            self.velocity_y = min(self.velocity_y, self.max_fall_speed)
            self.velocity_x = (
                0  # Stop horizontal movement in air if not on slippery surface
            )
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
        """Get collision rectangle based on sprite dimensions"""
        return pygame.Rect(
            self.player_pos.x - self.sprite_width / 2,
            self.player_pos.y - self.sprite_height / 2,
            self.sprite_width,
            self.sprite_height,
        )

    def check_platform_collision(self, platforms: list[Platform]):
        self.is_on_ground = False
        self.is_against_wall = False  # Track if player is touching a wall
        player_rect = self.get_rect()
        feet_rect = player_rect.copy()
        feet_rect.y += 1

        # previous / current edges for more reliable axis resolution
        prev_top = self.prev_y - self.sprite_height / 2
        prev_bottom = self.prev_y + self.sprite_height / 2
        prev_left = self.prev_x - self.sprite_width / 2
        prev_right = self.prev_x + self.sprite_width / 2

        curr_top = self.player_pos.y - self.sprite_height / 2
        curr_bottom = self.player_pos.y + self.sprite_height / 2
        curr_left = self.player_pos.x - self.sprite_width / 2
        curr_right = self.player_pos.x + self.sprite_width / 2

        # First pass: check for ground collision (highest priority)
        self.current_platform = None
        for platform in platforms:
            # Skip death platforms - don't allow standing on them
            if platform.is_deadly():
                continue
            if platform.is_noclip():
                continue

            # More robust ground collision: check if we're moving downward and crossing the platform top
            # Allow small tolerance for edge cases
            if feet_rect.colliderect(platform.rect) and self.velocity_y >= 0:
                # Check if we crossed from above the platform
                if prev_bottom <= platform.rect.top + 2:  # Small tolerance
                    # Ensure we're actually overlapping horizontally
                    if (
                        curr_right > platform.rect.left
                        and curr_left < platform.rect.right
                    ):
                        self.player_pos.y = platform.rect.top - self.sprite_height / 2
                        self.velocity_y = 0
                        self.is_on_ground = True
                        self.current_platform = platform
                        self.friction = platform.get_friction()
                        # Inherit platform velocity if it's moving
                        if hasattr(platform, "velocity_x") and platform.velocity_x != 0:
                            self.player_pos.x += platform.velocity_x * self.dt
                        break

        # Second pass: check for ceiling and wall collisions (only if not grounded or different platforms)
        player_rect = self.get_rect()  # Update rect after potential ground correction
        for platform in platforms:
            # Skip death platforms - they don't block movement
            if platform.is_noclip() or platform.is_deadly():
                continue

            # Skip all collision checks for the platform we're currently standing on
            # This prevents wall collision logic from triggering when at platform edges
            if self.is_on_ground and platform == self.current_platform:
                continue

            # Allow seamless movement across platform seams on the same top level
            if self.is_on_ground and self.current_platform:
                same_top = platform.rect.top == self.current_platform.rect.top
                if same_top and curr_bottom <= platform.rect.top + 2:
                    continue

            if player_rect.colliderect(platform.rect):
                # Head (bottom of platform) collision when moving up
                if (
                    self.velocity_y < 0
                    and prev_top >= platform.rect.bottom
                    and curr_top < platform.rect.bottom
                ):
                    self.player_pos.y = platform.rect.bottom + self.sprite_height / 2
                    self.velocity_y = 0
                    continue

                # Side collisions: detect approach side using previous X edges
                # Only apply if there's clear horizontal movement into the platform
                if (
                    prev_right <= platform.rect.left + 1
                    and curr_right > platform.rect.left
                ):  # Tighter tolerance
                    # collided from left -> push player to left side of platform
                    self.player_pos.x = platform.rect.left - self.sprite_width / 2
                    self.velocity_x = 0  # Stop horizontal velocity on wall hit
                    self.is_against_wall = True
                    continue

                if (
                    prev_left >= platform.rect.right - 1
                    and curr_left < platform.rect.right
                ):  # Tighter tolerance
                    # collided from right -> push player to right side of platform
                    self.player_pos.x = platform.rect.right + self.sprite_width / 2
                    self.velocity_x = 0  # Stop horizontal velocity on wall hit
                    self.is_against_wall = True
                    continue

                platform_type = getattr(platform, "platform_type", None)
                if platform_type == Platform.SLIPPERY:
                    self.prev_x = self.player_pos.x
                    self.player_pos.x += (self.player_pos.x - self.prev_x) * 0.2
                    pass  # This would be integrated with player movement logic

    def check_special_platform_interactions(self, platforms, current_checkpoint):
        """
        Check for special platform interactions (death, checkpoint)
        Returns: tuple (new_checkpoint, should_respawn)
        """
        player_rect = self.get_rect()
        new_checkpoint = current_checkpoint
        should_respawn = False

        for platform in platforms:
            if player_rect.colliderect(platform.rect):
                # Death platform - trigger respawn
                if platform.is_deadly():
                    self.player_pos = current_checkpoint.copy()
                    self.velocity_x = 0
                    self.velocity_y = 0
                    return (current_checkpoint, True)

                # Checkpoint platform - save position
                elif platform.is_checkpoint():
                    if not platform.checkpoint_activated:
                        platform.activate_checkpoint()
                    new_checkpoint = pygame.Vector2(
                        platform.rect.centerx, platform.rect.top - 30
                    )

                # Boost platforms - apply velocity changes
                if platform.is_boost_up():
                    # Strong upward boost (like a wind current or jump pad)
                    self.velocity_y = min(self.velocity_y, -450)

                if platform.is_boost_down():
                    # Strong downward boost (like a downdraft)
                    self.velocity_y = max(self.velocity_y, 450)

        return (new_checkpoint, should_respawn)

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
