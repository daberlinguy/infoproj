---
title: Creating Screens
description: Build custom game screens and menus
---

# Creating Screens

This guide explains how to create new screens (menus, game states) in Parkour Game.

## Overview

Screens are the building blocks of the game's UI. Each screen:
- Inherits from the `Screen` base class
- Has its own game loop (`run()` method)
- Can transition to other screens

## Screen Architecture

```
Screen (base class)
├── TitleScreen     - Main menu
├── WorldSelectScreen - World browser
├── LevelSelectScreen - Level browser
├── CharacterScreen - Character selection
├── SettingsScreen  - Game settings
├── GameScreen      - Main gameplay
└── FinishScreen    - Level complete
```

## Creating a Basic Screen

### 1. Create the File

Create `src/code/screens/MyScreen.py`:

```python
"""My custom screen module."""

import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.widget import WidgetHandler

from skeletons.screen import Screen
from assets.assets import getFont


class MyScreen(Screen):
    """A custom screen example.
    
    This screen demonstrates the basic structure for creating
    new game screens with buttons and text.
    """
    
    def __init__(self, screen, caption):
        # IMPORTANT: Clear previous widgets first
        widgets = WidgetHandler.getWidgets()
        WidgetHandler._widgets = widgets.__class__()
        
        # Initialize your state variables
        self.clock = pygame.time.Clock()
        self.dt = 0
        
        # Create buttons BEFORE calling super().__init__
        button_width = 200
        button_height = 50
        center_x = (screen.get_width() / 2) - (button_width / 2)
        
        self.back_btn = Button(
            screen,
            center_x,
            screen.get_height() - 100,
            button_width,
            button_height,
            False,
            text="Back",
            onClick=self.on_back_click,
            font=getFont(24),
            radius=10,
        )
        
        # Title setup
        self.title_text = "My Screen"
        self.title_width = getFont(48).size(self.title_text)[0]
        
        # Call parent constructor LAST - this starts the game loop
        super().__init__(screen, caption)
    
    def on_back_click(self):
        """Handle back button click."""
        self.running = False
        from screens.TitleScreen import TitleScreen
        TitleScreen(self.screen, "Title Screen")
    
    def run(self):
        """Main update loop - called every frame."""
        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.on_back_click()
        
        # Draw background
        self.set_backgroundImage("title.jpg")
        
        # Draw title
        self.draw_text(
            self.title_text,
            getFont(48),
            255, 255, 255,
            (self.screen.get_width() / 2) - (self.title_width / 2),
            100,
        )
        
        # Draw buttons
        self.back_btn.draw()
        
        # Update pygame_widgets
        pygame_widgets.update(events)
        
        # Update display
        pygame.display.update()
        
        # Update delta time
        self.dt = min(self.clock.tick() / 1000, 0.0167)
```

### 2. Important Patterns

#### Widget Cleanup

Always clear widgets at the start of `__init__`:

```python
def __init__(self, screen, caption):
    # Clear previous screen's widgets
    widgets = WidgetHandler.getWidgets()
    WidgetHandler._widgets = widgets.__class__()
```

#### Initialization Order

1. Clear widgets
2. Initialize state variables
3. Create buttons/UI elements
4. Call `super().__init__()` **LAST**

The parent constructor starts the game loop immediately!

#### Event Handling

Always handle `QUIT` and `ESCAPE`:

```python
def run(self):
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            self.running = False
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.go_back()
```

## Screen Transitions

### Basic Transition

```python
def go_to_game(self):
    self.running = False  # Stop current screen loop
    from screens.GameScreen import GameScreen
    GameScreen(self.screen, "Game", level_path=my_level)
```

### With Parameters

```python
def select_level(self, level_data):
    self.running = False
    from screens.GameScreen import GameScreen
    GameScreen(
        self.screen,
        "Game",
        level_path=level_data["path"],
    )
```

### Using Settings

```python
from screens.SettingsScreen import SETTINGS
from data.storage import save_settings

def on_select(self, item_id):
    SETTINGS["selected_item"] = item_id
    save_settings(SETTINGS)
    self.running = False
    from screens.NextScreen import NextScreen
    NextScreen(self.screen, "Next")
```

## Common UI Patterns

### Clickable Rows

For selection lists (like world/level select):

```python
class SelectionScreen(Screen):
    def __init__(self, screen, caption):
        # ... widget cleanup ...
        
        self.items = ["Item 1", "Item 2", "Item 3"]
        self.row_rects = []
        
        # Create clickable row rectangles
        grid_x = (screen.get_width() / 2) - 320
        grid_y = 150
        row_height = 80
        row_width = 640
        
        for idx, _ in enumerate(self.items):
            y = grid_y + idx * row_height
            self.row_rects.append(
                pygame.Rect(grid_x, y, row_width, row_height - 10)
            )
        
        super().__init__(screen, caption)
    
    def run(self):
        events = pygame.event.get()
        for event in events:
            # ... quit handling ...
            
            # Handle row clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, row_rect in enumerate(self.row_rects):
                    if row_rect.collidepoint(event.pos):
                        self.select_item(self.items[idx])
        
        # Draw rows with hover effect
        mouse_pos = pygame.mouse.get_pos()
        for idx, row_rect in enumerate(self.row_rects):
            is_hovered = row_rect.collidepoint(mouse_pos)
            
            # Background
            color = (30, 30, 30) if is_hovered else (20, 20, 20)
            pygame.draw.rect(self.screen, color, row_rect, border_radius=8)
            
            # Border
            border_color = (140, 140, 140) if is_hovered else (90, 90, 90)
            pygame.draw.rect(self.screen, border_color, row_rect, 2, border_radius=8)
            
            # Text
            self.draw_text(
                self.items[idx],
                getFont(24),
                255, 255, 255,
                row_rect.x + 20,
                row_rect.y + 20,
            )
```

### Pagination

For long lists:

```python
class PaginatedScreen(Screen):
    def __init__(self, screen, caption):
        # ... setup ...
        self.items = [...]  # Your items
        self.page = 0
        self.items_per_page = 5
        
        # Prev/Next buttons
        self.prev_rect = pygame.Rect(100, 500, 100, 40)
        self.next_rect = pygame.Rect(screen.get_width() - 200, 500, 100, 40)
        
        super().__init__(screen, caption)
    
    def get_page_items(self):
        start = self.page * self.items_per_page
        end = start + self.items_per_page
        return self.items[start:end]
    
    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.prev_rect.collidepoint(event.pos):
                    self.page = max(0, self.page - 1)
                if self.next_rect.collidepoint(event.pos):
                    max_page = (len(self.items) - 1) // self.items_per_page
                    self.page = min(max_page, self.page + 1)
        
        # Draw pagination controls
        pygame.draw.rect(self.screen, (50, 50, 50), self.prev_rect, border_radius=6)
        self.draw_text("Prev", getFont(20), 255, 255, 255, 
                       self.prev_rect.x + 30, self.prev_rect.y + 10)
        
        pygame.draw.rect(self.screen, (50, 50, 50), self.next_rect, border_radius=6)
        self.draw_text("Next", getFont(20), 255, 255, 255,
                       self.next_rect.x + 30, self.next_rect.y + 10)
        
        # Page indicator
        total_pages = max(1, (len(self.items) - 1) // self.items_per_page + 1)
        self.draw_text(f"{self.page + 1} / {total_pages}", ...)
```

### Toggle/Checkbox

```python
from pygame_widgets.toggle import Toggle

class SettingsScreen(Screen):
    def __init__(self, screen, caption):
        # ... setup ...
        
        self.debug_toggle = Toggle(
            screen,
            center_x,
            200,
            150, 40,
            startOn=SETTINGS.get('debug_mode', False),
        )
        
        super().__init__(screen, caption)
    
    def save_settings(self):
        SETTINGS['debug_mode'] = self.debug_toggle.getValue()
        save_settings(SETTINGS)
```

## Base Class Methods

The `Screen` class provides these utility methods:

| Method | Description |
|--------|-------------|
| `set_background(r, g, b)` | Fill with solid color |
| `set_backgroundImage(name)` | Set background image |
| `draw_text(text, font, r, g, b, x, y)` | Render text |
| `draw_sprite(name, x, y, w, h)` | Draw a sprite |

## Best Practices

### 1. Clean Widget Management

Always clear widgets when entering a screen to prevent UI artifacts.

### 2. Consistent Navigation

- `ESCAPE` should go back or open pause menu
- Provide clear back buttons
- Save settings before transitions

### 3. Delta Time

Use delta time for animations and timing:

```python
self.dt = min(self.clock.tick() / 1000, 0.0167)  # Cap at ~60 FPS
```

### 4. Event Handling

Pass events to both your handlers and pygame_widgets:

```python
events = pygame.event.get()
for event in events:
    # Your handling...

pygame_widgets.update(events)  # Widget handling
```

### 5. State Preservation

Use `SETTINGS` dict for persistent state:

```python
from screens.SettingsScreen import SETTINGS
from data.storage import save_settings

# Read
value = SETTINGS.get('key', default_value)

# Write
SETTINGS['key'] = new_value
save_settings(SETTINGS)
```

## Example: Complete Menu Screen

See [TitleScreen.py](src/code/screens/TitleScreen.py) for a complete example of a menu screen with multiple buttons, background image, and animated title.
