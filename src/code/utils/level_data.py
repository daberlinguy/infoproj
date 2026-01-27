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

    @staticmethod
    def merge_platform_cells(
        platforms_data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Merge single-cell platforms into larger rectangles when possible.

        Only merges entries that represent single grid cells (x1==x2 and y1==y2)
        and share the same visual/gameplay attributes.
        """
        if not platforms_data:
            return []

        merged: List[Dict[str, Any]] = []
        cell_groups: Dict[
            Tuple[Any, ...],
            Dict[str, Any],
        ] = {}

        for entry in platforms_data:
            x1 = entry.get("x1", entry.get("x"))
            y1 = entry.get("y1", entry.get("y"))
            x2 = entry.get("x2", x1)
            y2 = entry.get("y2", y1)
            if x1 is None or y1 is None or x2 is None or y2 is None:
                merged.append(entry)
                continue

            if x1 != x2 or y1 != y2:
                merged.append(entry)
                continue

            grid_size = entry.get("grid_size", 32)
            layer = entry.get("layer", 0)
            types = LevelDataUtils.normalize_platform_types(entry)
            texture = entry.get("texture")
            color = entry.get("color")
            comment = entry.get("comment")

            key = (
                grid_size,
                layer,
                tuple(types),
                texture,
                tuple(color) if isinstance(color, (list, tuple)) else color,
                comment,
            )

            group = cell_groups.get(key)
            if group is None:
                group = {
                    "cells": set(),
                    "template": entry,
                    "types": types,
                    "grid_size": grid_size,
                    "layer": layer,
                    "texture": texture,
                    "color": color,
                    "comment": comment,
                }
                cell_groups[key] = group
            group["cells"].add((int(x1), int(y1)))

        for group in cell_groups.values():
            cells = set(group["cells"])
            if not cells:
                continue
            while cells:
                start_x, start_y = min(cells)
                width = 1
                while (start_x + width, start_y) in cells:
                    width += 1
                height = 1
                while True:
                    next_row = start_y + height
                    if all((start_x + dx, next_row) in cells for dx in range(width)):
                        height += 1
                    else:
                        break

                for dy in range(height):
                    for dx in range(width):
                        cells.discard((start_x + dx, start_y + dy))

                merged_entry: Dict[str, Any] = {
                    "x1": start_x,
                    "y1": start_y,
                    "x2": start_x + width - 1,
                    "y2": start_y + height - 1,
                    "grid_size": group["grid_size"],
                    "types": group["types"],
                    "layer": group["layer"],
                }
                if group["texture"]:
                    merged_entry["texture"] = group["texture"]
                if group["color"] is not None:
                    merged_entry["color"] = group["color"]
                if group["comment"]:
                    merged_entry["comment"] = group["comment"]
                merged.append(merged_entry)

        return merged
