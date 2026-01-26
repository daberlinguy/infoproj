---
title: Main Entrypoint
description: Application entrypoint and startup behavior
---

# Main Entrypoint

The application starts in `src/code/main.py`, initializes pygame, and launches the title screen.

## Module Location

```python
from main import main
```

## Behavior

- Initializes pygame
- Creates a fullscreen display surface
- Applies a compatibility fix for `pygame_widgets` on Python 3.14+ by adding `OrderedSet.copy`
- Starts `TitleScreen`

## Entry Function

```python
def main() -> None
```

## Example

```python
if __name__ == "__main__":
    main()
```

## Related Links

- [Screens API](../api/screens)
- [Screen Base Class](../reference/screen-base-class)
