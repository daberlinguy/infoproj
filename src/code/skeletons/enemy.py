import pygame

from skeletons.character_classes.characters import CHARACTER_REGISTRY
from skeletons.spieler import Spieler


class Enemy:
    def __init__(
        self,
        position,
        page_index,
        move_speed=250,
        aggro_range=100000,
        attack_range=34,
        jump_cooldown=0.7,
    ):
        self.page_index = page_index
        self.move_speed = move_speed
        self.aggro_range = aggro_range
        self.attack_range = attack_range
        self.jump_cooldown = jump_cooldown
        self.jump_timer = 0.0

        self.body = Spieler(pygame.Vector2(position), dt=0.0)

        character_cls = CHARACTER_REGISTRY.get("emmanuel")
        if character_cls is None:
            character_cls = CHARACTER_REGISTRY[next(iter(CHARACTER_REGISTRY))]
        character_instance = character_cls()
        self.character = character_instance.build(self.body.player_pos)
        collider_width, collider_height = character_instance.get_collider_size(
            self.body.sprite_width,
            self.body.sprite_height,
        )
        self.body.set_sprite_size(collider_width, collider_height)

        self.target_pos = None
        self.path_points = []
        self.max_path_points = 30
        self.was_on_ground = False

    @property
    def position(self):
        return self.body.player_pos

    def distance_to(self, target_pos):
        return self.body.player_pos.distance_to(target_pos)

    def set_spawn_y_above_platform(self, platform_top):
        self.body.player_pos.y = platform_top - (self.body.sprite_height / 2)

    def _move_towards_target(self, target_pos, dt):
        delta_x = target_pos.x - self.body.player_pos.x
        if abs(delta_x) < 4:
            return
        direction = -1 if delta_x < 0 else 1
        self.body.player_pos.x += direction * self.move_speed * dt
        self.body.velocity_x = direction * self.move_speed
        self.character.facing = direction

    def _maybe_jump_towards_target(self, target_pos):
        if not self.body.is_on_ground or self.jump_timer > 0:
            return

        target_above = target_pos.y < self.body.player_pos.y - 40
        close_horizontally = abs(target_pos.x - self.body.player_pos.x) < 220
        if (self.body.is_against_wall and close_horizontally) or (
            target_above and close_horizontally
        ):
            self.body.jump()
            self.jump_timer = self.jump_cooldown

    def update_ai(self, target_pos, platforms, dt):
        self.jump_timer = max(0.0, self.jump_timer - dt)
        self.body.dt = dt

        self.body.prev_x = self.body.player_pos.x
        self.body.prev_y = self.body.player_pos.y

        self.target_pos = None
        if target_pos is not None:
            distance = self.distance_to(target_pos)
            if distance <= self.aggro_range:
                self.target_pos = pygame.Vector2(target_pos)
                self._move_towards_target(self.target_pos, dt)

        self.body.apply_physics(dt)
        self.body.check_platform_collision(platforms)

        if self.target_pos is not None:
            self._maybe_jump_towards_target(self.target_pos)

        is_moving = abs(self.body.velocity_x) > 0.1 or self.target_pos is not None
        is_landing = (not self.was_on_ground) and self.body.is_on_ground
        self.character.set_center(self.body.player_pos)
        self.character.update_state(
            self.body.is_on_ground,
            is_moving,
            is_flying=False,
            is_landing=is_landing,
        )
        self.character.update(dt)
        self.was_on_ground = self.body.is_on_ground

        self.path_points.append((self.body.player_pos.x, self.body.player_pos.y))
        if len(self.path_points) > self.max_path_points:
            self.path_points.pop(0)

    def draw(self, screen):
        self.character.draw(screen)

    def draw_debug(self, screen):
        if len(self.path_points) >= 2:
            pygame.draw.lines(
                screen,
                (255, 120, 30),
                False,
                [(int(x), int(y)) for x, y in self.path_points],
                2,
            )

        if self.target_pos is not None:
            start = (int(self.body.player_pos.x), int(self.body.player_pos.y))
            end = (int(self.target_pos.x), int(self.target_pos.y))
            pygame.draw.line(screen, (60, 220, 255), start, end, 2)
            pygame.draw.circle(screen, (60, 220, 255), end, 6, 1)

        pygame.draw.circle(
            screen,
            (255, 120, 120),
            (int(self.body.player_pos.x), int(self.body.player_pos.y)),
            int(self.attack_range),
            1,
        )
