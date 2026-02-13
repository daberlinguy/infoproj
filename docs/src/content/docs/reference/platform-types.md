---
title: Platform Types
description: Reference for all platform types and their behaviors
---

# Platform Types Reference

This page documents all available platform types, their behaviors, and visual indicators.

## Overview

Platforms are defined in the `Platform` class in `src/code/skeletons/platform.py`. Each type has distinct gameplay behavior and visual appearance.

**New in v2.0:** Platforms can now have **multiple types simultaneously**. For example, a platform can be both `CHECKPOINT` and `SLIPPERY` at the same time.

## Type Constants

```python
from skeletons.platform import Platform

Platform.NORMAL      # "normal"
Platform.DEATH       # "death"
Platform.SPAWN       # "spawn"
Platform.CHECKPOINT  # "checkpoint"
Platform.FINISH      # "finish"
Platform.SLIPPERY    # "slippery"
Platform.NOCLIP      # "noclip"
Platform.BOOST_UP    # "boost_up"
Platform.SPEED_UP    # "speed_up"
Platform.SLOW_DOWN   # "slow_down"
```

## Multiple Types

Platforms can have multiple types, combining different behaviors:

**Code Example:**
```python
Platform(
    x1=400, y1=450,
    x2=600, y2=450,
    grid_size=32,
    platform_types=[Platform.CHECKPOINT, Platform.SLIPPERY],  # Both checkpoint and slippery
    texture=Texture.ICE,
)
```

**JSON Example:**
```json
{
  "x1": 15, "y1": 12, "x2": 25, "y2": 12,
  "types": ["CHECKPOINT", "SLIPPERY"],
  "texture": "ICE"
}
```

**Legacy Support:** The old single `type` field is still supported for backward compatibility:
```json
{
  "type": "NORMAL"
}
```

## Detailed Reference

### NORMAL

**Purpose:** Standard walkable surface

**Behavior:**
- Player can walk and jump on it
- Normal friction (0.8)
- No special interactions

**Visual:**
- Default: Gray (100, 100, 100)
- Typically uses a texture

**Code Example:**
```python
Platform(
    x1=0, y1=500,
    x2=300, y2=500,
    grid_size=32,
    platform_type=Platform.NORMAL,
    texture=Texture.GRASS,
)
```

**JSON Example:**
```json
{
  "x1": 0, "y1": 15, "x2": 10, "y2": 15,
  "type": "NORMAL",
  "texture": "GRASS"
}
```

---

### DEATH

**Purpose:** Hazard that kills the player

**Behavior:**
- Player dies on contact
- Respawns at last checkpoint (or spawn)
- Does NOT block player movement (no collision)
- Can be touched from any direction

**Visual:**
- Default: Red (255, 0, 0)
- Shows X pattern overlay (if no texture)
- Recommended: Use `LAVA` texture

**Code Example:**
```python
Platform(
    x1=200, y1=550,
    x2=300, y2=550,
    grid_size=32,
    platform_type=Platform.DEATH,
    texture=Texture.LAVA,
)
```

**JSON Example:**
```json
{
  "x1": 10, "y1": 17, "x2": 14, "y2": 17,
  "type": "DEATH",
  "texture": "LAVA"
}
```

---

### SPAWN

**Purpose:** Player starting position marker

**Behavior:**
- Visual indicator only
- Does not affect gameplay
- Initial checkpoint is set above this platform

**Visual:**
- Default: Green (0, 255, 0)
- Shows "S" marker in center

**Code Example:**
```python
Platform(
    x1=100, y1=450,
    x2=100, y2=450,
    grid_size=32,
    platform_type=Platform.SPAWN,
    texture=Texture.GOLD_BLOCK,
)
```

**JSON Example:**
```json
{
  "x1": 3, "y1": 14, "x2": 3, "y2": 14,
  "type": "SPAWN"
}
```

**Note:** Usually a single cell, placed above a NORMAL platform.

---

### CHECKPOINT

**Purpose:** Save respawn position

**Behavior:**
- Activates when player touches it
- Sets new respawn point
- Once activated, cannot be deactivated
- Tracks page number for multi-page levels
- Required for FINISH (if checkpoints exist)

**Visual:**
- Default: Yellow (255, 255, 0)
- Inactive: Shows flag icon
- Active: Shows green border

**States:**
- `checkpoint_activated = False` → Flag shown
- `checkpoint_activated = True` → Green border, no flag

**Code Example:**
```python
Platform(
    x1=500, y1=400,
    x2=500, y2=400,
    grid_size=32,
    platform_type=Platform.CHECKPOINT,
)
```

**JSON Example:**
```json
{
  "x1": 25, "y1": 10, "x2": 25, "y2": 10,
  "type": "CHECKPOINT"
}
```

**Methods:**
```python
platform.is_checkpoint()       # Returns True
platform.activate_checkpoint() # Activates the checkpoint
platform.checkpoint_activated  # Check activation state
```

---

### FINISH

**Purpose:** Level completion trigger

**Behavior:**
- Player must touch to complete level
- Requires ALL checkpoints to be activated first
- Triggers transition to FinishScreen
- Saves level completion to progress

**Visual:**
- Default: Blue (0, 150, 255)
- No special indicator

**Code Example:**
```python
Platform(
    x1=900, y1=300,
    x2=900, y2=300,
    grid_size=32,
    platform_type=Platform.FINISH,
)
```

**JSON Example:**
```json
{
  "x1": 35, "y1": 6, "x2": 35, "y2": 6,
  "type": "FINISH"
}
```

**Completion Logic:**
```python
# In GameScreen.run()
if platform.is_finish() and player_rect.colliderect(platform.rect):
    if self.checkpoints_activated >= self.checkpoints_required:
        self.level_completed = True
        self._mark_level_complete()
        # Transition to FinishScreen
```

---

### SLIPPERY

**Purpose:** Low friction surface (ice)

**Behavior:**
- Very low friction (0.05)
- Player slides and maintains momentum
- Movement uses acceleration instead of direct position change
- Gradual deceleration when not pressing keys

**Visual:**
- Default: Light Blue (100, 200, 255)
- Shows wavy lines (if no texture)
- Recommended: Use `ICE` texture

**Physics:**
```python
# In Spieler class
if self.friction < 0.1:  # Slippery
    self.velocity_x += self.acceleration * self.dt
    # Gradual deceleration
else:
    self.player_pos.x += 300 * self.dt
    # Direct movement
```

**Code Example:**
```python
Platform(
    x1=400, y1=450,
    x2=600, y2=450,
    grid_size=32,
    platform_type=Platform.SLIPPERY,
    texture=Texture.ICE,
)
```

**JSON Example:**
```json
{
  "x1": 15, "y1": 12, "x2": 25, "y2": 12,
  "type": "SLIPPERY",
  "texture": "ICE"
}
```

---

### NOCLIP

**Purpose:** Passthrough platform that doesn't block player

**Behavior:**
- Player can pass through from any direction
- No collision detection
- Visual indicator only
- Often combined with other types (BOOST_UP, SPEED_UP, SLOW_DOWN)

**Visual:**
- Default: Light Gray (200, 200, 200)
- No special indicator

**Code Example:**
```python
Platform(
    x1=300, y1=400,
    x2=500, y2=400,
    grid_size=32,
    platform_types=[Platform.NOCLIP],
)
```

**JSON Example:**
```json
{
  "x1": 10, "y1": 12, "x2": 15, "y2": 12,
  "types": ["NOCLIP"]
}
```

---

### BOOST_UP

**Purpose:** Boost player upward when passing through

**Behavior:**
- Player can pass through (like NOCLIP)
- Applies upward velocity boost when touched
- Useful for creating wind currents or jump pads
- Often combined with NOCLIP type

**Visual:**
- Default: Light Green (150, 255, 150)
- Shows upward arrow indicator

**Code Example:**
```python
Platform(
    x1=300, y1=400,
    x2=300, y2=500,
    grid_size=32,
    platform_types=[Platform.NOCLIP, Platform.BOOST_UP],
)
```

**JSON Example:**
```json
{
  "x1": 10, "y1": 10, "x2": 10, "y2": 15,
  "types": ["NOCLIP", "BOOST_UP"]
}
```

---

### SPEED_UP

**Purpose:** Increase horizontal movement speed on contact

**Behavior:**
- Increases movement speed multiplier
- Usually combined with reduced friction for faster traversal
- Can be combined with `NOCLIP` for speed zones

**Visual:**
- Default: Cyan (0, 200, 255)

**Code Example:**
```python
Platform(
    x1=300, y1=400,
    x2=500, y2=400,
    grid_size=32,
    platform_types=[Platform.SPEED_UP],
)
```

**JSON Example:**
```json
{
  "x1": 10, "y1": 10, "x2": 18, "y2": 10,
  "types": ["SPEED_UP"]
}
```

---

### SLOW_DOWN

**Purpose:** Reduce horizontal movement speed on contact

**Behavior:**
- Reduces movement speed multiplier
- Uses higher friction than normal platforms
- Useful for mud/sand/slow zones

**Visual:**
- Default: Orange (255, 150, 0)

**Code Example:**
```python
Platform(
    x1=300, y1=400,
    x2=500, y2=400,
    grid_size=32,
    platform_types=[Platform.SLOW_DOWN],
)
```

**JSON Example:**
```json
{
  "x1": 20, "y1": 10, "x2": 28, "y2": 10,
  "types": ["SLOW_DOWN"]
}
```

---

## Helper Methods

The `Platform` class provides type-checking methods:

```python
platform.is_deadly()      # True if DEATH in types
platform.is_checkpoint()  # True if CHECKPOINT in types
platform.is_finish()      # True if FINISH in types
platform.is_spawn()       # True if SPAWN in types
platform.is_noclip()      # True if NOCLIP in types
platform.is_boost_up()    # True if BOOST_UP in types
platform.is_speed_up()    # True if SPEED_UP in types
platform.is_slow_down()   # True if SLOW_DOWN in types
platform.get_friction()   # Type-based friction
platform.get_speed_multiplier()  # Type-based movement multiplier
```

## Default Colors

| Type | RGB | Hex |
|------|-----|-----|
| NORMAL | (100, 100, 100) | #646464 |
| DEATH | (255, 0, 0) | #FF0000 |
| SPAWN | (0, 255, 0) | #00FF00 |
| CHECKPOINT | (255, 255, 0) | #FFFF00 |
| FINISH | (0, 150, 255) | #0096FF |
| SLIPPERY | (100, 200, 255) | #64C8FF |
| NOCLIP | (200, 200, 200) | #C8C8C8 |
| BOOST_UP | (150, 255, 150) | #96FF96 |
| SPEED_UP | (0, 200, 255) | #00C8FF |
| SLOW_DOWN | (255, 150, 0) | #FF9600 |

## Custom Colors

Override the default color:

```python
Platform(
    ...,
    platform_type=Platform.NORMAL,
    color=(139, 69, 19),  # Custom brown
)
```

```json
{
  "type": "NORMAL",
  "color": [139, 69, 19]
}
```

## Recommended Textures by Type

| Type | Recommended Textures |
|------|---------------------|
| NORMAL | GRASS, STONE, FLETCHINGTABLE |
| DEATH | LAVA |
| SPAWN | GOLD_BLOCK |
| CHECKPOINT | (use default color) |
| FINISH | (use default color) |
| SLIPPERY | ICE, ICEBROKEN variants |
