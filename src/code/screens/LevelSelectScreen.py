import pygame
import pygame_widgets
from pygame_widgets.button import Button
import sys
import json
from pathlib import Path

from skeletons.screen import Screen
from assets.assets import getFont

# Import JSONC support
sys.path.insert(0, str(Path(__file__).parent.parent / "leveleditor"))
try:
    from json_utils import load_jsonc
except ImportError:
    # Fallback if json_utils not available
    def load_jsonc(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)

# Stats file path (same as GameScreen)
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

def format_time(seconds):
    """Format time in mm:ss.ms format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    ms = int((seconds % 1) * 100)
    return f"{minutes:02d}:{secs:02d}.{ms:02d}"


class LevelSelectScreen(Screen):
    def __init__(self, screen, caption, world_name=None):
        # Clear all existing widgets from previous screens
        pygame_widgets.WidgetHandler.getWidgets().clear()
        
        self.world_name = world_name
        self.selected_world = None
        self.levels_dir = Path(__file__).parent.parent.parent.parent / "levels"
        
        # Get all worlds
        self.worlds = []
        if self.levels_dir.exists():
            self.worlds = [d.name for d in self.levels_dir.iterdir() if d.is_dir()]
        
        # If no world specified, show world selection
        self.show_world_select = world_name is None
        
        # Buttons for worlds or levels
        self.buttons = []
        self.back_btn = None
        
        # Level data
        self.levels = []
        
        # Initialize based on mode
        if self.show_world_select:
            self.setup_world_buttons(screen)
        else:
            self.selected_world = world_name
            self.setup_level_buttons(screen)
        
        super().__init__(screen, caption)

    def setup_world_buttons(self, screen):
        """Create buttons for world selection"""
        self.buttons.clear()
        
        button_width = 200
        button_height = 60
        button_spacing = 20
        
        # Calculate grid layout
        columns = 3
        start_x = (screen.get_width() - (columns * button_width + (columns - 1) * button_spacing)) / 2
        start_y = 150
        
        for i, world_name in enumerate(self.worlds):
            row = i // columns
            col = i % columns
            
            x = start_x + col * (button_width + button_spacing)
            y = start_y + row * (button_height + button_spacing)
            
            btn = Button(screen, x, y, button_width, button_height, False,
                        text=world_name.replace('_', ' ').title(),
                        onClick=lambda w=world_name: self.select_world(w),
                        font=getFont(24), radius=10)
            self.buttons.append(btn)
        
        # Back button
        self.back_btn = Button(screen, 20, screen.get_height() - 70, 150, 50, False,
                              text="Back", onClick=self.go_back,
                              font=getFont(24), radius=10)

    def setup_level_buttons(self, screen):
        """Create buttons for level selection"""
        self.buttons.clear()
        
        # Load all stats once
        self.all_stats = load_stats()
        
        # Load levels from selected world
        world_path = self.levels_dir / self.selected_world
        self.levels = []
        
        if world_path.exists():
            level_files = sorted(list(world_path.glob('*.json')) + list(world_path.glob('*.jsonc')))
            for level_file in level_files:
                try:
                    level_data = load_jsonc(level_file)
                    self.levels.append({
                        'name': level_data.get('name', level_file.stem),
                        'path': level_file
                    })
                except:
                    # If JSON parsing fails, just use filename
                    self.levels.append({
                        'name': level_file.stem,
                        'path': level_file
                    })
        
        # Create grid of level buttons (larger to fit stats)
        button_width = 180
        button_height = 100
        button_spacing = 20
        
        columns = 5
        start_x = (screen.get_width() - (columns * button_width + (columns - 1) * button_spacing)) / 2
        start_y = 150
        
        for i, level in enumerate(self.levels):
            row = i // columns
            col = i % columns
            
            x = start_x + col * (button_width + button_spacing)
            y = start_y + row * (button_height + button_spacing)
            
            # Level number display
            level_num = i + 1
            
            # Check if level is completed
            level_stats = self.all_stats.get(str(level['path']), {})
            is_completed = level_stats.get('completed', False)
            
            # Button color based on completion
            btn_color = (50, 150, 50) if is_completed else (100, 100, 100)
            hover_color = (70, 180, 70) if is_completed else (130, 130, 130)
            
            btn = Button(screen, x, y, button_width, button_height, False,
                        text=str(level_num),
                        onClick=lambda path=level['path']: self.select_level(path),
                        font=getFont(32), radius=10,
                        inactiveColour=btn_color,
                        hoverColour=hover_color)
            self.buttons.append(btn)
        
        # Back button
        self.back_btn = Button(screen, 20, screen.get_height() - 70, 150, 50, False,
                              text="Back", onClick=self.go_back,
                              font=getFont(24), radius=10)

    def select_world(self, world_name):
        """Select a world and show its levels"""
        self.selected_world = world_name
        self.show_world_select = False
        self.setup_level_buttons(self.screen)

    def select_level(self, level_path):
        """Load and start the selected level"""
        from screens.GameScreen import GameScreen
        # Pass the level path to GameScreen
        GameScreen(self.screen, "Game", level_path=level_path)

    def go_back(self):
        """Go back to previous screen"""
        if not self.show_world_select and self.selected_world:
            # Go back to world selection
            self.show_world_select = True
            self.selected_world = None
            self.setup_world_buttons(self.screen)
        else:
            # Go back to title screen
            from screens.TitleScreen import TitleScreen
            TitleScreen(self.screen, "Title Screen")

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                exit()
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.go_back()
        
        # Background
        self.screen.fill((30, 30, 50))
        
        # Title
        if self.show_world_select:
            title_text = "Select World"
        else:
            title_text = f"Select Level - {self.selected_world.replace('_', ' ').title()}"
        
        title_font = getFont(60)
        title_surface = title_font.render(title_text, True, (255, 255, 255))
        title_width = title_surface.get_width()
        self.screen.blit(title_surface, ((self.screen.get_width() - title_width) / 2, 50))
        
        # Draw buttons
        for btn in self.buttons:
            btn.draw()
        
        # Draw stats under level buttons (only in level select mode)
        if not self.show_world_select and hasattr(self, 'all_stats'):
            self.draw_level_stats()
        
        if self.back_btn:
            self.back_btn.draw()
        
        # Update widgets
        pygame_widgets.update(pygame.event.get())
        
        # Update Screen
        pygame.display.update()
    
    def draw_level_stats(self):
        """Draw stats under each level button"""
        button_width = 180
        button_height = 100
        button_spacing = 20
        columns = 5
        start_x = (self.screen.get_width() - (columns * button_width + (columns - 1) * button_spacing)) / 2
        start_y = 150
        
        stat_font = getFont(14)
        
        for i, level in enumerate(self.levels):
            row = i // columns
            col = i % columns
            
            x = start_x + col * (button_width + button_spacing)
            y = start_y + row * (button_height + button_spacing)
            
            # Get stats for this level
            level_stats = self.all_stats.get(str(level['path']), {})
            
            if level_stats.get('completed', False):
                # Draw time
                best_time = level_stats.get('best_time', 0)
                time_text = stat_font.render(f"⏱ {format_time(best_time)}", True, (200, 200, 200))
                self.screen.blit(time_text, (x + 10, y + 45))
                
                # Draw attempts
                best_attempts = level_stats.get('best_attempts', 0)
                attempts_text = stat_font.render(f"💀 {best_attempts}", True, (200, 200, 200))
                self.screen.blit(attempts_text, (x + 10, y + 65))
                
                # Draw checkmark
                check_font = getFont(20)
                check_text = check_font.render("✓", True, (100, 255, 100))
                self.screen.blit(check_text, (x + button_width - 30, y + 10))
            else:
                # Not completed - show placeholder
                not_completed = stat_font.render("Not completed", True, (120, 120, 120))
                self.screen.blit(not_completed, (x + 10, y + 55))
