---
title: Adding Characters
description: Complete guide to creating new playable characters
---

# Adding Characters

This guide explains how to create new playable characters with custom sprites and animations.

## Overview

Characters in Parkour Game are defined by:
1. **Sprite images** - PNG files for animations
2. **A CharacterClass** - Python class defining the character
3. **Registry entry** - Adding the character to `CHARACTER_REGISTRY`

## File Structure

Character sprites should be organized in subfolders:
```
src/resources/assets/sprites/characters/
├── my_hero/
│   ├── walk1.png
│   ├── walk2.png
│   ├── walk3.png
│   ├── jump.png
│   └── ...
├── chatlink/
│   ├── walk1.png
│   └── ...
└── dino/
    ├── run1.png
    └── ...
```

## Creating a Character Class

### Basic Character

Edit `src/code/skeletons/character_classes/characters.py`:

```python
from skeletons.character_classes.base import CharacterClass

class MyAwesomeCharacter(CharacterClass):
    """A cool new character!"""
    
    # Display name in character selection
    name = "Awesome Hero"
    
    # Scale factor (width, height) - 1.0 = original size
    sprite_scale = (0.3, 0.3)
    
    # Subfolder in sprites/characters/ for this character's sprites
    sprite_folder = "characters/my_hero"
    
    # Walk animation frames (first frame also used for idle)
    walk_frames = [
        "walk1.png",
        "walk2.png",
        "walk3.png",
        "walk4.png",
    ]
    
    # Jump animation frames
    jump_frames = [
        "jump1.png",
        "jump2.png",
    ]
```

### Register the Character

Add to `CHARACTER_REGISTRY` at the bottom of the file:

```python
CHARACTER_REGISTRY = {
    "character1": CharacterOne,
    "character2": CharacterTwo,
    "character3": CharacterThree,
    "awesome_hero": MyAwesomeCharacter,  # Add your character
}
```

## Character Attributes

### Required Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Display name in character selection |
| `walk_frames` | `List[str]` | Filenames for walk animation |
| `jump_frames` | `List[str]` | Filenames for jump animation |

### Optional Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `sprite_scale` | `(float, float)` | `(0.25, 0.25)` | Scale factor (x, y) |
| `collider_size` | `(int, int)` | Auto | Fixed hitbox size in pixels |
| `collider_scale` | `(float, float)` | `None` | Hitbox scale relative to sprite |

## Sprite Requirements

### Image Format
- **Format**: PNG with transparency (RGBA)
- **Background**: Transparent
- **Recommended size**: 100-500 pixels (will be scaled)

### Animation Guidelines

- **Walk cycle**: 4-8 frames recommended
- **Jump**: 1-4 frames (can be a single pose)
- **Facing direction**: Face RIGHT (flipped automatically for left)

### Example Sprite Sheet Layout

```
hero_walk1.png  - Standing/first walk frame (also used for idle)
hero_walk2.png  - Mid-stride
hero_walk3.png  - Other leg forward
hero_walk4.png  - Return to standing
hero_jump1.png  - Jump pose
```

## Custom Collider (Hitbox)

If your character's shape differs significantly from its sprite bounds, define a custom collider:

### Fixed Size Collider

```python
class WideCharacter(CharacterClass):
    name = "Wide Boy"
    sprite_scale = (0.5, 0.5)
    
    # Fixed hitbox: 60 pixels wide, 40 pixels tall
    collider_size = (60, 40)
    
    walk_frames = ["wide_walk1.png", "wide_walk2.png"]
    jump_frames = ["wide_jump.png"]
```

### Scaled Collider

```python
class TallCharacter(CharacterClass):
    name = "Tall Guy"
    sprite_scale = (0.3, 0.4)
    
    # Hitbox is 80% width, 90% height of sprite
    collider_scale = (0.8, 0.9)
    
    walk_frames = ["tall_walk1.png", "tall_walk2.png"]
    jump_frames = ["tall_jump.png"]
```

## Complete Example

Here's a complete example of a dinosaur character:

```python
class DinoCharacter(CharacterClass):
    """A friendly dinosaur character.
    
    The Dino has a wider body shape, so we define a custom
    collider_size to match its actual hitbox.
    """
    
    name = "Dino"
    
    # Different X/Y scale for proper proportions
    sprite_scale = (0.45, 0.50)
    
    # Custom hitbox for the dino's body shape
    collider_size = (42, 47)
    
    walk_frames = [
        "DinoRun1.png",
        "DinoRun2.png",
    ]
    
    jump_frames = [
        "DinoJump.png",
    ]


# In CHARACTER_REGISTRY:
CHARACTER_REGISTRY = {
    # ... other characters
    "dino": DinoCharacter,
}
```

## Testing Your Character

1. **Run the game**:
   ```bash
   cd src/code
   python main.py
   ```

2. **Select your character** from the Characters menu

3. **Check the debug view** (F3) to see:
   - Sprite rendering
   - Collision box alignment
   - Animation playback

## Troubleshooting

### Character Not Appearing

- Check that sprite files exist in `src/resources/assets/sprites/`
- Verify filenames match exactly (case-sensitive)
- Ensure the character is added to `CHARACTER_REGISTRY`

### Collision Issues

- Enable debug mode (F3) to see hitbox
- Adjust `collider_size` or `collider_scale`
- Remember: collider is centered on sprite center

### Animation Too Fast/Slow

The default animation speed is 12 FPS. To customize, override the `animations()` method:

```python
class SlowCharacter(CharacterClass):
    # ... other attributes
    
    def animations(self):
        from skeletons.character import Animation, Character
        
        anims = {}
        if self.walk_frames:
            anims["idle"] = Animation(
                Character.load_frames(self.base_folder, [self.walk_frames[0]]),
                fps=1,
                loop=True,
            )
            anims["walk"] = Animation(
                Character.load_frames(self.base_folder, self.walk_frames),
                fps=8,  # Slower walk
                loop=True,
            )
        if self.jump_frames:
            anims["jump"] = Animation(
                Character.load_frames(self.base_folder, self.jump_frames),
                fps=6,  # Slower jump
                loop=False,
            )
        return anims
```

## Advanced: Animation States

The character system supports these animation states:

| State | When Active | Loop |
|-------|-------------|------|
| `idle` | Standing still | Yes |
| `walk` | Moving horizontally | Yes |
| `jump` | In the air | No |
| `fly` | Flying (if implemented) | Yes |
| `land` | Just landed (if implemented) | No |

To add more states, extend the `animations()` method and update `update_state()` logic in your game screen.
