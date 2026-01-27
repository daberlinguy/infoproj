---
title: Creating Levels
description: Design custom levels using the JSON level format
---

# Creating Levels

This guide explains how to create new levels for Parkour Game using the JSON level format.

## Overview

Levels are stored as JSON files in the `data/worlds/` directory. Each world is a folder containing level files:

```
data/worlds/
├── world1/
│   ├── level1.json
│   ├── level2.json
│   └── level3.json
├── world2/
│   └── my_level.json
└── tutorial/
    └── intro.json
```

## Basic Level Structure

Here's a minimal level file:

```json
{
  "name": "My First Level",
  "player_spawn": {
    "x": 5,
    "y": 14,
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
          "x1": 0, "y1": 15,
          "x2": 20, "y2": 15,
          "type": "NORMAL",
          "texture": "GRASS"
        }
      ]
    }
  }
}
```

## Level Properties

### Root Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | `string` | Yes | Display name in level selection |
| `player_spawn` | `object` | Yes | Starting position |
| `background_color` | `object` | No | Background RGB color or image |
| `pages` | `object` | Yes | Level pages (screens) |

### Player Spawn

```json
{
  "player_spawn": {
    "x": 5,          // X position
    "y": 14,         // Y position  
    "grid": true,    // true = grid units, false = pixels
    "grid_size": 32  // Grid cell size in pixels
  }
}
```

### Background Options

**Solid Color:**
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

**Background Image:**
```json
{
  "background_color": {
    "image": "sky.jpg"
  }
}
```

## Platform Definition

### Basic Platform

```json
{
  "x1": 0,       // Left edge (grid units)
  "y1": 15,      // Top edge (grid units)
  "x2": 10,      // Right edge (grid units)
  "y2": 15,      // Bottom edge (grid units)
  "type": "NORMAL"
}
```

### Platform with Texture

```json
{
  "x1": 0, "y1": 15,
  "x2": 10, "y2": 15,
  "type": "NORMAL",
  "texture": "GRASS"
}
```

### Platform with Custom Color

```json
{
  "x1": 0, "y1": 15,
  "x2": 10, "y2": 15,
  "type": "NORMAL",
  "color": [139, 69, 19]
}
```

### Moving Platforms + Triggers

Give a platform an `id` and `path`, then add a trigger in the page:

```json
{
  "id": "bridge_1",
  "x1": 8, "y1": 12, "x2": 10, "y2": 12,
  "types": ["NORMAL"],
  "path": {
    "points": [
      {"x": 256, "y": 384},
      {"x": 512, "y": 384, "control": {"x": 420, "y": 300}}
    ],
    "speed": 140,
    "loop": true
  }
}
```

```json
{
  "triggers": [
    {
      "id": "plate_1",
      "type": "plate",
      "x": 300,
      "y": 500,
      "w": 64,
      "h": 16,
      "targets": ["bridge_1"]
    }
  ]
}
```

### Alternative Size Syntax

You can use width/height instead of x2/y2:

```json
{
  "x": 0,      // Same as x1
  "y": 15,     // Same as y1
  "w": 10,     // Width (x2 = x + w)
  "h": 0,      // Height (y2 = y + h)
  "type": "NORMAL"
}
```

## Platform Types

| Type | Description | Visual |
|------|-------------|--------|
| `NORMAL` | Standard walkable platform | Gray or textured |
| `DEATH` | Kills player on contact | Red with X pattern |
| `SPAWN` | Player starting position | Green with "S" |
| `CHECKPOINT` | Saves respawn point | Yellow with flag |
| `FINISH` | Level completion trigger | Blue |
| `SLIPPERY` | Low friction (ice) | Light blue with waves |

## Available Textures

| Texture Name | Description |
|--------------|-------------|
| `GRASS` | Green grass block |
| `STONE` | Gray stone |
| `ICE` | Ice block |
| `LAVA` | Orange lava |
| `GOLD_BLOCK` | Gold/yellow block |
| `FLETCHINGTABLE` | Wood texture |

## Multi-Page Levels

Large levels can span multiple pages. The player transitions between pages when reaching screen edges.

```json
{
  "name": "Multi-Page Level",
  "player_spawn": { "x": 5, "y": 14, "grid": true, "grid_size": 32 },
  "background_color": { "r": 100, "g": 150, "b": 200 },
  "pages": {
    "1": {
      "platforms": [
        { "x1": 0, "y1": 15, "x2": 38, "y2": 15, "texture": "GRASS" },
        { "x1": 5, "y1": 15, "x2": 5, "y2": 15, "type": "SPAWN" }
      ]
    },
    "2": {
      "platforms": [
        { "x1": 0, "y1": 15, "x2": 38, "y2": 15, "texture": "STONE" },
        { "x1": 20, "y1": 10, "x2": 25, "y2": 10, "type": "CHECKPOINT" }
      ]
    },
    "3": {
      "platforms": [
        { "x1": 0, "y1": 15, "x2": 30, "y2": 15, "texture": "GRASS" },
        { "x1": 30, "y1": 12, "x2": 30, "y2": 12, "type": "FINISH" }
      ]
    }
  }
}
```

### Page Dimensions

- Default page width: **40 cells** (1280px at 32px grid)
- Default page height: **23 cells** (736px at 32px grid)
- X coordinates: 0-39 for each page
- Y coordinates: 0-22 (top to bottom)

### Page Transitions

- Player moving past **x < 0** goes to previous page
- Player moving past **x > page_width** goes to next page
- Y position is preserved during transitions

## Complete Level Example

Here's a full level with various platform types:

```json
{
  "name": "Tutorial Level",
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
          "x1": 0, "y1": 15,
          "x2": 12, "y2": 15,
          "type": "NORMAL",
          "texture": "GRASS",
          "grid_size": 32
        },
        {
          "x1": 3, "y1": 14,
          "x2": 3, "y2": 14,
          "type": "SPAWN"
        },
        {
          "x1": 15, "y1": 12,
          "x2": 20, "y2": 12,
          "type": "NORMAL",
          "texture": "STONE"
        },
        {
          "x1": 23, "y1": 9,
          "x2": 28, "y2": 9,
          "type": "SLIPPERY",
          "texture": "ICE"
        },
        {
          "x1": 10, "y1": 17,
          "x2": 14, "y2": 17,
          "type": "DEATH",
          "texture": "LAVA"
        },
        {
          "x1": 30, "y1": 8,
          "x2": 30, "y2": 8,
          "type": "CHECKPOINT"
        },
        {
          "x1": 35, "y1": 6,
          "x2": 35, "y2": 6,
          "type": "FINISH"
        }
      ]
    }
  }
}
```

## Creating a New World

1. **Create a folder** in `data/worlds/`:
   ```bash
   mkdir data/worlds/my_world
   ```

2. **Add level files** to the folder:
   - Files are sorted alphabetically
   - Name them `level1.json`, `level2.json`, etc. for ordering

3. **The world appears** automatically in the Worlds menu

## Level Design Tips

### Difficulty Progression

- Start with simple jumps and safe platforms
- Introduce hazards gradually
- Place checkpoints before difficult sections

### Visual Clarity

- Use consistent textures for platform types
- Death platforms should be clearly visible (red/lava)
- Checkpoints and finish should stand out

### Testing

1. Enable debug mode (F3) to see grid and hitboxes
2. Test all possible paths
3. Ensure checkpoints are reachable
4. Verify the level is completable

### Common Patterns

**Staircase:**
```json
{ "x1": 5, "y1": 15, "x2": 8, "y2": 15, "texture": "STONE" },
{ "x1": 9, "y1": 13, "x2": 12, "y2": 13, "texture": "STONE" },
{ "x1": 13, "y1": 11, "x2": 16, "y2": 11, "texture": "STONE" }
```

**Pit with death:**
```json
{ "x1": 0, "y1": 15, "x2": 10, "y2": 15, "texture": "GRASS" },
{ "x1": 11, "y1": 18, "x2": 14, "y2": 18, "type": "DEATH" },
{ "x1": 15, "y1": 15, "x2": 25, "y2": 15, "texture": "GRASS" }
```

**Ice slide:**
```json
{ "x1": 10, "y1": 12, "x2": 20, "y2": 12, "type": "SLIPPERY", "texture": "ICE" }
```

## Validation

The game will skip invalid platforms. Check for:

- All required coordinates (`x1`, `y1`, `x2`/`w`, `y2`/`h`)
- Valid platform type names (uppercase)
- Valid texture names (if used)
- Proper JSON syntax
