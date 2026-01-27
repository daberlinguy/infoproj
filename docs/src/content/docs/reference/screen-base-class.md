---
title: Screen Base Class Reference
description: API reference for the Screen base class
---

# Screen Base Class Reference

This page documents the `Screen` base class used for creating game screens.

## Module Location

```python
from skeletons.screen import Screen
```

## Class Overview

```python
class Screen:
    """Base class for all game screens."""
    
    # Attributes
    screen: pygame.Surface
    caption: str
    running: bool
    
    # Methods
    def __init__(self, screen: pygame.Surface, caption: str) -> None: ...
    def set_background(self, r: int, g: int, b: int) -> None: ...
    def set_backgroundImage(self, name: str, scale_width: int = 1280, scale_height: int = 720) -> None: ...
    def draw_text(self, text: str, font: pygame.font.Font, r: int, g: int, b: int, x: float, y: float) -> None: ...
    def draw_sprite(self, name: str, x: float, y: float, scale_width: int = None, scale_height: int = None) -> None: ...
    def clear_widgets(mode: str = "reset") -> None: ...
    def run(self) -> None: ...
```

## Attributes

### screen

```python
screen: pygame.Surface
```

The pygame display Surface to render to.

---

### caption

```python
caption: str
```

The window title for this screen.

---

### running

```python
running: bool
```

Controls the main loop. Set to `False` to exit the screen and allow transitions.

---

## Constructor

### \_\_init\_\_

```python
def __init__(self, screen: pygame.Surface, caption: str) -> None
```

Initialize the screen and start the game loop.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `screen` | `pygame.Surface` | The pygame display surface |
| `caption` | `str` | Window title for this screen |

**Important:** The constructor immediately starts the game loop by calling `run()` repeatedly until `self.running` is `False`. All initialization (widgets, state) must happen BEFORE calling `super().__init__()`.

**Example:**
```python
class MyScreen(Screen):
    def __init__(self, screen, caption):
        # 1. Clear widgets first
        self.clear_widgets()
        
        # 2. Initialize state
        self.score = 0
        self.clock = pygame.time.Clock()
        
        # 3. Create UI elements
        self.button = Button(...)
        
        # 4. Call parent LAST (starts game loop)
        super().__init__(screen, caption)
```

---

## Methods

### set_background

```python
def set_background(self, r: int, g: int, b: int) -> None
```

Fill the entire screen with a solid color.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `r` | `int` | Red component (0-255) |
| `g` | `int` | Green component (0-255) |
| `b` | `int` | Blue component (0-255) |

**Example:**
```python
def run(self):
    # Light blue background
    self.set_background(135, 206, 235)
```

---

### set_backgroundImage

```python
def set_backgroundImage(
    self,
    name: str,
    scale_width: int = 1280,
    scale_height: int = 720,
) -> None
```

Set a background image from the assets folder.

This method caches scaled backgrounds by filename and size so repeated calls
in the main loop don't reload images every frame.

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `str` | - | Filename in `assets/backgrounds/` |
| `scale_width` | `int` | `1280` | Target width in pixels |
| `scale_height` | `int` | `720` | Target height in pixels |

**Raises:**
- `FileNotFoundError` if image doesn't exist

**Example:**
```python
def run(self):
    self.set_backgroundImage("title.jpg")
    # Or custom size
    self.set_backgroundImage("title.jpg", 1920, 1080)

    # Sprite draws are cached by name and scale
    self.draw_sprite("player.png", 100, 100, 64, 64)
```

---

### draw_text

```python
def draw_text(
    self,
    text: str,
    font: pygame.font.Font,
    r: int,
    g: int,
    b: int,
    x: float,
    y: float,
) -> None
```

Render text to the screen.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `text` | `str` | Text string to display |
| `font` | `pygame.font.Font` | Font to use |
| `r` | `int` | Red component (0-255) |
| `g` | `int` | Green component (0-255) |
| `b` | `int` | Blue component (0-255) |
| `x` | `float` | X position in pixels |
| `y` | `float` | Y position in pixels |

**Example:**
```python
from assets.assets import getFont

def run(self):
    # White text
    self.draw_text("Hello World", getFont(32), 255, 255, 255, 100, 100)
    
    # Centered text
    text = "Centered"
    width = getFont(32).size(text)[0]
    self.draw_text(
        text, getFont(32), 255, 255, 255,
        (self.screen.get_width() / 2) - (width / 2),
        200
    )
```

---

### draw_sprite

```python
def draw_sprite(
    self,
    name: str,
    x: float,
    y: float,
    scale_width: int = None,
    scale_height: int = None,
) -> None
```

Draw a sprite from the assets folder.

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `str` | - | Filename in `assets/sprites/` |
| `x` | `float` | - | X position in pixels |
| `y` | `float` | - | Y position in pixels |
| `scale_width` | `int` | `None` | Optional target width |
| `scale_height` | `int` | `None` | Optional target height |

Scaling only occurs if BOTH `scale_width` and `scale_height` are provided.

**Example:**
```python
def run(self):
    # Original size
    self.draw_sprite("icon.png", 100, 100)
    
    # Scaled to 64x64
    self.draw_sprite("icon.png", 200, 100, 64, 64)
```

---

### run

```python
def run(self) -> None
```

Main update method called every frame. **Override this in subclasses.**

This method should:
1. Handle pygame events (especially QUIT)
2. Process input
3. Update game state
4. Render the screen
5. Call `pygame.display.update()` or `flip()`

**Example:**
```python
def run(self):
    # 1. Handle events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            self.running = False
            pygame.quit()
            exit()
    
    # 2. Process input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        self.running = False
    
    # 3. Update state
    self.timer += self.dt
    
    # 4. Render
    self.set_backgroundImage("background.jpg")
    self.draw_text("Timer: " + str(self.timer), getFont(24), 255, 255, 255, 10, 10)
    self.button.draw()
    
    # 5. Update display
    pygame_widgets.update(events)
    pygame.display.update()
    
    # Update delta time
    self.dt = min(self.clock.tick() / 1000, 0.0167)
```

---

## Screen Lifecycle

```
1. __init__ called
   ├── Clear previous widgets
   ├── Initialize state variables
   ├── Create UI elements (buttons, etc.)
   └── Call super().__init__()
       └── Sets caption
       └── Enters game loop

2. Game Loop (while self.running)
   └── run() called repeatedly
       ├── Handle events
       ├── Update state
       ├── Render
       └── Display update

3. Exit (self.running = False)
   └── Loop exits
   └── Transition to next screen
```

---

## Common Patterns

### Widget Cleanup

Always clear widgets at screen start to prevent UI artifacts:

```python
def __init__(self, screen, caption):
    from pygame_widgets.widget import WidgetHandler
    widgets = WidgetHandler.getWidgets()
    WidgetHandler._widgets = widgets.__class__()
    # ... rest of init
```

### Screen Transition

```python
def go_to_game(self):
    self.running = False  # Exit current loop
    from screens.GameScreen import GameScreen
    GameScreen(self.screen, "Game")  # Start new screen
```

### Event Handling with Widgets

```python
def run(self):
    events = pygame.event.get()
    for event in events:
        # Your event handling
        pass
    
    # Pass events to widgets
    pygame_widgets.update(events)
```

### Delta Time

For smooth animations:

```python
def __init__(self, screen, caption):
    self.clock = pygame.time.Clock()
    self.dt = 0
    # ...

def run(self):
    # ... rendering ...
    
    # Cap at ~60 FPS to prevent physics issues
    self.dt = min(self.clock.tick() / 1000, 0.0167)
```

---

## Existing Screens

| Screen | Purpose | Location |
|--------|---------|----------|
| `TitleScreen` | Main menu | `screens/TitleScreen.py` |
| `WorldSelectScreen` | World browser | `screens/WorldSelectScreen.py` |
| `LevelSelectScreen` | Level browser | `screens/LevelSelectScreen.py` |
| `CharacterScreen` | Character selection | `screens/CharacterScreen.py` |
| `SettingsScreen` | Game settings | `screens/SettingsScreen.py` |
| `GameScreen` | Main gameplay | `screens/GameScreen.py` |
| `FinishScreen` | Level complete | `screens/FinishScreen.py` |

---

## Complete Example

```python
"""Custom screen example."""

import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.widget import WidgetHandler

from skeletons.screen import Screen
from assets.assets import getFont


class CreditsScreen(Screen):
    """Display game credits."""
    
    def __init__(self, screen, caption):
        # Clear widgets
        widgets = WidgetHandler.getWidgets()
        WidgetHandler._widgets = widgets.__class__()
        
        # State
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.scroll_y = screen.get_height()
        
        # Credits text
        self.credits = [
            ("Game Design", "Your Name"),
            ("Programming", "Your Name"),
            ("Art", "Various Artists"),
            ("Music", "Creative Commons"),
        ]
        
        # Back button
        self.back_btn = Button(
            screen,
            20, 20,
            100, 40,
            False,
            text="Back",
            onClick=self.go_back,
            font=getFont(20),
            radius=8,
        )
        
        super().__init__(screen, caption)
    
    def go_back(self):
        self.running = False
        from screens.TitleScreen import TitleScreen
        TitleScreen(self.screen, "Title")
    
    def run(self):
        # Events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.go_back()
        
        # Update scroll
        self.scroll_y -= 30 * self.dt
        if self.scroll_y < -len(self.credits) * 60:
            self.scroll_y = self.screen.get_height()
        
        # Render
        self.set_background(0, 0, 0)
        
        # Draw scrolling credits
        for i, (role, name) in enumerate(self.credits):
            y = self.scroll_y + i * 60
            if -50 < y < self.screen.get_height() + 50:
                self.draw_text(role, getFont(24), 150, 150, 150,
                              self.screen.get_width() / 2 - 100, y)
                self.draw_text(name, getFont(20), 255, 255, 255,
                              self.screen.get_width() / 2 - 100, y + 25)
        
        # Draw button
        self.back_btn.draw()
        
        # Update
        pygame_widgets.update(events)
        pygame.display.update()
        self.dt = min(self.clock.tick() / 1000, 0.0167)
```
### clear_widgets

```python
def clear_widgets(mode: str = "reset") -> None
```

Clear `pygame_widgets` state between screens.

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `mode` | `str` | `"reset"` | `"reset"` to replace handler storage, `"remove"` to detach widgets |

**Example:**
```python
def __init__(self, screen, caption):
    self.clear_widgets()
    # build UI, then start loop
    super().__init__(screen, caption)
```

---
