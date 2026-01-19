# Packaging

These scripts build standalone, GUI executables using PyInstaller.

## Install build tool

```bash
./parkour/bin/python -m pip install pyinstaller
```

## Build

```bash
./packaging/build_game.sh
./packaging/build_editor.sh
```

Outputs land under `dist/` as two separate folders:

- `dist/ParkourGame/`
- `dist/ParkourEditor/`

Each folder contains the executable plus bundled assets and data.

## One-file build

These scripts use `--onefile`. The executable extracts bundled resources
at runtime, and save data is still written next to the executable.
