---
title: Platform API
description: API reference for the Platform class
---

# Platform API Reference

The `Platform` class represents interactive level geometry.

## Module Location

```python
from skeletons.platform import Platform
```

## Class Constants

### Platform Types

```python
Platform.NORMAL     # "normal"
Platform.DEATH      # "death"
Platform.SPAWN      # "spawn"
Platform.CHECKPOINT # "checkpoint"
Platform.FINISH     # "finish"
Platform.SLIPPERY   # "slippery"
```

## Constructor

```python
Platform(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    grid_size: int,
    platform_type: Optional[str] = None,
    color: Optional[Tuple[int, int, int]] = None,
    texture: Optional[pygame.Surface] = None,
    velocity_x: float = 0,
)
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `x1` | `int` | - | Left edge X (pixels) |
| `y1` | `int` | - | Top edge Y (pixels) |
| `x2` | `int` | - | Right edge X (pixels) |
| `y2` | `int` | - | Bottom edge Y (pixels) |
| `grid_size` | `int` | - | Cell size in pixels |
| `platform_type` | `str` | `"normal"` | Platform type constant |
| `color` | `tuple` | Based on type | RGB color tuple |
| `texture` | `Surface` | `None` | Texture to apply |
| `velocity_x` | `float` | `0` | Movement speed (px/sec) |

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `platform_type` | `str` | Type constant |
| `checkpoint_activated` | `bool` | Checkpoint state |
| `grid_size` | `int` | Cell size |
| `velocity_x` | `float` | Horizontal velocity |
| `color` | `tuple` | RGB color |
| `texture` | `Surface` | Optional texture |
| `cells` | `List[Cell]` | Grid cells |
| `rect` | `pygame.Rect` | Bounding rectangle |

## Methods

### draw(screen)

Render the platform.

```python
platform.draw(screen)
```

### update(dt)

Update moving platforms.

```python
platform.update(delta_time)
```

### get_friction()

Get friction coefficient.

**Returns:** `0.05` for SLIPPERY, `0.8` otherwise

```python
friction = platform.get_friction()
```

### Type Checking Methods

```python
platform.is_deadly()      # True if DEATH
platform.is_checkpoint()  # True if CHECKPOINT
platform.is_finish()      # True if FINISH
platform.is_spawn()       # True if SPAWN
```

### activate_checkpoint()

Activate a checkpoint platform.

```python
if platform.is_checkpoint():
    platform.activate_checkpoint()
```

## Example Usage

```python
from skeletons.platform import Platform
from assets.assets import Texture

# Normal platform with texture
ground = Platform(
    x1=0, y1=500,
    x2=800, y2=500,
    grid_size=32,
    texture=Texture.GRASS,
)

# Death platform
spikes = Platform(
    x1=300, y1=550,
    x2=400, y2=550,
    grid_size=32,
    platform_type=Platform.DEATH,
    texture=Texture.LAVA,
)

# Moving platform
moving = Platform(
    x1=500, y1=400,
    x2=600, y2=400,
    grid_size=32,
    velocity_x=50,  # 50 px/sec
)

# In game loop
for platform in platforms:
    platform.update(dt)
    platform.draw(screen)
```
