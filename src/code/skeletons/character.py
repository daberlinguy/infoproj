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
    _transform_cache: dict = {}

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
        self.index = 0
        self.time_accum = 0.0

    def update(self, dt: float) -> None:
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

    def get_frame(self, scale_x: float = 1.0, scale_y: float = 1.0, flip: bool = False) -> pygame.Surface:
        frame = self.frames[self.index]
        if scale_x == 1.0 and scale_y == 1.0 and not flip:
            return frame
        
        cache_key = (id(frame), scale_x, scale_y, flip)
        cached = Animation._transform_cache.get(cache_key)
        if cached is not None:
            return cached

        result = frame
        if scale_x != 1.0 or scale_y != 1.0:
            width = int(frame.get_width() * scale_x)
            height = int(frame.get_height() * scale_y)
            result = pygame.transform.scale(frame, (width, height))

        if flip:
            result = pygame.transform.flip(result, True, False)

        Animation._transform_cache[cache_key] = result
        return result


class Character:
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
        self._animations: Dict[str, Animation] = animations
        self.scale_x: float = scale if scale_x is None else scale_x
        self.scale_y: float = scale if scale_y is None else scale_y
        self.facing: int = 1

        self.state: str = (
            default_state if default_state in animations else next(iter(animations))
        )
        self.animation: Animation = animations[self.state]

    def set_state(self, name: str, force: bool = False) -> None:
        if name == self.state and not force:
            return
        if name not in self.animations:
            return

        self.state = name
        self.animation = self.animations[name]
        self.animation.reset()

    @property
    def animations(self) -> Dict[str, Animation]:
        return self._animations

    @animations.setter
    def animations(self, value: Dict[str, Animation]) -> None:
        self._animations = value

    def update_state(
        self,
        is_on_ground: bool,
        is_moving: bool,
        is_flying: bool = False,
        is_landing: bool = False,
    ) -> None:
        if is_flying and self.STATE_FLY in self._animations:
            self.set_state(self.STATE_FLY)
        elif not is_on_ground and self.STATE_JUMP in self._animations:
            self.set_state(self.STATE_JUMP)
        elif is_landing and self.STATE_LAND in self._animations:
            self.set_state(self.STATE_LAND)
        elif is_moving and self.STATE_WALK in self._animations:
            self.set_state(self.STATE_WALK)
        else:
            self.set_state(self.STATE_IDLE)

    def update(self, dt: float) -> None:
        self.animation.update(dt)

    def get_draw_size(self) -> Tuple[int, int]:
        frame = self.animation.frames[self.animation.index]
        width = int(frame.get_width() * self.scale_x)
        height = int(frame.get_height() * self.scale_y)
        return width, height

    def set_center(self, center_pos: pygame.Vector2) -> None:
        width, height = self.get_draw_size()
        self.position.x = center_pos.x - width / 2
        self.position.y = center_pos.y - height / 2

    def draw(self, screen: pygame.Surface) -> None:
        frame = self.animation.get_frame(
            scale_x=self.scale_x,
            scale_y=self.scale_y,
            flip=(self.facing == -1)
        )
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
