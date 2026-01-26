"""Platform and grid system for level geometry.

This module provides classes for creating and managing platforms in the game.
Platforms are the building blocks of levels, supporting various types like
normal, death, spawn, checkpoint, finish, and slippery surfaces.

Example:
    Creating platforms::

        from skeletons.platform import Platform, Grid

        # Create a normal platform
        ground = Platform(
            x1=0, y1=500,
            x2=800, y2=500,
            grid_size=32,
            texture=Texture.GRASS,
        )

        # Create a death platform (kills player on contact)
        spikes = Platform(
            x1=200, y1=400,
            x2=300, y2=400,
            grid_size=32,
            platform_type=Platform.DEATH,
        )

        # Create a checkpoint
        checkpoint = Platform(
            x1=500, y1=450,
            x2=500, y2=450,
            grid_size=32,
            platform_type=Platform.CHECKPOINT,
        )

See Also:
    - :class:`Platform` for main platform functionality
    - :class:`Grid` for debug grid overlay
    - :class:`Cell` for individual grid cells
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import pygame

from utils.colors import ColorUtils
from utils.platform_types import PlatformTypes


class Cell:
    """Represents a single cell in a platform's grid.

    Cells are the visual building blocks of platforms. Each cell can have
    a solid color or a texture applied.

    Attributes:
        rect: The pygame Rect defining position and size.
        color: RGB tuple for the cell's color.
        texture: Optional pygame Surface for textured rendering.
        size: The cell size in pixels.

    Args:
        x: X position in pixels.
        y: Y position in pixels.
        size: Width and height of the cell in pixels.
        color: RGB tuple for the cell's color. Defaults to gray.
        texture: Optional texture Surface to render instead of color.
    """

    def __init__(
        self,
        x: int,
        y: int,
        size: int,
        color: Tuple[int, int, int] = (100, 100, 100),
        texture: Optional[pygame.Surface] = None,
    ) -> None:
        self.rect: pygame.Rect = pygame.Rect(x, y, size, size)
        self.color: Tuple[int, int, int] = color
        self.texture: Optional[pygame.Surface] = texture
        self.size: int = size

    def draw(
        self,
        screen: pygame.Surface,
        platform_type: Optional[str] = None,
        checkpoint_activated: bool = False,
    ) -> None:
        """Draw the cell to the screen.

        Args:
            screen: The pygame Surface to draw to.
            platform_type: Optional platform type for special rendering.
            checkpoint_activated: Whether the checkpoint is active.
        """
        if self.texture:
            texture_scaled = pygame.transform.scale(
                self.texture, (self.size, self.size)
            )
            screen.blit(texture_scaled, self.rect.topleft)
        else:
            pygame.draw.rect(screen, self.color, self.rect)


class Grid:
    """Debug grid overlay for level editing and alignment.

    Provides a toggleable grid overlay to help visualize and align
    platforms during development.

    Attributes:
        cell_size: Size of each grid cell in pixels.
        color: RGB tuple for grid line color.
        line_width: Width of grid lines in pixels.
        visible: Whether the grid is currently displayed.

    Args:
        cell_size: Size of grid cells in pixels. Defaults to 16.
        color: RGB color for grid lines. Defaults to dark gray.
        line_width: Width of grid lines. Defaults to 1.

    Example::

        grid = Grid(cell_size=32, color=(50, 50, 50))
        grid.visible = True  # Enable in debug mode

        # In game loop:
        grid.draw(screen)
    """

    def __init__(
        self,
        cell_size: int = 16,
        color: Tuple[int, int, int] = (50, 50, 50),
        line_width: int = 1,
    ) -> None:
        self.cell_size: int = cell_size
        self.color: Tuple[int, int, int] = color
        self.line_width: int = line_width
        self.visible: bool = False

    def toggle(self) -> None:
        """Toggle grid visibility on/off."""
        self.visible = not self.visible

    def set_cell_size(self, size: int) -> None:
        """Set the grid cell size.

        Args:
            size: New cell size in pixels. Clamped between 10-200.
        """
        self.cell_size = max(10, min(200, size))

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the grid overlay.

        Args:
            screen: The pygame Surface to draw to.
        """
        if not self.visible:
            return

        width, height = screen.get_size()

        # Draw vertical lines
        for x in range(0, width + 1, self.cell_size):
            pygame.draw.line(screen, self.color, (x, 0), (x, height), self.line_width)

        # Draw horizontal lines
        for y in range(0, height + 1, self.cell_size):
            pygame.draw.line(screen, self.color, (0, y), (width, y), self.line_width)

    def snap_to_grid(self, x: int, y: int) -> Tuple[int, int]:
        """Snap coordinates to the nearest grid point.

        Args:
            x: X coordinate to snap.
            y: Y coordinate to snap.

        Returns:
            Tuple of (x, y) snapped to grid.
        """
        return (
            (x // self.cell_size) * self.cell_size,
            (y // self.cell_size) * self.cell_size,
        )


class Platform:
    """A platform that players can interact with.

    Platforms are the main level geometry elements. They support different
    types that affect gameplay: normal platforms for walking, death platforms
    that kill the player, checkpoints for respawn points, and more.

    Platform Types:
        - ``NORMAL``: Standard walkable platform
        - ``DEATH``: Kills player on contact (e.g., spikes, lava)
        - ``SPAWN``: Player's starting position
        - ``CHECKPOINT``: Saves respawn position when touched
        - ``FINISH``: Level completion trigger
        - ``SLIPPERY``: Low friction surface (ice)

    Attributes:
        platform_type: One of the type constants (NORMAL, DEATH, etc.).
        checkpoint_activated: True if this checkpoint has been touched.
        grid_size: Size of each cell in pixels.
        velocity_x: Horizontal movement speed for moving platforms.
        color: RGB color tuple for rendering.
        texture: Optional texture Surface.
        cells: List of Cell objects making up this platform.
        rect: Bounding rectangle for collision detection.

    Args:
        x1: Left edge X coordinate in pixels.
        y1: Top edge Y coordinate in pixels.
        x2: Right edge X coordinate in pixels.
        y2: Bottom edge Y coordinate in pixels.
        grid_size: Size of each cell in the platform grid.
        platform_type: Type of platform. Defaults to NORMAL.
        color: Optional custom RGB color. If None, uses type default.
        texture: Optional texture Surface to apply to all cells.
        velocity_x: Horizontal velocity for moving platforms (pixels/sec).

    Example::

        # Simple grass platform
        grass = Platform(
            x1=100, y1=400,
            x2=500, y2=400,
            grid_size=32,
            texture=Texture.GRASS,
        )

        # Checkpoint platform
        checkpoint = Platform(
            x1=600, y1=350,
            x2=600, y2=350,
            grid_size=32,
            platform_type=Platform.CHECKPOINT,
        )
    """

    # Platform type constants (delegated to PlatformTypes for consistency)
    NORMAL: str = PlatformTypes.NORMAL
    DEATH: str = PlatformTypes.DEATH
    SPAWN: str = PlatformTypes.SPAWN
    CHECKPOINT: str = PlatformTypes.CHECKPOINT
    FINISH: str = PlatformTypes.FINISH
    SLIPPERY: str = PlatformTypes.SLIPPERY
    NOCLIP: str = PlatformTypes.NOCLIP
    BOOST_UP: str = PlatformTypes.BOOST_UP
    BOOST_DOWN: str = PlatformTypes.BOOST_DOWN

    def __init__(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        grid_size: int,
        platform_type: Optional[str] = None,
        platform_types: Optional[List[str]] = None,
        color: Optional[Tuple[int, int, int]] = None,
        texture: Optional[pygame.Surface] = None,
        velocity_x: float = 0,
        layer: int = 0,
    ) -> None:
        # Handle both single type (legacy) and multiple types (new)
        if platform_types is not None:
            self.platform_types: List[str] = (
                platform_types if platform_types else [Platform.NORMAL]
            )
        elif platform_type is not None:
            self.platform_types: List[str] = [platform_type]
        else:
            self.platform_types: List[str] = [Platform.NORMAL]

        # Keep platform_type for backward compatibility (returns first type)
        self.platform_type: str = self.platform_types[0]

        self.checkpoint_activated: bool = False
        self.grid_size: int = grid_size
        self.velocity_x: float = velocity_x
        self.original_x1: int = x1
        self.original_x2: int = x2
        self.layer: int = layer  # Layer for depth rendering (-10 to +10, 0 is normal)

        # Ensure coordinates are properly ordered
        self.x1: int = min(x1, x2)
        self.y1: int = min(y1, y2)
        self.x2: int = max(x1, x2)
        self.y2: int = max(y1, y2)

        # Determine color based on type if not provided
        if color is None:
            self.color: Tuple[int, int, int] = PlatformTypes.get_color(
                self.platform_type
            )
        else:
            self.color = color

        self.texture: Optional[pygame.Surface] = texture

        # Create cells for the platform area with layer tinting applied
        self.cells: List[Cell] = []

        # Apply layer tint using ColorUtils
        tinted_color = ColorUtils.apply_layer_tint(self.color, layer)
        tinted_texture = (
            ColorUtils.apply_layer_tint_to_texture(texture, layer) if texture else None
        )

        for y in range(self.y1, self.y2 + 1, grid_size):
            for x in range(self.x1, self.x2 + 1, grid_size):
                cell = Cell(x, y, grid_size, tinted_color, tinted_texture)
                self.cells.append(cell)

        # Create bounding rect for collision detection
        self.rect: pygame.Rect = pygame.Rect(
            self.x1,
            self.y1,
            self.x2 - self.x1 + grid_size,
            self.y2 - self.y1 + grid_size,
        )

    def draw(self, screen: pygame.Surface) -> None:
        """Render the platform to the screen.

        Draws all cells and adds visual indicators for special platform types:
        - DEATH: X pattern overlay
        - CHECKPOINT: Flag (inactive) or green border (activated)
        - SLIPPERY: Wavy lines
        - SPAWN: "S" marker

        Args:
            screen: The pygame Surface to draw to.
        """
        # Draw all cells
        for cell in self.cells:
            cell.draw(screen, self.platform_type, self.checkpoint_activated)

        # Draw indicators on top for special platforms (only if no texture)
        if not self.texture:
            self._draw_special_indicators(screen)

    def _draw_special_indicators(self, screen: pygame.Surface) -> None:
        """Draw visual indicators for special platform types.

        Args:
            screen: The pygame Surface to draw to.
        """
        # Draw indicators for each type the platform has
        if Platform.DEATH in self.platform_types:
            # Draw X pattern for death platforms
            for cell in self.cells:
                pygame.draw.line(
                    screen, (150, 0, 0), cell.rect.topleft, cell.rect.bottomright, 2
                )
                pygame.draw.line(
                    screen, (150, 0, 0), cell.rect.topright, cell.rect.bottomleft, 2
                )

        if Platform.CHECKPOINT in self.platform_types:
            if self.checkpoint_activated:
                # Green border when activated
                pygame.draw.rect(screen, (0, 200, 0), self.rect, 3)
            else:
                # Draw flag on center cell
                center_cell = self.cells[len(self.cells) // 2]
                center_x = center_cell.rect.centerx
                top_y = center_cell.rect.top + 5
                pygame.draw.line(
                    screen,
                    (0, 0, 0),
                    (center_x, top_y),
                    (center_x, center_cell.rect.bottom - 5),
                    2,
                )
                pygame.draw.polygon(
                    screen,
                    (0, 0, 0),
                    [
                        (center_x, top_y),
                        (center_x + 10, top_y + 5),
                        (center_x, top_y + 10),
                    ],
                )

        if Platform.SLIPPERY in self.platform_types:
            # Draw wavy lines for slippery surfaces
            for cell in self.cells:
                for i in range(3):
                    y = cell.rect.centery - 5 + i * 5
                    pygame.draw.line(
                        screen,
                        (50, 100, 150),
                        (cell.rect.left + 5, y),
                        (cell.rect.right - 5, y),
                        1,
                    )

        if Platform.SPAWN in self.platform_types:
            # Draw "S" marker on center cell
            center_cell = self.cells[len(self.cells) // 2]
            font = pygame.font.Font(None, 20)
            text = font.render("S", True, (0, 150, 0))
            screen.blit(
                text, (center_cell.rect.centerx - 5, center_cell.rect.centery - 10)
            )

        if Platform.BOOST_UP in self.platform_types:
            # Draw upward arrow
            center_cell = self.cells[len(self.cells) // 2]
            center_x = center_cell.rect.centerx
            center_y = center_cell.rect.centery
            # Arrow shaft
            pygame.draw.line(
                screen,
                (0, 200, 0),
                (center_x, center_y + 8),
                (center_x, center_y - 8),
                3,
            )
            # Arrow head
            pygame.draw.polygon(
                screen,
                (0, 200, 0),
                [
                    (center_x, center_y - 10),
                    (center_x - 5, center_y - 5),
                    (center_x + 5, center_y - 5),
                ],
            )

        if Platform.BOOST_DOWN in self.platform_types:
            # Draw downward arrow
            center_cell = self.cells[len(self.cells) // 2]
            center_x = center_cell.rect.centerx
            center_y = center_cell.rect.centery
            # Arrow shaft
            pygame.draw.line(
                screen,
                (200, 0, 0),
                (center_x, center_y - 8),
                (center_x, center_y + 8),
                3,
            )
            # Arrow head
            pygame.draw.polygon(
                screen,
                (200, 0, 0),
                [
                    (center_x, center_y + 10),
                    (center_x - 5, center_y + 5),
                    (center_x + 5, center_y + 5),
                ],
            )

    def get_friction(self) -> float:
        """Get the friction coefficient for this platform.

        Returns:
            Friction value based on platform type.
        """
        # Check all types and use the most specific friction
        for ptype in self.platform_types:
            friction = PlatformTypes.get_friction(ptype)
            if friction != PlatformTypes.DEFAULT_FRICTION:
                return friction
        return PlatformTypes.DEFAULT_FRICTION

    def is_deadly(self) -> bool:
        """Check if this platform kills the player on contact.

        Returns:
            True if this is a DEATH platform.
        """
        return Platform.DEATH in self.platform_types

    def is_checkpoint(self) -> bool:
        """Check if this platform is a checkpoint.

        Returns:
            True if this is a CHECKPOINT platform.
        """
        return Platform.CHECKPOINT in self.platform_types

    def is_finish(self) -> bool:
        """Check if this platform is a finish point.

        Returns:
            True if this is a FINISH platform.
        """
        return Platform.FINISH in self.platform_types

    def is_spawn(self) -> bool:
        """Check if this platform is a spawn point.

        Returns:
            True if this is a SPAWN platform.
        """
        return Platform.SPAWN in self.platform_types

    def is_noclip(self) -> bool:
        """Check if this platform is a noclip platform.

        Returns:
            True if this is a NOCLIP platform.
        """
        return Platform.NOCLIP in self.platform_types

    def is_boost_up(self) -> bool:
        """Check if this platform boosts player upward.

        Returns:
            True if this is a BOOST_UP platform.
        """
        return Platform.BOOST_UP in self.platform_types

    def is_boost_down(self) -> bool:
        """Check if this platform boosts player downward.

        Returns:
            True if this is a BOOST_DOWN platform.
        """
        return Platform.BOOST_DOWN in self.platform_types

    def activate_checkpoint(self) -> None:
        """Activate this checkpoint.

        Only affects CHECKPOINT platforms. Once activated, the checkpoint
        displays a green border and serves as the player's respawn point.
        """
        if Platform.CHECKPOINT in self.platform_types:
            self.checkpoint_activated = True

    def update(self, dt: float) -> None:
        """Update platform position for moving platforms.

        Args:
            dt: Delta time in seconds since last update.
        """
        if self.velocity_x != 0:
            # Calculate movement offset
            offset = self.velocity_x * dt
            self.x1 += offset
            self.x2 += offset

            # Update cells and rect
            for cell in self.cells:
                cell.rect.x += offset
            self.rect.x += offset
