---
title: Platform Types
description: Reference for all platform types and their behaviors
---

# Platform Types Reference

This page documents all available platform types, their behaviors, and visual indicators.

## Overview

Platforms are defined in the `Platform` class in `src/code/skeletons/platform.py`. Each type has distinct gameplay behavior and visual appearance.

## Type Constants

```python
from skeletons.platform import Platform

Platform.NORMAL      # "normal"
Platform.DEATH       # "death"
Platform.SPAWN       # "spawn"
Platform.CHECKPOINT  # "checkpoint"
Platform.FINISH      # "finish"
Platform.SLIPPERY    # "slippery"
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

## Helper Methods

The `Platform` class provides type-checking methods:

```python
platform.is_deadly()      # True for DEATH
platform.is_checkpoint()  # True for CHECKPOINT
platform.is_finish()      # True for FINISH
platform.is_spawn()       # True for SPAWN
platform.get_friction()   # 0.05 for SLIPPERY, 0.8 for others
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
