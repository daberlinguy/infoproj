# Level Editor (PyQt6)

Simple standalone editor for the level JSON format used by the game.

Run:
```
python main.py
```

Notes:
- Coordinates are grid-based.
- The game multiplies coords by `grid_size` when loading.
- Save into `data/worlds/<world>/<level>.json` (or any JSON path you choose).
