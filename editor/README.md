# Level Editor (PyQt6)

Simple standalone editor for the level JSON format used by the game.

## Running the Editor

```bash
python editor/main.py
```

Or use the start script:
```bash
# Windows
start_editor.bat

# Linux/Mac
python editor/main.py
```

## Features

- **Multiple Platform Types**: Select multiple types per platform (e.g., CHECKPOINT + SLIPPERY)
- **Texture Search**: Search for textures in the dropdown
- **Visual Selection**: Click or drag to select blocks in the canvas
- **Two Modes**: 
  - **Add Mode**: Draw new platforms by clicking and dragging
  - **Select Mode**: Select and edit existing platforms
- **Batch Operations**: 
  - Update multiple selected platforms at once
  - Remove multiple platforms
  - Apply only texture or only type to selection

## Usage Notes

- Coordinates are grid-based
- The game multiplies coords by `grid_size` when loading
- Save into `data/worlds/<world>/<level>.json` (or any JSON path you choose)
- Textures are loaded from `src/resources/textures.json`
- Platform types are dynamically loaded from the same configuration

## Keyboard Shortcuts

- **Ctrl+Z**: Undo
- **Ctrl+Y**: Redo  
- **Delete**: Remove selected platforms

## Tips

- Use "Update Type Only" or "Update Texture Only" buttons to modify specific properties without changing others
- Platforms can have multiple types - check multiple boxes in the Platform Types section
- Use texture search to quickly find textures in the large list
- Zoom in/out with mouse wheel while in the canvas
