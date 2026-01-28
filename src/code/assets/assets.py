"""Asset loading utilities for fonts, textures, and sprites.

This module provides helper functions and classes for loading and managing
game assets including fonts and textures. Textures are dynamically loaded
from a JSON configuration file (textures.json).

Example:
    Using fonts::

        from assets.assets import getFont

        # Get a font at specific size
        title_font = getFont(60)
        small_font = getFont(16)

    Using textures::

        from assets.assets import Texture

        # Use dynamically loaded textures for platforms
        platform = Platform(..., texture=Texture.GRASS)
        ice_block = Platform(..., texture=Texture.ICE)

        # Get texture by name (string)
        texture = Texture.get("GRASS")

        # List all available textures
        print(Texture.list_all())  # ['GRASS', 'ICE', 'STONE', ...]

    Adding new textures:
        1. Open src/resources/textures.json
        2. Add a new entry in the "textures" object::

            "MY_NEW_TEXTURE": {
                "x": 100,
                "y": 200,
                "width": 16,
                "height": 16,
                "description": "My custom texture"
            }

        3. The texture is now available as Texture.MY_NEW_TEXTURE

Note:
    - Font sizes are cached on import for sizes 1-99
    - Textures are loaded from textures.json on module import
    - Both game and editor share the same texture configuration
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Tuple

import pygame

from utils.paths import assets_path, resources_path


# ---------------------------------------------------------------------------
# Font Loading
# ---------------------------------------------------------------------------

_font_path: str = assets_path("fonts", "Minecraft.ttf")
_default_font_size: int = 40
custom_font: pygame.font.Font = pygame.font.Font(_font_path, _default_font_size)

# Pre-cache fonts for sizes 1-99 for fast access
cfont: Dict[int, pygame.font.Font] = {}
for i in range(1, 100):
    cfont[i] = pygame.font.Font(_font_path, i)


def getFont(size: int) -> pygame.font.Font:
    """Get a cached font at the specified size.

    Args:
        size: Font size in points (1-99).

    Returns:
        A pygame Font object at the requested size.

    Raises:
        RuntimeError: If size is less than 0 or greater than 100.

    Example::

        title_font = getFont(60)
        text_surface = title_font.render("Hello", True, (255, 255, 255))
    """
    if size > 100:
        raise RuntimeError("Out of Range above 100")
    elif size < 0:
        raise RuntimeError("Out of Range below 0")
    else:
        return cfont[size]


# ---------------------------------------------------------------------------
# Texture Configuration Loading
# ---------------------------------------------------------------------------


def _load_texture_config() -> dict:
    """Load the texture configuration from textures.json.

    Returns:
        Dictionary containing texture definitions and platform types.
    """
    config_path = resources_path("textures.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Texture configuration not found at {config_path}. "
            "Please ensure textures.json exists in the resources folder."
        )

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_texture_config() -> dict:
    """Get the texture configuration dictionary.

    Returns:
        The full texture configuration including atlas path, textures, and platform types.
    """
    return _load_texture_config()


def get_platform_types() -> List[str]:
    """Get the list of available platform type names.

    Returns:
        List of platform type names (e.g., ['NORMAL', 'DEATH', 'CHECKPOINT', ...])
    """
    config = _load_texture_config()
    return [pt["name"] for pt in config.get("platform_types", [])]


def get_texture_names() -> List[str]:
    """Get the list of available texture names.

    Returns:
        List of texture names (e.g., ['GRASS', 'ICE', 'STONE', ...])
    """
    config = _load_texture_config()
    return list(config.get("textures", {}).keys())


# ---------------------------------------------------------------------------
# Texture Loading
# ---------------------------------------------------------------------------

# Cache for the texture atlas to avoid reloading it multiple times
_texture_atlas_cache: Optional[pygame.Surface] = None


def getMinecraftTexture(
    location_x: int,
    location_y: int,
    width: int,
    height: int,
    top_left: Tuple[int, int] = (0, 0),
) -> pygame.Surface:
    """Extract a texture region from the Minecraft texture atlas.

    Loads a rectangular region from the texture_atlas.png sprite sheet.
    The atlas is cached after first load to improve performance.

    Args:
        location_x: X coordinate in the atlas (pixels from left).
        location_y: Y coordinate in the atlas (pixels from top).
        width: Width of the region to extract.
        height: Height of the region to extract.
        top_left: Offset within the output surface. Defaults to (0, 0).

    Returns:
        A pygame Surface containing the extracted texture region.

    Example::

        # Extract grass texture at position (352, 576)
        grass = getMinecraftTexture(352, 576, 16, 16)
    """
    global _texture_atlas_cache

    # Load and cache the texture atlas on first use
    if _texture_atlas_cache is None:
        texture_path = assets_path("sprites", "tiles", "texture_atlas.png")
        _texture_atlas_cache = pygame.image.load(texture_path).convert_alpha()

    texture_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    texture_surface.blit(
        _texture_atlas_cache,
        top_left,
        pygame.Rect(location_x, location_y, width, height),
    )

    return texture_surface


class TextureMeta(type):
    """Metaclass for dynamic texture attribute access.

    Allows accessing textures as Texture.NAME where NAME is defined
    in the textures.json configuration file.
    """

    _textures: Dict[str, pygame.Surface] = {}
    _loaded: bool = False
    _config: dict = {}

    def _ensure_loaded(cls) -> None:
        """Ensure textures are loaded from configuration."""
        if cls._loaded:
            return

        cls._config = _load_texture_config()
        textures = cls._config.get("textures", {})

        for name, tex_data in textures.items():
            surface = getMinecraftTexture(
                location_x=tex_data["x"],
                location_y=tex_data["y"],
                width=tex_data.get("width", 16),
                height=tex_data.get("height", 16),
            )
            cls._textures[name] = surface

        cls._loaded = True

    def __getattr__(cls, name: str) -> pygame.Surface:
        """Get a texture by attribute name.

        Args:
            name: The texture name (e.g., 'GRASS', 'ICE').

        Returns:
            The pygame Surface for the texture.

        Raises:
            AttributeError: If the texture name is not found.
        """
        if name.startswith("_"):
            raise AttributeError(f"'{cls.__name__}' has no attribute '{name}'")

        cls._ensure_loaded()

        if name in cls._textures:
            return cls._textures[name]

        raise AttributeError(
            f"Texture '{name}' not found. "
            f"Available textures: {list(cls._textures.keys())}"
        )


class Texture(metaclass=TextureMeta):
    """Dynamically loaded textures from the texture atlas.

    Textures are defined in textures.json and loaded automatically.
    Access textures as class attributes (e.g., Texture.GRASS).

    Adding new textures:
        1. Open src/resources/textures.json
        2. Add entry to "textures" object with x, y, width, height
        3. Access as Texture.YOUR_TEXTURE_NAME

    Methods:
        get(name): Get texture by string name
        list_all(): Get list of all texture names
        reload(): Force reload textures from config

    Example::

        from assets.assets import Texture

        # Access as attribute
        grass = Texture.GRASS
        ice = Texture.ICE

        # Access by name string
        texture = Texture.get("GRASS")

        # List all available
        names = Texture.list_all()
    """

    @classmethod
    def get(cls, name: str) -> Optional[pygame.Surface]:
        """Get a texture by name.

        Args:
            name: The texture name (e.g., 'GRASS').

        Returns:
            The pygame Surface, or None if not found.
        """
        type(cls)._ensure_loaded(cls)
        return type(cls)._textures.get(name)

    @classmethod
    def list_all(cls) -> List[str]:
        """Get a list of all available texture names.

        Returns:
            List of texture name strings.
        """
        type(cls)._ensure_loaded(cls)
        return list(type(cls)._textures.keys())

    @classmethod
    def reload(cls) -> None:
        """Force reload all textures from the configuration file.

        Call this after modifying textures.json to pick up changes.
        """
        type(cls)._loaded = False
        type(cls)._textures.clear()
        type(cls)._ensure_loaded(cls)

    @classmethod
    def preload(cls) -> None:
        """Preload all textures immediately.

        Call this during game initialization to load all textures
        upfront rather than on first access. This improves performance
        when loading levels.
        """
        type(cls)._ensure_loaded(cls)

    @classmethod
    def get_config(cls) -> dict:
        """Get the raw texture configuration dictionary.

        Returns:
            The textures section from textures.json.
        """
        type(cls)._ensure_loaded(cls)
        return type(cls)._config.get("textures", {})
