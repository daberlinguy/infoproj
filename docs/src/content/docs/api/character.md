---
title: Character API
description: API reference for the Character class and helpers
---

# Character API Reference

The `Character` class renders and animates player characters using state-based animations. It works with the `Animation` class and is commonly created via `CharacterClass.build()`.

## Module Location

```python
from skeletons.character import Character
```

## Overview

Use `Character` to:
- Manage animation state (`idle`, `walk`, `jump`, etc.)
- Update animations each frame
- Draw sprites with scaling and facing

## Constructor

```python
Character(
    position: Tuple[float, float],
    animations: Dict[str, Animation],
    default_state: str = "idle",
    scale: float = 1.0,
    scale_x: Optional[float] = None,
    scale_y: Optional[float] = None,
)
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `position` | `Tuple[float, float]` | - | Initial position in pixels |
| `animations` | `Dict[str, Animation]` | - | State → Animation mapping |
| `default_state` | `str` | `"idle"` | Initial animation state |
| `scale` | `float` | `1.0` | Uniform scale if `scale_x`/`scale_y` not set |
| `scale_x` | `float` | `None` | Horizontal scale override |
| `scale_y` | `float` | `None` | Vertical scale override |

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `position` | `pygame.Vector2` | Current position (top-left) |
| `animations` | `Dict[str, Animation]` | Animation map |
| `scale_x` | `float` | Horizontal scale |
| `scale_y` | `float` | Vertical scale |
| `facing` | `int` | `1` for right, `-1` for left |
| `state` | `str` | Current animation state |
| `animation` | `Animation` | Active animation |

## State Constants

```python
Character.STATE_IDLE
Character.STATE_WALK
Character.STATE_JUMP
Character.STATE_FLY
Character.STATE_LAND
```

## Methods

### set_state(name, force=False)

Switch the current animation state.

```python
character.set_state("walk")
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `str` | - | State name to switch to |
| `force` | `bool` | `False` | Reset animation even if already in state |

---

### update_state(is_on_ground, is_moving, is_flying=False, is_landing=False)

Automatically select a state based on movement flags.

```python
character.update_state(is_on_ground=True, is_moving=False)
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `is_on_ground` | `bool` | - | True if standing |
| `is_moving` | `bool` | - | True if moving horizontally |
| `is_flying` | `bool` | `False` | Flying state (optional) |
| `is_landing` | `bool` | `False` | Just landed this frame |

---

### update(dt)

Advance the active animation.

```python
character.update(delta_time)
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `dt` | `float` | Delta time in seconds |

---

### get_draw_size()

Get the scaled width/height of the current frame.

**Returns:** `(width, height)` in pixels.

---

### set_center(center_pos)

Position the character so its center is at `center_pos`.

```python
character.set_center(pygame.Vector2(400, 300))
```

---

### draw(screen)

Draw the current frame with scaling and facing.

```python
character.draw(screen)
```

---

### load_frames(folder, names, scale=1.0)

Static helper to load frames from a folder.

```python
frames = Character.load_frames(
    "assets/sprites/characters/hero",
    ["walk1.png", "walk2.png"],
    scale=0.5,
)
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `folder` | `str` | - | Folder path containing images |
| `names` | `List[str]` | - | Filenames to load |
| `scale` | `float` | `1.0` | Optional scale factor |

**Returns:** `List[pygame.Surface]`

## Usage Example

```python
from skeletons.character import Character, Animation

idle_frames = Character.load_frames("assets/sprites/hero", ["idle.png"])
walk_frames = Character.load_frames("assets/sprites/hero", ["walk1.png", "walk2.png"])

animations = {
    "idle": Animation(idle_frames, fps=1, loop=True),
    "walk": Animation(walk_frames, fps=12, loop=True),
}

character = Character((100, 100), animations, default_state="idle", scale=0.5)

# In game loop
character.update_state(is_on_ground=True, is_moving=True)
character.update(dt)
character.draw(screen)
```

## Related Links

- [Animation API](../api/animation)
- [Character Class Reference](../reference/character-class)
