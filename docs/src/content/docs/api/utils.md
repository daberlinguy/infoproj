---
title: Utility Modules API
description: API reference for utility classes and helper functions
---

# Utility Modules API Reference

The utility modules provide shared functionality for color manipulation, platform type management, and level data parsing.

## Module Location

```python
from utils.colors import ColorUtils
from utils.platform_types import PlatformTypes
from utils.level_data import LevelDataUtils
```

---

## ColorUtils

Provides color manipulation utilities for layer tinting and texture processing.

### apply_layer_tint(color, layer)

Apply layer-based tinting to a color (10% per layer).

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `color` | `Tuple[int, int, int]` | RGB color tuple |
| `layer` | `int` | Layer value (-10 to +10) |

**Returns:** `Tuple[int, int, int]` - Tinted RGB color

- Negative layers: Darker (towards black)
- Positive layers: Brighter (towards white)
- Layer 0: No change

```python
# Background layer (darker)
dark_color = ColorUtils.apply_layer_tint((128, 128, 128), -5)

# Foreground layer (brighter)
bright_color = ColorUtils.apply_layer_tint((128, 128, 128), 5)

# Normal layer (unchanged)
normal_color = ColorUtils.apply_layer_tint((128, 128, 128), 0)
```

### apply_layer_tint_to_texture(texture, layer)

Apply layer-based tinting to a pygame Surface texture.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `texture` | `pygame.Surface` | Texture to tint |
| `layer` | `int` | Layer value (-10 to +10) |

**Returns:** `pygame.Surface` - Tinted texture copy

```python
tinted_texture = ColorUtils.apply_layer_tint_to_texture(grass_texture, -3)
```

### clamp(value, min_val, max_val)

Clamp a value between min and max bounds.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `value` | `int` | Value to clamp |
| `min_val` | `int` | Minimum value |
| `max_val` | `int` | Maximum value |

**Returns:** `int` - Clamped value

```python
clamped = ColorUtils.clamp(300, 0, 255)  # Returns 255
```

### blend_colors(color1, color2, factor)

Blend two colors together.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `color1` | `Tuple[int, int, int]` | First RGB color |
| `color2` | `Tuple[int, int, int]` | Second RGB color |
| `factor` | `float` | Blend factor (0.0-1.0) |

**Returns:** `Tuple[int, int, int]` - Blended RGB color

```python
# 50% blend between red and blue
purple = ColorUtils.blend_colors((255, 0, 0), (0, 0, 255), 0.5)
```

---

## PlatformTypes

Centralized platform type constants, colors, and metadata.

### Type Constants

```python
PlatformTypes.NORMAL       # "normal"
PlatformTypes.DEATH        # "death"
PlatformTypes.SPAWN        # "spawn"
PlatformTypes.CHECKPOINT   # "checkpoint"
PlatformTypes.FINISH       # "finish"
PlatformTypes.SLIPPERY     # "slippery"
PlatformTypes.NOCLIP       # "noclip"
PlatformTypes.BOOST_UP     # "boost_up"
PlatformTypes.SPEED_UP     # "speed_up"
PlatformTypes.SLOW_DOWN    # "slow_down"
```

### ALL_TYPES

List of all valid platform type strings.

```python
all_types = PlatformTypes.ALL_TYPES
# ['normal', 'death', 'spawn', 'checkpoint', 'finish', 
#  'slippery', 'noclip', 'boost_up', 'speed_up', 'slow_down']
```

### TYPE_COLORS

Dictionary mapping type names to RGB colors.

```python
color = PlatformTypes.TYPE_COLORS[PlatformTypes.DEATH]
# (255, 0, 0) - Red
```

### FRICTION_VALUES

Dictionary mapping type names to friction coefficients.

```python
friction = PlatformTypes.FRICTION_VALUES[PlatformTypes.SLIPPERY]
# 0.05
```

### SPEED_MULTIPLIERS

Dictionary mapping type names to movement speed multipliers.

```python
speed = PlatformTypes.SPEED_MULTIPLIERS[PlatformTypes.SPEED_UP]
# 1.5
```

### get_color(platform_type)

Get the default color for a platform type.

**Parameters:**
| Name | Type | Description |

### get_speed_multiplier(platform_type)

Get the movement speed multiplier for a platform type.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `platform_type` | `str` | Platform type constant |

**Returns:** `float` - Speed multiplier

```python
fast = PlatformTypes.get_speed_multiplier(PlatformTypes.SPEED_UP)
# Returns 1.5
```
|------|------|-------------|
| `platform_type` | `str` | Platform type constant |

**Returns:** `Tuple[int, int, int]` - RGB color tuple

```python
death_color = PlatformTypes.get_color(PlatformTypes.DEATH)
# Returns (255, 0, 0)
```

### get_friction(platform_type)

Get the friction coefficient for a platform type.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `platform_type` | `str` | Platform type constant |

**Returns:** `float` - Friction coefficient (0.05 for SLIPPERY, 0.8 otherwise)

```python
friction = PlatformTypes.get_friction(PlatformTypes.SLIPPERY)
# Returns 0.05
```

### is_valid_type(platform_type)

Check if a string is a valid platform type.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `platform_type` | `str` | Type string to validate |

**Returns:** `bool` - True if valid type

```python
is_valid = PlatformTypes.is_valid_type("death")      # True
is_valid = PlatformTypes.is_valid_type("invalid")    # False
```

### normalize_types(types)

Normalize platform types to a list of valid lowercase strings.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `types` | `Union[str, List[str]]` | Single type or list of types |

**Returns:** `List[str]` - Normalized list of valid types

```python
# Single type
normalized = PlatformTypes.normalize_types("DEATH")
# Returns ["death"]

# List of types
normalized = PlatformTypes.normalize_types(["NORMAL", "SLIPPERY"])
# Returns ["normal", "slippery"]

# Invalid types filtered out
normalized = PlatformTypes.normalize_types(["normal", "invalid"])
# Returns ["normal"]
```

---

## LevelDataUtils

Utilities for loading and parsing level JSON data.

### load_level_json(file_path)

Load and parse a level JSON file with error handling.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `file_path` | `str` | Path to level JSON file |

**Returns:** `Optional[Dict]` - Parsed level data or None on error

```python
level_data = LevelDataUtils.load_level_json("data/worlds/world1/level1.json")
if level_data:
    print(f"Loaded {len(level_data.get('pages', []))} pages")
```

### normalize_platform_types(entry)

Extract and normalize platform types from a platform entry.

Handles both old `"type"` and new `"types"` formats for backward compatibility.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `entry` | `Dict` | Platform data dictionary |

**Returns:** `List[str]` - List of normalized type strings

```python
# Old format
platform = {"type": "DEATH", "x": 0, "y": 0}
types = LevelDataUtils.normalize_platform_types(platform)
# Returns ["death"]

# New format
platform = {"types": ["NORMAL", "SLIPPERY"], "x": 0, "y": 0}
types = LevelDataUtils.normalize_platform_types(platform)
# Returns ["normal", "slippery"]
```

### parse_color(color_data)

Parse color from various formats.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `color_data` | `Union[List, Tuple, Dict]` | Color in various formats |

**Returns:** `Optional[Tuple[int, int, int]]` - RGB tuple or None

```python
# List format
color = LevelDataUtils.parse_color([255, 0, 0])
# Returns (255, 0, 0)

# Dict format
color = LevelDataUtils.parse_color({"r": 255, "g": 0, "b": 0})
# Returns (255, 0, 0)

# Tuple format
color = LevelDataUtils.parse_color((255, 0, 0))
# Returns (255, 0, 0)
```

### get_platform_coordinates(entry, grid_size)

Extract and validate platform coordinates from entry.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `entry` | `Dict` | Platform data dictionary |
| `grid_size` | `int` | Grid cell size in pixels |

**Returns:** `Optional[Tuple[int, int, int, int]]` - (x1, y1, x2, y2) or None

```python
platform = {"x1": 0, "y1": 0, "x2": 100, "y2": 100}
coords = LevelDataUtils.get_platform_coordinates(platform, 32)
# Returns (0, 0, 100, 100)
```

### get_page_data(level_data, page_index)

Get data for a specific page from level data.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `level_data` | `Dict` | Full level data |
| `page_index` | `int` | Page index (1-based) |

**Returns:** `Dict` - Page data dictionary

```python
page_data = LevelDataUtils.get_page_data(level_data, 1)
platforms = page_data.get("platforms", [])
```

---

## Example Usage

### Using ColorUtils for Layer System

```python
from utils.colors import ColorUtils

# Create a background platform (layer -5)
bg_color = ColorUtils.apply_layer_tint((100, 100, 100), -5)
# Darker: (50, 50, 50)

# Create a foreground platform (layer +5)
fg_color = ColorUtils.apply_layer_tint((100, 100, 100), 5)
# Brighter: (150, 150, 150)

# Apply tinting to textures
tinted_bg = ColorUtils.apply_layer_tint_to_texture(texture, -5)
```

### Using PlatformTypes

```python
from utils.platform_types import PlatformTypes

# Get type color
death_color = PlatformTypes.get_color(PlatformTypes.DEATH)

# Check if type is valid
if PlatformTypes.is_valid_type(user_input):
    # Create platform with this type
    pass

# Normalize mixed case types
types = PlatformTypes.normalize_types(["NORMAL", "slippery"])
# Returns ["normal", "slippery"]
```

### Using LevelDataUtils

```python
from utils.level_data import LevelDataUtils

# Load level
level_data = LevelDataUtils.load_level_json("path/to/level.json")

if level_data:
    # Get first page
    page_data = LevelDataUtils.get_page_data(level_data, 1)
    
    # Process platforms
    for platform_entry in page_data.get("platforms", []):
        # Get coordinates
        coords = LevelDataUtils.get_platform_coordinates(platform_entry, 32)
        
        # Get types
        types = LevelDataUtils.normalize_platform_types(platform_entry)
        
        # Get color
        color = LevelDataUtils.parse_color(platform_entry.get("color"))
        
        # Get layer
        layer = platform_entry.get("layer", 0)
```

---

## See Also

- [Platform API](platform) - Uses ColorUtils and PlatformTypes
- [Level Format](../reference/level-format) - JSON structure parsed by LevelDataUtils
- [Platform Types](../reference/platform-types) - Platform type reference
