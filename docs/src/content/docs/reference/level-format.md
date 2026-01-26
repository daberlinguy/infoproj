---
title: Level Format Reference
description: Complete JSON schema for level files
---

# Level Format Reference

This page documents the complete JSON schema for level files.

## File Location

Level files are stored in:
```
data/worlds/<world_name>/<level_name>.json
```

## Complete Schema

```json
{
  "name": "string (required)",
  "player_spawn": {
    "x": "number (required)",
    "y": "number (required)",
    "grid": "boolean (default: true)",
    "grid_size": "number (default: 32)"
  },
  "background_color": {
    "r": "number (0-255)",
    "g": "number (0-255)",
    "b": "number (0-255)",
    "a": "number (0-255, optional)",
    "image": "string (optional, overrides color)"
  },
  "pages": {
    "<page_number>": {
      "platforms": [
        {
          "x1": "number",
          "y1": "number",
          "x2": "number (or use w)",
          "y2": "number (or use h)",
          "x": "number (alias for x1)",
          "y": "number (alias for y1)",
          "w": "number (width, alternative to x2)",
          "h": "number (height, alternative to y2)",
          "grid_size": "number (default: 32)",
          "type": "string (legacy, use types instead)",
          "types": "array of strings (NORMAL|DEATH|SPAWN|CHECKPOINT|FINISH|SLIPPERY|NOCLIP|BOOST_UP|BOOST_DOWN)",
          "texture": "string (texture name)",
          "color": "[r, g, b] array",
          "layer": "number (-10 to +10, default: 0)"
        }
      ]
    }
  }
}
```

## Root Properties

### name

| Property | Value |
|----------|-------|
| Type | `string` |
| Required | Yes |
| Description | Display name shown in level selection |

```json
{
  "name": "My Awesome Level"
}
```

### player_spawn

| Property | Value |
|----------|-------|
| Type | `object` |
| Required | Yes |
| Description | Starting position for the player |

**Sub-properties:**

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `x` | `number` | - | X coordinate |
| `y` | `number` | - | Y coordinate |
| `grid` | `boolean` | `true` | If true, x/y are grid units; if false, pixels |
| `grid_size` | `number` | `32` | Size of each grid cell in pixels |

```json
{
  "player_spawn": {
    "x": 5,
    "y": 14,
    "grid": true,
    "grid_size": 32
  }
}
```

### background_color

| Property | Value |
|----------|-------|
| Type | `object` |
| Required | No |
| Default | Purple |
| Description | Background color or image |

**For solid color:**

```json
{
  "background_color": {
    "r": 135,
    "g": 206,
    "b": 235,
    "a": 255
  }
}
```

**For background image:**

```json
{
  "background_color": {
    "image": "sky.jpg"
  }
}
```

Images are loaded from `src/resources/assets/backgrounds/`.

### pages

| Property | Value |
|----------|-------|
| Type | `object` |
| Required | Yes |
| Description | Dictionary of page number to page data |

```json
{
  "pages": {
    "1": { "platforms": [...] },
    "2": { "platforms": [...] }
  }
}
```

## Platform Properties

### Coordinate Properties

Platforms can be defined using two methods:

**Method 1: Corner coordinates (x1, y1, x2, y2)**

```json
{
  "x1": 0,
  "y1": 15,
  "x2": 10,
  "y2": 15
}
```

**Method 2: Position and size (x, y, w, h)**

```json
{
  "x": 0,
  "y": 15,
  "w": 10,
  "h": 0
}
```

Both methods result in a platform from (0, 15) to (10, 15).

### types (New in v2.0)

| Property | Value |
|----------|-------|
| Type | `array of strings` |
| Default | `["NORMAL"]` |
| Values | `NORMAL`, `DEATH`, `SPAWN`, `CHECKPOINT`, `FINISH`, `SLIPPERY`, `NOCLIP`, `BOOST_UP`, `BOOST_DOWN` |

Platforms can now have multiple types simultaneously:

```json
{
  "types": ["CHECKPOINT", "SLIPPERY"]
}
```

```json
{
  "types": ["NOCLIP", "BOOST_UP"]
}
```

### type (Legacy)

| Property | Value |
|----------|-------|
| Type | `string` |
| Default | `"NORMAL"` |
| Values | `NORMAL`, `DEATH`, `SPAWN`, `CHECKPOINT`, `FINISH`, `SLIPPERY`, `NOCLIP`, `BOOST_UP`, `BOOST_DOWN` |
| Status | **Deprecated** - Use `types` array instead |

The old single type format is still supported for backward compatibility:

```json
{
  "type": "CHECKPOINT"
}
```

### texture

| Property | Value |
|----------|-------|
| Type | `string` |
| Default | None (uses color) |
| Values | See [Using Textures](/guides/using-textures) |

```json
{
  "texture": "GRASS"
}
```

### color

| Property | Value |
|----------|-------|
| Type | `array` |
| Format | `[r, g, b]` |
| Default | Based on platform type |

```json
{
  "color": [139, 69, 19]
}
```

### grid_size

| Property | Value |
|----------|-------|
| Type | `number` |
| Default | `32` |
| Description | Size of each grid cell for this platform |

```json
{
  "grid_size": 32
}
```

### layer (New in v2.0)

| Property | Value |
|----------|-------|
| Type | `number` |
| Default | `0` |
| Range | `-10` to `+10` |
| Description | Rendering layer for depth effect |

The layer system creates a visual depth effect:

- **Negative layers (-10 to -1):** Background layers, rendered darker (10% per layer)
- **Layer 0:** Normal rendering, no tint applied
- **Positive layers (+1 to +10):** Foreground layers, rendered brighter (10% per layer)

Platforms are rendered in layer order (background first, foreground last).

```json
{
  "layer": -5
}
```

**Examples:**

```json
// Far background (50% darker)
{
  "x1": 0, "y1": 0, "x2": 60, "y2": 18,
  "layer": -5,
  "texture": "STONE"
}

// Normal layer
{
  "x1": 10, "y1": 15, "x2": 20, "y2": 15,
  "layer": 0,
  "texture": "GRASS"
}

// Foreground (30% brighter)
{
  "x1": 5, "y1": 5, "x2": 8, "y2": 5,
  "layer": 3,
  "texture": "GOLD_BLOCK"
}
```

## Platform Types Reference

### NORMAL

Standard walkable platform.

```json
{
  "x1": 0, "y1": 15, "x2": 10, "y2": 15,
  "type": "NORMAL",
  "texture": "GRASS"
}
```

### DEATH

Kills the player on contact. Player respawns at last checkpoint.

```json
{
  "x1": 5, "y1": 18, "x2": 8, "y2": 18,
  "type": "DEATH",
  "texture": "LAVA"
}
```

### SPAWN

Marks the player's starting position. Usually combined with NORMAL platform below.

```json
{
  "x1": 3, "y1": 14, "x2": 3, "y2": 14,
  "type": "SPAWN"
}
```

### CHECKPOINT

Saves the player's respawn point when touched. Shows flag until activated.

```json
{
  "x1": 20, "y1": 10, "x2": 20, "y2": 10,
  "type": "CHECKPOINT"
}
```

### FINISH

Level completion trigger. All checkpoints must be activated first.

```json
{
  "x1": 35, "y1": 8, "x2": 35, "y2": 8,
  "type": "FINISH"
}
```

### SLIPPERY

Low friction surface (ice). Player slides and has momentum.

```json
{
  "x1": 10, "y1": 12, "x2": 20, "y2": 12,
  "type": "SLIPPERY",
  "texture": "ICE"
}
```

### NOCLIP (New in v2.0)

Platform the player can pass through (no collision). Useful for visual elements or combined with boost types.

```json
{
  "x1": 10, "y1": 10, "x2": 15, "y2": 10,
  "type": "NOCLIP"
}
```

### BOOST_UP (New in v2.0)

Applies upward velocity boost when player passes through. Typically combined with NOCLIP.

```json
{
  "x1": 12, "y1": 8, "x2": 14, "y2": 8,
  "types": ["NOCLIP", "BOOST_UP"]
}
```

### BOOST_DOWN (New in v2.0)

Applies downward velocity boost when player passes through. Typically combined with NOCLIP.

```json
{
  "x1": 20, "y1": 5, "x2": 22, "y2": 5,
  "types": ["NOCLIP", "BOOST_DOWN"]
}
```

## Complete Example

```json
{
  "name": "Complete Example Level",
  "player_spawn": {
    "x": 3,
    "y": 13,
    "grid": true,
    "grid_size": 32
  },
  "background_color": {
    "r": 135,
    "g": 206,
    "b": 235
  },
  "pages": {
    "1": {
      "platforms": [
        {
          "x1": 0,
          "y1": 15,
          "x2": 12,
          "y2": 15,
          "types": ["NORMAL"],
          "texture": "GRASS",
          "grid_size": 32,
          "layer": 0
        },
        {
          "x1": 3,
          "y1": 14,
          "x2": 3,
          "y2": 14,
          "types": ["SPAWN"]
        },
        {
          "x1": 15,
          "y1": 12,
          "x2": 20,
          "y2": 12,
          "types": ["NORMAL"],
          "texture": "STONE"
        },
        {
          "x1": 10,
          "y1": 17,
          "x2": 14,
          "y2": 17,
          "types": ["DEATH"],
          "texture": "LAVA"
        },
        {
          "x1": 23,
          "y1": 9,
          "x2": 28,
          "y2": 9,
          "types": ["SLIPPERY"],
          "texture": "ICE"
        },
        {
          "x1": 30,
          "y1": 8,
          "x2": 30,
          "y2": 8,
          "types": ["CHECKPOINT"]
        },
        {
          "x1": 25,
          "y1": 6,
          "x2": 25,
          "y2": 6,
          "types": ["NOCLIP", "BOOST_UP"],
          "comment": "Boost pad"
        },
        {
          "x1": 0,
          "y1": 0,
          "x2": 40,
          "y2": 18,
          "types": ["NORMAL"],
          "texture": "STONE",
          "layer": -5,
          "comment": "Background layer"
        },
        {
          "x1": 35,
          "y1": 6,
          "x2": 35,
          "y2": 6,
          "types": ["FINISH"]
        }
      ]
    },
    "2": {
      "platforms": [
        {
          "x1": 0,
          "y1": 6,
          "x2": 38,
          "y2": 6,
          "types": ["NORMAL"],
          "texture": "STONE"
        }
      ]
    }
  }
}
```

## Validation

The game validates levels on load:

- Platforms without required coordinates are skipped
- Unknown texture names result in no texture (color used instead)
- Unknown platform types default to NORMAL
- Invalid JSON syntax prevents level from loading

## Multi-Page Considerations

- Page numbers are strings: `"1"`, `"2"`, etc.
- Players transition at x < 0 (previous page) and x > page_width (next page)
- Y position is preserved across transitions
- Checkpoint pages are tracked for respawn
