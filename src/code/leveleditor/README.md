# Level Editor

A standalone level editor for creating and editing platformer levels.

## Features

- **Grid-based editor**: Create levels on a customizable grid (default 32x32)
- **Block types**: 
  - Normal - Standard platforms
  - Death - Kills player on contact
  - Spawn - Player spawn point
  - Checkpoint - Save progress
  - Slippery - Ice-like surfaces
  - Finish - Level completion trigger
- **Color customization**: Choose from 8 preset colors
- **Drag to create**: Left-click and drag to paint blocks
- **Easy erasing**: Middle-click or Shift+Left-click to erase
- **Right-click editing**: Context menu for block properties (coming soon)
- **JSON/JSONC support**: Save and load levels in JSON format

## Controls

### Drawing
- **Left Click + Drag**: Draw blocks
- **Middle Click / Shift+Left Click**: Erase blocks
- **Right Click**: Open context menu (for future editing features)

### Keyboard Shortcuts
- **Ctrl+S**: Save level
- **Ctrl+O**: Load level
- **Ctrl+N**: New level
- **G**: Toggle grid visibility
- **ESC**: Close menus

## How to Use

1. Run the level editor:
   ```bash
   python src/code/leveleditor/editor.py
   ```
   Or use the provided batch file:
   ```bash
   run_editor.bat
   ```

2. **Select a block type** from the bottom panel

3. **Choose a color** from the color palette

4. **Draw on the grid** by clicking and dragging

5. **Save your level** with Ctrl+S
   - Levels are saved to `levels/world1/` by default
   - Files are automatically numbered (level_1.json, level_2.json, etc.)

6. **Play your level** in the main game
   - Launch the game
   - Click "Levels"
   - Select your world
   - Choose your level

## Level File Format

Levels are saved in JSON format:

```json
{
  "name": "Level Name",
  "world": "world1",
  "spawn_point": [1, 14],
  "background_color": [128, 0, 128],
  "grid_size": 32,
  "platforms": [
    {
      "grid_x1": 0,
      "grid_y1": 15,
      "grid_x2": 5,
      "grid_y2": 15,
      "type": "normal",
      "color": [100, 100, 100],
      "texture": null
    }
  ]
}
```

## Tips

- **Spawn points**: Always include at least one SPAWN block
- **Finish blocks**: Add a FINISH block to enable level completion
- **Checkpoints**: Place checkpoints for longer levels
- **Death blocks**: Use sparingly for challenge areas
- **Grid visibility**: Toggle with 'G' for precise placement

## Coming Soon

- Texture selection
- Custom colors (RGB picker)
- Copy/paste platforms
- Undo/redo functionality
- Multi-platform selection
- Level testing from within editor
