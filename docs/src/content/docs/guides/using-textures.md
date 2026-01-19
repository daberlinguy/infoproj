---
title: Using Textures
description: Work with the texture atlas and create custom textures
---

# Using Textures

This guide explains how to use and create textures for platforms and visual elements.

## Overview

Parkour Game uses a Minecraft-style texture atlas for platform visuals. Textures are 16x16 pixel regions extracted from a single image file.

**New in this version:** Textures are now dynamically loaded from `textures.json`, making it easy to add new textures without modifying Python code!

## Using Built-in Textures

### In Code

```python
from assets.assets import Texture
from skeletons.platform import Platform

# Create a platform with a grass texture
grass_platform = Platform(
    x1=0, y1=500,
    x2=300, y2=500,
    grid_size=32,
    texture=Texture.GRASS,
)

# Get texture by name (useful for dynamic loading)
texture_name = "ICE"
ice_texture = Texture.get(texture_name)

# List all available textures
print(Texture.list_all())  # ['GRASS', 'ICE', 'STONE', ...]
```

### In Level JSON

```json
{
  "platforms": [
    {
      "x1": 0, "y1": 15,
      "x2": 10, "y2": 15,
      "type": "NORMAL",
      "texture": "GRASS"
    },
    {
      "x1": 15, "y1": 12,
      "x2": 20, "y2": 12,
      "type": "SLIPPERY",
      "texture": "ICE"
    }
  ]
}
```

## Available Textures

| Name | Description | Typical Use |
|------|-------------|-------------|
| `GRASS` | Green grass block top | Ground, outdoor platforms |
| `STONE` | Gray stone | Underground, walls |
| `ICE` | Solid ice block | Slippery platforms |
| `ICE_BROKEN` | Cracked ice | Damaged ice |
| `ICE_BROKEN2` | More cracked ice | - |
| `ICE_BROKEN3` | Very cracked ice | - |
| `LAVA` | Orange lava | Death platforms |
| `GOLD_BLOCK` | Gold/yellow block | Special platforms, spawn |
| `FLETCHING_TABLE` | Wood texture | Indoor platforms |
| `FLETCHING_TABLE_SIDE` | Wood side | - |
| `FLETCHING_TABLE_TOP` | Wood top | - |
| `OVEN_OFF` | Furnace (off) | Decoration |
| `OVEN_ON` | Furnace (on) | Decoration |
| `OVEN_BACK` | Furnace back | - |
| `OVEN_TOP` | Furnace top | - |

## Adding Custom Textures (The Easy Way!)

With the new dynamic texture system, adding textures requires **zero code changes**:

### 1. Edit textures.json

Open `src/resources/textures.json` and add your texture:

```json
{
    "textures": {
        "GRASS": { "x": 352, "y": 576, "width": 16, "height": 16 },
        "ICE": { "x": 112, "y": 576, "width": 16, "height": 16 },
        
        "MY_NEW_TEXTURE": {
            "x": 100,
            "y": 200,
            "width": 16,
            "height": 16,
            "description": "My awesome custom texture"
        }
    }
}
```

### 2. That's It!

The texture is now automatically available:

**In code:**
```python
from assets.assets import Texture

# Access as attribute
platform = Platform(..., texture=Texture.MY_NEW_TEXTURE)

# Or by name
texture = Texture.get("MY_NEW_TEXTURE")
```

**In the editor:** The texture appears in the dropdown automatically!

**In JSON levels:**
```json
{ "texture": "MY_NEW_TEXTURE" }
```

## The Texture Atlas

The texture atlas is located at:
```
src/resources/assets/sprites/tiles/texture_atlas.png
```

Add your 16x16 texture to an empty space in the atlas. Note its position (x, y coordinates from top-left).

## Texture Configuration File

The `textures.json` file contains all texture definitions:

```json
{
    "$schema": "./textures.schema.json",
    "_description": "Texture atlas configuration...",
    "atlas": "assets/sprites/tiles/texture_atlas.png",
    "tile_size": 16,
    "textures": {
        "TEXTURE_NAME": {
            "x": 100,          // X position in atlas
            "y": 200,          // Y position in atlas  
            "width": 16,       // Width (usually 16)
            "height": 16,      // Height (usually 16)
            "description": "Optional description"
        }
    },
    "platform_types": [...]
}
```

## Advanced: Loading Separate Images

For textures not in the atlas:

```python
import pygame
from utils.paths import assets_path

def load_custom_texture(filename):
    """Load a texture from a separate file."""
    path = assets_path("sprites", "tiles", filename)
    return pygame.image.load(path).convert_alpha()

# Use it
custom_texture = load_custom_texture("my_texture.png")
platform = Platform(..., texture=custom_texture)
```
```

## Texture Scaling

Textures are automatically scaled to match the grid size. A 16x16 texture becomes 32x32 when used with a 32-pixel grid.

The scaling happens in the `Cell.draw()` method:

```python
def draw(self, screen, ...):
    if self.texture:
        texture_scaled = pygame.transform.scale(
            self.texture, 
            (self.size, self.size)  # Scale to cell size
        )
        screen.blit(texture_scaled, self.rect.topleft)
```

## Color Fallbacks

If no texture is specified, platforms use colors based on their type:

| Platform Type | Default Color | RGB |
|---------------|---------------|-----|
| NORMAL | Gray | (100, 100, 100) |
| DEATH | Red | (255, 0, 0) |
| SPAWN | Green | (0, 255, 0) |
| CHECKPOINT | Yellow | (255, 255, 0) |
| FINISH | Blue | (0, 150, 255) |
| SLIPPERY | Light Blue | (100, 200, 255) |

### Custom Colors

Override the default color:

**In code:**
```python
platform = Platform(
    ...,
    color=(139, 69, 19),  # Brown
)
```

**In JSON:**
```json
{
  "x1": 0, "y1": 15, "x2": 10, "y2": 15,
  "color": [139, 69, 19]
}
```

## Best Practices

### 1. Consistent Sizing

Keep textures at 16x16 for consistency with the atlas system.

### 2. Visual Clarity

- Use distinct textures for different platform types
- Death platforms should look dangerous (lava, spikes)
- Slippery platforms should look icy/smooth

### 3. Performance

- Reuse texture references instead of loading multiple times
- The `Texture` class loads each texture once at startup

### 4. Transparency

Use PNG format with alpha channel for textures that need transparency.

## Texture Atlas Layout

The default atlas (`texture_atlas.png`) is organized in a grid. Here are some key regions:

```
Row 576 (y=576):
- x=48:  FLETCHINGTABLE
- x=64:  FLETCHINGTABLE2  
- x=80:  FLETCHINGTABLE3
- x=112: ICE
- x=128: ICEBROKEN
- x=144: ICEBROKEN2
- x=160: ICEBROKEN3
- x=176: OVENOFF
- x=192: OVENON
- x=208: OVENBEHIND
- x=224: OVENTOP
- x=288: GOLD_BLOCK
- x=352: GRASS

Row 592 (y=592):
- x=400: LAVA

Row 640 (y=640):
- x=640: STONE
```

## Animated Textures

For animated textures (like flowing lava), you would need to:

1. Create multiple texture variants
2. Cycle through them in the draw method
3. Track animation time

This is not implemented in the base game but could be added as an extension.
