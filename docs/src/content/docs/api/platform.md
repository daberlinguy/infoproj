---
title: Platform API
description: API reference for the Platform class
---

# Platform API Reference

The `Platform` class represents interactive level geometry.

## Module Location

```python
from skeletons.platform import Platform, Grid, Cell
```

## Cell Class

The `Cell` class represents a single grid cell used by `Platform` rendering.

```python
Cell(
    x: int,
    y: int,
    size: int,
    color: Tuple[int, int, int] = (100, 100, 100),
    texture: Optional[pygame.Surface] = None,
)
```

**Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| `rect` | `pygame.Rect` | Cell rectangle |
| `color` | `Tuple[int, int, int]` | RGB color |
| `texture` | `pygame.Surface` | Optional texture |
| `size` | `int` | Cell size in pixels |

**Methods:**

### draw(screen, platform_type=None, checkpoint_activated=False)

Draw the cell to the screen.

```python
cell.draw(screen)
```

---

## Grid Class

The `Grid` class provides a toggleable debug grid overlay.

```python
Grid(
    cell_size: int = 16,
    color: Tuple[int, int, int] = (50, 50, 50),
    line_width: int = 1,
)
```

**Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| `cell_size` | `int` | Size of grid cells |
| `color` | `Tuple[int, int, int]` | Grid line color |
| `line_width` | `int` | Line width in pixels |
| `visible` | `bool` | Whether grid is shown |

**Methods:**

### toggle()

Toggle the grid on/off.

### set_cell_size(size)

Set the grid size, clamped between 10-200.

### draw(screen)

Draw the grid if `visible` is `True`.

### snap_to_grid(x, y)

Snap coordinates to the nearest grid point.

**Returns:** `(x, y)` tuple

## Class Constants

### Platform Types

```python
Platform.NORMAL     # "normal"
Platform.DEATH      # "death"
Platform.SPAWN      # "spawn"
Platform.CHECKPOINT # "checkpoint"
Platform.FINISH     # "finish"
Platform.SLIPPERY   # "slippery"
Platform.NOCLIP     # "noclip"
Platform.BOOST_UP   # "boost_up"
Platform.SPEED_UP   # "speed_up"
Platform.SLOW_DOWN  # "slow_down"
```

**Note:** These constants are now provided by the `PlatformTypes` utility class. See [Utility Modules API](utils) for more details.

## Constructor

```python
Platform(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    grid_size: int,
    platform_types: Optional[List[str]] = None,
    color: Optional[Tuple[int, int, int]] = None,
    texture: Optional[pygame.Surface] = None,
    velocity_x: float = 0,
    layer: int = 0,
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
| `platform_types` | `List[str]` | `["normal"]` | List of platform type constants |
| `color` | `tuple` | Based on type | RGB color tuple |
| `texture` | `Surface` | `None` | Texture to apply |
| `velocity_x` | `float` | `0` | Movement speed (px/sec) |
| `layer` | `int` | `0` | Rendering layer (-10 to +10) |

**Layer System:**
- Range: -10 (far background) to +10 (far foreground)
- Negative layers: 10% darker per layer (background depth)
- Positive layers: 10% brighter per layer (foreground pop)
- Layer 0: Normal rendering (no tint)
- Platforms are rendered in layer order (background to foreground)

**Multiple Types:**
Platforms can now have multiple types simultaneously by passing a list:
```python
# Platform that's both a checkpoint and slippery
Platform(..., platform_types=["checkpoint", "slippery"])
```

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `platform_types` | `List[str]` | List of type constants |
| `checkpoint_activated` | `bool` | Checkpoint state |
| `grid_size` | `int` | Cell size |
| `velocity_x` | `float` | Horizontal velocity |
| `color` | `tuple` | RGB color |
| `texture` | `Surface` | Optional texture |
| `layer` | `int` | Rendering layer (-10 to +10) |
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

Get friction coefficient for the platform.

**Returns:** 
- `0.05` if platform has SLIPPERY type
- `0.8` otherwise (normal friction)

**Note:** Uses the `PlatformTypes.get_friction()` utility method.

```python
friction = platform.get_friction()
```

### Type Checking Methods

These methods check if a platform has a specific type:

```python
platform.is_deadly()      # True if has DEATH type
platform.is_checkpoint()  # True if has CHECKPOINT type
platform.is_finish()      # True if has FINISH type
platform.is_spawn()       # True if has SPAWN type
platform.is_noclip()      # True if has NOCLIP type
platform.is_boost_up()    # True if has BOOST_UP type
platform.is_speed_up()    # True if has SPEED_UP type
platform.is_slow_down()   # True if has SLOW_DOWN type
```

### get_speed_multiplier()

Get movement speed multiplier for the platform.

**Returns:**
- `1.5` for `SPEED_UP`
- `0.5` for `SLOW_DOWN`
- `1.0` otherwise

**Note:** Since platforms can have multiple types, these methods check if the type is present in the `platform_types` list.

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
    platform_types=["death"],
    texture=Texture.LAVA,
)

# Moving platform
moving = Platform(
    x1=500, y1=400,
    x2=600, y2=400,
    grid_size=32,
    velocity_x=50,  # 50 px/sec
)

# Background platform (darker due to layer)
background = Platform(
    x1=0, y1=0,
    x2=800, y2=600,
    grid_size=32,
    layer=-5,  # Background layer (50% darker)
    texture=Texture.STONE,
)

# Foreground platform (brighter due to layer)
foreground = Platform(
    x1=100, y1=100,
    x2=200, y2=100,
    grid_size=32,
    layer=3,  # Foreground layer (30% brighter)
)

# Multi-type platform (checkpoint + slippery)
checkpoint_ice = Platform(
    x1=400, y1=300,
    x2=500, y2=300,
    grid_size=32,
    platform_types=["checkpoint", "slippery"],
    texture=Texture.ICE,
)

# Boost platform (passes through, boosts upward)
boost_pad = Platform(
    x1=600, y1=400,
    x2=700, y2=400,
    grid_size=32,
    platform_types=["noclip", "boost_up"],
)

# In game loop
for platform in platforms:
    platform.update(dt)
    platform.draw(screen)
```

## See Also

- [Utility Modules API](utils) - ColorUtils and PlatformTypes used internally
- [Level Format Reference](../reference/level-format) - JSON structure for platforms
- [Platform Types Reference](../reference/platform-types) - Detailed type descriptions
