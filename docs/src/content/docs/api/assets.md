---
title: Assets API
description: API reference for asset loading functions
---

# Assets API Reference

Functions and classes for loading game assets.

## Module Location

```python
from assets.assets import (
    getFont,
    getMinecraftTexture,
    get_texture_config,
    get_platform_types,
    get_texture_names,
    Texture,
)
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

### get_texture_config()

Load the full texture configuration from `textures.json`.

```python
def get_texture_config() -> dict
```

**Returns:** Configuration dictionary with atlas, textures, and platform types.

---

### get_platform_types()

Get the list of platform type names defined in `textures.json`.

```python
def get_platform_types() -> List[str]
```

**Example:**
```python
types = get_platform_types()
print(types)  # ['NORMAL', 'DEATH', 'CHECKPOINT', ...]
```

---

### get_texture_names()

Get the list of available texture names.

```python
def get_texture_names() -> List[str]
```

**Example:**
```python
names = get_texture_names()
print(names)  # ['GRASS', 'ICE', 'STONE', ...]
```

---

## Texture Class

Dynamically loaded textures from `textures.json`.

```python
class Texture:
    # Dynamically generated attributes
    GRASS: pygame.Surface
    STONE: pygame.Surface
    ICE: pygame.Surface
    LAVA: pygame.Surface
    # ...and more from textures.json

    @classmethod
    def get(cls, name: str) -> Optional[pygame.Surface]: ...

    @classmethod
    def list_all(cls) -> List[str]: ...

    @classmethod
    def reload(cls) -> None: ...

    @classmethod
    def get_config(cls) -> dict: ...
```

**Example:**
```python
from assets.assets import Texture
from skeletons.platform import Platform

platform = Platform(..., texture=Texture.GRASS)
```

---

## Texture Helper Methods

### Texture.get(name)

Get a texture by string name.

```python
texture = Texture.get("GRASS")
```

---

### Texture.list_all()

List all texture names loaded from config.

```python
names = Texture.list_all()
```

---

### Texture.reload()

Reload textures after editing `textures.json`.

```python
Texture.reload()
```

---

### Texture.get_config()

Return the raw `textures` dictionary from config.

```python
config = Texture.get_config()
```

---

## Adding Custom Textures

```python
# In assets.py, add to Texture class:
class Texture:
    # ... existing textures ...
    MY_TEXTURE = getMinecraftTexture(x, y, 16, 16)
```

With dynamic textures, you can also add entries directly in `textures.json` without touching code. See [Using Textures](../guides/using-textures).
