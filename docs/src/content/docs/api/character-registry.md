---
title: Character Registry API
description: API reference for CHARACTER_REGISTRY and built-in characters
---

# Character Registry API Reference

`CHARACTER_REGISTRY` maps character IDs to their `CharacterClass` definitions.

## Module Location

```python
from skeletons.character_classes.characters import CHARACTER_REGISTRY
```

## Registry Structure

```python
CHARACTER_REGISTRY: Dict[str, Type[CharacterClass]]
```

**Keys:** Character IDs saved in settings

**Values:** `CharacterClass` subclasses

## Built-in Characters

| ID | Class | Display Name | Notes |
|----|-------|--------------|------|
| `character1` | `CharacterOne` | ChatLink | Default character |
| `character2` | `CharacterTwo` | Dino | Custom collider size |
| `character3` | `CharacterThree` | CKghnit | Large scale sprite |

## Usage Example

```python
from skeletons.character_classes.characters import CHARACTER_REGISTRY

character_cls = CHARACTER_REGISTRY["character1"]
character = character_cls().build(pygame.Vector2(100, 100))
```

## Adding New Characters

Register new characters by adding them to `CHARACTER_REGISTRY`:

```python
CHARACTER_REGISTRY["robot"] = RobotCharacter
```

## Related Links

- [Character Class Reference](../reference/character-class)
- [Adding Characters Guide](../guides/adding-characters)
