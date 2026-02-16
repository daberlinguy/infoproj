import pygame
from typing import Optional

from skeletons.platform import Platform


class Spieler:
    def __init__(self, player_pos, dt, radius=24):
        self.player_pos = player_pos
        self.dt = dt
        self.radius = radius
        self.sprite_width = int(182 * 0.2)
        self.sprite_height = int(243 * 0.2)
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 980
        self.jump_strength = -450
        self.acceleration = 1200
        self.max_speed = 300
        self.max_fall_speed = 1000
        self.friction = 0.8
        self.speed_multiplier = 1.0
        self.base_speed = 300
        self.current_platform = None
        self.is_on_ground = False
        self.is_against_wall = False
        self._move_input = False
        self.prev_y = player_pos.y
        self.prev_x = player_pos.x
        
        self._player_rect = pygame.Rect(0, 0, self.sprite_width, self.sprite_height)
        self._feet_rect = pygame.Rect(0, 0, self.sprite_width, self.sprite_height)
        self._sweep_rect = pygame.Rect(0, 0, 0, 0)

    def set_sprite_size(self, width, height):
        self.sprite_width = int(width)
        self.sprite_height = int(height)
        self._player_rect = pygame.Rect(0, 0, self.sprite_width, self.sprite_height)
        self._feet_rect = pygame.Rect(0, 0, self.sprite_width, self.sprite_height)

    def _update_rects(self):
        half_w = self.sprite_width / 2
        half_h = self.sprite_height / 2
        self._player_rect.centerx = int(self.player_pos.x)
        self._player_rect.centery = int(self.player_pos.y)
        self._feet_rect.centerx = int(self.player_pos.x)
        self._feet_rect.centery = int(self.player_pos.y) + 1

    def get_rect(self):
        self._update_rects()
        return self._player_rect

    def move_left(self, dt: float = None):
        if dt is None:
            dt = self.dt
        self._move_input = True
        if self.is_on_ground and self.friction < 0.1:
            self.velocity_x -= self.acceleration * dt
            self.velocity_x = max(self.velocity_x, -self.max_speed * self.speed_multiplier)
        else:
            speed = self.base_speed * self.speed_multiplier
            if self.is_on_ground:
                self.player_pos.x -= speed * dt
            self.velocity_x = -speed

    def move_right(self, dt: float = None):
        if dt is None:
            dt = self.dt
        self._move_input = True
        if self.is_on_ground and self.friction < 0.1:
            self.velocity_x += self.acceleration * dt
            self.velocity_x = min(self.velocity_x, self.max_speed * self.speed_multiplier)
        else:
            speed = self.base_speed * self.speed_multiplier
            if self.is_on_ground:
                self.player_pos.x += speed * dt
            self.velocity_x = speed

    def apply_velocity(self, dt: float):
        self.player_pos.y += self.velocity_y * dt
        if self.friction < 0.1 or not self.is_on_ground:
            self.player_pos.x += self.velocity_x * dt

    def jump(self):
        if not self.is_on_ground:
            return

        jump_velocity = self.jump_strength

        if self.current_platform and self.current_platform.is_boost_up():
            jump_velocity = self.current_platform.get_boost_power()

        self.velocity_y = jump_velocity
        self.is_on_ground = False
        self.current_platform = None

    def on_ground(self):
        return self.is_on_ground

    def apply_physics(self, dt):
        if not self.is_on_ground:
            self.velocity_y += self.gravity * dt
            self.velocity_y = min(self.velocity_y, self.max_fall_speed)
            if not self._move_input:
                if self.friction >= 0.1:
                    self.velocity_x = 0
                else:
                    deceleration = self.friction * 1000 * dt
                    if abs(self.velocity_x) <= deceleration:
                        self.velocity_x = 0
                    else:
                        self.velocity_x -= deceleration * (1 if self.velocity_x > 0 else -1)
        else:
            self.velocity_y = 0
            if not self._move_input:
                if self.friction < 0.1 and abs(self.velocity_x) > 0:
                    deceleration = self.friction * 1000 * dt
                    if abs(self.velocity_x) <= deceleration:
                        self.velocity_x = 0
                    else:
                        self.velocity_x -= deceleration * (1 if self.velocity_x > 0 else -1)
                elif self.friction >= 0.1:
                    self.velocity_x = 0
        self._move_input = False

    def get_substeps(self, dt: float) -> int:
        max_speed = max(abs(self.velocity_x), abs(self.velocity_y))
        if max_speed <= 0:
            return 1
        min_dimension = min(self.sprite_width, self.sprite_height)
        steps = max(1, int(max_speed * dt / (min_dimension * 0.5)) + 1)
        return min(steps, 8)

    def check_platform_collision(self, platforms: list[Platform], adjacent_platforms: Optional[list[Platform]] = None):
        self.is_on_ground = False
        self.is_against_wall = False
        self._update_rects()
        player_rect = self._player_rect
        feet_rect = self._feet_rect

        all_platforms = list(platforms)
        if adjacent_platforms:
            all_platforms.extend(adjacent_platforms)

        prev_top = self.prev_y - self.sprite_height / 2
        prev_bottom = self.prev_y + self.sprite_height / 2
        prev_left = self.prev_x - self.sprite_width / 2
        prev_right = self.prev_x + self.sprite_width / 2

        curr_top = self.player_pos.y - self.sprite_height / 2
        curr_bottom = self.player_pos.y + self.sprite_height / 2
        curr_left = self.player_pos.x - self.sprite_width / 2
        curr_right = self.player_pos.x + self.sprite_width / 2

        sweep_left = min(prev_left, curr_left) - 4
        sweep_top = min(prev_top, curr_top) - 4
        sweep_right = max(prev_right, curr_right) + 4
        sweep_bottom = max(prev_bottom, curr_bottom) + 4
        self._sweep_rect.x = int(sweep_left)
        self._sweep_rect.y = int(sweep_top)
        self._sweep_rect.width = int(sweep_right - sweep_left)
        self._sweep_rect.height = int(sweep_bottom - sweep_top)
        query_rect = self._sweep_rect.inflate(self.sprite_width * 2, self.sprite_height * 2)
        candidate_platforms = [
            platform for platform in all_platforms if query_rect.colliderect(platform.rect)
        ]

        self.current_platform = None
        for platform in candidate_platforms:
            if platform.is_deadly():
                continue
            if platform.is_noclip():
                continue

            if feet_rect.colliderect(platform.rect) and self.velocity_y >= 0:
                if prev_bottom <= platform.rect.top + 2:
                    if (
                        curr_right > platform.rect.left
                        and curr_left < platform.rect.right
                    ):
                        self.player_pos.y = platform.rect.top - self.sprite_height / 2
                        self.velocity_y = 0
                        self.is_on_ground = True
                        self.current_platform = platform
                        self.friction = platform.get_friction()
                        if hasattr(platform, "get_speed_multiplier"):
                            self.speed_multiplier = platform.get_speed_multiplier()
                        else:
                            self.speed_multiplier = 1.0

                        if hasattr(platform, "velocity_x") and platform.velocity_x != 0:
                            self.player_pos.x += platform.velocity_x * self.dt
                        break

        self._update_rects()
        player_rect = self._player_rect
        for platform in candidate_platforms:
            if platform.is_noclip() or platform.is_deadly():
                continue

            if self.is_on_ground and platform == self.current_platform:
                continue

            if self.is_on_ground and self.current_platform:
                same_top = platform.rect.top == self.current_platform.rect.top
                if same_top and curr_bottom <= platform.rect.top + 2:
                    continue

            if player_rect.colliderect(platform.rect):
                if (
                    self.velocity_y < 0
                    and prev_top >= platform.rect.bottom
                    and curr_top < platform.rect.bottom
                ):
                    self.player_pos.y = platform.rect.bottom + self.sprite_height / 2
                    self.velocity_y = 0
                    continue

                if (
                    prev_right <= platform.rect.left + 1
                    and curr_right > platform.rect.left
                ):
                    self.player_pos.x = platform.rect.left - self.sprite_width / 2
                    self.velocity_x = 0
                    self.is_against_wall = True
                    continue

                if (
                    prev_left >= platform.rect.right - 1
                    and curr_left < platform.rect.right
                ):
                    self.player_pos.x = platform.rect.right + self.sprite_width / 2
                    self.velocity_x = 0
                    self.is_against_wall = True
                    continue

                platform_type = getattr(platform, "platform_type", None)
                if platform_type == Platform.SLIPPERY:
                    self.prev_x = self.player_pos.x
                    self.player_pos.x += (self.player_pos.x - self.prev_x) * 0.2

    def check_special_platform_interactions(self, platforms, current_checkpoint):
        """
        Check for special platform interactions (death, checkpoint)
        Returns: tuple (new_checkpoint, should_respawn)
        """
        player_rect = self.get_rect()
        new_checkpoint = current_checkpoint
        should_respawn = False

        for platform in platforms:
            if platform.is_noclip():
                continue
            if player_rect.colliderect(platform.rect):
                # Death platform - trigger respawn
                if platform.is_deadly():
                    self.player_pos = current_checkpoint.copy()
                    self.velocity_x = 0
                    self.velocity_y = 0
                    self.speed_multiplier = 1.0
                    return (current_checkpoint, True)

                # Checkpoint platform - save position
                elif platform.is_checkpoint():
                    if not platform.checkpoint_activated:
                        platform.activate_checkpoint()
                    new_checkpoint = pygame.Vector2(
                        platform.rect.centerx, platform.rect.top - 30
                    )

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
            self.speed_multiplier = 1.0
            return True
        return False
