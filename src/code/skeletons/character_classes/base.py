"""Base character class for creating playable characters.

This module provides the base `CharacterClass` that serves as a template
for creating new playable characters with custom sprites and animations.

Example:
    Creating a new character class::

        from skeletons.character_classes.base import CharacterClass

        class MyCharacter(CharacterClass):
            name = "Hero"
            sprite_scale = (0.3, 0.3)  # 30% of original size

            # Optional: Custom collider (hitbox) size
            collider_size = (40, 60)  # width, height in pixels

            # Animation frames (must be in assets/sprites/)
            walk_frames = [
                "hero_walk1.png",
                "hero_walk2.png",
                "hero_walk3.png",
            ]
            jump_frames = [
                "hero_jump.png",
            ]

        # Register in CHARACTER_REGISTRY (characters.py)
        CHARACTER_REGISTRY = {
            "my_hero": MyCharacter,
        }
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import pygame

from skeletons.character import Animation, Character
from utils.paths import assets_path


class CharacterClass:
    """Base class for defining playable characters.

    Subclass this to create new characters with custom sprites and animations.
    Override class attributes to customize appearance and behavior.

    Class Attributes:
        name: Display name shown in character selection. Required.
        sprite_scale: Tuple of (scale_x, scale_y) for rendering size.
        collider_size: Optional fixed (width, height) for collision box.
            If None, uses sprite dimensions.
        collider_scale: Optional (scale_x, scale_y) to calculate collider
            from sprite size. Ignored if collider_size is set.
        walk_frames: List of filenames for walk animation.
            First frame is also used for idle.
        jump_frames: List of filenames for jump animation.

    Note:
        All sprite files must be located in the ``assets/sprites/`` folder.

    Example::

        class Ninja(CharacterClass):
            name = "Shadow Ninja"
            sprite_scale = (0.25, 0.25)
            walk_frames = ["ninja_run1.png", "ninja_run2.png"]
            jump_frames = ["ninja_jump.png"]
    """

    # Display name shown in character selection
    name: str = "Character"

    # Scale factor for sprite rendering (scale_x, scale_y)
    sprite_scale: Tuple[float, float] = (0.25, 0.25)

    # Optional fixed collider size (width, height) in pixels
    # If None, calculated from sprite size
    collider_size: Optional[Tuple[int, int]] = None

    # Optional collider scale relative to sprite (scale_x, scale_y)
    # Only used if collider_size is None
    collider_scale: Optional[Tuple[float, float]] = None

    # Subfolder within sprites/ for this character's assets
    # e.g., "characters/dino" -> assets/sprites/characters/dino/
    sprite_folder: Optional[str] = None

    # Animation frame filenames (relative to sprite_folder or sprites/)
    walk_frames: List[str] = []
    jump_frames: List[str] = []

    def __init__(self, base_folder: Optional[str] = None) -> None:
        """Initialize the character class.

        Args:
            base_folder: Optional custom folder for sprite files.
                Defaults to assets/sprites/{sprite_folder}/ or assets/sprites/.
        """
        if base_folder is not None:
            self.base_folder = base_folder
        elif self.sprite_folder is not None:
            self.base_folder = assets_path("sprites", self.sprite_folder)
        else:
            self.base_folder = assets_path("sprites")

    def animations(self) -> Dict[str, Animation]:
        """Build the animations dictionary for this character.

        Creates idle, walk, and jump animations from the defined frame lists.
        The idle animation uses the first walk frame.

        Returns:
            Dictionary mapping animation state names to Animation objects.
        """
        animations: Dict[str, Animation] = {}

        if self.walk_frames:
            # Idle uses first walk frame
            animations["idle"] = Animation(
                Character.load_frames(self.base_folder, [self.walk_frames[0]]),
                fps=1,
                loop=True,
            )
            # Walk animation
            animations["walk"] = Animation(
                Character.load_frames(self.base_folder, self.walk_frames),
                fps=12,
                loop=True,
            )

        if self.jump_frames:
            animations["jump"] = Animation(
                Character.load_frames(self.base_folder, self.jump_frames),
                fps=12,
                loop=False,
            )

        return animations

    def build(self, position: pygame.Vector2) -> Character:
        """Create a Character instance from this class definition.

        Args:
            position: Initial position for the character.

        Returns:
            A fully configured Character instance.
        """
        character_animations = self.animations()
        default_state = (
            "idle" if "idle" in character_animations else next(iter(character_animations))
        )
        scale_x, scale_y = self.sprite_scale

        return Character(
            position,
            character_animations,
            default_state=default_state,
            scale_x=scale_x,
            scale_y=scale_y,
        )

    def get_collider_size(
        self,
        default_width: int,
        default_height: int,
    ) -> Tuple[int, int]:
        """Calculate the collision box size for this character.

        Args:
            default_width: Default width from player sprite settings.
            default_height: Default height from player sprite settings.

        Returns:
            Tuple of (width, height) for the collision box.
        """
        if self.collider_size is not None:
            return self.collider_size

        if self.collider_scale is not None:
            scale_x, scale_y = self.collider_scale
            return int(default_width * scale_x), int(default_height * scale_y)

        return default_width, default_height
