---
title: Installation
description: How to set up the Parkour Game development environment
---

# Installation

This guide walks you through setting up the Parkour Game for development.

## Prerequisites

- **Python 3.10+** - Download from [python.org](https://python.org)
- **pip** - Python package manager (included with Python)
- **Git** (optional) - For version control

## Setting Up the Environment

### 1. Create a Virtual Environment

It's recommended to use a virtual environment to isolate dependencies:

```bash
# Navigate to the project directory
cd infoproj

# Create virtual environment
python -m venv parkour

# Activate it (Linux/macOS)
source parkour/bin/activate

# Activate it (Windows)
parkour\Scripts\activate
```

### 2. Install Dependencies

Install the required packages:

```bash
pip install pygame pygame-widgets pyperclip
```

For the level editor, also install PyQt6:

```bash
pip install PyQt6
```

### 3. Verify Installation

Test the installation by running the game:

```bash
cd src/code
python main.py
```

You should see the title screen appear.

## Project Structure After Setup

```
infoproj/
├── parkour/           # Virtual environment (created by you)
├── src/
│   ├── code/          # Source code
│   └── resources/     # Game assets
├── data/              # Runtime data (settings, worlds)
├── levels/            # Legacy levels
└── docs/              # Documentation
```

## Running the Game

### Main Game

```bash
cd src/code
python main.py
```

### Level Editor

```bash
cd editor
python main.py
```

## Building Executables

The project includes PyInstaller specs for creating standalone executables:

```bash
# Build the game
cd packaging
./build_game.sh

# Build the editor
./build_editor.sh
```

## Troubleshooting

### "pygame not found" Error

Make sure your virtual environment is activated:

```bash
source parkour/bin/activate  # Linux/macOS
```

### Display Issues on Linux

If you have display issues, try setting the SDL video driver:

```bash
export SDL_VIDEODRIVER=x11
python main.py
```

### Font Loading Errors

Ensure the assets folder is in the correct location:
- `src/resources/assets/fonts/font.ttf` should exist

## Next Steps

- [Quick Start](/getting-started/quick-start) - Start modifying the game
- [Adding Characters](/guides/adding-characters) - Create new playable characters
- [Creating Levels](/guides/creating-levels) - Design your own levels
