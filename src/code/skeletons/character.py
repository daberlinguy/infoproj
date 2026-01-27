"""Character animation and rendering module.

This module provides classes for managing animated characters in the game.
It includes frame-based animation support and character state management.

Example:
    Creating a simple animated character::

        from skeletons.character import Character, Animation

        # Load animation frames
        walk_frames = Character.load_frames("sprites/", ["walk1.png", "walk2.png"])
        idle_frames = Character.load_frames("sprites/", ["idle.png"])

        # Create animations dictionary
        animations = {
            "idle": Animation(idle_frames, fps=1, loop=True),
            "walk": Animation(walk_frames, fps=12, loop=True),
        }

        # Create character
        character = Character(
            position=(100, 100),
            animations=animations,
            default_state="idle",
            scale=1.5,
        )

        # In game loop
        character.update(dt)
        character.draw(screen)
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

import pygame


class Animation:
    """Frame-based animation controller.

    Manages a sequence of frames with timing control for smooth animations.

    Attributes:
        frames: List of pygame Surface objects representing animation frames.
        fps: Frames per second for playback.
        loop: Whether the animation loops or stops at the last frame.
        index: Current frame index.
        time_accum: Accumulated time for frame timing.

    Args:
        frames: List of pygame Surface objects.
        fps: Animation speed in frames per second. Minimum is 1.
        loop: If True, animation loops; if False, stops at last frame.

    Example::

        walk_animation = Animation(
            frames=[frame1, frame2, frame3],
            fps=12,
            loop=True,
        )
    """

    def __init__(
        self,
        frames: List[pygame.Surface],
        fps: int = 12,
        loop: bool = True,
    ) -> None:
        self.frames: List[pygame.Surface] = frames
        self.fps: int = max(1, fps)
        self.loop: bool = loop
        self.index: int = 0
        self.time_accum: float = 0.0

    def reset(self) -> None:
        """Reset the animation to the first frame."""
        self.index = 0
        self.time_accum = 0.0

    def update(self, dt: float) -> None:
        """Advance the animation based on elapsed time.

        Args:
            dt: Delta time in seconds since last update.
        """
        if len(self.frames) <= 1:
            return

        frame_time = 1.0 / self.fps
        self.time_accum += dt

        while self.time_accum >= frame_time:
            self.time_accum -= frame_time
            self.index += 1

            if self.index >= len(self.frames):
                if self.loop:
                    self.index = 0
                else:
                    self.index = len(self.frames) - 1

    def get_frame(self) -> pygame.Surface:
        """Get the current animation frame.

        Returns:
            The pygame Surface for the current frame.
        """
        return self.frames[self.index]


class Character:
    """Animated character with state-based animation management.

    Handles rendering, animation state transitions, and sprite transformations
    for game characters.

    Attributes:
        position: Current position as pygame.Vector2.
        animations: Dictionary mapping state names to Animation objects.
        scale_x: Horizontal scale factor.
        scale_y: Vertical scale factor.
        facing: Direction the character faces (1 = right, -1 = left).
        state: Current animation state name.
        animation: Current Animation object.

    Args:
        position: Initial (x, y) position as tuple or Vector2.
        animations: Dictionary of state name -> Animation mappings.
        default_state: Initial animation state. Defaults to "idle".
        scale: Uniform scale factor (used if scale_x/scale_y not set).
        scale_x: Horizontal scale factor. Overrides scale if provided.
        scale_y: Vertical scale factor. Overrides scale if provided.

    Example::

        character = Character(
            position=(400, 300),
            animations={
                "idle": idle_anim,
                "walk": walk_anim,
                "jump": jump_anim,
            },
            default_state="idle",
            scale_x=0.5,
            scale_y=0.5,
        )
    """

    # Standard animation state names used by update_state()
    STATE_IDLE = "idle"
    STATE_WALK = "walk"
    STATE_JUMP = "jump"
    STATE_FLY = "fly"
    STATE_LAND = "land"
    _frames_cache: Dict[Tuple[str, Tuple[str, ...], float], List[pygame.Surface]] = {}

    def __init__(
        self,
        position: Tuple[float, float],
        animations: Dict[str, Animation],
        default_state: str = "idle",
        scale: float = 1.0,
        scale_x: Optional[float] = None,
        scale_y: Optional[float] = None,
    ) -> None:
        self.position: pygame.Vector2 = pygame.Vector2(position)
        self.animations: Dict[str, Animation] = animations
        self.scale_x: float = scale if scale_x is None else scale_x
        self.scale_y: float = scale if scale_y is None else scale_y
        self.facing: int = 1  # 1 = right, -1 = left

        # Set initial state, fallback to first available if default not found
        self.state: str = (
            default_state if default_state in animations else next(iter(animations))
        )
        self.animation: Animation = animations[self.state]

    def set_state(self, name: str, force: bool = False) -> None:
        """Change the current animation state.

        Args:
            name: Name of the animation state to switch to.
            force: If True, resets animation even if already in this state.
        """
        if name == self.state and not force:
            return
        if name not in self.animations:
            return

        self.state = name
        self.animation = self.animations[name]
        self.animation.reset()

    def update_state(
        self,
        is_on_ground: bool,
        is_moving: bool,
        is_flying: bool = False,
        is_landing: bool = False,
    ) -> None:
        """Automatically update animation state based on character conditions.

        This method implements standard platformer animation logic.
        States are checked in priority order: fly > jump > land > walk > idle.

        Args:
            is_on_ground: True if the character is standing on a surface.
            is_moving: True if the character has horizontal movement input.
            is_flying: True if the character is in a flying state.
            is_landing: True if the character just landed this frame.
        """
        if is_flying and self.STATE_FLY in self.animations:
            self.set_state(self.STATE_FLY)
        elif not is_on_ground and self.STATE_JUMP in self.animations:
            self.set_state(self.STATE_JUMP)
        elif is_landing and self.STATE_LAND in self.animations:
            self.set_state(self.STATE_LAND)
        elif is_moving and self.STATE_WALK in self.animations:
            self.set_state(self.STATE_WALK)
        else:
            self.set_state(self.STATE_IDLE)

    def update(self, dt: float) -> None:
        """Update the current animation.

        Args:
            dt: Delta time in seconds since last update.
        """
        self.animation.update(dt)

    def get_draw_size(self) -> Tuple[int, int]:
        """Get the scaled dimensions of the current frame.

        Returns:
            Tuple of (width, height) in pixels after scaling.
        """
        frame = self.animation.get_frame()
        width = int(frame.get_width() * self.scale_x)
        height = int(frame.get_height() * self.scale_y)
        return width, height

    def set_center(self, center_pos: pygame.Vector2) -> None:
        """Position the character so its center is at the given point.

        Args:
            center_pos: The target center position as Vector2.
        """
        width, height = self.get_draw_size()
        self.position.x = center_pos.x - width / 2
        self.position.y = center_pos.y - height / 2

    def draw(self, screen: pygame.Surface) -> None:
        """Render the character to the screen.

        Applies scaling and horizontal flip based on facing direction.

        Args:
            screen: The pygame Surface to draw to.
        """
        frame = self.animation.get_frame()

        # Apply scaling if needed
        if self.scale_x != 1.0 or self.scale_y != 1.0:
            width = int(frame.get_width() * self.scale_x)
            height = int(frame.get_height() * self.scale_y)
            frame = pygame.transform.scale(frame, (width, height))

        # Flip horizontally if facing left
        if self.facing == -1:
            frame = pygame.transform.flip(frame, True, False)

        screen.blit(frame, self.position)

    @staticmethod
    def load_frames(
        folder: str,
        names: List[str],
        scale: float = 1.0,
    ) -> List[pygame.Surface]:
        """Load a list of image files as animation frames.

        Args:
            folder: Directory containing the image files.
            names: List of filenames to load.
            scale: Optional scale factor to apply to all frames.

        Returns:
            List of pygame Surfaces ready for animation.

        Example::

            frames = Character.load_frames(
                "assets/sprites/",
                ["walk1.png", "walk2.png", "walk3.png"],
                scale=0.5,
            )
        """
        cache_key = (folder, tuple(names), scale)
        cached_frames = Character._frames_cache.get(cache_key)
        if cached_frames is not None:
            return cached_frames

        frames: List[pygame.Surface] = []

        for name in names:
            image_path = os.path.join(folder, name)
            image = pygame.image.load(image_path).convert_alpha()

            if scale != 1.0:
                width = int(image.get_width() * scale)
                height = int(image.get_height() * scale)
                image = pygame.transform.scale(image, (width, height))

            frames.append(image)

        Character._frames_cache[cache_key] = frames
        return frames
