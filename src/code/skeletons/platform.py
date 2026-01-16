import pygame
import sys

class Cell:
    """Represents a single cell in a platform"""
    def __init__(self, x, y, size, color=(100, 100, 100), texture=None):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = color
        self.texture = texture
        self.size = size
    
    def draw(self, screen, platform_type=None, checkpoint_activated=False):
        """Draw the cell with optional texture or color"""
        if self.texture:
            texture_scaled = pygame.transform.scale(self.texture, (self.size, self.size))
            screen.blit(texture_scaled, self.rect.topleft)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

class Grid:
    def __init__(self, cell_size=16, color=(50, 50, 50), line_width=1):
        self.cell_size = cell_size
        self.color = color
        self.line_width = line_width
        self.visible = False
    
    def toggle(self):
        self.visible = not self.visible
    
    def set_cell_size(self, size):
        self.cell_size = max(10, min(200, size))  # Begrenzt zwischen 10 und 200
    
    def draw(self, screen):
        if not self.visible:
            return
        
        width, height = screen.get_size()
        
        # Vertikale Linien - eine extra Linie am rechten Rand
        for x in range(0, width + 1, self.cell_size):
            pygame.draw.line(screen, self.color, (x, 0), (x, height), self.line_width)
        
        # Horizontale Linien - eine extra Linie am unteren Rand
        for y in range(0, height + 1, self.cell_size):
            pygame.draw.line(screen, self.color, (0, y), (width, y), self.line_width)
    
    def snap_to_grid(this, x, y):
        """Schnapp Koordinaten zum nächsten Grid-Punkt"""
        return (x // this.cell_size) * this.cell_size, (y // this.cell_size) * this.cell_size

class Platform:
    # Platform types
    NORMAL = "normal"
    DEATH = "death"
    SPAWN = "spawn"
    CHECKPOINT = "checkpoint"
    SLIPPERY = "slippery"
    FINISH = "finish"
    
    def __init__(self, x1, y1, x2, y2, grid_size, platform_type=None, color=None, texture=None, velocity_x=0):
        """
        Create a platform composed of cells
        
        Args:
            x1, y1: Top-left corner coordinates (in pixels)
            x2, y2: Bottom-right corner coordinates (in pixels)
            grid_size: Size of each cell
            platform_type: Type of platform (NORMAL, DEATH, SPAWN, CHECKPOINT, SLIPPERY)
            color: Optional custom color for the platform
            texture: Optional texture to apply to all cells
            velocity_x: Horizontal velocity for moving platforms (pixels per second)
        """
        self.platform_type = platform_type if platform_type else Platform.NORMAL
        self.checkpoint_activated = False
        self.grid_size = grid_size
        self.velocity_x = velocity_x
        self.original_x1 = x1
        self.original_x2 = x2
        
        # Ensure coordinates are properly ordered
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        
        # Set default colors based on type if no custom color provided
        if color is None:
            if platform_type == Platform.DEATH:
                self.color = (255, 0, 0)  # Red
            elif platform_type == Platform.SPAWN:
                self.color = (0, 255, 0)  # Green
            elif platform_type == Platform.CHECKPOINT:
                self.color = (255, 255, 0)  # Yellow
            elif platform_type == Platform.SLIPPERY:
                self.color = (100, 200, 255)  # Light blue
            elif platform_type == Platform.FINISH:
                self.color = (255, 215, 0)  # Gold
            else:
                self.color = (100, 100, 100)  # Gray
        else:
            self.color = color
        
        self.texture = texture
        
        # Create cells for the platform area
        self.cells = []
        for y in range(self.y1, self.y2 + 1, grid_size):
            for x in range(self.x1, self.x2 + 1, grid_size):
                cell = Cell(x, y, grid_size, self.color, self.texture)
                self.cells.append(cell)
        
        # Create a bounding rect for collision detection
        self.rect = pygame.Rect(self.x1, self.y1, self.x2 - self.x1 + grid_size, self.y2 - self.y1 + grid_size)
    
    def draw(self, screen):
        # Draw all cells
        for cell in self.cells:
            cell.draw(screen, self.platform_type, self.checkpoint_activated)
        
        # Draw indicators on top for special platforms
        if not self.texture:
            if self.platform_type == Platform.DEATH:
                # Draw X pattern for death
                for cell in self.cells:
                    pygame.draw.line(screen, (150, 0, 0), cell.rect.topleft, cell.rect.bottomright, 2)
                    pygame.draw.line(screen, (150, 0, 0), cell.rect.topright, cell.rect.bottomleft, 2)
            elif self.platform_type == Platform.CHECKPOINT:
                # Draw border when activated or flag when not
                if self.checkpoint_activated:
                    pygame.draw.rect(screen, (0, 200, 0), self.rect, 3)  # Green border when activated
                else:
                    # Draw flag on center cell
                    center_cell = self.cells[len(self.cells) // 2]
                    center_x = center_cell.rect.centerx
                    top_y = center_cell.rect.top + 5
                    pygame.draw.line(screen, (0, 0, 0), (center_x, top_y), (center_x, center_cell.rect.bottom - 5), 2)
                    pygame.draw.polygon(screen, (0, 0, 0), [(center_x, top_y), (center_x + 10, top_y + 5), (center_x, top_y + 10)])
            elif self.platform_type == Platform.SLIPPERY:
                # Draw wavy lines for slippery on each cell
                for cell in self.cells:
                    for i in range(3):
                        y = cell.rect.centery - 5 + i * 5
                        pygame.draw.line(screen, (50, 100, 150), (cell.rect.left + 5, y), (cell.rect.right - 5, y), 1)
            elif self.platform_type == Platform.SPAWN:
                # Draw S on center cell
                center_cell = self.cells[len(self.cells) // 2]
                font = pygame.font.Font(None, 20)
            elif self.platform_type == Platform.FINISH:
                # Draw F on center cell with checkered flag pattern
                center_cell = self.cells[len(self.cells) // 2]
                font = pygame.font.Font(None, 24)
                text = font.render("F", True, (0, 0, 0))
                screen.blit(text, (center_cell.rect.centerx - 6, center_cell.rect.centery - 12))
                # Draw stars around it
                pygame.draw.circle(screen, (255, 255, 255), (center_cell.rect.left + 5, center_cell.rect.top + 5), 3)
                pygame.draw.circle(screen, (255, 255, 255), (center_cell.rect.right - 5, center_cell.rect.top + 5), 3)
                text = font.render("S", True, (0, 150, 0))
                screen.blit(text, (center_cell.rect.centerx - 5, center_cell.rect.centery - 10))
    
    def get_friction(self):
        """Return friction coefficient based on platform type"""
        if self.platform_type == Platform.SLIPPERY:
            return 0.05  # Very low friction
        else:
            return 0.8  # Normal friction
    
    def is_deadly(self):
        """Check if platform kills player"""
        return self.platform_type == Platform.DEATH
    
    def is_finish(self):
        """Check if platform is finish/goal"""
        return self.platform_type == Platform.FINISH
    
    def is_checkpoint(self):
        """Check if platform is a checkpoint"""
        return self.platform_type == Platform.CHECKPOINT
    
    def is_spawn(self):
        """Check if platform is spawn point"""
        return self.platform_type == Platform.SPAWN
    
    def activate_checkpoint(self):
        """Activate this checkpoint"""
        if self.platform_type == Platform.CHECKPOINT:
            self.checkpoint_activated = True
    
    def update(self, dt):
        """Update platform position for moving platforms"""
        if self.velocity_x != 0:
            # Move platform
            offset = self.velocity_x * dt
            self.x1 += offset
            self.x2 += offset
            
            # Update cells and rect
            for cell in self.cells:
                cell.rect.x += offset
            self.rect.x += offset