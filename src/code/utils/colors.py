"""Color manipulation utilities.

This module provides utilities for color operations including tinting,
brightness adjustments, and layer-based color transformations.
"""

from typing import Tuple
import pygame


class ColorUtils:
    """Utility class for color manipulation operations."""

    @staticmethod
    def apply_layer_tint(
        color: Tuple[int, int, int], layer: int
    ) -> Tuple[int, int, int]:
        """Apply brightness/darkness tint based on layer depth.

        Background layers (negative) become darker (10% per layer towards black).
        Foreground layers (positive) become brighter (10% per layer towards white).

        Args:
            color: Original RGB color tuple (0-255 each).
            layer: Layer depth (-10 to +10, 0 is normal).

        Returns:
            Tinted RGB color tuple.

        Example:
            >>> ColorUtils.apply_layer_tint((100, 100, 100), -5)
            (50, 50, 50)  # 50% darker
            >>> ColorUtils.apply_layer_tint((100, 100, 100), 5)
            (177, 177, 177)  # 50% brighter towards white
        """
        if layer == 0:
            return color

        # Calculate tint factor: -10 to +10 layers, 10% per layer
        tint_factor = layer * 0.1

        if tint_factor < 0:
            # Background: darken towards black
            multiplier = max(0.0, 1.0 + tint_factor)
            return (
                int(color[0] * multiplier),
                int(color[1] * multiplier),
                int(color[2] * multiplier),
            )
        else:
            # Foreground: brighten towards white, capped at 30 % to avoid
            # colours washing out to pure white at higher layer values.
            effective_tint = min(tint_factor, 0.3)
            return (
                int(color[0] + (255 - color[0]) * effective_tint),
                int(color[1] + (255 - color[1]) * effective_tint),
                int(color[2] + (255 - color[2]) * effective_tint),
            )

    @staticmethod
    def apply_layer_tint_to_texture(
        texture: pygame.Surface, layer: int
    ) -> pygame.Surface:
        """Apply brightness/darkness tint to a texture based on layer depth.

        Args:
            texture: Original texture surface.
            layer: Layer depth (-10 to +10, 0 is normal).

        Returns:
            Tinted texture surface (new copy).
        """
        if layer == 0:
            return texture

        # Create a copy to avoid modifying the original
        tinted = texture.copy()

        # Calculate tint factor
        tint_factor = layer * 0.1

        if tint_factor < 0:
            # Background: darken
            multiplier = max(0.0, 1.0 + tint_factor)
            dark_overlay = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 0, int(255 * (1 - multiplier))))
            tinted.blit(dark_overlay, (0, 0))
        else:
            # Foreground: brighten, capped at 30 % to prevent white wash-out.
            bright_overlay = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
            bright_overlay.fill((255, 255, 255, int(255 * min(tint_factor, 0.3))))
            tinted.blit(bright_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        return tinted

    @staticmethod
    def clamp(value: int, min_val: int = 0, max_val: int = 255) -> int:
        """Clamp a value between min and max.

        Args:
            value: Value to clamp.
            min_val: Minimum value.
            max_val: Maximum value.

        Returns:
            Clamped value.
        """
        return max(min_val, min(max_val, value))

    @staticmethod
    def blend_colors(
        color1: Tuple[int, int, int], color2: Tuple[int, int, int], factor: float
    ) -> Tuple[int, int, int]:
        """Blend two colors together.

        Args:
            color1: First RGB color.
            color2: Second RGB color.
            factor: Blend factor (0.0 = color1, 1.0 = color2).

        Returns:
            Blended RGB color.
        """
        factor = max(0.0, min(1.0, factor))
        return (
            int(color1[0] + (color2[0] - color1[0]) * factor),
            int(color1[1] + (color2[1] - color1[1]) * factor),
            int(color1[2] + (color2[2] - color1[2]) * factor),
        )
