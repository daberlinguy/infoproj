import os
import pygame
import sys
import json

from skeletons.screen import Screen
from skeletons.spieler import Spieler
from skeletons.platform import Platform, Grid
from skeletons.character import Character
from skeletons.character_classes.characters import CHARACTER_REGISTRY
from assets.assets import getFont, getMinecraftTexture, Texture, assets_path
from screens.SettingsScreen import SETTINGS
from data.storage import load_worlds, save_settings

class GameScreen(Screen):
    def __init__(self, screen, caption, level_path=None):
        # Clear all previous widgets
        from pygame_widgets.widget import WidgetHandler
        widgets = WidgetHandler.getWidgets()
        WidgetHandler._widgets = widgets.__class__()
        
        self.dt = 0
        self.clock=pygame.time.Clock()

        self.player_pos = pygame.Vector2(screen.get_width() / 2, 100)
        self.player = Spieler(self.player_pos, self.dt)
        self.was_on_ground = False

        self.character = self._create_character()
        self.level_path = level_path
        self.level_completed = False
        self.checkpoints_required = 0
        self.checkpoints_activated = 0
        self.background_color = "purple"
        self.background_image = None
        self.background_image_cached = None
        self.level_data = None
        self.page_index = 1
        self.page_width_cells = 60
        self.page_height_cells = 34
        self.page_grid_size = 32
        
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
        
        # Create platforms - all grid-aligned with different types
        self.platforms = [
            # Spawn platform at grid position (6, 15) - single cell
            Platform(1 * grid_size, 15 * grid_size, 1 * grid_size, 15 * grid_size, grid_size, platform_type=Platform.SPAWN, texture=Texture.GOLD_BLOCK),
            
            # Multi-segment normal platform - 5 cells next to each other at grid position (18, 12)
            Platform(2 * grid_size, 15 * grid_size, 7 * grid_size, 15 * grid_size, grid_size, 
                     texture=Texture.GRASS),

            # Multi-segment normal platform - 5 cells next to each other at grid position (18, 12)
            Platform(18 * grid_size, 12 * grid_size, 22 * grid_size, 12 * grid_size, grid_size, 
                     texture=Texture.GRASS),
            
            # Checkpoint platform at (25, 12)
            Platform(25 * grid_size, 12 * grid_size, 25 * grid_size, 12 * grid_size, grid_size, 
                     platform_type=Platform.CHECKPOINT),
            
            # Death platforms at (10, 17) - 3 cells
            Platform(10 * grid_size, 17 * grid_size, 12 * grid_size, 17 * grid_size, grid_size, 
                     platform_type=Platform.DEATH),
            
            # Slippery platform - 4 cells at (14, 16)
            Platform(14 * grid_size, 16 * grid_size, 17 * grid_size, 16 * grid_size, grid_size, 
                     platform_type=Platform.SLIPPERY, texture=Texture.ICE),
            
            # Ground platform - 12 cells at bottom
            Platform(12 * grid_size, 18 * grid_size, 23 * grid_size, 18 * grid_size, grid_size, 
                     texture=Texture.STONE),
            
            # Orange platform - 3x2 cells at grid position (28, 9)
            Platform(28 * grid_size, 9 * grid_size, 30 * grid_size, 10 * grid_size, grid_size, 
                     texture=Texture.LAVA),

            Platform(0 * grid_size, 22 * grid_size, 500 * grid_size, 22 * grid_size, grid_size, 
                     texture=Texture.LAVA, platform_type=Platform.DEATH),
        ]

        if self.level_path:
            self._load_level(self.level_path)

        super().__init__(screen, caption)

    def _create_character(self):
        character_id = SETTINGS.get('character', 'character1')
        character_cls = CHARACTER_REGISTRY.get(character_id, CHARACTER_REGISTRY["character1"])
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

        self.page_width_cells = int(level_data.get("page_width_cells", self.page_width_cells))
        self.page_height_cells = int(level_data.get("page_height_cells", self.page_height_cells))

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
            total_checkpoints = sum(1 for platform in self.platforms if platform.is_checkpoint())
        self.checkpoints_required = total_checkpoints
        print(f"Total checkpoints in level: {self.checkpoints_required}")

    def _build_platforms_from_level(self, level_data, page_index=1):
        pages = level_data.get("pages")
        if pages:
            page_data = pages.get(str(page_index)) or pages.get(page_index) or {}
            platforms_data = page_data.get("platforms", [])
        else:
            platforms_data = level_data.get("platforms", [])
        platforms = []
        for entry in platforms_data:
            grid_size = entry.get("grid_size", 32)
            x1 = entry.get("x1", entry.get("x", 0))
            y1 = entry.get("y1", entry.get("y", 0))
            x2 = entry.get("x2")
            y2 = entry.get("y2")
            w = entry.get("w")
            h = entry.get("h")
            if x2 is None and w is not None:
                x2 = x1 + w
            if y2 is None and h is not None:
                y2 = y1 + h
            if x2 is None or y2 is None:
                continue
            x1 *= grid_size
            y1 *= grid_size
            x2 *= grid_size
            y2 *= grid_size
            platform_type_name = str(entry.get("type", "NORMAL")).upper()
            platform_type = getattr(Platform, platform_type_name, Platform.NORMAL)
            texture_name = entry.get("texture")
            texture = getattr(Texture, texture_name, None) if texture_name else None
            color = entry.get("color")
            if color and isinstance(color, list):
                color = tuple(color)

            platforms.append(
                Platform(x1, y1, x2, y2, grid_size, platform_type=platform_type, color=color, texture=texture)
            )
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
                checkpoint_key = (self.page_index, platform.x1, platform.y1, platform.x2, platform.y2)
                self.activated_checkpoints.add(checkpoint_key)
        
        self.page_index = new_page
        self.platforms = self._build_platforms_from_level(self.level_data, self.page_index)
        
        # Restore checkpoint states for this page
        for platform in self.platforms:
            if platform.is_checkpoint():
                checkpoint_key = (self.page_index, platform.x1, platform.y1, platform.x2, platform.y2)
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
        world_progress = progress.setdefault(world_id, {"levels": {}, "complete": False})
        world_progress.setdefault("levels", {})[level_id] = True
        total_levels = len(worlds[world_id]["levels"])
        completed_levels = sum(1 for level in worlds[world_id]["levels"] if world_progress["levels"].get(level["id"]))
        world_progress["complete"] = total_levels > 0 and completed_levels == total_levels
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
                exit()
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:  # Toggle debug mode with 'F3' key
                    SETTINGS['debug_mode'] = not SETTINGS.get('debug_mode', False)
                if event.key == pygame.K_r:  # Reset to spawn point with 'R' key
                    self.player.player_pos = self.spawn_point.copy()
                    self.player.velocity = pygame.Vector2(0, 0)

        # Handle input
        keys = pygame.key.get_pressed()
        
        # Update player dt
        self.player.dt = self.dt

        # Timer
        self.timer += self.dt
        
        # Store previous position before any movement
        self.player.prev_x = self.player.player_pos.x
        self.player.prev_y = self.player.player_pos.y
        
        if keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_d]:
            self.player.move_right()
        if keys[pygame.K_ESCAPE]:
            self.running = False
            from screens.TitleScreen import TitleScreen
            TitleScreen(self.screen, "Title Screen")
        if keys[pygame.K_SPACE] or keys[pygame.K_w]:
            self.player.jump()
        
        # Update moving platforms
        for platform in self.platforms:
            platform.update(self.dt)
        
        # Apply physics - apply gravity first, then check collisions to resolve
        self.player.apply_physics(self.dt)
        self.player.check_platform_collision(self.platforms)
        
        # Check if player fell off the screen
        respawned = self.player.check_fell_off_screen(self.screen.get_height(), self.current_checkpoint)
        
        # Check for special platform interactions (death, checkpoint)
        prev_checkpoint_count = self.checkpoints_activated
        self.current_checkpoint, should_respawn = self.player.check_special_platform_interactions(
            self.platforms,
            self.current_checkpoint,
        )
        
        # Check if player is standing on a checkpoint platform
        if self.player.current_platform and self.player.current_platform.is_checkpoint():
            if not self.player.current_platform.checkpoint_activated:
                self.player.current_platform.activate_checkpoint()
                self.current_checkpoint = pygame.Vector2(
                    self.player.current_platform.rect.centerx, 
                    self.player.current_platform.rect.top - 30
                )
                # Save to global activated checkpoints set
                checkpoint_key = (self.page_index, self.player.current_platform.x1, 
                                self.player.current_platform.y1, self.player.current_platform.x2, 
                                self.player.current_platform.y2)
                self.activated_checkpoints.add(checkpoint_key)
        
        # Count all activated checkpoints across all pages (not just current page)
        prev_checkpoint_count = self.checkpoints_activated
        self.checkpoints_activated = len(self.activated_checkpoints)
        if self.checkpoints_activated > prev_checkpoint_count:
            self.current_checkpoint_page = self.page_index
        if respawned or should_respawn:
            if self.page_index != self.current_checkpoint_page:
                self._switch_page(self.current_checkpoint_page)

        is_moving = abs(self.player.velocity_x) > 0 or keys[pygame.K_a] or keys[pygame.K_d]
        is_landing = (not self.was_on_ground) and self.player.is_on_ground
        if keys[pygame.K_a]:
            self.character.facing = -1
        elif keys[pygame.K_d]:
            self.character.facing = 1
        self.character.set_center(self.player.player_pos)
        self.character.update_state(self.player.is_on_ground, is_moving, is_flying=False, is_landing=is_landing)
        self.character.update(self.dt)
        self.was_on_ground = self.player.is_on_ground

        page_width_px = self.page_width_cells * self.page_grid_size
        player_pos = self.player.player_pos
        if player_pos.x < 0:
            if self.level_data and self.level_data.get("pages") and self.page_index > 1:
                player_pos.x = page_width_px - 1
                self._switch_page(self.page_index - 1)
            else:
                player_pos.x = 0
        elif player_pos.x > page_width_px:
            next_page = self.page_index + 1
            if self.level_data and self.level_data.get("pages") and (str(next_page) in self.level_data["pages"] or next_page in self.level_data["pages"]):
                player_pos.x = 1
                self._switch_page(next_page)
            else:
                player_pos.x = page_width_px

        if not self.isImageLoaded:
            if self.background_image:
                # Load and cache the background image once
                if self.background_image_cached is None:
                    image = pygame.image.load(assets_path("backgrounds", self.background_image)).convert()
                    self.background_image_cached = pygame.transform.scale(image, (self.screen.get_width(), self.screen.get_height()))
                self.isImageLoaded = True
        
        # Draw cached background image or solid color
        if self.background_image_cached:
            self.screen.blit(self.background_image_cached, (0, 0))
        else:
            self.set_background(*self.background_color)

        # Debug mode: Draw grid first so other elements render on top.
        if SETTINGS.get('debug_mode', False):
            self.grid.visible = True
            self.grid.draw(self.screen)
        else:
            self.grid.visible = False

        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)

        # Draw player (animated)
        self.character.draw(self.screen)

        if self.player.current_platform and self.player.current_platform.is_finish() and not self.checkpoints_activated < self.checkpoints_required:
            self.level_completed = True
            self._mark_level_complete()
            from screens.FinishScreen import FinishScreen
            self.running = False
            FinishScreen(self.screen, "Finished")
            return
        
        # Debug mode: Draw bounding boxes on top.
        if SETTINGS.get('debug_mode', False):
            # Draw player collision bounding box (now matches sprite)
            pygame.draw.rect(self.screen, "yellow", self.player.get_rect(), 2)
            # Draw platform bounding boxes
            for platform in self.platforms:
                pygame.draw.rect(self.screen, "red", platform.rect, 2)
            # Draw FPS counter and platform info
            debug_y = 10
            self.draw_text(f"FPS: {int(self.clock.get_fps())}", getFont(30), 255, 255, 255, 10, debug_y)
            
            # Display checkpoint progress
            debug_y += 40
            self.draw_text(f"Checkpoints: {self.checkpoints_activated}/{self.checkpoints_required}", getFont(24), 255, 255, 0, 10, debug_y)
            
            debug_y += 50
            self.draw_text(f"Timer: {self.timer:.2f} seconds", getFont(24), 255, 255, 255, 10, debug_y)

            # Display current platform info
            if self.player.current_platform:
                platform = self.player.current_platform
                texture_name = "None"
                if platform.texture:
                    # Try to get texture name from Texture enum
                    for attr_name in dir(Texture):
                        if not attr_name.startswith('_'):
                            if getattr(Texture, attr_name) == platform.texture:
                                texture_name = attr_name
                                break
                
                debug_y += 40
                self.draw_text(f"Platform Type: {platform.platform_type}", getFont(20), 100, 200, 255, 10, debug_y)
                debug_y += 25
                self.draw_text(f"Coords: ({platform.rect.x}, {platform.rect.y})", getFont(20), 100, 200, 255, 10, debug_y)
                debug_y += 25
                self.draw_text(f"Texture: {texture_name}", getFont(20), 100, 200, 255, 10, debug_y)

        # Flip() the display to put your work on screen
        pygame.display.flip()

        # Cap dt to prevent large jumps and physics issues
        # Limit to max 16.67ms (60 FPS) to prevent tunneling on lag spikes
        self.dt = min(self.clock.tick() / 1000, 0.0167)
