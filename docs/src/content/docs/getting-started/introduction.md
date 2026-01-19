---
title: Introduction
description: Welcome to the Parkour Game documentation
---

# Welcome to Parkour Game

Parkour Game is a 2D platformer built with Python and Pygame. This documentation will help you understand the codebase, create new content, and extend the game.

## Features

- **Animated Characters**: Support for multiple playable characters with walk and jump animations
- **Level System**: JSON-based level format with multi-page support
- **Platform Types**: Normal, death, slippery, checkpoint, spawn, and finish platforms
- **Texture Support**: Minecraft-style texture atlas for platform visuals
- **World/Level Selection**: Organized level browser with progress tracking
- **Debug Mode**: Built-in debug features for development

## Project Structure

```
infoproj/
├── src/
│   ├── code/
│   │   ├── main.py              # Game entry point
│   │   ├── assets/              # Asset loading utilities
│   │   ├── data/                # Save/load functionality
│   │   ├── screens/             # Game screens (Title, Game, etc.)
│   │   ├── skeletons/           # Core game classes
│   │   │   ├── screen.py        # Base screen class
│   │   │   ├── character.py     # Animation & character rendering
│   │   │   ├── platform.py      # Platform & grid system
│   │   │   ├── spieler.py       # Player physics & collision
│   │   │   └── character_classes/
│   │   │       ├── base.py      # CharacterClass base
│   │   │       └── characters.py # Character definitions
│   │   └── utils/               # Path utilities
│   └── resources/
│       └── assets/              # Game assets (sprites, fonts, backgrounds)
├── data/
│   ├── settings.json            # User settings
│   └── worlds/                  # Level files organized by world
├── levels/                      # Legacy levels (auto-migrated)
└── docs/                        # This documentation
```

## Quick Links

import { Card, CardGrid } from '@astrojs/starlight/components';

<CardGrid>
  <Card title="Adding Characters" icon="pencil">
    Learn how to create new playable characters with custom sprites.
    [Read guide →](/guides/adding-characters)
  </Card>
  <Card title="Creating Levels" icon="document">
    Design new levels using the JSON level format.
    [Read guide →](/guides/creating-levels)
  </Card>
  <Card title="Creating Screens" icon="laptop">
    Build new game screens and menus.
    [Read guide →](/guides/creating-screens)
  </Card>
  <Card title="Level Format Reference" icon="open-book">
    Complete reference for the level JSON schema.
    [View reference →](/reference/level-format)
  </Card>
</CardGrid>

## Requirements

- Python 3.10+
- Pygame 2.x
- pygame-widgets
- PyQt6 (for editor only)
