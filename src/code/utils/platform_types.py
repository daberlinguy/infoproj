"""Platform type constants and configuration.

This module centralizes all platform type definitions and their properties.
"""

from typing import Dict, List, Tuple


class PlatformTypes:
    """Platform type constants and metadata."""

    # Type constants
    NORMAL: str = "normal"
    DEATH: str = "death"
    SPAWN: str = "spawn"
    CHECKPOINT: str = "checkpoint"
    FINISH: str = "finish"
    SLIPPERY: str = "slippery"
    NOCLIP: str = "noclip"
    BOOST_UP: str = "boost_up"
    BOOST_DOWN: str = "boost_down"

    # All valid platform types
    ALL_TYPES: List[str] = [
        NORMAL,
        DEATH,
        SPAWN,
        CHECKPOINT,
        FINISH,
        SLIPPERY,
        NOCLIP,
        BOOST_UP,
        BOOST_DOWN,
    ]

    # Default colors for each platform type
    TYPE_COLORS: Dict[str, Tuple[int, int, int]] = {
        DEATH: (255, 0, 0),  # Red
        SPAWN: (0, 255, 0),  # Green
        CHECKPOINT: (255, 255, 0),  # Yellow
        FINISH: (0, 150, 255),  # Blue
        SLIPPERY: (100, 200, 255),  # Light blue
        NOCLIP: (200, 200, 200),  # Light gray
        BOOST_UP: (150, 255, 150),  # Light green
        BOOST_DOWN: (255, 150, 150),  # Light red
        NORMAL: (100, 100, 100),  # Gray
    }

    DEFAULT_COLOR: Tuple[int, int, int] = (100, 100, 100)  # Gray

    # Friction values for platform types
    FRICTION_VALUES: Dict[str, float] = {
        SLIPPERY: 0.95,  # Very low friction
        NORMAL: 0.8,  # Normal friction
    }

    DEFAULT_FRICTION: float = 0.8

    @classmethod
    def get_color(cls, platform_type: str) -> Tuple[int, int, int]:
        """Get the default color for a platform type.

        Args:
            platform_type: The platform type constant.

        Returns:
            RGB color tuple.
        """
        return cls.TYPE_COLORS.get(platform_type, cls.DEFAULT_COLOR)

    @classmethod
    def get_friction(cls, platform_type: str) -> float:
        """Get the friction value for a platform type.

        Args:
            platform_type: The platform type constant.

        Returns:
            Friction coefficient (0.0 to 1.0).
        """
        return cls.FRICTION_VALUES.get(platform_type, cls.DEFAULT_FRICTION)

    @classmethod
    def is_valid_type(cls, platform_type: str) -> bool:
        """Check if a platform type is valid.

        Args:
            platform_type: The platform type to check.

        Returns:
            True if valid, False otherwise.
        """
        return platform_type in cls.ALL_TYPES

    @classmethod
    def normalize_types(cls, types: List[str]) -> List[str]:
        """Normalize a list of platform types, filtering invalid ones.

        Args:
            types: List of platform type strings.

        Returns:
            List of valid platform types, defaults to [NORMAL] if empty.
        """
        valid_types = [t for t in types if cls.is_valid_type(t)]
        return valid_types if valid_types else [cls.NORMAL]
