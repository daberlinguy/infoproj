---
title: Animation API
description: API reference for the Animation class
---

# Animation API Reference

The `Animation` class manages frame-based sprite animations.

## Module Location

```python
from skeletons.character import Animation
```

## Class Definition

```python
class Animation:
    """Frame-based animation controller."""
    
    def __init__(
        self,
        frames: List[pygame.Surface],
        fps: int = 12,
        loop: bool = True,
    ) -> None: ...
    
    def reset(self) -> None: ...
    def update(self, dt: float) -> None: ...
    def get_frame(self) -> pygame.Surface: ...
```

## Constructor

```python
Animation(frames, fps=12, loop=True)
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `frames` | `List[pygame.Surface]` | - | Animation frame images |
| `fps` | `int` | `12` | Frames per second (minimum: 1) |
| `loop` | `bool` | `True` | Whether to loop the animation |

**Example:**
```python
from skeletons.character import Animation, Character

# Load frames
frames = Character.load_frames("sprites/", ["walk1.png", "walk2.png"])

# Create animation
walk_anim = Animation(frames, fps=12, loop=True)
```

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `frames` | `List[pygame.Surface]` | The animation frames |
| `fps` | `int` | Playback speed |
| `loop` | `bool` | Whether animation loops |
| `index` | `int` | Current frame index |
| `time_accum` | `float` | Accumulated time for timing |

## Methods

### reset()

Reset the animation to the first frame.

```python
animation.reset()
```

### update(dt)

Advance the animation based on elapsed time.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `dt` | `float` | Delta time in seconds |

```python
# In game loop
animation.update(delta_time)
```

### get_frame()

Get the current frame Surface.

**Returns:** `pygame.Surface`

```python
frame = animation.get_frame()
screen.blit(frame, position)
```

## Looping Behavior

**When `loop=True`:**
- Animation cycles back to frame 0 after the last frame

**When `loop=False`:**
- Animation stops at the last frame
- Useful for one-shot animations (jump, attack, etc.)

## Example Usage

```python
from skeletons.character import Animation, Character

# Create animations
idle_frames = Character.load_frames("sprites/", ["idle.png"])
walk_frames = Character.load_frames("sprites/", ["walk1.png", "walk2.png", "walk3.png"])
jump_frames = Character.load_frames("sprites/", ["jump.png"])

animations = {
    "idle": Animation(idle_frames, fps=1, loop=True),
    "walk": Animation(walk_frames, fps=12, loop=True),
    "jump": Animation(jump_frames, fps=12, loop=False),
}

# In game loop
current_animation = animations["walk"]
current_animation.update(dt)
frame = current_animation.get_frame()
screen.blit(frame, (x, y))
```
