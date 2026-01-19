---
title: Quick Start
description: Get up and running with Parkour Game in minutes
---

# Quick Start

This guide will help you make your first modifications to the game.

## Running the Game

1. Activate your virtual environment:
   ```bash
   source parkour/bin/activate
   ```

2. Run the game:
   ```bash
   cd src/code
   python main.py
   ```

3. Use the menu to select a world, level, and character.

## Game Controls

| Key | Action |
|-----|--------|
| `A` / `D` | Move left / right |
| `Space` / `W` | Jump |
| `Escape` | Return to menu |
| `R` | Reset to last checkpoint |
| `F3` | Toggle debug mode |

## Your First Modification

Let's add a simple change - modify the window title:

### 1. Open the Main File

Edit `src/code/main.py`:

```python
import pygame

from pygame_widgets.widget import OrderedSet

pygame.init()
# Change the window size or title here
screen = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)

def main():
    # ... rest of the code
```

### 2. Create a New Character

Create a simple character by adding to `src/code/skeletons/character_classes/characters.py`:

```python
class MyCharacter(CharacterClass):
    name = "My Hero"
    sprite_scale = (0.25, 0.25)
    
    walk_frames = [
        "Sprite_laufen-0001.png",
        "Sprite_laufen-0002.png",
    ]
    
    jump_frames = [
        "Sprite_springen-0006.png",
    ]

# Add to registry
CHARACTER_REGISTRY["my_hero"] = MyCharacter
```

### 3. Create a Simple Level

Create `data/worlds/tutorial/my_level.json`:

```json
{
  "name": "My First Level",
  "player_spawn": {
    "x": 2,
    "y": 14,
    "grid": true,
    "grid_size": 32
  },
  "background_color": {
    "r": 135,
    "g": 206,
    "b": 235
  },
  "pages": {
    "1": {
      "platforms": [
        {
          "x1": 0, "y1": 15,
          "x2": 10, "y2": 15,
          "type": "NORMAL",
          "texture": "GRASS"
        },
        {
          "x1": 2, "y1": 15,
          "x2": 2, "y2": 15,
          "type": "SPAWN"
        },
        {
          "x1": 15, "y1": 12,
          "x2": 20, "y2": 12,
          "type": "NORMAL",
          "texture": "STONE"
        },
        {
          "x1": 25, "y1": 10,
          "x2": 25, "y2": 10,
          "type": "FINISH"
        }
      ]
    }
  }
}
```

### 4. Test Your Changes

Restart the game and you should see:
- Your new character in the character selection
- Your new level in the "tutorial" world

## Debug Mode

Press `F3` to toggle debug mode, which shows:
- Grid overlay for level alignment
- Collision boxes (yellow for player, red for platforms)
- FPS counter

## What's Next?

Now that you've made your first changes, explore these guides:

- **[Adding Characters](/guides/adding-characters)** - Create characters with custom sprites
- **[Creating Levels](/guides/creating-levels)** - Design complex multi-page levels
- **[Creating Screens](/guides/creating-screens)** - Build new menu screens
- **[Using Textures](/guides/using-textures)** - Work with the texture atlas

## Common Patterns

### Switching Screens

```python
def on_button_click(self):
    self.running = False  # Stop current screen
    from screens.GameScreen import GameScreen
    GameScreen(self.screen, "Game", level_path=my_level)
```

### Loading Saved Settings

```python
from screens.SettingsScreen import SETTINGS

character_id = SETTINGS.get('character', 'character1')
debug_mode = SETTINGS.get('debug_mode', False)
```

### Creating Platform Instances

```python
from skeletons.platform import Platform
from assets.assets import Texture

platform = Platform(
    x1=100, y1=400,
    x2=300, y2=400,
    grid_size=32,
    platform_type=Platform.NORMAL,
    texture=Texture.GRASS,
)
```
