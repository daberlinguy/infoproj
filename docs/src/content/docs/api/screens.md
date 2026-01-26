---
title: Screens API
description: API reference for built-in screen classes
---

# Screens API Reference

This page documents the built-in screen classes under `src/code/screens/`.

## Module Location

```python
from screens.TitleScreen import TitleScreen
from screens.SettingsScreen import SettingsScreen, SETTINGS
from screens.WorldSelectScreen import WorldSelectScreen
from screens.LevelSelectScreen import LevelSelectScreen
from screens.CharacterScreen import CharacterScreen
from screens.GameScreen import GameScreen
from screens.FinishScreen import FinishScreen
```

## Overview

Each screen:
- Inherits from `Screen`
- Starts its own loop in `__init__`
- Transitions by setting `self.running = False` and instantiating the next screen

## TitleScreen

**Purpose:** Main menu for Worlds, Characters, Settings, and Exit.

```python
TitleScreen(screen, "Title Screen")
```

**Key Methods:**
- `onBtnOpenWorldsScreen()`
- `onBtnOpenCharacterScreen()`
- `onBtnOpenSettingsScreen()`

---

## SettingsScreen

**Purpose:** Toggle debug mode and save settings.

```python
SettingsScreen(screen, "Settings")
```

**Key Behavior:**
- Uses global `SETTINGS` from `data.storage`
- Saves changes via `save_settings(SETTINGS)`

---

## CharacterScreen

**Purpose:** Select a playable character from `CHARACTER_REGISTRY`.

```python
CharacterScreen(screen, "Characters")
```

**Key Behavior:**
- Shows animated previews
- Saves selection to `SETTINGS["character"]`

---

## WorldSelectScreen

**Purpose:** List available worlds from `data/worlds/`.

```python
WorldSelectScreen(screen, "Worlds")
```

**Key Behavior:**
- Loads worlds via `load_worlds()`
- Sets `SETTINGS["selected_world"]`

---

## LevelSelectScreen

**Purpose:** List levels for the selected world (paginated).

```python
LevelSelectScreen(screen, "Levels", world_id)
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `world_id` | `str` | ID of the world to browse |

**Key Behavior:**
- Saves selected level in `SETTINGS`
- Launches `GameScreen` with `level_path`

---

## GameScreen

**Purpose:** Main gameplay loop.

```python
GameScreen(screen, "Game", level_path=None)
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `level_path` | `str` | `None` | Optional path to a level JSON |

**Key Behavior:**
- Builds platforms from level data
- Handles checkpoints, pages, and completion
- Uses `Spieler` for physics and `Character` for rendering

---

## FinishScreen

**Purpose:** Shows completion state and returns to level list.

```python
FinishScreen(screen, "Finished")
```

**Key Behavior:**
- Returns to `LevelSelectScreen` for `SETTINGS["selected_world"]`

---

## Usage Example

```python
from screens.TitleScreen import TitleScreen

# In main.py
TitleScreen(screen, "Title Screen")
```

## Related Links

- [Screen Base Class](../reference/screen-base-class)
- [Creating Screens Guide](../guides/creating-screens)
- [Storage API](../api/storage)
