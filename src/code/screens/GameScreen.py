import os
import pygame
import sys
import json
import random

from skeletons.screen import Screen
from skeletons.spieler import Spieler
from skeletons.platform import Platform, Grid
from skeletons.character import Character
from skeletons.character_classes.characters import CHARACTER_REGISTRY
from assets.assets import getFont, getMinecraftTexture, Texture, assets_path
from screens.SettingsScreen import SETTINGS
from data.storage import load_worlds, save_settings
from utils.level_data import LevelDataUtils
from utils.platform_types import PlatformTypes


class GameScreen(Screen):
    def __init__(self, screen, caption, level_path=None):
        # Clear all previous widgets
        self.clear_widgets()

        self.dt = 0.0
        self.clock = pygame.time.Clock()

        self.page_index = 1
        self.page_width_cells = 60
        self.page_height_cells = 34
        self.page_grid_size = 32
        self.page_positions = {1: (0, 0)}
        self.page_key_by_position = {(0, 0): 1}

        self.player_pos = pygame.Vector2(
            (self.page_width_cells * self.page_grid_size) / 2, 100
        )
        self.player = Spieler(self.player_pos, self.dt)
        self.was_on_ground = False

        self.character = self._create_character()
        self.level_path = level_path
        self.level_completed = False
        self.checkpoints_required = 0
        self.checkpoints_activated = 0
        self.background_color = (128, 0, 128)
        self.background_image = None
        self.background_image_cached = None
        self.level_data = None

        # Spawn point and checkpoint tracking
        self.spawn_point = pygame.Vector2(1 * 32 + 16, 14 * 32)  # Above spawn platform
        self.current_checkpoint = self.spawn_point.copy()
        self.current_checkpoint_page = self.page_index

        # Track activated checkpoints across all pages (page_index, x1, y1, x2, y2)
        self.activated_checkpoints = set()

        # Create debug grid
        self.grid = Grid(cell_size=32, color=(80, 80, 80), line_width=1)
        self.grid.visible = False  # Grid is part of debug mode

        # Grid cell size for alignment
        grid_size = 32

        self.isImageLoaded = False
        self.imageTick = 20

        self.timer = 0.0
        self.run_timer = 0.0
        self.latest_run_time = 0.0
        self.attempts = 1
        self.deaths = 0

        # Platforms are loaded from level JSON
        self.platforms = []

        if self.level_path:
            self._load_level(self.level_path)

        # Setup virtual resolution handling
        self.virtual_width = self.page_width_cells * self.page_grid_size
        self.virtual_height = self.page_height_cells * self.page_grid_size
        self.virtual_surface = pygame.Surface((self.virtual_width, self.virtual_height))

        # Save real screen for final blit
        self.real_screen = screen
        self._real_screen_size = self.real_screen.get_size()
        self._scaled_surface = None
        if self._real_screen_size != (self.virtual_width, self.virtual_height):
            self._scaled_surface = pygame.Surface(self._real_screen_size)

        # Pass virtual surface to superclass so drawing operations use it
        super().__init__(self.virtual_surface, caption)

    def _create_character(self):
        character_id = SETTINGS.get("character", "character1")
        character_cls = CHARACTER_REGISTRY.get(
            character_id, CHARACTER_REGISTRY["character1"]
        )
        character_instance = character_cls()
        character = character_instance.build(self.player_pos)
        collider_width, collider_height = character_instance.get_collider_size(
            self.player.sprite_width,
            self.player.sprite_height,
        )
        self.player.set_sprite_size(collider_width, collider_height)
        return character

    def onBtnOpenGameScreen(self):
        print("Game Screen would open here.")  # Add your game screen transition here

    def _load_level(self, level_path):
        if not level_path or not os.path.exists(level_path):
            return

        try:
            with open(level_path, "r", encoding="utf-8") as f:
                level_data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Error loading level file: {e}")
            return

        self.level_data = level_data
        self.timer = 0.0
        self.run_timer = 0.0
        self.latest_run_time = 0.0
        self.attempts = 1
        self.deaths = 0

        self.page_width_cells = int(
            level_data.get("page_width_cells", self.page_width_cells)
        )
        self.page_height_cells = int(
            level_data.get("page_height_cells", self.page_height_cells)
        )

        self._sync_page_layout(level_data)
        if self.page_index not in self.page_positions and self.page_positions:
            self.page_index = min(self.page_positions.keys())

        player_spawn = level_data.get("player_spawn")
        if player_spawn:
            spawn_grid = player_spawn.get("grid", True)
            grid_size = player_spawn.get("grid_size", 32)
            self.page_grid_size = grid_size
            spawn_x = player_spawn.get("x", 200)
            spawn_y = player_spawn.get("y", 450)
            if spawn_grid:
                spawn_x *= grid_size
                spawn_y *= grid_size
            self.player_pos = pygame.Vector2(spawn_x, spawn_y)
            self.player.player_pos = self.player_pos
            self.spawn_point = self.player_pos.copy()
            self.current_checkpoint = self.spawn_point.copy()
            self.current_checkpoint_page = self.page_index

        background_color = level_data.get("background_color")
        if background_color:
            if isinstance(background_color, dict) and background_color.get("image"):
                image_path = background_color.get("image")
                if image_path:
                    self.background_image = image_path
            else:
                self.background_color = (
                    background_color.get("r", 135),
                    background_color.get("g", 206),
                    background_color.get("b", 235),
                )

        self.platforms = self._build_platforms_from_level(level_data, self.page_index)

        # Count total checkpoints across ALL pages
        total_checkpoints = 0
        pages = level_data.get("pages")
        if pages:
            for page_key in pages.keys():
                page_platforms = self._build_platforms_from_level(level_data, page_key)
                total_checkpoints += sum(1 for p in page_platforms if p.is_checkpoint())
        else:
            total_checkpoints = sum(
                1 for platform in self.platforms if platform.is_checkpoint()
            )
        self.checkpoints_required = total_checkpoints
        print(f"Total checkpoints in level: {self.checkpoints_required}")

    def _available_pages(self):
        if self.page_positions:
            return list(self.page_positions.keys()) or [self.page_index]
        if self.level_data and self.level_data.get("pages"):
            pages = []
            for key in self.level_data["pages"].keys():
                try:
                    pages.append(int(key))
                except (TypeError, ValueError):
                    continue
            return pages or [self.page_index]
        return [self.page_index]

    def _sync_page_layout(self, level_data):
        pages = level_data.get("pages", {}) if level_data else {}
        positions = level_data.get("page_positions", {}) if level_data else {}
        page_positions = {}

        if isinstance(positions, dict) and positions:
            for key, pos in positions.items():
                if not isinstance(pos, dict):
                    continue
                try:
                    key_int = int(key)
                except (TypeError, ValueError):
                    continue
                try:
                    x = int(pos.get("x", 0))
                    y = int(pos.get("y", 0))
                except (TypeError, ValueError):
                    continue
                page_positions[key_int] = (x, y)

        if not page_positions:
            page_numbers = []
            for page_key in pages.keys():
                try:
                    page_numbers.append(int(page_key))
                except (TypeError, ValueError):
                    continue
            page_numbers = sorted(page_numbers) or [1]
            for index, page_key in enumerate(page_numbers):
                page_positions[page_key] = (index, 0)

        if page_positions:
            max_x = max(pos[0] for pos in page_positions.values())
        else:
            max_x = 0

        for page_key in pages.keys():
            try:
                key_int = int(page_key)
            except (TypeError, ValueError):
                continue
            if key_int not in page_positions:
                max_x += 1
                page_positions[key_int] = (max_x, 0)

        self.page_positions = page_positions or {1: (0, 0)}
        self.page_key_by_position = {
            (pos[0], pos[1]): page_key for page_key, pos in self.page_positions.items()
        }

    def _neighbor_page(self, dx, dy):
        if not self.page_positions:
            return None
        current_pos = self.page_positions.get(self.page_index, (0, 0))
        target_pos = (current_pos[0] + dx, current_pos[1] + dy)
        return self.page_key_by_position.get(target_pos)

    def _is_control_pressed(self, keys, control_name):
        for key_name in SETTINGS.get("controls", {}).get(control_name, []):
            try:
                if keys[pygame.key.key_code(key_name)]:
                    return True
            except ValueError:
                continue
        return False

    def _build_platforms_from_level(self, level_data, page_index=1):
        """Build platforms from level data using utility functions.

        Args:
            level_data: The full level data dictionary.
            page_index: The page index to load (default 1).

        Returns:
            List of Platform objects sorted by layer.
        """
        # Get page data using utility
        page_data = LevelDataUtils.get_page_data(level_data, page_index)
        platforms_data = (
            page_data.get("platforms", [])
            if page_data
            else level_data.get("platforms", [])
        )
        platforms_data = LevelDataUtils.merge_platform_cells(platforms_data)

        platforms = []
        for entry in platforms_data:
            grid_size = entry.get("grid_size", 32)

            # Get coordinates using utility
            coords = LevelDataUtils.get_platform_coordinates(entry, grid_size)
            if not coords:
                continue
            x1, y1, x2, y2 = coords

            # Normalize platform types using utility
            platform_types_list = LevelDataUtils.normalize_platform_types(entry)

            # Convert type names to Platform constants
            platform_types = []
            for type_name in platform_types_list:
                platform_types.append(getattr(Platform, type_name, Platform.NORMAL))

            # Parse texture and color
            texture_name = entry.get("texture")
            texture = getattr(Texture, texture_name, None) if texture_name else None
            color = LevelDataUtils.parse_color(entry.get("color"))

            # Get layer (defaults to 0 if not specified)
            layer = entry.get("layer", 0)

            platforms.append(
                Platform(
                    x1,
                    y1,
                    x2,
                    y2,
                    grid_size,
                    platform_types=platform_types,
                    color=color,
                    texture=texture,
                    layer=layer,
                )
            )

        # Sort platforms by layer (background to foreground)
        # This ensures proper rendering order
        platforms.sort(key=lambda p: p.layer)

        return platforms

    def _switch_page(self, new_page):
        if not self.level_data:
            return
        pages = self.level_data.get("pages")
        if not pages:
            return
        if str(new_page) not in pages and new_page not in pages:
            return

        # Save current checkpoint states before switching
        for platform in self.platforms:
            if platform.is_checkpoint() and platform.checkpoint_activated:
                checkpoint_key = (
                    self.page_index,
                    platform.x1,
                    platform.y1,
                    platform.x2,
                    platform.y2,
                )
                self.activated_checkpoints.add(checkpoint_key)

        self.page_index = new_page
        self.platforms = self._build_platforms_from_level(
            self.level_data, self.page_index
        )

        # Restore checkpoint states for this page
        for platform in self.platforms:
            if platform.is_checkpoint():
                checkpoint_key = (
                    self.page_index,
                    platform.x1,
                    platform.y1,
                    platform.x2,
                    platform.y2,
                )
                if checkpoint_key in self.activated_checkpoints:
                    platform.activate_checkpoint()

    def _mark_level_complete(self):
        if not self.level_path:
            return
        worlds = load_worlds()
        world_id = None
        level_id = None
        for world_name, world in worlds.items():
            for level in world["levels"]:
                if level["path"] == self.level_path:
                    world_id = world_name
                    level_id = level["id"]
                    break
            if world_id:
                break
        if not world_id or not level_id:
            return
        progress = SETTINGS.setdefault("progress", {}).setdefault("worlds", {})
        world_progress = progress.setdefault(
            world_id, {"levels": {}, "complete": False}
        )
        world_progress.setdefault("levels", {})[level_id] = True
        total_levels = len(worlds[world_id]["levels"])
        completed_levels = sum(
            1
            for level in worlds[world_id]["levels"]
            if world_progress["levels"].get(level["id"])
        )
        world_progress["complete"] = (
            total_levels > 0 and completed_levels == total_levels
        )
        SETTINGS["selected_world"] = world_id
        SETTINGS["selected_level"] = level_id
        save_settings(SETTINGS)

    def run(self):
        self.player_pos = self.player.player_pos
        pygame.display.set_caption(
            f"X: {int(self.player_pos.x)} Y: {int(self.player_pos.y)} On Ground: {self.player.is_on_ground}"
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return  # Exit immediately without drawing
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:  # Toggle debug mode with 'F3' key
                    SETTINGS["debug_mode"] = not SETTINGS.get("debug_mode", False)
                if event.key == pygame.K_r:  # Reset to spawn point with 'R' key
                    self.player.player_pos = self.spawn_point.copy()
                    self.player.velocity_x = 0
                    self.player.velocity_y = 0

        # Handle input
        keys = pygame.key.get_pressed()

        # Update player dt
        self.player.dt = self.dt

        # Timer
        self.timer += self.dt
        self.run_timer += self.dt

        # Store previous position before any movement
        self.player.prev_x = self.player.player_pos.x
        self.player.prev_y = self.player.player_pos.y

        if self._is_control_pressed(keys, "move_left"):
            self.player.move_left()
        if self._is_control_pressed(keys, "move_right"):
            self.player.move_right()
        if keys[pygame.K_ESCAPE]:
            self.running = False
            from screens.TitleScreen import TitleScreen

            TitleScreen(
                self.real_screen,
                "Title Screen",
                block_escape_until_release=True,
            )
            return  # Exit immediately to prevent further updates

        if self._is_control_pressed(keys, "jump"):
            self.player.jump()

        # Update moving platforms
        for platform in self.platforms:
            platform.update(self.dt)

        # Apply physics - apply gravity first, then check collisions to resolve
        self.player.apply_physics(self.dt)
        self.player.check_platform_collision(self.platforms)

        # Check page boundaries FIRST before death checks to prevent false deaths when crossing pages
        page_width_px = self.page_width_cells * self.page_grid_size
        page_height_px = self.page_height_cells * self.page_grid_size
        player_pos = self.player.player_pos
        half_width = self.player.sprite_width / 2
        half_height = self.player.sprite_height / 2
        
        if player_pos.x < 0:
            prev_page = self._neighbor_page(-1, 0)
            if self.level_data and self.level_data.get("pages") and prev_page:
                player_pos.x = page_width_px - half_width
                self._switch_page(prev_page)
                # Update prev position to new position to prevent falling through platforms
                self.player.prev_y = player_pos.y
                self.player.prev_x = player_pos.x
                # Run collision detection to prevent noclip into blocks
                self.player.check_platform_collision(self.platforms)
            else:
                player_pos.x = half_width
        elif player_pos.x > page_width_px:
            next_page = self._neighbor_page(1, 0)
            if self.level_data and self.level_data.get("pages") and next_page:
                player_pos.x = half_width
                self._switch_page(next_page)
                # Update prev position to new position to prevent falling through platforms
                self.player.prev_y = player_pos.y
                self.player.prev_x = player_pos.x
                # Run collision detection to prevent noclip into blocks
                self.player.check_platform_collision(self.platforms)
            else:
                player_pos.x = page_width_px - half_width

        if player_pos.y < 0:
            up_page = self._neighbor_page(0, -1)
            if self.level_data and self.level_data.get("pages") and up_page:
                player_pos.y = page_height_px - half_height
                self._switch_page(up_page)
                # Update prev position to new position to prevent falling through platforms
                self.player.prev_y = player_pos.y
                self.player.prev_x = player_pos.x
                # Run collision detection to prevent noclip into blocks
                self.player.check_platform_collision(self.platforms)
            else:
                player_pos.y = half_height
        elif player_pos.y > page_height_px:
            down_page = self._neighbor_page(0, 1)
            if self.level_data and self.level_data.get("pages") and down_page:
                player_pos.y = half_height
                self._switch_page(down_page)
                # Update prev position to new position to prevent falling through platforms
                self.player.prev_y = player_pos.y
                self.player.prev_x = player_pos.x
                # Run collision detection to prevent noclip into blocks
                self.player.check_platform_collision(self.platforms)
            else:
                player_pos.y = page_height_px - half_height

        # Check if player fell off the screen
        respawned = self.player.check_fell_off_screen(
            self.screen.get_height(), self.current_checkpoint
        )

        # Check for special platform interactions (death, checkpoint)
        prev_checkpoint_count = self.checkpoints_activated
        self.current_checkpoint, should_respawn = (
            self.player.check_special_platform_interactions(
                self.platforms,
                self.current_checkpoint,
            )
        )

        # Check if player is standing on a checkpoint platform
        if (
            self.player.current_platform
            and self.player.current_platform.is_checkpoint()
        ):
            if not self.player.current_platform.checkpoint_activated:
                self.player.current_platform.activate_checkpoint()
                self.current_checkpoint = pygame.Vector2(
                    self.player.current_platform.rect.centerx,
                    self.player.current_platform.rect.top - 30,
                )
                # Save to global activated checkpoints set
                checkpoint_key = (
                    self.page_index,
                    self.player.current_platform.x1,
                    self.player.current_platform.y1,
                    self.player.current_platform.x2,
                    self.player.current_platform.y2,
                )
                self.activated_checkpoints.add(checkpoint_key)

        # Count all activated checkpoints across all pages (not just current page)
        prev_checkpoint_count = self.checkpoints_activated
        self.checkpoints_activated = len(self.activated_checkpoints)
        if self.checkpoints_activated > prev_checkpoint_count:
            self.current_checkpoint_page = self.page_index
        if respawned or should_respawn:
            self.deaths += 1
            self.attempts += 1
            self.latest_run_time = self.run_timer
            self.run_timer = 0.0
            # Always switch to checkpoint page on respawn
            if self.page_index != self.current_checkpoint_page:
                self._switch_page(self.current_checkpoint_page)
            # Update prev position after respawn to prevent falling through platforms
            self.player.prev_y = self.player.player_pos.y
            self.player.prev_x = self.player.player_pos.x

        is_moving = (
            abs(self.player.velocity_x) > 0
            or self._is_control_pressed(keys, "move_left")
            or self._is_control_pressed(keys, "move_right")
        )
        is_landing = (not self.was_on_ground) and self.player.is_on_ground
        if self._is_control_pressed(keys, "move_left"):
            self.character.facing = -1
        elif self._is_control_pressed(keys, "move_right"):
            self.character.facing = 1
        self.character.set_center(self.player.player_pos)
        self.character.update_state(
            self.player.is_on_ground, is_moving, is_flying=False, is_landing=is_landing
        )
        self.character.update(self.dt)
        self.was_on_ground = self.player.is_on_ground

        if not self.isImageLoaded:
            if self.background_image:
                # Load and cache the background image once
                if self.background_image_cached is None:
                    image = pygame.image.load(
                        assets_path("backgrounds", self.background_image)
                    ).convert()
                    self.background_image_cached = pygame.transform.scale(
                        image, (self.screen.get_width(), self.screen.get_height())
                    )
                self.isImageLoaded = True

        # Draw cached background image or solid color
        if self.background_image_cached:
            self.screen.blit(self.background_image_cached, (0, 0))
        else:
            self.set_background(*self.background_color)

        # Debug mode: Draw grid first so other elements render on top.
        if SETTINGS.get("debug_mode", False):
            self.grid.visible = True
            self.grid.draw(self.screen)
        else:
            self.grid.visible = False

        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)

        # Draw player (animated)
        self.character.draw(self.screen)

        if (
            self.player.current_platform and self.player.current_platform.is_finish()
            #            and not self.checkpoints_activated < self.checkpoints_required
        ):
            self.level_completed = True
            self._mark_level_complete()
            from screens.FinishScreen import FinishScreen

            self.running = False
            background = None
            if self._scaled_surface is not None:
                pygame.transform.scale(
                    self.screen, self._real_screen_size, self._scaled_surface
                )
                background = self._scaled_surface.copy()
            else:
                background = self.screen.copy()
            FinishScreen(
                self.real_screen,
                "Finished",
                attempts=self.attempts,
                deaths=self.deaths,
                total_time=self.timer,
                latest_run_time=self.run_timer,
                background=background,
            )
            return
        
        # Debug mode: Draw bounding boxes on top.
        if SETTINGS.get("debug_mode", False):
            # Draw player collision bounding box (now matches sprite)
            pygame.draw.rect(self.screen, "yellow", self.player.get_rect(), 2)
            # Draw platform bounding boxes
            for platform in self.platforms:
                pygame.draw.rect(self.screen, "red", platform.rect, 2)
            # Draw FPS counter and platform info
            debug_y = 10
            self.draw_text(
                f"FPS: {int(self.clock.get_fps())}",
                getFont(30),
                255,
                255,
                255,
                10,
                debug_y,
            )

            # Display checkpoint progress
            debug_y += 40
            self.draw_text(
                f"Checkpoints: {self.checkpoints_activated}/{self.checkpoints_required}",
                getFont(24),
                255,
                255,
                0,
                10,
                debug_y,
            )

            debug_y += 50
            self.draw_text(
                f"Timer: {self.timer:.2f} seconds",
                getFont(24),
                255,
                255,
                255,
                10,
                debug_y,
            )

            # Display current platform info
            if self.player.current_platform:
                platform = self.player.current_platform
                texture_name = "None"
                if platform.texture:
                    # Try to get texture name from Texture enum
                    for attr_name in dir(Texture):
                        if not attr_name.startswith("_"):
                            if getattr(Texture, attr_name) == platform.texture:
                                texture_name = attr_name
                                break

                debug_y += 40
                self.draw_text(
                    f"Platform Type: {platform.platform_type}",
                    getFont(20),
                    100,
                    200,
                    255,
                    10,
                    debug_y,
                )
                debug_y += 25
                self.draw_text(
                    f"Coords: ({platform.rect.x}, {platform.rect.y})",
                    getFont(20),
                    100,
                    200,
                    255,
                    10,
                    debug_y,
                )
                debug_y += 25
                self.draw_text(
                    f"Texture: {texture_name}", getFont(20), 100, 200, 255, 10, debug_y
                )

        # Scale the virtual surface to the real screen size
        if self._scaled_surface is None:
            self.real_screen.blit(self.screen, (0, 0))
        else:
            pygame.transform.scale(
                self.screen, self._real_screen_size, self._scaled_surface
            )
            self.real_screen.blit(self._scaled_surface, (0, 0))

        # Flip() the display to put your work on screen
        pygame.display.flip()

        # Cap dt to prevent large jumps and physics issues
        # Limit to max 16.67ms (60 FPS) to prevent tunneling on lag spikes
        self.dt = min(self.clock.tick() / 1000, 0.0167)
