import pygame
from pygame_widgets.button import Button
import sys

from skeletons.screen import Screen
from skeletons.spieler import Spieler
from skeletons.platform import Platform, Grid
from assets.assets import getFont, getMinecraftTexture, Texture
from screens.SettingsScreen import SETTINGS

class GameScreen(Screen):
    def __init__(self, screen, caption):
        # Clear all previous widgets
        from pygame_widgets.widget import WidgetHandler
        widgets = WidgetHandler.getWidgets()
        for widget in list(widgets):
            WidgetHandler.removeWidget(widget)
        
        self.dt = 0
        self.clock=pygame.time.Clock()

        self.player_pos = pygame.Vector2(screen.get_width() / 2, 100)
        self.player = Spieler(self.player_pos, self.dt)
        
        # Spawn point and checkpoint tracking
        self.spawn_point = pygame.Vector2(1 * 32 + 16, 14 * 32)  # Above spawn platform
        self.current_checkpoint = self.spawn_point.copy()
        
        # Create debug grid
        self.grid = Grid(cell_size=32, color=(80, 80, 80), line_width=1)
        self.grid.visible = False  # Grid is part of debug mode
        
        # Grid cell size for alignment
        grid_size = 32
        
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

        super().__init__(screen, caption)

    def onBtnOpenGameScreen(self):
        print("Game Screen would open here.")  # Add your game screen transition here

    def run(self):
        pygame.display.set_caption(f"X: {int(self.player_pos.x)} Y: {int(self.player_pos.y)} On Ground: {self.player.is_on_ground}")


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

        self.screen.fill("purple")
        
        self.draw_text(f"FPS: {int(self.clock.get_fps())}", getFont(30), 255, 255, 255, 10, 10)


        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)

        # Draw player
        scale_factor = 0.2# Scale factor for the sprite and bounding box
        sprite_width = self.player.sprite_width
        sprite_height = self.player.sprite_height
        self.draw_sprite("Sprite_laufen-0001.png", 
                 self.player.player_pos.x - sprite_width / 2, 
                 self.player.player_pos.y - sprite_height / 2, 
                 sprite_width, sprite_height)
        
        # Debug mode: Draw bounding boxes and grid
        if SETTINGS.get('debug_mode', False):
            # Draw grid
            self.grid.draw(self.screen)
            # Draw player collision bounding box (now matches sprite)
            pygame.draw.rect(self.screen, "yellow", self.player.get_rect(), 2)
            # Draw platform bounding boxes
            for platform in self.platforms:
                pygame.draw.rect(self.screen, "red", platform.rect, 2)

        # Handle input
        keys = pygame.key.get_pressed()
        
        # Update player dt
        self.player.dt = self.dt
        
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
        self.player.check_fell_off_screen(self.screen.get_height(), self.current_checkpoint)
        
        # Check for special platform interactions (death, checkpoint)
        self.current_checkpoint, _ = self.player.check_special_platform_interactions(self.platforms, self.current_checkpoint)

        # Flip() the display to put your work on screen
        pygame.display.flip()

        # Cap dt to prevent large jumps and physics issues
        # Limit to max 16.67ms (60 FPS) to prevent tunneling on lag spikes
        self.dt = min(self.clock.tick() / 1000, 0.0167)
