---
title: Player (Spieler) API
description: API reference for the Spieler physics and collision class
---

# Player (Spieler) API Reference

The `Spieler` class controls player physics, movement, and collision detection against `Platform` objects.

## Module Location

```python
from skeletons.spieler import Spieler
```

## Overview

`Spieler` handles:
- Horizontal movement and jumping
- Gravity and falling speed limits
- Collision resolution with platforms
- Checkpoints and respawn logic

## Constructor

```python
Spieler(player_pos, dt, radius=24)
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `player_pos` | `pygame.Vector2` | - | Shared player position vector |
| `dt` | `float` | - | Delta time in seconds |
| `radius` | `int` | `24` | Legacy radius (kept for compatibility) |

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `player_pos` | `pygame.Vector2` | Shared position vector |
| `sprite_width` | `int` | Collision box width in pixels |
| `sprite_height` | `int` | Collision box height in pixels |
| `velocity_x` | `float` | Horizontal velocity |
| `velocity_y` | `float` | Vertical velocity |
| `gravity` | `float` | Gravity acceleration |
| `jump_strength` | `float` | Jump impulse (negative) |
| `acceleration` | `float` | Slippery acceleration |
| `max_speed` | `float` | Max horizontal speed |
| `max_fall_speed` | `float` | Max vertical speed |
| `friction` | `float` | Current friction coefficient |
| `current_platform` | `Platform` | Platform under player (if any) |
| `is_on_ground` | `bool` | Grounded state |
| `prev_x` | `float` | Previous X position |
| `prev_y` | `float` | Previous Y position |

## Methods

### set_sprite_size(width, height)

Override collision box size to match sprite.

---

### move_left() / move_right()

Move horizontally. Uses acceleration on slippery surfaces and direct movement otherwise.

---

### jump()

Start a jump if grounded.

---

### on_ground()

Return `True` if grounded.

---

### apply_physics(dt)

Apply gravity, friction, and velocity updates.

---

### get_rect()

Get the collision rectangle for the player.

**Returns:** `pygame.Rect`

---

### check_platform_collision(platforms)

Resolve collisions with solid platforms and update `is_on_ground`, `current_platform`, and friction.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `platforms` | `List[Platform]` | Platforms to check |

---

### check_special_platform_interactions(platforms, current_checkpoint)

Check for death/checkpoint platforms.

**Returns:** `(new_checkpoint, should_respawn)`

---

### check_fell_off_screen(screen_height, current_checkpoint)

Respawn if the player fell below the screen.

**Returns:** `True` if respawned

## Usage Example

```python
from skeletons.spieler import Spieler
from skeletons.platform import Platform

player_pos = pygame.Vector2(100, 100)
player = Spieler(player_pos, dt=0)

# In game loop
player.apply_physics(dt)
player.check_platform_collision(platforms)
checkpoint, respawn = player.check_special_platform_interactions(platforms, checkpoint)
if player.check_fell_off_screen(screen_height, checkpoint):
    pass
```

## Related Links

- [Platform API](../api/platform)
- [Platform Types](../reference/platform-types)
