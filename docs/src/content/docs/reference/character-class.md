---
title: Character Class Reference
description: API reference for the CharacterClass base class
---

# Character Class Reference

This page documents the `CharacterClass` base class used for defining playable characters.

## Module Location

```python
from skeletons.character_classes.base import CharacterClass
```

## Class Overview

```python
class CharacterClass:
    """Base class for defining playable characters."""
    
    # Class attributes (override these)
    name: str = "Character"
    sprite_scale: Tuple[float, float] = (0.25, 0.25)
    collider_size: Optional[Tuple[int, int]] = None
    collider_scale: Optional[Tuple[float, float]] = None
    walk_frames: List[str] = []
    jump_frames: List[str] = []
    
    # Methods
    def __init__(self, base_folder: Optional[str] = None) -> None: ...
    def animations(self) -> Dict[str, Animation]: ...
    def build(self, position: pygame.Vector2) -> Character: ...
    def get_collider_size(self, default_width: int, default_height: int) -> Tuple[int, int]: ...
```

## Class Attributes

### name

```python
name: str = "Character"
```

Display name shown in the character selection screen.

**Example:**
```python
class MyCharacter(CharacterClass):
    name = "Super Hero"
```

---

### sprite_scale

```python
sprite_scale: Tuple[float, float] = (0.25, 0.25)
```

Scale factor for rendering sprites as `(scale_x, scale_y)`.

- `1.0` = original size
- `0.5` = half size
- `2.0` = double size

**Example:**
```python
class MyCharacter(CharacterClass):
    sprite_scale = (0.3, 0.35)  # Different X and Y scale
```

---

### collider_size

```python
collider_size: Optional[Tuple[int, int]] = None
```

Fixed collision box size in pixels as `(width, height)`.

If `None`, the collider is calculated from sprite dimensions.

**Example:**
```python
class WideCharacter(CharacterClass):
    collider_size = (50, 40)  # 50px wide, 40px tall
```

---

### collider_scale

```python
collider_scale: Optional[Tuple[float, float]] = None
```

Scale factor for the collider relative to sprite size.

Only used if `collider_size` is `None`.

**Example:**
```python
class SlimCharacter(CharacterClass):
    collider_scale = (0.8, 0.9)  # 80% width, 90% height of sprite
```

---

### walk_frames

```python
walk_frames: List[str] = []
```

List of sprite filenames for the walk animation.

- Files must be in `src/resources/assets/sprites/`
- First frame is also used for idle animation
- Order determines animation sequence

**Example:**
```python
class MyCharacter(CharacterClass):
    walk_frames = [
        "hero_walk1.png",
        "hero_walk2.png",
        "hero_walk3.png",
        "hero_walk4.png",
    ]
```

---

### jump_frames

```python
jump_frames: List[str] = []
```

List of sprite filenames for the jump animation.

- Files must be in `src/resources/assets/sprites/`
- Can be a single frame for static jump pose

**Example:**
```python
class MyCharacter(CharacterClass):
    jump_frames = [
        "hero_jump.png",
    ]
```

---

## Methods

### \_\_init\_\_

```python
def __init__(self, base_folder: Optional[str] = None) -> None
```

Initialize the character class.

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `base_folder` | `str` or `None` | `None` | Custom folder for sprite files |

If `base_folder` is `None`, defaults to `assets/sprites/`.

**Example:**
```python
# Default folder
char = MyCharacter()

# Custom folder
char = MyCharacter(base_folder="/path/to/sprites")
```

---

### animations

```python
def animations(self) -> Dict[str, Animation]
```

Build the animations dictionary for this character.

**Returns:**
Dictionary mapping animation state names to `Animation` objects.

**Default states created:**
- `"idle"` - First walk frame, 1 FPS, looping
- `"walk"` - All walk frames, 12 FPS, looping
- `"jump"` - Jump frames, 12 FPS, non-looping

**Example (override for custom FPS):**
```python
class SlowCharacter(CharacterClass):
    walk_frames = ["walk1.png", "walk2.png"]
    
    def animations(self):
        from skeletons.character import Animation, Character
        
        return {
            "idle": Animation(
                Character.load_frames(self.base_folder, [self.walk_frames[0]]),
                fps=1,
                loop=True,
            ),
            "walk": Animation(
                Character.load_frames(self.base_folder, self.walk_frames),
                fps=6,  # Slower than default
                loop=True,
            ),
        }
```

---

### build

```python
def build(self, position: pygame.Vector2) -> Character
```

Create a `Character` instance from this class definition.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `position` | `pygame.Vector2` | Initial position |

**Returns:**
A fully configured `Character` instance.

**Example:**
```python
from skeletons.character_classes.characters import CharacterOne

char_class = CharacterOne()
character = char_class.build(pygame.Vector2(100, 100))

# Now use character in game loop
character.update(dt)
character.draw(screen)
```

---

### get_collider_size

```python
def get_collider_size(
    self,
    default_width: int,
    default_height: int,
) -> Tuple[int, int]
```

Calculate the collision box size for this character.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `default_width` | `int` | Default width from player settings |
| `default_height` | `int` | Default height from player settings |

**Returns:**
Tuple of `(width, height)` in pixels.

**Priority:**
1. `collider_size` if set
2. `collider_scale` applied to defaults
3. Default values unchanged

**Example:**
```python
char_class = MyCharacter()
width, height = char_class.get_collider_size(36, 48)
```

---

## Complete Example

```python
from skeletons.character_classes.base import CharacterClass


class RobotCharacter(CharacterClass):
    """A robot character with custom hitbox.
    
    The robot is wider than it is tall, so we define
    a custom collider_size to match its shape.
    """
    
    name = "Robo-Bot"
    
    # Render at 40% size
    sprite_scale = (0.4, 0.4)
    
    # Custom hitbox for robot shape
    collider_size = (48, 40)
    
    # Walk animation (4 frames)
    walk_frames = [
        "robot_walk1.png",
        "robot_walk2.png",
        "robot_walk3.png",
        "robot_walk4.png",
    ]
    
    # Jump is single frame
    jump_frames = [
        "robot_jump.png",
    ]
    
    def animations(self):
        """Override for custom animation speeds."""
        from skeletons.character import Animation, Character
        
        anims = {}
        
        # Idle: first walk frame
        anims["idle"] = Animation(
            Character.load_frames(self.base_folder, [self.walk_frames[0]]),
            fps=1,
            loop=True,
        )
        
        # Walk: slower mechanical movement
        anims["walk"] = Animation(
            Character.load_frames(self.base_folder, self.walk_frames),
            fps=8,  # Slower than default 12
            loop=True,
        )
        
        # Jump: quick animation
        anims["jump"] = Animation(
            Character.load_frames(self.base_folder, self.jump_frames),
            fps=15,
            loop=False,
        )
        
        return anims


# Register in CHARACTER_REGISTRY
from skeletons.character_classes.characters import CHARACTER_REGISTRY
CHARACTER_REGISTRY["robot"] = RobotCharacter
```

---

## Related Classes

### Animation

```python
from skeletons.character import Animation

Animation(
    frames: List[pygame.Surface],
    fps: int = 12,
    loop: bool = True,
)
```

### Character

```python
from skeletons.character import Character

Character(
    position: Tuple[float, float],
    animations: Dict[str, Animation],
    default_state: str = "idle",
    scale: float = 1.0,
    scale_x: Optional[float] = None,
    scale_y: Optional[float] = None,
)
```

---

## Registration

Characters must be registered in `CHARACTER_REGISTRY` to appear in the game:

```python
# In characters.py
CHARACTER_REGISTRY = {
    "character1": CharacterOne,
    "character2": CharacterTwo,
    "robot": RobotCharacter,  # Add your character
}
```

The key (`"robot"`) is used internally for settings and save data.
