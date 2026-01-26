"""Level data loading and parsing utilities.

This module provides utilities for loading and parsing level JSON data.
"""

from typing import Any, Dict, List, Optional, Tuple
import json
import os


class LevelDataUtils:
    """Utility class for level data operations."""

    @staticmethod
    def load_level_json(file_path: str) -> Optional[Dict[str, Any]]:
        """Load and parse a level JSON file.

        Args:
            file_path: Path to the level JSON file.

        Returns:
            Parsed JSON data dict, or None if loading failed.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Error loading level file '{file_path}': {e}")
            return None

    @staticmethod
    def normalize_platform_types(entry: Dict[str, Any]) -> List[str]:
        """Extract and normalize platform types from a platform entry.

        Handles both old "type" (single string) and new "types" (list) format.

        Args:
            entry: Platform data dictionary.

        Returns:
            List of platform type strings (uppercase).

        Example:
            >>> LevelDataUtils.normalize_platform_types({"types": ["normal", "checkpoint"]})
            ["NORMAL", "CHECKPOINT"]
            >>> LevelDataUtils.normalize_platform_types({"type": "death"})
            ["DEATH"]
        """
        platform_types_list = entry.get("types", [])
        if not platform_types_list:
            # Fallback to old single type format
            old_type = str(entry.get("type", "NORMAL")).upper()
            platform_types_list = [old_type]

        # Normalize to uppercase
        return [str(t).upper() for t in platform_types_list]

    @staticmethod
    def parse_color(color_data: Any) -> Optional[Tuple[int, int, int]]:
        """Parse color data from various formats.

        Args:
            color_data: Color data (list, tuple, or None).

        Returns:
            RGB tuple (int, int, int) or None if invalid.
        """
        if (
            color_data
            and isinstance(color_data, (list, tuple))
            and len(color_data) >= 3
        ):
            return tuple(color_data[:3])
        return None

    @staticmethod
    def get_platform_coordinates(
        entry: Dict[str, Any], grid_size: int
    ) -> Optional[Tuple[int, int, int, int]]:
        """Extract and calculate platform coordinates.

        Supports multiple coordinate formats:
        - x1, y1, x2, y2 (explicit corners)
        - x, y, w, h (position + size)

        Args:
            entry: Platform data dictionary.
            grid_size: Grid size multiplier.

        Returns:
            Tuple of (x1, y1, x2, y2) in pixels, or None if invalid.
        """
        x1 = entry.get("x1", entry.get("x", 0))
        y1 = entry.get("y1", entry.get("y", 0))
        x2 = entry.get("x2")
        y2 = entry.get("y2")

        # Handle width/height format
        w = entry.get("w")
        h = entry.get("h")
        if x2 is None and w is not None:
            x2 = x1 + w
        if y2 is None and h is not None:
            y2 = y1 + h

        # Validate we have all coordinates
        if x2 is None or y2 is None:
            return None

        # Scale by grid size
        return (
            x1 * grid_size,
            y1 * grid_size,
            x2 * grid_size,
            y2 * grid_size,
        )

    @staticmethod
    def get_page_data(level_data: Dict[str, Any], page_index: Any) -> Dict[str, Any]:
        """Get data for a specific page from level data.

        Args:
            level_data: Full level data dictionary.
            page_index: Page index (int or string).

        Returns:
            Page data dictionary (empty if not found).
        """
        pages = level_data.get("pages")
        if not pages:
            return {}

        # Try both string and int keys
        page_data = pages.get(str(page_index)) or pages.get(page_index) or {}
        return page_data
