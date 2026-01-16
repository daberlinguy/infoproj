"""
Level Editor - A standalone program to create and edit levels
"""
import pygame
import json
import os
import sys
from pathlib import Path

# Initialize pygame before importing any modules that use pygame
pygame.init()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skeletons.platform import Platform, Grid
from assets.assets import getFont, Texture
from leveleditor.json_utils import load_jsonc, save_json


def show_input_dialog(screen, font, prompt, default_text=""):
    """Simple text input dialog"""
    dialog_width = 500
    dialog_height = 150
    dialog_x = (screen.get_width() - dialog_width) // 2
    dialog_y = (screen.get_height() - dialog_height) // 2
    
    input_text = default_text
    active = True
    confirmed = False
    
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    confirmed = True
                    active = False
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    # Add character if it's printable
                    if event.unicode.isprintable():
                        input_text += event.unicode
        
        # Draw dialog
        screen.fill((30, 30, 50))
        
        # Dialog background
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(screen, (60, 60, 60), dialog_rect)
        pygame.draw.rect(screen, (200, 200, 200), dialog_rect, 2)
        
        # Prompt text
        prompt_surface = font.render(prompt, True, (255, 255, 255))
        screen.blit(prompt_surface, (dialog_x + 10, dialog_y + 10))
        
        # Input box
        input_box = pygame.Rect(dialog_x + 10, dialog_y + 50, dialog_width - 20, 40)
        pygame.draw.rect(screen, (80, 80, 80), input_box)
        pygame.draw.rect(screen, (150, 150, 150), input_box, 2)
        
        # Input text
        text_surface = font.render(input_text, True, (255, 255, 255))
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 10))
        
        # Instructions
        instructions = font.render("Press Enter to confirm, Esc to cancel", True, (180, 180, 180))
        screen.blit(instructions, (dialog_x + 10, dialog_y + 110))
        
        pygame.display.flip()
    
    return input_text if confirmed else None


def show_confirm_dialog(screen, font, message):
    """Simple yes/no confirmation dialog"""
    dialog_width = 400
    dialog_height = 120
    dialog_x = (screen.get_width() - dialog_width) // 2
    dialog_y = (screen.get_height() - dialog_height) // 2
    
    active = True
    result = None
    
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y or event.key == pygame.K_RETURN:
                    result = True
                    active = False
                elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                    result = False
                    active = False
        
        # Draw dialog
        screen.fill((30, 30, 50))
        
        # Dialog background
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(screen, (60, 60, 60), dialog_rect)
        pygame.draw.rect(screen, (200, 200, 200), dialog_rect, 2)
        
        # Message text
        msg_surface = font.render(message, True, (255, 255, 255))
        screen.blit(msg_surface, (dialog_x + 10, dialog_y + 20))
        
        # Instructions
        instructions = font.render("Press Y (Yes) or N (No)", True, (180, 180, 180))
        screen.blit(instructions, (dialog_x + 10, dialog_y + 70))
        
        pygame.display.flip()
    
    return result if result is not None else False


class BlockType:
    """Define different block types available in the editor"""
    NORMAL = "normal"
    DEATH = "death"
    SPAWN = "spawn"
    CHECKPOINT = "checkpoint"
    SLIPPERY = "slippery"
    FINISH = "finish"


class BlockData:
    """Represents a block in the editor"""
    def __init__(self, grid_x, grid_y, block_type=BlockType.NORMAL, color=None, texture_name=None):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.block_type = block_type
        self.color = color or self.get_default_color()
        self.texture_name = texture_name
    
    def get_default_color(self):
        """Get default color based on block type"""
        colors = {
            BlockType.NORMAL: (100, 100, 100),
            BlockType.DEATH: (255, 0, 0),
            BlockType.SPAWN: (0, 255, 0),
            BlockType.CHECKPOINT: (255, 255, 0),
            BlockType.SLIPPERY: (100, 200, 255),
            BlockType.FINISH: (255, 215, 0)
        }
        return colors.get(self.block_type, (100, 100, 100))
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "grid_x": self.grid_x,
            "grid_y": self.grid_y,
            "type": self.block_type,
            "color": list(self.color),
            "texture": self.texture_name
        }
    
    @staticmethod
    def from_dict(data):
        """Create BlockData from dictionary"""
        return BlockData(
            data["grid_x"],
            data["grid_y"],
            data.get("type", BlockType.NORMAL),
            tuple(data.get("color", [100, 100, 100])),
            data.get("texture")
        )


class BlockSelector:
    """UI Panel for selecting block types"""
    def __init__(self, x, y, width, height, grid_size):
        self.rect = pygame.Rect(x, y, width, height)
        self.grid_size = grid_size
        self.selected_type = BlockType.NORMAL
        self.selected_color = (100, 100, 100)
        self.selected_texture = None
        
        # Texture pagination
        self.texture_page = 0
        self.textures_per_page = 25
        # TO ADD MORE TEXTURES: 
        # 1. Add texture to Texture class in assets.py (e.g., Texture.WOOD = ...)
        # 2. Add to this list as ("NAME", Texture.NAME)
        # 3. Textures will automatically paginate (25 per page supported)
        self.available_textures = [
            ("GRASS", Texture.GRASS),
            ("DIRT", Texture.DIRT),
            ("ICE", Texture.ICE),
            ("STONE", Texture.STONE),
            ("GOLD_BLOCK", Texture.GOLD_BLOCK),
        ]
        
        # Block type buttons
        self.block_types = [
            None,  # None = Don't place blocks
            BlockType.NORMAL,
            BlockType.DEATH,
            BlockType.SPAWN,
            BlockType.CHECKPOINT,
            BlockType.SLIPPERY,
            BlockType.FINISH
        ]
        
        self.type_buttons = []
        button_width = 80
        button_height = 40
        button_spacing = 10
        start_x = x + 10
        current_y = y + 50
        
        for block_type in self.block_types:
            button_rect = pygame.Rect(start_x, current_y, button_width, button_height)
            self.type_buttons.append((block_type, button_rect))
            start_x += button_width + button_spacing
            if start_x + button_width > x + width - 10:
                start_x = x + 10
                current_y += button_height + button_spacing
        
        # Predefined colors
        self.preset_colors = [
            (100, 100, 100),  # Gray
            (139, 69, 19),    # Brown
            (34, 139, 34),    # Green
            (169, 169, 169),  # Light Gray
            (255, 140, 0),    # Orange
            (0, 0, 255),      # Blue
            (255, 255, 255),  # White
            (0, 0, 0),        # Black
        ]
        
        self.color_buttons = []
        color_size = 30
        color_spacing = 5
        start_x = x + 10
        current_y = current_y + button_height + button_spacing + 20
        
        for color in self.preset_colors:
            color_rect = pygame.Rect(start_x, current_y, color_size, color_size)
            self.color_buttons.append((color, color_rect))
            start_x += color_size + color_spacing
            if start_x + color_size > x + width - 10:
                start_x = x + 10
                current_y += color_size + color_spacing
        
        # Texture selector area
        self.texture_area_y = current_y + color_size + color_spacing + 20
        self.texture_buttons = []
        self.prev_page_btn = None
        self.next_page_btn = None
    
    def draw(self, screen, font):
        """Draw the block selector panel"""
        # Background
        pygame.draw.rect(screen, (40, 40, 40), self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)
        
        # Title
        title = font.render("Block Selector", True, (255, 255, 255))
        screen.blit(title, (self.rect.x + 10, self.rect.y + 10))
        
        # Block type buttons
        for block_type, button_rect in self.type_buttons:
            # Button background
            color = (70, 70, 200) if block_type == self.selected_type else (60, 60, 60)
            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, (200, 200, 200), button_rect, 2)
            
            # Button text
            if block_type is None:
                text = font.render("NONE", True, (255, 255, 255))
            else:
                text = font.render(block_type.upper(), True, (255, 255, 255))
            text_rect = text.get_rect(center=button_rect.center)
            screen.blit(text, text_rect)
        
        # Color selector title
        color_title = font.render("Color:", True, (255, 255, 255))
        screen.blit(color_title, (self.rect.x + 10, self.color_buttons[0][1].y - 25))
        
        # Color buttons
        for color, color_rect in self.color_buttons:
            pygame.draw.rect(screen, color, color_rect)
            if color == self.selected_color:
                pygame.draw.rect(screen, (255, 255, 0), color_rect, 3)
            else:
                pygame.draw.rect(screen, (200, 200, 200), color_rect, 1)
        
        # Texture selector
        self.texture_buttons.clear()
        texture_title = font.render("Texture:", True, (255, 255, 255))
        screen.blit(texture_title, (self.rect.x + 10, self.texture_area_y))
        
        # Calculate page info
        total_pages = (len(self.available_textures) + self.textures_per_page - 1) // self.textures_per_page
        start_idx = self.texture_page * self.textures_per_page
        end_idx = min(start_idx + self.textures_per_page, len(self.available_textures))
        
        # Draw textures for current page
        texture_x = self.rect.x + 100
        texture_y = self.texture_area_y
        texture_size = 40
        texture_spacing = 10
        
        for i in range(start_idx, end_idx):
            tex_name, tex_surface = self.available_textures[i]
            tex_rect = pygame.Rect(texture_x, texture_y, texture_size, texture_size)
            
            # Draw texture
            if tex_surface:
                scaled_tex = pygame.transform.scale(tex_surface, (texture_size, texture_size))
                screen.blit(scaled_tex, tex_rect)
            else:
                pygame.draw.rect(screen, (80, 80, 80), tex_rect)
            
            # Highlight if selected
            if self.selected_texture == tex_name:
                pygame.draw.rect(screen, (255, 255, 0), tex_rect, 3)
            else:
                pygame.draw.rect(screen, (200, 200, 200), tex_rect, 2)
            
            # Draw name below
            name_text = font.render(tex_name, True, (255, 255, 255))
            name_rect = name_text.get_rect(centerx=tex_rect.centerx, top=tex_rect.bottom + 2)
            screen.blit(name_text, name_rect)
            
            self.texture_buttons.append((tex_name, tex_rect))
            texture_x += texture_size + texture_spacing
        
        # "None" texture option
        none_rect = pygame.Rect(texture_x, texture_y, texture_size, texture_size)
        pygame.draw.rect(screen, (80, 80, 80), none_rect)
        pygame.draw.line(screen, (255, 0, 0), none_rect.topleft, none_rect.bottomright, 2)
        pygame.draw.line(screen, (255, 0, 0), none_rect.topright, none_rect.bottomleft, 2)
        if self.selected_texture is None:
            pygame.draw.rect(screen, (255, 255, 0), none_rect, 3)
        else:
            pygame.draw.rect(screen, (200, 200, 200), none_rect, 2)
        none_text = font.render("NONE", True, (255, 255, 255))
        none_text_rect = none_text.get_rect(centerx=none_rect.centerx, top=none_rect.bottom + 2)
        screen.blit(none_text, none_text_rect)
        self.texture_buttons.append((None, none_rect))
        
        # Pagination buttons (if more than one page)
        if total_pages > 1:
            btn_y = texture_y + texture_size + 25
            self.prev_page_btn = pygame.Rect(self.rect.x + 100, btn_y, 60, 30)
            self.next_page_btn = pygame.Rect(self.rect.x + 170, btn_y, 60, 30)
            
            # Previous button
            prev_color = (60, 60, 60) if self.texture_page == 0 else (80, 120, 80)
            pygame.draw.rect(screen, prev_color, self.prev_page_btn)
            pygame.draw.rect(screen, (200, 200, 200), self.prev_page_btn, 2)
            prev_text = font.render("<", True, (255, 255, 255))
            screen.blit(prev_text, prev_text.get_rect(center=self.prev_page_btn.center))
            
            # Next button
            next_color = (60, 60, 60) if self.texture_page >= total_pages - 1 else (80, 120, 80)
            pygame.draw.rect(screen, next_color, self.next_page_btn)
            pygame.draw.rect(screen, (200, 200, 200), self.next_page_btn, 2)
            next_text = font.render(">", True, (255, 255, 255))
            screen.blit(next_text, next_text.get_rect(center=self.next_page_btn.center))
            
            # Page indicator
            page_text = font.render(f"{self.texture_page + 1}/{total_pages}", True, (255, 255, 255))
            screen.blit(page_text, (self.rect.x + 240, btn_y + 5))
    
    def handle_click(self, pos):
        """Handle mouse clicks on the selector"""
        # Check block type buttons
        for block_type, button_rect in self.type_buttons:
            if button_rect.collidepoint(pos):
                self.selected_type = block_type
                return True
        
        # Check color buttons
        for color, color_rect in self.color_buttons:
            if color_rect.collidepoint(pos):
                self.selected_color = color
                return True
        
        # Check texture buttons
        for tex_name, tex_rect in self.texture_buttons:
            if tex_rect.collidepoint(pos):
                self.selected_texture = tex_name
                return True
        
        # Check pagination buttons
        total_pages = (len(self.available_textures) + self.textures_per_page - 1) // self.textures_per_page
        if self.prev_page_btn and self.prev_page_btn.collidepoint(pos) and self.texture_page > 0:
            self.texture_page -= 1
            return True
        if self.next_page_btn and self.next_page_btn.collidepoint(pos) and self.texture_page < total_pages - 1:
            self.texture_page += 1
            return True
        
        return False


class LevelEditor:
    """Main level editor class"""
    def __init__(self, width=1280, height=720, grid_size=32, return_to_game=False):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.return_to_game = return_to_game  # If True, return to game instead of quitting
        
        # UI Layout
        self.selector_height = 200
        self.grid_area_height = height - self.selector_height
        
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Level Editor")
        
        # Initialize textures now that display mode is set
        Texture.init_textures()
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Grid
        self.grid = Grid(cell_size=grid_size, color=(80, 80, 80), line_width=1)
        self.grid.visible = True
        
        # Page system
        self.current_page = 0
        self.max_pages = 10  # Support up to 10 pages
        self.cells_per_page = width // grid_size  # 40 cells per page at 1280px
        
        # Blocks in the level
        self.blocks = {}  # Key: (grid_x, grid_y), Value: BlockData
        
        # Block selector
        self.selector = BlockSelector(0, self.grid_area_height, width, self.selector_height, grid_size)
        
        # Drawing state
        self.is_drawing = False
        self.is_erasing = False
        self.last_drawn_cell = None
        
        # Selection state
        self.is_selecting = False
        self.selection_start = None
        self.selection_end = None
        self.selected_blocks = set()
        
        # Level metadata
        self.level_name = "Untitled Level"
        self.level_filename = None
        self.world_name = "world1"
        self.spawn_point = (1, 14)  # Grid coordinates
        self.background_color = (128, 0, 128)  # Purple
        
        # UI state
        self.show_start_screen = True
        self.show_level_list = False
        self.level_list = []
        self.level_list_scroll = 0
        
        # Fonts
        try:
            self.font = getFont(20)
            self.small_font = getFont(16)
        except:
            self.font = pygame.font.Font(None, 20)
            self.small_font = pygame.font.Font(None, 16)
        
        # Context menu for right-click
        self.context_menu_open = False
        self.context_menu_pos = None
        self.context_menu_block = None
    
    def grid_to_pixel(self, grid_x, grid_y):
        """Convert grid coordinates to pixel coordinates (with page offset)"""
        # Adjust for current page
        screen_grid_x = grid_x - (self.current_page * self.cells_per_page)
        return screen_grid_x * self.grid_size, grid_y * self.grid_size
    
    def pixel_to_grid(self, pixel_x, pixel_y):
        """Convert pixel coordinates to grid coordinates (with page offset)"""
        # Add current page offset to get absolute grid position
        grid_x = pixel_x // self.grid_size + (self.current_page * self.cells_per_page)
        grid_y = pixel_y // self.grid_size
        return grid_x, grid_y
    
    def is_block_on_current_page(self, grid_x):
        """Check if a block's x position is on the current page"""
        page_start = self.current_page * self.cells_per_page
        page_end = page_start + self.cells_per_page
        return page_start <= grid_x < page_end
    
    def add_block(self, grid_x, grid_y):
        """Add a block at the specified grid position"""
        if grid_y >= self.grid_area_height // self.grid_size:
            return  # Don't draw in selector area
        
        # Don't place if block type is None
        if self.selector.selected_type is None:
            return
        
        # Special handling for unique block types
        block_type = self.selector.selected_type
        
        # For SPAWN blocks: only allow one spawn point, remove old one
        if block_type == BlockType.SPAWN:
            # Remove any existing spawn blocks
            spawn_blocks = [(k, v) for k, v in self.blocks.items() if v.block_type == BlockType.SPAWN]
            for key, _ in spawn_blocks:
                del self.blocks[key]
            # Update spawn point
            self.spawn_point = (grid_x, grid_y)
        
        # For FINISH blocks: only allow one finish point, remove old one
        if block_type == BlockType.FINISH:
            # Remove any existing finish blocks
            finish_blocks = [(k, v) for k, v in self.blocks.items() if v.block_type == BlockType.FINISH]
            for key, _ in finish_blocks:
                del self.blocks[key]
        
        key = (grid_x, grid_y)
        self.blocks[key] = BlockData(
            grid_x, grid_y,
            self.selector.selected_type,
            self.selector.selected_color,
            self.selector.selected_texture
        )
    
    def remove_block(self, grid_x, grid_y):
        """Remove a block at the specified grid position"""
        key = (grid_x, grid_y)
        if key in self.blocks:
            del self.blocks[key]
    
    def get_block(self, grid_x, grid_y):
        """Get block at specified grid position"""
        return self.blocks.get((grid_x, grid_y))
    
    def handle_events(self):
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                # Left click
                if event.button == 1:
                    # Check if clicking on level list (highest priority when visible)
                    if self.show_level_list:
                        if self.handle_level_list_click(pos):
                            self.show_level_list = False
                            self.show_start_screen = False  # Also close start screen
                        # If clicked outside level list, close it
                        elif hasattr(self, 'level_list_rect') and not self.level_list_rect.collidepoint(pos):
                            self.show_level_list = False
                    # Check if clicking on start screen
                    elif self.show_start_screen:
                        if self.handle_start_screen_click(pos):
                            self.show_start_screen = False
                    # Check if clicking on context menu
                    elif self.context_menu_open:
                        if self.handle_context_menu_click(pos):
                            self.context_menu_open = False
                        else:
                            self.context_menu_open = False
                    # Check if clicking on page navigation buttons
                    elif hasattr(self, 'prev_page_btn') and self.prev_page_btn.collidepoint(pos):
                        self.current_page = max(self.current_page - 1, 0)
                    elif hasattr(self, 'next_page_btn') and self.next_page_btn.collidepoint(pos):
                        self.current_page = min(self.current_page + 1, self.max_pages - 1)
                    # Check if clicking in selector area
                    elif self.selector.rect.collidepoint(pos):
                        self.selector.handle_click(pos)
                    # Check if holding Ctrl for selection mode
                    elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.is_selecting = True
                        grid_x, grid_y = self.pixel_to_grid(pos[0], pos[1])
                        self.selection_start = (grid_x, grid_y)
                        self.selection_end = (grid_x, grid_y)
                        self.update_selection()
                    else:
                        # Start drawing in grid area
                        self.is_drawing = True
                        grid_x, grid_y = self.pixel_to_grid(pos[0], pos[1])
                        self.add_block(grid_x, grid_y)
                        self.last_drawn_cell = (grid_x, grid_y)
                
                # Middle click or Shift+Left click to erase
                elif event.button == 2 or (event.button == 1 and pygame.key.get_mods() & pygame.KMOD_SHIFT):
                    self.is_erasing = True
                    grid_x, grid_y = self.pixel_to_grid(pos[0], pos[1])
                    self.remove_block(grid_x, grid_y)
                
                # Right click for context menu
                elif event.button == 3:
                    if self.context_menu_open:
                        # Check if clicking on menu item
                        if self.handle_context_menu_click(pos):
                            self.context_menu_open = False
                    elif not self.selector.rect.collidepoint(pos):
                        grid_x, grid_y = self.pixel_to_grid(pos[0], pos[1])
                        block = self.get_block(grid_x, grid_y)
                        if block:
                            self.context_menu_open = True
                            self.context_menu_pos = pos
                            self.context_menu_block = block
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_drawing = False
                    self.is_selecting = False
                    self.last_drawn_cell = None
                elif event.button == 2:
                    self.is_erasing = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.is_selecting:
                    pos = pygame.mouse.get_pos()
                    if not self.selector.rect.collidepoint(pos):
                        grid_x, grid_y = self.pixel_to_grid(pos[0], pos[1])
                        self.selection_end = (grid_x, grid_y)
                        self.update_selection()
                elif self.is_drawing:
                    pos = pygame.mouse.get_pos()
                    if not self.selector.rect.collidepoint(pos):
                        grid_x, grid_y = self.pixel_to_grid(pos[0], pos[1])
                        if (grid_x, grid_y) != self.last_drawn_cell:
                            self.add_block(grid_x, grid_y)
                            self.last_drawn_cell = (grid_x, grid_y)
                elif self.is_erasing:
                    pos = pygame.mouse.get_pos()
                    if not self.selector.rect.collidepoint(pos):
                        grid_x, grid_y = self.pixel_to_grid(pos[0], pos[1])
                        self.remove_block(grid_x, grid_y)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.save_level()
                elif event.key == pygame.K_o and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.show_level_list = True
                    self.load_level_list()
                elif event.key == pygame.K_n and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.new_level()
                elif event.key == pygame.K_m and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.edit_metadata()
                elif event.key == pygame.K_l:
                    self.show_level_list = not self.show_level_list
                    if self.show_level_list:
                        self.load_level_list()
                elif event.key == pygame.K_g:
                    self.grid.toggle()
                elif event.key == pygame.K_DELETE:
                    self.delete_selected_blocks()
                # Page navigation
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if not (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        self.current_page = min(self.current_page + 1, self.max_pages - 1)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if not (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        self.current_page = max(self.current_page - 1, 0)
                elif event.key == pygame.K_HOME:
                    self.current_page = 0
                elif event.key == pygame.K_END:
                    # Go to last page with blocks
                    max_block_page = 0
                    for (gx, gy) in self.blocks.keys():
                        block_page = gx // self.cells_per_page
                        max_block_page = max(max_block_page, block_page)
                    self.current_page = max_block_page
                elif event.key == pygame.K_ESCAPE:
                    if self.context_menu_open:
                        self.context_menu_open = False
                    elif self.show_level_list:
                        self.show_level_list = False
                    elif self.selected_blocks:
                        self.selected_blocks.clear()
                    else:
                        # Return to start screen
                        self.show_start_screen = True
    
    def draw(self):
        """Draw everything"""
        # Show start screen if active
        if self.show_start_screen:
            self.draw_start_screen()
            # Draw level list on top of start screen if open
            if self.show_level_list:
                self.draw_level_list()
            pygame.display.flip()
            return
        
        # Background
        self.screen.fill(self.background_color)
        
        # Grid (only in grid area)
        grid_surface = pygame.Surface((self.width, self.grid_area_height))
        grid_surface.fill(self.background_color)
        
        # Draw grid
        if self.grid.visible:
            for x in range(0, self.width + 1, self.grid_size):
                pygame.draw.line(grid_surface, self.grid.color, (x, 0), (x, self.grid_area_height), 1)
            for y in range(0, self.grid_area_height + 1, self.grid_size):
                pygame.draw.line(grid_surface, self.grid.color, (0, y), (self.width, y), 1)
        
        # Draw blocks (only those on current page)
        for block in self.blocks.values():
            # Skip blocks not on current page
            if not self.is_block_on_current_page(block.grid_x):
                continue
            
            x, y = self.grid_to_pixel(block.grid_x, block.grid_y)
            rect = pygame.Rect(x, y, self.grid_size, self.grid_size)
            
            # Draw texture if available, otherwise draw color
            if block.texture_name and hasattr(Texture, block.texture_name):
                texture = getattr(Texture, block.texture_name)
                if texture:
                    scaled_texture = pygame.transform.scale(texture, (self.grid_size, self.grid_size))
                    grid_surface.blit(scaled_texture, rect)
                else:
                    pygame.draw.rect(grid_surface, block.color, rect)
            else:
                pygame.draw.rect(grid_surface, block.color, rect)
            
            pygame.draw.rect(grid_surface, (0, 0, 0), rect, 1)
            
            # Draw type indicator (overlaid on texture)
            if block.block_type == BlockType.DEATH:
                pygame.draw.line(grid_surface, (200, 0, 0), rect.topleft, rect.bottomright, 3)
                pygame.draw.line(grid_surface, (200, 0, 0), rect.topright, rect.bottomleft, 3)
            elif block.block_type == BlockType.SPAWN:
                text = self.small_font.render("S", True, (0, 255, 0))
                # Draw text with outline for visibility
                for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                    outline = self.small_font.render("S", True, (0, 0, 0))
                    grid_surface.blit(outline, (x + self.grid_size // 2 - 5 + dx, y + self.grid_size // 2 - 8 + dy))
                grid_surface.blit(text, (x + self.grid_size // 2 - 5, y + self.grid_size // 2 - 8))
            elif block.block_type == BlockType.CHECKPOINT:
                center_x = x + self.grid_size // 2
                top_y = y + 5
                pygame.draw.line(grid_surface, (255, 255, 0), (center_x, top_y), (center_x, y + self.grid_size - 5), 3)
                pygame.draw.polygon(grid_surface, (255, 255, 0), [(center_x, top_y), (center_x + 10, top_y + 5), (center_x, top_y + 10)])
            elif block.block_type == BlockType.FINISH:
                text = self.small_font.render("F", True, (255, 215, 0))
                # Draw text with outline for visibility
                for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                    outline = self.small_font.render("F", True, (0, 0, 0))
                    grid_surface.blit(outline, (x + self.grid_size // 2 - 5 + dx, y + self.grid_size // 2 - 8 + dy))
                grid_surface.blit(text, (x + self.grid_size // 2 - 5, y + self.grid_size // 2 - 8))
        
        # Draw selection overlay (only for blocks on current page)
        for grid_pos in self.selected_blocks:
            if not self.is_block_on_current_page(grid_pos[0]):
                continue
            sx, sy = self.grid_to_pixel(grid_pos[0], grid_pos[1])
            selection_rect = pygame.Rect(sx, sy, self.grid_size, self.grid_size)
            # Draw semi-transparent overlay
            s = pygame.Surface((self.grid_size, self.grid_size))
            s.set_alpha(100)
            s.fill((0, 150, 255))
            grid_surface.blit(s, (sx, sy))
            pygame.draw.rect(grid_surface, (0, 200, 255), selection_rect, 2)
        
        self.screen.blit(grid_surface, (0, 0))
        
        # Draw spawn point indicator (only if on current page)
        if self.is_block_on_current_page(self.spawn_point[0]):
            spawn_x, spawn_y = self.grid_to_pixel(self.spawn_point[0], self.spawn_point[1])
            spawn_rect = pygame.Rect(spawn_x, spawn_y, self.grid_size, self.grid_size)
            pygame.draw.rect(self.screen, (0, 255, 0), spawn_rect, 3)
        
        # Draw selector panel
        self.selector.draw(self.screen, self.font)
        
        # Draw context menu if open
        if self.context_menu_open and self.context_menu_block:
            self.draw_context_menu()
        
        # Draw page indicator and UI info
        page_info = f"Page: {self.current_page + 1}/{self.max_pages} (Arrow keys to navigate)"
        
        # Get level stats
        stats = self.get_level_stats()
        spawn_status = "✓" if stats['spawn_count'] > 0 else "✗"
        finish_status = "✓" if stats['finish_count'] > 0 else "✗"
        
        info_texts = [
            page_info,
            f"Level: {self.level_name} | File: {self.level_filename or 'New'}",
            f"Blocks: {stats['total_blocks']} | Selected: {len(self.selected_blocks)}",
            f"Spawn: {spawn_status} | Finish: {finish_status} | Checkpoints: {stats['checkpoint_count']} | Deaths: {stats['death_count']}",
            "Ctrl+S: Save | Ctrl+O/L: Load | Ctrl+N: New | Ctrl+M: Edit Metadata",
            "Left Click: Draw | Ctrl+Drag: Select | Del: Delete Selected",
            "Middle/Shift+Click: Erase | Right Click: Edit | G: Toggle Grid"
        ]
        
        y_offset = 5
        for text in info_texts:
            surface = self.small_font.render(text, True, (255, 255, 255))
            # Add background for readability
            bg_rect = surface.get_rect(topleft=(5, y_offset))
            bg_rect.inflate_ip(10, 4)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
            self.screen.blit(surface, (5, y_offset))
            y_offset += 20
        
        # Draw page navigation buttons
        self.draw_page_navigation()
        
        # Draw level list if open
        if self.show_level_list:
            self.draw_level_list()
        
        pygame.display.flip()
    
    def draw_page_navigation(self):
        """Draw page navigation buttons"""
        btn_width = 50
        btn_height = 40
        margin = 10
        
        # Previous page button
        prev_btn_rect = pygame.Rect(self.width - 2 * btn_width - 2 * margin, margin, btn_width, btn_height)
        prev_color = (60, 60, 60) if self.current_page == 0 else (80, 120, 80)
        pygame.draw.rect(self.screen, prev_color, prev_btn_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), prev_btn_rect, 2)
        prev_text = self.font.render("<", True, (255, 255, 255))
        self.screen.blit(prev_text, prev_text.get_rect(center=prev_btn_rect.center))
        
        # Next page button
        next_btn_rect = pygame.Rect(self.width - btn_width - margin, margin, btn_width, btn_height)
        next_color = (60, 60, 60) if self.current_page >= self.max_pages - 1 else (80, 120, 80)
        pygame.draw.rect(self.screen, next_color, next_btn_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), next_btn_rect, 2)
        next_text = self.font.render(">", True, (255, 255, 255))
        self.screen.blit(next_text, next_text.get_rect(center=next_btn_rect.center))
        
        # Store button rects for click handling
        self.prev_page_btn = prev_btn_rect
        self.next_page_btn = next_btn_rect
    
    def draw_context_menu(self):
        """Draw context menu for block editing"""
        menu_width = 200
        menu_x = self.context_menu_pos[0]
        menu_y = self.context_menu_pos[1]
        
        # Calculate menu height based on options
        options = ["Change Type", "Change Color", "Change Texture", "Delete Block", "Close"]
        menu_height = 10 + len(options) * 30 + 10
        
        # Keep menu on screen
        if menu_x + menu_width > self.width:
            menu_x = self.width - menu_width
        if menu_y + menu_height > self.height:
            menu_y = self.height - menu_height
        
        self.context_menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(self.screen, (50, 50, 50), self.context_menu_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), self.context_menu_rect, 2)
        
        # Menu options with clickable areas
        self.context_menu_items = []
        
        y = menu_y + 10
        for i, option in enumerate(options):
            item_rect = pygame.Rect(menu_x + 5, y, menu_width - 10, 28)
            self.context_menu_items.append((option, item_rect))
            
            # Highlight on hover
            mouse_pos = pygame.mouse.get_pos()
            if item_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (80, 80, 80), item_rect)
            
            text = self.small_font.render(option, True, (255, 255, 255))
            self.screen.blit(text, (menu_x + 10, y + 5))
            y += 30
    
    def handle_context_menu_click(self, pos):
        """Handle clicks on context menu items"""
        if not hasattr(self, 'context_menu_items'):
            return False
        
        for option, rect in self.context_menu_items:
            if rect.collidepoint(pos):
                if option == "Change Type":
                    self.cycle_block_type()
                elif option == "Change Color":
                    self.cycle_block_color()
                elif option == "Change Texture":
                    self.cycle_block_texture()
                elif option == "Delete Block":
                    self.delete_context_block()
                elif option == "Close":
                    pass  # Just close
                return True
        return False
    
    def cycle_block_type(self):
        """Cycle through block types for the selected block"""
        if self.context_menu_block:
            types = [BlockType.NORMAL, BlockType.DEATH, BlockType.SPAWN, 
                    BlockType.CHECKPOINT, BlockType.SLIPPERY, BlockType.FINISH]
            current_idx = types.index(self.context_menu_block.block_type) if self.context_menu_block.block_type in types else 0
            next_idx = (current_idx + 1) % len(types)
            self.context_menu_block.block_type = types[next_idx]
            self.context_menu_block.color = self.context_menu_block.get_default_color()
    
    def cycle_block_color(self):
        """Open input dialog for custom RGB color"""
        if self.context_menu_block:
            current_color = f"{self.context_menu_block.color[0]},{self.context_menu_block.color[1]},{self.context_menu_block.color[2]}"
            result = show_input_dialog(self.screen, self.small_font, "Enter RGB (e.g., 255,128,0):", current_color)
            if result:
                try:
                    parts = result.split(',')
                    if len(parts) == 3:
                        r = max(0, min(255, int(parts[0].strip())))
                        g = max(0, min(255, int(parts[1].strip())))
                        b = max(0, min(255, int(parts[2].strip())))
                        self.context_menu_block.color = (r, g, b)
                except ValueError:
                    pass  # Invalid input, keep current color
    
    def cycle_block_texture(self):
        """Open input dialog for texture name"""
        if self.context_menu_block:
            current = self.context_menu_block.texture_name if self.context_menu_block.texture_name else ""
            result = show_input_dialog(self.screen, self.small_font, "Enter texture (GRASS/ICE/STONE/GOLD_BLOCK) or leave empty:", current)
            if result is not None:  # None means canceled, empty string means no texture
                result = result.strip().upper()
                if result in ["", "GRASS", "ICE", "STONE", "GOLD_BLOCK"]:
                    self.context_menu_block.texture_name = result if result else None
                else:
                    # Invalid texture name, keep current
                    pass
    
    def delete_context_block(self):
        """Delete the block that was right-clicked"""
        if self.context_menu_block:
            key = (self.context_menu_block.grid_x, self.context_menu_block.grid_y)
            if key in self.blocks:
                del self.blocks[key]
    
    def update_selection(self):
        """Update selected blocks based on current selection rectangle"""
        if self.selection_start is None or self.selection_end is None:
            return
        
        self.selected_blocks.clear()
        
        # Get rectangle bounds
        min_x = min(self.selection_start[0], self.selection_end[0])
        max_x = max(self.selection_start[0], self.selection_end[0])
        min_y = min(self.selection_start[1], self.selection_end[1])
        max_y = max(self.selection_start[1], self.selection_end[1])
        
        # Add all blocks in rectangle to selection
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                if (x, y) in self.blocks:
                    self.selected_blocks.add((x, y))
    
    def delete_selected_blocks(self):
        """Delete all selected blocks"""
        for pos in self.selected_blocks:
            if pos in self.blocks:
                del self.blocks[pos]
        self.selected_blocks.clear()
    
    def save_level(self):
        """Save level to JSON file"""
        # Validate level before saving
        validation_errors = self.validate_level()
        if validation_errors:
            error_msg = "Level validation errors:\n" + "\n".join(validation_errors)
            print(error_msg)
            # Show error dialog
            show_confirm_dialog(self.screen, self.small_font, f"Warning: {validation_errors[0]}")
        
        # Ask for filename if not set
        if not self.level_filename:
            filename = show_input_dialog(self.screen, self.small_font, "Enter filename (e.g., level_1.json):", "level_new.json")
            if not filename:
                return  # Canceled
            if not filename.endswith('.json'):
                filename += '.json'
            self.level_filename = filename
        
        # Confirm save
        confirm_msg = f"Save as {self.level_filename}?"
        if not show_confirm_dialog(self.screen, self.small_font, confirm_msg):
            return
        
        # Group consecutive blocks into platforms
        platforms = self.group_blocks_into_platforms()
        
        level_data = {
            "name": self.level_name,
            "world": self.world_name,
            "spawn_point": list(self.spawn_point),
            "background_color": list(self.background_color),
            "grid_size": self.grid_size,
            "platforms": platforms
        }
        
        # Create directory if it doesn't exist
        level_dir = Path(__file__).parent.parent.parent.parent / "levels" / self.world_name
        level_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        filepath = level_dir / self.level_filename
        
        with open(filepath, 'w') as f:
            json.dump(level_data, f, indent=2)
        
        print(f"Level saved to: {filepath}")
    
    def validate_level(self):
        """Validate level has required elements"""
        errors = []
        
        # Check for spawn point
        has_spawn = any(b.block_type == BlockType.SPAWN for b in self.blocks.values())
        if not has_spawn:
            errors.append("No SPAWN block! Add a spawn point.")
        
        # Check for finish point
        has_finish = any(b.block_type == BlockType.FINISH for b in self.blocks.values())
        if not has_finish:
            errors.append("No FINISH block! Add a finish point.")
        
        # Count checkpoints
        checkpoint_count = sum(1 for b in self.blocks.values() if b.block_type == BlockType.CHECKPOINT)
        
        # Check spawn is before finish (x-coordinate)
        spawn_blocks = [b for b in self.blocks.values() if b.block_type == BlockType.SPAWN]
        finish_blocks = [b for b in self.blocks.values() if b.block_type == BlockType.FINISH]
        
        if spawn_blocks and finish_blocks:
            spawn_x = spawn_blocks[0].grid_x
            finish_x = finish_blocks[0].grid_x
            if spawn_x >= finish_x:
                errors.append("SPAWN should be before FINISH (left to right)")
        
        return errors
    
    def get_level_stats(self):
        """Get statistics about the level"""
        stats = {
            'total_blocks': len(self.blocks),
            'spawn_count': sum(1 for b in self.blocks.values() if b.block_type == BlockType.SPAWN),
            'finish_count': sum(1 for b in self.blocks.values() if b.block_type == BlockType.FINISH),
            'checkpoint_count': sum(1 for b in self.blocks.values() if b.block_type == BlockType.CHECKPOINT),
            'death_count': sum(1 for b in self.blocks.values() if b.block_type == BlockType.DEATH),
            'slippery_count': sum(1 for b in self.blocks.values() if b.block_type == BlockType.SLIPPERY),
        }
        return stats
    
    def group_blocks_into_platforms(self):
        """Group adjacent blocks into platforms for optimization"""
        platforms = []
        processed = set()
        
        for key, block in self.blocks.items():
            if key in processed:
                continue
            
            # Find all horizontally connected blocks of the same type and color
            platform_blocks = [block]
            processed.add(key)
            
            # Check right
            check_x = block.grid_x + 1
            while True:
                check_key = (check_x, block.grid_y)
                check_block = self.blocks.get(check_key)
                if (check_block and 
                    check_block.block_type == block.block_type and 
                    check_block.color == block.color):
                    platform_blocks.append(check_block)
                    processed.add(check_key)
                    check_x += 1
                else:
                    break
            
            # Create platform data
            min_x = min(b.grid_x for b in platform_blocks)
            max_x = max(b.grid_x for b in platform_blocks)
            
            platform = {
                "grid_x1": min_x,
                "grid_y1": block.grid_y,
                "grid_x2": max_x,
                "grid_y2": block.grid_y,
                "type": block.block_type,
                "color": list(block.color),
                "texture": block.texture_name
            }
            platforms.append(platform)
        
        return platforms
    
    def load_level(self, filepath=None):
        """Load level from JSON/JSONC file"""
        if filepath is None:
            # For now, load a default level
            level_dir = Path(__file__).parent.parent.parent.parent / "levels" / self.world_name
            json_files = list(level_dir.glob('*.json')) + list(level_dir.glob('*.jsonc'))
            if not json_files:
                print("No levels found")
                return
            filepath = json_files[0]
        
        try:
            level_data = load_jsonc(filepath)
            
            # Clear existing blocks
            self.blocks.clear()
            
            # Load metadata
            self.level_name = level_data.get("name", "Untitled")
            self.level_filename = filepath.name
            self.world_name = level_data.get("world", "world1")
            self.spawn_point = tuple(level_data.get("spawn_point", [1, 14]))
            self.background_color = tuple(level_data.get("background_color", [128, 0, 128]))
            
            # Load platforms
            for platform in level_data.get("platforms", []):
                # Check if it's the new format (grid_x1) or old format (x, y, w, h)
                if "grid_x1" in platform:
                    # New format - expand platform into individual blocks
                    for x in range(platform["grid_x1"], platform["grid_x2"] + 1):
                        for y in range(platform["grid_y1"], platform["grid_y2"] + 1):
                            block = BlockData(
                                x, y,
                                platform.get("type", BlockType.NORMAL),
                                tuple(platform.get("color", [100, 100, 100])),
                                platform.get("texture")
                            )
                            self.blocks[(x, y)] = block
                elif "x" in platform:
                    # Old format - convert pixel coordinates to grid (ignore for now)
                    print(f"Warning: Old format level detected. Skipping platform at ({platform['x']}, {platform['y']})")
                    # Could add conversion logic here if needed
            
            print(f"Level loaded from: {filepath}")
        except Exception as e:
            print(f"Error loading level: {e}")
            import traceback
            traceback.print_exc()
    
    def new_level(self):
        """Create a new empty level"""
        self.blocks.clear()
        self.level_name = "Untitled Level"
        self.level_filename = None
        self.spawn_point = (1, 14)
        self.background_color = (128, 0, 128)
    
    def load_level_list(self):
        """Load list of available levels"""
        self.level_list.clear()
        level_dir = Path(__file__).parent.parent.parent.parent / "levels"
        
        if level_dir.exists():
            for world_dir in sorted(level_dir.iterdir()):
                if world_dir.is_dir():
                    level_files = sorted(list(world_dir.glob('*.json')) + list(world_dir.glob('*.jsonc')))
                    for level_file in level_files:
                        try:
                            level_data = load_jsonc(level_file)
                            self.level_list.append({
                                'name': level_data.get('name', level_file.stem),
                                'world': world_dir.name,
                                'path': level_file,
                                'filename': level_file.name
                            })
                        except:
                            self.level_list.append({
                                'name': level_file.stem,
                                'world': world_dir.name,
                                'path': level_file,
                                'filename': level_file.name
                            })
    
    def draw_level_list(self):
        """Draw the level list overlay"""
        list_width = 600
        list_height = 500
        list_x = (self.width - list_width) // 2
        list_y = (self.height - list_height) // 2
        
        # Store rect for click detection
        self.level_list_rect = pygame.Rect(list_x, list_y, list_width, list_height)
        
        # Background
        pygame.draw.rect(self.screen, (40, 40, 40), self.level_list_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), self.level_list_rect, 3)
        
        # Title
        title = self.font.render("Select Level to Load", True, (255, 255, 255))
        self.screen.blit(title, (list_x + 20, list_y + 10))
        
        # Instructions
        inst = self.small_font.render("Click level to load, ESC to cancel", True, (180, 180, 180))
        self.screen.blit(inst, (list_x + 20, list_y + 40))
        
        # Level items
        self.level_list_items = []
        item_y = list_y + 70
        item_height = 30
        visible_items = min(12, len(self.level_list))
        
        for i in range(min(visible_items, len(self.level_list))):
            level = self.level_list[i + self.level_list_scroll]
            item_rect = pygame.Rect(list_x + 10, item_y, list_width - 20, item_height)
            
            # Highlight on hover
            mouse_pos = pygame.mouse.get_pos()
            if item_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (70, 70, 70), item_rect)
            else:
                pygame.draw.rect(self.screen, (50, 50, 50), item_rect)
            
            pygame.draw.rect(self.screen, (150, 150, 150), item_rect, 1)
            
            # Level info
            name_text = self.small_font.render(f"{level['name']}", True, (255, 255, 255))
            self.screen.blit(name_text, (list_x + 15, item_y + 2))
            
            file_text = self.small_font.render(f"{level['world']}/{level['filename']}", True, (180, 180, 180))
            self.screen.blit(file_text, (list_x + 15, item_y + 16))
            
            self.level_list_items.append((level, item_rect))
            item_y += item_height + 5
    
    def handle_level_list_click(self, pos):
        """Handle clicks on level list"""
        if hasattr(self, 'level_list_items'):
            for level, rect in self.level_list_items:
                if rect.collidepoint(pos):
                    self.load_level(level['path'])
                    self.show_start_screen = False  # Close start screen too
                    return True
        return False
    
    def edit_metadata(self):
        """Edit level metadata"""
        # Edit level name
        new_name = show_input_dialog(self.screen, self.small_font, "Enter level name:", self.level_name)
        if new_name:
            self.level_name = new_name
        
        # Edit filename
        if self.level_filename:
            new_filename = show_input_dialog(self.screen, self.small_font, "Enter filename:", self.level_filename)
            if new_filename:
                if not new_filename.endswith('.json'):
                    new_filename += '.json'
                self.level_filename = new_filename
        
        # Edit world
        new_world = show_input_dialog(self.screen, self.small_font, "Enter world name:", self.world_name)
        if new_world:
            self.world_name = new_world
    
    def draw_start_screen(self):
        """Draw the start screen for creating/loading levels"""
        self.screen.fill((30, 30, 50))
        
        # Title
        title = self.font.render("Level Editor", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.small_font.render("Select an option to continue", True, (180, 180, 180))
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 150))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Buttons
        button_width = 300
        button_height = 60
        button_spacing = 20
        start_y = 220
        
        self.start_screen_buttons = []
        
        # New Level button
        new_btn_rect = pygame.Rect((self.width - button_width) // 2, start_y, button_width, button_height)
        mouse_pos = pygame.mouse.get_pos()
        new_btn_color = (70, 120, 70) if new_btn_rect.collidepoint(mouse_pos) else (50, 100, 50)
        pygame.draw.rect(self.screen, new_btn_color, new_btn_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), new_btn_rect, 3)
        new_text = self.font.render("Create New Level", True, (255, 255, 255))
        new_text_rect = new_text.get_rect(center=new_btn_rect.center)
        self.screen.blit(new_text, new_text_rect)
        self.start_screen_buttons.append(("new", new_btn_rect))
        
        # Load Level button
        load_btn_rect = pygame.Rect((self.width - button_width) // 2, start_y + button_height + button_spacing, button_width, button_height)
        load_btn_color = (70, 70, 120) if load_btn_rect.collidepoint(mouse_pos) else (50, 50, 100)
        pygame.draw.rect(self.screen, load_btn_color, load_btn_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), load_btn_rect, 3)
        load_text = self.font.render("Load Existing Level", True, (255, 255, 255))
        load_text_rect = load_text.get_rect(center=load_btn_rect.center)
        self.screen.blit(load_text, load_text_rect)
        self.start_screen_buttons.append(("load", load_btn_rect))
        
        # Back to Game button (only if launched from game)
        if self.return_to_game:
            back_btn_rect = pygame.Rect((self.width - button_width) // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height)
            back_btn_color = (120, 70, 70) if back_btn_rect.collidepoint(mouse_pos) else (100, 50, 50)
            pygame.draw.rect(self.screen, back_btn_color, back_btn_rect)
            pygame.draw.rect(self.screen, (200, 200, 200), back_btn_rect, 3)
            back_text = self.font.render("Back to Game", True, (255, 255, 255))
            back_text_rect = back_text.get_rect(center=back_btn_rect.center)
            self.screen.blit(back_text, back_text_rect)
            self.start_screen_buttons.append(("back", back_btn_rect))
        
        # Instructions
        inst_y = start_y + (3 if self.return_to_game else 2) * (button_height + button_spacing) + 30
        instructions = [
            "Controls:",
            "Left Click: Draw blocks",
            "Middle/Shift+Click: Erase",
            "Ctrl+Drag: Select multiple",
            "Ctrl+S: Save | Ctrl+M: Edit Metadata",
            "G: Toggle Grid | L: Load Level",
            "ESC: Return to this menu"
        ]
        
        for i, inst in enumerate(instructions):
            inst_surface = self.small_font.render(inst, True, (180, 180, 180))
            inst_rect = inst_surface.get_rect(center=(self.width // 2, inst_y + i * 22))
            self.screen.blit(inst_surface, inst_rect)
    
    def handle_start_screen_click(self, pos):
        """Handle clicks on start screen"""
        if hasattr(self, 'start_screen_buttons'):
            for action, rect in self.start_screen_buttons:
                if rect.collidepoint(pos):
                    if action == "new":
                        self.new_level()
                        return True
                    elif action == "load":
                        self.show_level_list = True
                        self.load_level_list()
                        return False  # Don't close start screen yet, show level list
                    elif action == "back":
                        self.running = False  # Exit editor to return to game
                        return True
        return False
    
    def run(self):
        """Main editor loop"""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
        
        # Only quit pygame if not returning to game
        if not self.return_to_game:
            pygame.quit()


def main():
    """Entry point for the level editor"""
    editor = LevelEditor()
    editor.run()


if __name__ == '__main__':
    main()
