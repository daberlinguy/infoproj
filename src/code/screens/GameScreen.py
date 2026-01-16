import pygame
from pygame_widgets.button import Button
import pygame_widgets
import sys
import json
from pathlib import Path
import time

from skeletons.screen import Screen
from skeletons.spieler import Spieler
from skeletons.platform import Platform, Grid
from assets.assets import getFont, getMinecraftTexture, Texture

# Import JSONC support
sys.path.insert(0, str(Path(__file__).parent.parent / "leveleditor"))
try:
    from json_utils import load_jsonc
except ImportError:
    # Fallback if json_utils not available
    def load_jsonc(filepath):
        import json
        with open(filepath, 'r') as f:
            return json.load(f)

# Stats file path
STATS_FILE = Path(__file__).parent.parent.parent.parent / "level_stats.json"

def load_stats():
    """Load level stats from file"""
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_stats(stats):
    """Save level stats to file"""
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        print(f"Error saving stats: {e}")

class GameScreen(Screen):
    def __init__(self, screen, caption, level_path=None):
        # Clear all existing widgets from previous screens
        pygame_widgets.WidgetHandler.getWidgets().clear()
        
        self.screen = screen  # Need to set this before loading level
        self.dt = 0
        self.clock=pygame.time.Clock()
        self.level_path = level_path
        self.level_complete = False
        self.level_complete_time = 0
        
        # Stats tracking
        self.attempts = 1  # Start at 1 (first attempt)
        self.start_time = time.time()
        self.elapsed_time = 0
        self.final_time = 0  # Time when level was completed
        
        # Finish platform location (for progress bar)
        self.finish_x = 0
        self.spawn_x = 0

        self.player_pos = pygame.Vector2(screen.get_width() / 2, 100)
        self.player = Spieler(self.player_pos, self.dt)
        
        # Spawn point and checkpoint tracking
        self.spawn_point = pygame.Vector2(1 * 32 + 16, 14 * 32)  # Above spawn platform
        self.current_checkpoint = self.spawn_point.copy()
        
        # Create debug grid
        self.grid = Grid(cell_size=32, color=(80, 80, 80), line_width=1)
        self.grid.visible = False  # Start with grid off
        
        # Grid cell size for alignment
        self.grid_size = 32
        
        # Page/scrolling system
        self.current_page = 0
        self.page_width = screen.get_width()  # 1280 pixels
        self.camera_offset_x = 0
        
        # Platforms will be loaded from level or use default
        self.platforms = []
        
        self.background_color = (128, 0, 128)
        
        # Load level BEFORE calling parent init (which starts the game loop)
        if level_path:
            self.load_level(level_path)
        else:
            # Initialize textures for default level
            Texture.init_textures()
            # Create default platforms (original hardcoded level)
            self.create_default_level()
        
        # Initialize parent class (this starts the game loop)
        super().__init__(screen, caption)

    def create_default_level(self):
        """Create the original hardcoded level"""
        grid_size = self.grid_size
        
        self.platforms = [
            # Spawn platform at grid position (1, 15) - single cell
            Platform(1 * grid_size, 15 * grid_size, 1 * grid_size, 15 * grid_size, grid_size, platform_type=Platform.SPAWN, texture=Texture.GOLD_BLOCK),
            
            # Multi-segment normal platform
            Platform(2 * grid_size, 15 * grid_size, 7 * grid_size, 15 * grid_size, grid_size, 
                     texture=Texture.GRASS),

            # Multi-segment normal platform
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
                     color=(255, 140, 0)),
        ]
    
    def load_level(self, level_path):
        """Load level from JSON/JSONC file"""
        try:
            # Ensure textures are initialized
            Texture.init_textures()
            
            level_data = load_jsonc(level_path)
            print(f"Loading level from: {level_path}")
            print(f"Level data: {level_data.get('name', 'Untitled')}")
            print(f"Number of platforms in file: {len(level_data.get('platforms', []))}")
            
            # Load metadata
            spawn_point = level_data.get("spawn_point", [1, 14])
            self.spawn_point = pygame.Vector2(spawn_point[0] * self.grid_size + 16, 
                                              spawn_point[1] * self.grid_size)
            self.current_checkpoint = self.spawn_point.copy()
            self.player_pos = self.spawn_point.copy()
            self.player.player_pos = self.spawn_point.copy()
            
            self.background_color = tuple(level_data.get("background_color", [128, 0, 128]))
            
            # Load platforms
            self.platforms = []
            for platform_data in level_data.get("platforms", []):
                grid_x1 = platform_data["grid_x1"]
                grid_y1 = platform_data["grid_y1"]
                grid_x2 = platform_data["grid_x2"]
                grid_y2 = platform_data["grid_y2"]
                
                platform_type = platform_data.get("type", Platform.NORMAL)
                color = tuple(platform_data.get("color", [100, 100, 100])) if platform_data.get("color") else None
                texture = platform_data.get("texture")
                
                # Convert grid coordinates to pixel coordinates
                x1 = grid_x1 * self.grid_size
                y1 = grid_y1 * self.grid_size
                x2 = grid_x2 * self.grid_size
                y2 = grid_y2 * self.grid_size
                
                # Get texture object if specified
                texture_obj = None
                if texture:
                    try:
                        texture_obj = getattr(Texture, texture, None)
                    except:
                        pass
                
                platform = Platform(x1, y1, x2, y2, self.grid_size,
                                  platform_type=platform_type,
                                  color=color,
                                  texture=texture_obj)
                self.platforms.append(platform)
            
            print(f"Platforms created: {len(self.platforms)}")
            
            # Find spawn platform and set checkpoint to it
            for platform in self.platforms:
                if platform.is_spawn():
                    self.spawn_point = pygame.Vector2(platform.rect.centerx, platform.rect.top - 30)
                    self.current_checkpoint = self.spawn_point.copy()
                    self.player_pos = self.spawn_point.copy()
                    self.player.player_pos = self.spawn_point.copy()
                    self.spawn_x = platform.rect.centerx
                if platform.is_finish():
                    self.finish_x = platform.rect.centerx
            
            print(f"Level loaded: {level_data.get('name', 'Untitled')}")
        except Exception as e:
            print(f"Error loading level: {e}")
            import traceback
            traceback.print_exc()
            print("Using default level instead")
            self.create_default_level()

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
                if event.key == pygame.K_g:  # Toggle grid with 'G' key
                    self.grid.toggle()
                if event.key == pygame.K_r:  # Reset to spawn point with 'R' key
                    self.player.player_pos = self.spawn_point.copy()
                    self.player.velocity_x = 0
                    self.player.velocity_y = 0
                    self.level_complete = False
                    self.attempts = 1  # Reset attempts
                    self.start_time = time.time()  # Reset timer
                    self.current_checkpoint = self.spawn_point.copy()
                    # Reset camera
                    self.current_page = int(self.spawn_point.x // self.page_width)
                    self.camera_offset_x = self.current_page * self.page_width
                    # Reset checkpoint activations
                    for platform in self.platforms:
                        if platform.is_checkpoint():
                            platform.checkpoint_activated = False
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    from screens.LevelSelectScreen import LevelSelectScreen
                    LevelSelectScreen(self.screen, "Level Select")
                    return

        # Fill with background color or image
        self.screen.fill(self.background_color)
        
        # Draw grid first (behind everything)
        self.grid.draw(self.screen)
        
        # Update elapsed time (only if level not complete)
        if not self.level_complete:
            self.elapsed_time = time.time() - self.start_time
        
        # Draw progress bar at top
        self.draw_progress_bar()
        
        # Draw HUD (FPS, time, attempts)
        self.draw_hud()


        # Draw platforms (with camera offset)
        for platform in self.platforms:
            # Only draw platforms visible on current page
            if self.is_platform_visible(platform):
                self.draw_platform_with_offset(platform)

        # Draw player (with camera offset)
        scale_factor = 0.2# Scale factor for the sprite and bounding box
        sprite_width = int(182 * scale_factor)
        sprite_height = int(243 * scale_factor)
        screen_x = self.player.player_pos.x - self.camera_offset_x
        screen_y = self.player.player_pos.y
        self.draw_sprite("Sprite_laufen-0001.png", 
                 screen_x - sprite_width / 2, 
                 screen_y - sprite_height / 2, 
                 sprite_width, sprite_height)
        #pygame.draw.rect(self.screen, "black", 
        #         pygame.Rect(screen_x - sprite_width / 2, 
        #                 screen_y - sprite_height / 2, 
        #                 sprite_width, sprite_height), 2)  # Draw scaled bounding box for debugging

        # Handle input
        keys = pygame.key.get_pressed()
        
        # Don't allow movement if level is complete
        if not self.level_complete:
            # Update player dt
            self.player.dt = self.dt
            
            # Store previous position before any movement
            self.player.prev_x = self.player.player_pos.x
            self.player.prev_y = self.player.player_pos.y
            
            if keys[pygame.K_a]:
                self.player.move_left()
            if keys[pygame.K_d]:
                self.player.move_right()
            if keys[pygame.K_SPACE] or keys[pygame.K_w]:
                self.player.jump()
            
            # Update moving platforms
            for platform in self.platforms:
                platform.update(self.dt)
            
            # Apply physics - apply gravity first, then check collisions to resolve
            self.player.apply_physics(self.dt)
            #[pygame.draw.rect(self.screen, "red", platform.rect, 2) for platform in self.platforms]  # Draw platform bounding boxes for debugging
            self.player.check_platform_collision(self.platforms)
            
            # Check for page transitions
            self.handle_page_transitions()
            
            # Check if player fell off the screen
            if self.player.check_fell_off_screen(self.screen.get_height(), self.current_checkpoint):
                # Set camera to the page containing the checkpoint
                self.current_page = int(self.current_checkpoint.x // self.page_width)
                self.camera_offset_x = self.current_page * self.page_width
                self.attempts += 1  # Increment attempts on fall death
            
            # Check for special platform interactions (death, checkpoint, finish)
            new_checkpoint, did_respawn = self.player.check_special_platform_interactions(self.platforms, self.current_checkpoint)
            if new_checkpoint != self.current_checkpoint:
                self.current_checkpoint = new_checkpoint
            if did_respawn:
                # Set camera to the page containing the checkpoint
                self.current_page = int(self.current_checkpoint.x // self.page_width)
                self.camera_offset_x = self.current_page * self.page_width
                self.attempts += 1  # Increment attempts on death platform
            
            # Check for level completion
            self.check_level_complete()
        
        # Draw level complete message if needed
        if self.level_complete:
            self.draw_level_complete()
        
        # Flip() the display to put your work on screen
        pygame.display.flip()

        # Limits FPS to 60 and cap dt to prevent large jumps
        self.dt = min(self.clock.tick(60) / 1000, 0.05)  # Cap at 50ms (20 FPS minimum)
    
    def check_level_complete(self):
        """Check if player touched the finish block"""
        player_rect = pygame.Rect(self.player.player_pos.x - 18, self.player.player_pos.y - 24, 36, 48)
        
        for platform in self.platforms:
            if platform.is_finish() and player_rect.colliderect(platform.rect):
                if not self.level_complete:
                    self.level_complete = True
                    self.level_complete_time = pygame.time.get_ticks()
                    self.final_time = self.elapsed_time
                    
                    # Save stats
                    self.save_level_stats()
                return
    
    def handle_page_transitions(self):
        """Handle page transitions when player reaches screen edges"""
        screen_x = self.player.player_pos.x - self.camera_offset_x
        
        # Check if player is going right past the screen edge
        if screen_x > self.page_width:
            # Move to next page
            self.current_page += 1
            self.camera_offset_x = self.current_page * self.page_width
        
        # Check if player is going left past the screen edge
        elif screen_x < 0:
            if self.current_page > 0:
                # Move to previous page
                self.current_page -= 1
                self.camera_offset_x = self.current_page * self.page_width
            else:
                # Prevent player from going past the left edge of first page
                self.player.player_pos.x = self.camera_offset_x + 1
    
    def is_platform_visible(self, platform):
        """Check if platform is visible on current page"""
        page_left = self.camera_offset_x
        page_right = self.camera_offset_x + self.page_width
        
        # Platform is visible if any part overlaps with current page
        return platform.rect.right > page_left and platform.rect.left < page_right
    
    def draw_platform_with_offset(self, platform):
        """Draw a platform with camera offset applied"""
        # Create a copy of the platform's cells with offset positions
        for cell in platform.cells:
            offset_rect = cell.rect.copy()
            offset_rect.x -= self.camera_offset_x
            
            # Draw cell
            if cell.texture:
                texture_scaled = pygame.transform.scale(cell.texture, (cell.size, cell.size))
                self.screen.blit(texture_scaled, offset_rect.topleft)
            else:
                pygame.draw.rect(self.screen, cell.color, offset_rect)
        
        # Draw platform type indicators
        if not platform.texture:
            if platform.platform_type == platform.DEATH:
                for cell in platform.cells:
                    offset_rect = cell.rect.copy()
                    offset_rect.x -= self.camera_offset_x
                    pygame.draw.line(self.screen, (150, 0, 0), offset_rect.topleft, offset_rect.bottomright, 2)
                    pygame.draw.line(self.screen, (150, 0, 0), offset_rect.topright, offset_rect.bottomleft, 2)
            elif platform.platform_type == platform.CHECKPOINT:
                center_cell = platform.cells[len(platform.cells) // 2]
                offset_rect = center_cell.rect.copy()
                offset_rect.x -= self.camera_offset_x
                if platform.checkpoint_activated:
                    offset_platform_rect = platform.rect.copy()
                    offset_platform_rect.x -= self.camera_offset_x
                    pygame.draw.rect(self.screen, (0, 200, 0), offset_platform_rect, 3)
                else:
                    center_x = offset_rect.centerx
                    top_y = offset_rect.top + 5
                    pygame.draw.line(self.screen, (0, 0, 0), (center_x, top_y), (center_x, offset_rect.bottom - 5), 2)
                    pygame.draw.polygon(self.screen, (0, 0, 0), [(center_x, top_y), (center_x + 10, top_y + 5), (center_x, top_y + 10)])
            elif platform.platform_type == platform.SLIPPERY:
                for cell in platform.cells:
                    offset_rect = cell.rect.copy()
                    offset_rect.x -= self.camera_offset_x
                    for i in range(3):
                        y = offset_rect.centery - 5 + i * 5
                        pygame.draw.line(self.screen, (50, 100, 150), (offset_rect.left + 5, y), (offset_rect.right - 5, y), 1)
            elif platform.platform_type == platform.SPAWN:
                center_cell = platform.cells[len(platform.cells) // 2]
                offset_rect = center_cell.rect.copy()
                offset_rect.x -= self.camera_offset_x
                font = pygame.font.Font(None, 20)
                text = font.render("S", True, (0, 150, 0))
                self.screen.blit(text, (offset_rect.centerx - 5, offset_rect.centery - 10))
            elif platform.platform_type == platform.FINISH:
                center_cell = platform.cells[len(platform.cells) // 2]
                offset_rect = center_cell.rect.copy()
                offset_rect.x -= self.camera_offset_x
                font = pygame.font.Font(None, 24)
                text = font.render("F", True, (0, 0, 0))
                self.screen.blit(text, (offset_rect.centerx - 6, offset_rect.centery - 12))
                pygame.draw.circle(self.screen, (255, 255, 255), (offset_rect.left + 5, offset_rect.top + 5), 3)
                pygame.draw.circle(self.screen, (255, 255, 255), (offset_rect.right - 5, offset_rect.top + 5), 3)
    
    def draw_hud(self):
        """Draw heads-up display with FPS, time, and attempts"""
        # FPS (top left)
        self.draw_text(f"FPS: {int(self.clock.get_fps())}", getFont(24), 255, 255, 255, 10, 45)
        
        # Time (top center)
        minutes = int(self.elapsed_time // 60)
        seconds = int(self.elapsed_time % 60)
        milliseconds = int((self.elapsed_time % 1) * 100)
        time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
        time_font = getFont(28)
        time_surface = time_font.render(time_str, True, (255, 255, 255))
        time_x = (self.screen.get_width() - time_surface.get_width()) // 2
        self.screen.blit(time_surface, (time_x, 45))
        
        # Attempts (top right)
        attempts_text = f"Attempts: {self.attempts}"
        attempts_font = getFont(24)
        attempts_surface = attempts_font.render(attempts_text, True, (255, 255, 255))
        attempts_x = self.screen.get_width() - attempts_surface.get_width() - 10
        self.screen.blit(attempts_surface, (attempts_x, 45))
    
    def draw_progress_bar(self):
        """Draw progress bar at the top of the screen"""
        bar_height = 35
        bar_y = 0
        bar_padding = 5
        
        # Background of bar
        pygame.draw.rect(self.screen, (40, 40, 40), (0, bar_y, self.screen.get_width(), bar_height))
        
        # Calculate progress (0 to 1)
        if self.finish_x > self.spawn_x:
            progress = (self.player.player_pos.x - self.spawn_x) / (self.finish_x - self.spawn_x)
            progress = max(0, min(1, progress))  # Clamp between 0 and 1
        else:
            progress = 0
        
        # Progress fill
        fill_width = int((self.screen.get_width() - bar_padding * 2) * progress)
        if fill_width > 0:
            # Gradient effect - darker to lighter green
            progress_color = (50, 200, 50)
            pygame.draw.rect(self.screen, progress_color, 
                           (bar_padding, bar_y + bar_padding, fill_width, bar_height - bar_padding * 2),
                           border_radius=3)
        
        # Border
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (bar_padding, bar_y + bar_padding, 
                         self.screen.get_width() - bar_padding * 2, bar_height - bar_padding * 2), 
                        2, border_radius=3)
        
        # Progress percentage text
        progress_text = f"{int(progress * 100)}%"
        progress_font = getFont(20)
        progress_surface = progress_font.render(progress_text, True, (255, 255, 255))
        text_x = (self.screen.get_width() - progress_surface.get_width()) // 2
        self.screen.blit(progress_surface, (text_x, bar_y + bar_padding))
        
        # Finish flag icon at end of bar
        flag_x = self.screen.get_width() - 30
        flag_y = bar_y + bar_height // 2
        pygame.draw.line(self.screen, (255, 255, 255), (flag_x, flag_y - 10), (flag_x, flag_y + 10), 2)
        pygame.draw.polygon(self.screen, (255, 215, 0), 
                           [(flag_x, flag_y - 10), (flag_x + 15, flag_y - 5), (flag_x, flag_y)])
    
    def save_level_stats(self):
        """Save the current level's completion stats"""
        if not self.level_path:
            return
        
        stats = load_stats()
        level_key = str(self.level_path)
        
        # Check if this is a new best time or first completion
        current_stats = stats.get(level_key, {})
        best_time = current_stats.get('best_time', float('inf'))
        best_attempts = current_stats.get('best_attempts', float('inf'))
        
        is_new_best_time = self.final_time < best_time
        is_new_best_attempts = self.attempts < best_attempts
        
        # Update stats
        stats[level_key] = {
            'best_time': min(self.final_time, best_time),
            'best_attempts': min(self.attempts, best_attempts),
            'last_time': self.final_time,
            'last_attempts': self.attempts,
            'completed': True
        }
        
        save_stats(stats)
        
        # Store for display
        self.is_new_best_time = is_new_best_time
        self.is_new_best_attempts = is_new_best_attempts
    
    def format_time(self, seconds):
        """Format time in mm:ss.ms format"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 100)
        return f"{minutes:02d}:{secs:02d}.{ms:02d}"
    
    def draw_level_complete(self):
        """Draw level complete overlay with stats"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        center_x = self.screen.get_width() // 2
        
        # Level complete text
        title_font = getFont(70)
        title_text = title_font.render("LEVEL COMPLETE!", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(center_x, 120))
        self.screen.blit(title_text, title_rect)
        
        # Stats box background
        box_width = 500
        box_height = 280
        box_x = center_x - box_width // 2
        box_y = 180
        pygame.draw.rect(self.screen, (50, 50, 70), (box_x, box_y, box_width, box_height), border_radius=15)
        pygame.draw.rect(self.screen, (100, 100, 120), (box_x, box_y, box_width, box_height), 3, border_radius=15)
        
        # Time stat
        stat_font = getFont(36)
        label_font = getFont(28)
        
        # Time
        time_label = label_font.render("Time:", True, (180, 180, 180))
        self.screen.blit(time_label, (box_x + 40, box_y + 30))
        
        time_value = stat_font.render(self.format_time(self.final_time), True, (255, 255, 255))
        self.screen.blit(time_value, (box_x + 200, box_y + 25))
        
        # New best indicator for time
        if hasattr(self, 'is_new_best_time') and self.is_new_best_time:
            new_best = getFont(20).render("NEW BEST!", True, (50, 255, 50))
            self.screen.blit(new_best, (box_x + 380, box_y + 35))
        
        # Attempts
        attempts_label = label_font.render("Attempts:", True, (180, 180, 180))
        self.screen.blit(attempts_label, (box_x + 40, box_y + 90))
        
        attempts_value = stat_font.render(str(self.attempts), True, (255, 255, 255))
        self.screen.blit(attempts_value, (box_x + 200, box_y + 85))
        
        # New best indicator for attempts
        if hasattr(self, 'is_new_best_attempts') and self.is_new_best_attempts:
            new_best = getFont(20).render("NEW BEST!", True, (50, 255, 50))
            self.screen.blit(new_best, (box_x + 380, box_y + 95))
        
        # Load and show best stats
        if self.level_path:
            stats = load_stats()
            level_stats = stats.get(str(self.level_path), {})
            
            # Separator line
            pygame.draw.line(self.screen, (100, 100, 120), 
                           (box_x + 30, box_y + 150), (box_x + box_width - 30, box_y + 150), 2)
            
            # Best records header
            best_header = label_font.render("Best Records:", True, (255, 215, 0))
            self.screen.blit(best_header, (box_x + 40, box_y + 165))
            
            # Best time
            best_time = level_stats.get('best_time', self.final_time)
            best_time_label = getFont(24).render("Best Time:", True, (150, 150, 150))
            self.screen.blit(best_time_label, (box_x + 50, box_y + 205))
            best_time_value = getFont(24).render(self.format_time(best_time), True, (200, 200, 200))
            self.screen.blit(best_time_value, (box_x + 200, box_y + 205))
            
            # Best attempts
            best_attempts = level_stats.get('best_attempts', self.attempts)
            best_att_label = getFont(24).render("Best Attempts:", True, (150, 150, 150))
            self.screen.blit(best_att_label, (box_x + 50, box_y + 240))
            best_att_value = getFont(24).render(str(best_attempts), True, (200, 200, 200))
            self.screen.blit(best_att_value, (box_x + 230, box_y + 240))
        
        # Instructions
        instruction_font = getFont(26)
        instruction_text = instruction_font.render("Press ESC to return to level select", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(center_x, box_y + box_height + 50))
        self.screen.blit(instruction_text, instruction_rect)
        
        # Restart option
        restart_text = instruction_font.render("Press R to restart", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(center_x, box_y + box_height + 90))
        self.screen.blit(restart_text, restart_rect)
