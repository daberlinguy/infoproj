---
title: Storage API
description: API reference for save/load functions
---

# Storage API Reference

Functions for saving and loading game data.

## Module Location

```python
from data.storage import load_settings, save_settings, load_worlds
```

## Settings Functions

### load_settings()

Load user settings from disk.

```python
def load_settings() -> dict
```

**Returns:** Settings dictionary with defaults applied

**Default settings:**
```python
{
    "debug_mode": False,
    "character": "character1",
    "selected_world": None,
    "selected_level": None,
    "progress": {"worlds": {}},
}
```

**Example:**
```python
settings = load_settings()
debug = settings.get('debug_mode', False)
```

---

### save_settings(settings)

Save settings to disk.

```python
def save_settings(settings: dict) -> None
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `settings` | `dict` | Settings to save |

**Example:**
```python
from data.storage import save_settings
from screens.SettingsScreen import SETTINGS

SETTINGS['debug_mode'] = True
save_settings(SETTINGS)
```

---

## World Functions

### load_worlds()

Load all worlds and their levels.

```python
def load_worlds() -> dict
```

**Returns:** Dictionary of world_id → world data

**Structure:**
```python
{
    "world1": {
        "name": "world1",
        "path": "/path/to/world1",
        "levels": [
            {
                "id": "level1.json",
                "name": "Level 1",
                "path": "/path/to/level1.json",
                "data": { ... level JSON ... }
            }
        ]
    }
}
```

**Example:**
```python
worlds = load_worlds()

for world_id, world in worlds.items():
    print(f"World: {world['name']}")
    for level in world['levels']:
        print(f"  - {level['name']}")
```

---

## Global Settings

The `SETTINGS` dict is loaded once and shared:

```python
from screens.SettingsScreen import SETTINGS

# Read
character = SETTINGS.get('character', 'character1')

# Write
SETTINGS['character'] = 'character2'
save_settings(SETTINGS)
```

---

## File Locations

- Settings: `data/settings.json`
- Worlds: `data/worlds/<world_name>/<level>.json`

---

## Progress Tracking

```python
# Check level completion
progress = SETTINGS.get("progress", {}).get("worlds", {})
world_progress = progress.get("world1", {})
level_complete = world_progress.get("levels", {}).get("level1.json", False)

# Mark level complete
SETTINGS.setdefault("progress", {}).setdefault("worlds", {})
SETTINGS["progress"]["worlds"].setdefault("world1", {"levels": {}, "complete": False})
SETTINGS["progress"]["worlds"]["world1"]["levels"]["level1.json"] = True
save_settings(SETTINGS)
```
