from __future__ import annotations

from typing import List

import pygame


class Trigger:
    TYPE_PLATE = "plate"
    TYPE_BUTTON = "button"
    TYPE_LEVER = "lever"

    def __init__(
        self,
        trigger_id: str,
        x: int,
        y: int,
        width: int,
        height: int,
        trigger_type: str,
        targets: List[str],
        duration: float = 1.5,
    ) -> None:
        self.trigger_id = trigger_id
        self.rect = pygame.Rect(x, y, width, height)
        self.trigger_type = trigger_type
        self.targets = targets
        self.duration = duration
        self.active = False
        self._timer = 0.0
        self._was_overlapping = False
        self._was_pressed = False

    def update(self, player_rect: pygame.Rect, keys, dt: float) -> None:
        overlapping = self.rect.colliderect(player_rect)

        if self.trigger_type == Trigger.TYPE_PLATE:
            self.active = overlapping

        elif self.trigger_type == Trigger.TYPE_BUTTON:
            if overlapping and not self._was_overlapping:
                self._timer = self.duration
            if self._timer > 0:
                self._timer = max(0.0, self._timer - dt)
            self.active = self._timer > 0.0

        elif self.trigger_type == Trigger.TYPE_LEVER:
            pressed = bool(keys[pygame.K_e]) if keys is not None else False
            if overlapping and pressed and not self._was_pressed:
                self.active = not self.active
            self._was_pressed = pressed

        self._was_overlapping = overlapping

    def is_active(self) -> bool:
        return self.active

    def draw_debug(self, surface: pygame.Surface) -> None:
        color = (120, 120, 120)
        if self.trigger_type == Trigger.TYPE_PLATE:
            color = (180, 180, 40)
        elif self.trigger_type == Trigger.TYPE_BUTTON:
            color = (40, 180, 180)
        elif self.trigger_type == Trigger.TYPE_LEVER:
            color = (180, 40, 180)

        pygame.draw.rect(surface, color, self.rect, 2)
