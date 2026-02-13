---
title: Using the Level Editor
description: Guide to using the PyQt6 level editor for creating and editing levels
---

# Using the Level Editor

The Parkour Game includes a visual level editor built with PyQt6 that makes it easy to create and modify levels without manually editing JSON files.

## Starting the Editor

```bash
python editor/main.py
```

The editor will open with a blank canvas and control panels on the right side.

## Editor Interface

### Main Components

**Canvas (Left Side):**
- Visual representation of your level
- Click and drag to create platforms
- Ctrl+Click to select multiple platforms
- Shift+Click to select range of platforms

**Platform List (Right Side Top):**
- Lists all platforms in the current page
- Shows platform types, coordinates, and layer
- Click to select a platform
- Ctrl+Click for multi-selection
- Shift+Click for range selection

**Platform Properties (Right Side Bottom):**
- Edit selected platform properties
- Set coordinates, types, texture, color, and layer

**Top Menu:**
- File operations (New, Open, Save)
- Page navigation
- Grid controls

## Creating Platforms

### Using the Canvas

1. **Set Platform Properties** in the right panel:
   - Choose platform types (check multiple for combined types)
   - Set texture (optional)
   - Set layer (-10 to +10)
   - Set grid size

2. **Click and Drag** on the canvas:
   - Click where you want the platform to start
   - Drag to where you want it to end
   - Release to create the platform

3. **Platform appears** in both canvas and platform list

### Manual Entry

You can also manually enter coordinates in the properties panel:
- Set x1, y1, x2, y2 coordinates
- Click "Add Platform" button

## Selecting Platforms

### Single Selection

**On Canvas:**
- Click on a platform to select it
- Selected platform highlights with a blue border

**In Platform List:**
- Click on a platform entry

### Multi-Selection (New in v2.0)

**Ctrl+Click:**
- Hold Ctrl and click platforms to add/remove from selection
- Works on both canvas and platform list

**Shift+Click:**
- Hold Shift and click to select a range
- Works in platform list only

**Selecting All:**
- Canvas selection takes priority
- If any platforms selected on canvas, those are used
- Otherwise, platform list selection is used

## Editing Platforms

### Edit Single Platform

1. Select the platform (canvas or list)
2. Modify properties in the properties panel
3. Properties update in real-time

### Edit Multiple Platforms

1. Select multiple platforms (Ctrl+Click or Shift+Click)
2. Modify properties in the properties panel
3. Click "Update Platform" button
4. **All selected platforms** are updated with the new properties

**Note:** Canvas selections take priority over list selections.

## Deleting Platforms

### Delete Single Platform

1. Select the platform
2. Click "Remove Platform" button (or press Delete)

### Delete Multiple Platforms

1. Select multiple platforms (Ctrl+Click or Shift+Click)
2. Click "Remove Platform" button
3. **All selected platforms** are deleted

## Platform Types

### Single Type

Check one type checkbox:
- `NORMAL` - Standard walkable platform
- `DEATH` - Kills player on contact
- `SPAWN` - Player starting position
- `CHECKPOINT` - Saves respawn point
- `FINISH` - Level completion trigger
- `SLIPPERY` - Low friction (ice)
- `NOCLIP` - Player passes through
- `BOOST_UP` - Boosts player upward
- `SPEED_UP` - Increases player movement speed
- `SLOW_DOWN` - Reduces player movement speed

### Multiple Types (New in v2.0)

Check multiple type checkboxes to combine behaviors:

**Example Combinations:**
- `CHECKPOINT + SLIPPERY` - Icy checkpoint platform
- `NOCLIP + BOOST_UP` - Upward wind current
- `NORMAL + CHECKPOINT` - Solid platform that saves progress

## Layer System (New in v2.0)

The layer system creates visual depth in your levels.

### Layer Range

- **-10 to -1:** Background layers (darker)
- **0:** Normal layer (default)
- **+1 to +10:** Foreground layers (brighter)

### Visual Effect

Each layer applies a 10% tint:
- **Layer -5:** 50% darker (deep background)
- **Layer -1:** 10% darker (near background)
- **Layer 0:** No tint (normal)
- **Layer +1:** 10% brighter (near foreground)
- **Layer +5:** 50% brighter (prominent foreground)

### Using Layers

**In Editor:**
1. Select platform(s)
2. Adjust the "Layer" spinbox (-10 to +10)
3. Platform color/texture tints automatically

**Rendering Order:**
- Platforms render from lowest to highest layer
- Background layers (-10) render first
- Foreground layers (+10) render last

**Use Cases:**
- **Background (-5 to -10):** Distant scenery, decoration
- **Midground (-2 to -1):** Secondary platforms
- **Normal (0):** Main gameplay platforms
- **Foreground (+1 to +3):** Important highlighted platforms

### Layer Example

```json
{
  "platforms": [
    {
      "x1": 0, "y1": 0, "x2": 60, "y2": 18,
      "types": ["NORMAL"],
      "texture": "STONE",
      "layer": -8,
      "comment": "Far background wall"
    },
    {
      "x1": 10, "y1": 15, "x2": 20, "y2": 15,
      "types": ["NORMAL"],
      "texture": "GRASS",
      "layer": 0,
      "comment": "Main platform"
    },
    {
      "x1": 15, "y1": 10, "x2": 15, "y2": 10,
      "types": ["CHECKPOINT"],
      "layer": 2,
      "comment": "Highlighted checkpoint"
    }
  ]
}
```

## Textures

### Available Textures

The editor loads textures from `src/resources/textures.json`. Common textures:
- `GRASS` - Green grass
- `STONE` - Gray stone
- `ICE` - Ice blocks
- `LAVA` - Lava texture
- `GOLD_BLOCK` - Gold blocks
- And many more...

See [Using Textures](using-textures) for the complete list.

### Applying Textures

1. Select platform(s)
2. Choose texture from dropdown
3. Leave blank for color-only platforms

**Note:** Textures are automatically tinted based on the platform's layer.

## Colors

### Default Colors

Each platform type has a default color:
- NORMAL: Gray
- DEATH: Red
- CHECKPOINT: Yellow
- FINISH: Blue
- SLIPPERY: Light Blue
- etc.

### Custom Colors

Override the default with RGB values (0-255):
1. Set R (red), G (green), B (blue) spinboxes
2. Color applies immediately

**Note:** Colors are also affected by layer tinting.

## Pages (Multi-Screen Levels)

### Page Navigation

- Use "Previous Page" / "Next Page" buttons
- Current page shown in status bar
- Each page is a separate screen

### Page Transitions

- Player moves left (x < 0): Go to previous page
- Player moves right (x > page_width): Go to next page
- Y position preserved across pages

### Creating Multi-Page Levels

1. Create platforms on page 1
2. Click "Next Page"
3. Create platforms on page 2
4. Save - both pages stored in JSON

## Level Properties

### Level Name

Set in the "Level Name" field at the top. This appears in level selection.

### Background Color

Set RGB values for background:
- R: 0-255
- G: 0-255
- B: 0-255
- A: Alpha (opacity)

### Background Image

Enter image filename to use an image instead of solid color.
Images load from `src/resources/assets/backgrounds/`.

### Player Spawn

Set starting position:
- **X:** Grid column
- **Y:** Grid row
- **Grid:** Use grid units (vs pixels)
- **Grid Size:** Size of grid cells

## File Operations

### New Level

1. Click "File" → "New"
2. Clears canvas and properties
3. Creates blank level

### Open Level

1. Click "File" → "Open"
2. Navigate to `data/worlds/<world>/`
3. Select `.json` file
4. Level loads into editor

### Save Level

1. Click "File" → "Save" or "Save As"
2. Choose location in `data/worlds/<world>/`
3. Enter filename (e.g., `my_level.json`)
4. Level saved

**Save Format:**
```json
{
  "name": "Level Name",
  "player_spawn": {...},
  "background_color": {...},
  "pages": {
    "1": {"platforms": [...]},
    "2": {"platforms": [...]}
  }
}
```

## Grid System

### Grid Display

Toggle grid overlay:
- Press `G` key
- Or use Grid menu

### Grid Size

- Default: 32 pixels
- Adjustable per platform
- Affects snapping and coordinates

### Snapping

Platforms automatically snap to grid when using canvas.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+N` | New level |
| `Ctrl+O` | Open level |
| `Ctrl+S` | Save level |
| `Ctrl+Z` | Undo (if implemented) |
| `Delete` | Remove selected platform(s) |
| `G` | Toggle grid |
| `Ctrl+Click` | Multi-select platforms |
| `Shift+Click` | Range select (list only) |

## Tips & Best Practices

### Design Tips

1. **Start with ground platforms:** Create the main path first
2. **Add checkpoints regularly:** Don't make players replay too much
3. **Test frequently:** Play your level often during design
4. **Use layers for depth:** Create visual interest with background/foreground
5. **Combine types creatively:** Slippery checkpoint, boost platforms, etc.

### Performance

1. **Avoid too many platforms:** Limit to ~100 per page
2. **Use larger platforms:** Fewer large platforms > many small ones
3. **Optimize textures:** Not every platform needs a texture

### Multi-Selection Workflow

1. **Bulk editing:** Select multiple platforms, change type/texture/layer together
2. **Mass deletion:** Clean up mistakes quickly
3. **Consistent styling:** Apply same layer/texture to group of platforms

### Layer Workflow

1. **Create background first:** Layer -5 to -10 for scenery
2. **Add main platforms:** Layer 0 for gameplay
3. **Highlight important elements:** Layer +1 to +3 for checkpoints/finish

## Troubleshooting

### Platforms not appearing

- Check if on correct page
- Verify coordinates are within canvas bounds
- Ensure grid_size is reasonable (16-64)

### Can't select platform

- Try clicking center of platform
- Check platform list for small platforms
- Zoom in if canvas is crowded

### Multiple platforms update when editing

- This is the multi-select feature
- Deselect unwanted platforms (Ctrl+Click)
- Or select only the one you want

### Colors look wrong

- Check layer value - layers tint colors
- Verify RGB values are 0-255
- Try resetting to default platform type color

## See Also

- [Level Format Reference](../reference/level-format) - Complete JSON schema
- [Platform Types Reference](../reference/platform-types) - All platform types
- [Creating Levels Guide](creating-levels) - Level design tips
- [Using Textures](using-textures) - Texture reference
