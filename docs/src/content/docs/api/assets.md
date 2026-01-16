---
title: Assets API
description: API reference for asset loading functions
---

# Assets API Reference

Functions and classes for loading game assets.

## Module Location

```python
from assets.assets import getFont, getMinecraftTexture, Texture
```

## Functions

### getFont(size)

Get a cached font at the specified size.

```python
def getFont(size: int) -> pygame.font.Font
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `size` | `int` | Font size (1-99) |

**Returns:** `pygame.font.Font`

**Raises:** `RuntimeError` if size < 0 or > 100

**Example:**
```python
title_font = getFont(60)
small_font = getFont(16)

text = title_font.render("Hello", True, (255, 255, 255))
```

---

### getMinecraftTexture(...)

Extract a texture region from the texture atlas.

```python
def getMinecraftTexture(
    location_x: int,
    location_y: int,
    width: int,
    height: int,
    top_left: Tuple[int, int] = (0, 0),
) -> pygame.Surface
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `location_x` | `int` | - | X in atlas (pixels) |
| `location_y` | `int` | - | Y in atlas (pixels) |
| `width` | `int` | - | Width to extract |
| `height` | `int` | - | Height to extract |
| `top_left` | `tuple` | `(0, 0)` | Output offset |

**Returns:** `pygame.Surface`

**Example:**
```python
# Extract 16x16 texture at position (352, 576)
grass = getMinecraftTexture(352, 576, 16, 16)
```

---

## Texture Class

Pre-loaded textures from the atlas.

```python
class Texture:
    GRASS: pygame.Surface
    STONE: pygame.Surface
    ICE: pygame.Surface
    ICEBROKEN: pygame.Surface
    ICEBROKEN2: pygame.Surface
    ICEBROKEN3: pygame.Surface
    LAVA: pygame.Surface
    GOLD_BLOCK: pygame.Surface
    FLETCHINGTABLE: pygame.Surface
    FLETCHINGTABLE2: pygame.Surface
    FLETCHINGTABLE3: pygame.Surface
    OVENOFF: pygame.Surface
    OVENON: pygame.Surface
    OVENBEHIND: pygame.Surface
    OVENTOP: pygame.Surface
```

**Example:**
```python
from assets.assets import Texture
from skeletons.platform import Platform

platform = Platform(..., texture=Texture.GRASS)
```

---

## Adding Custom Textures

```python
# In assets.py, add to Texture class:
class Texture:
    # ... existing textures ...
    MY_TEXTURE = getMinecraftTexture(x, y, 16, 16)
```
