"""Character definitions and registry.

This module contains all playable character definitions and the global
CHARACTER_REGISTRY used by the game to load characters.

To add a new character:

1. Create a new class extending CharacterClass
2. Define the required class attributes (name, frames, etc.)
3. Add it to CHARACTER_REGISTRY with a unique ID

Example::

    class MyNewCharacter(CharacterClass):
        name = "Cool Hero"
        sprite_scale = (0.3, 0.3)
        sprite_folder = "characters/hero"  # Subfolder in sprites/
        walk_frames = ["walk1.png", "walk2.png"]
        jump_frames = ["jump.png"]

    # Add to registry
    CHARACTER_REGISTRY["my_hero"] = MyNewCharacter

See Also:
    :class:`skeletons.character_classes.base.CharacterClass` for base class details.
"""

from __future__ import annotations

from typing import Dict, Type

from skeletons.character_classes.base import CharacterClass


class CharacterOne(CharacterClass):
    """ChatLink - The default character.

    A friendly chat mascot with smooth walking and jumping animations.
    """

    name = "ChatLink"
    sprite_scale = (0.20, 0.20)
    sprite_folder = "characters/chatlink"

    walk_frames = [
        "walk1.png",
        "walk2.png",
        "walk3.png",
        "walk4.png",
        "walk5.png",
    ]

    jump_frames = [
        "jump1.png",
        "jump2.png",
        "jump3.png",
        "jump4.png",
    ]


class CharacterTwo(CharacterClass):
    """Dino - A dinosaur character.

    A cute dinosaur with a unique hitbox size for its body shape.

    Note:
        This character has a custom collider_size because its sprite
        proportions differ significantly from the default.
    """

    name = "Dino"
    sprite_scale = (0.45, 0.50)  # Width, Height scale
    collider_size = (42, 47)  # Custom hitbox: Width, Height in pixels
    sprite_folder = "characters/dino"

    walk_frames = [
        "run1.png",
        "run2.png",
    ]

    jump_frames = [
        "jump.png",
    ]


class CharacterThree(CharacterClass):
    """Character 3 - An alternative character option.

    Uses the same sprites as ChatLink but at a larger scale.
    """

    name = "Character 3"
    sprite_scale = (0.25, 0.25)
    sprite_folder = "characters/chatlink"

    walk_frames = [
        "walk1.png",
        "walk2.png",
        "walk3.png",
        "walk4.png",
        "walk5.png",
    ]

    jump_frames = [
        "jump1.png",
        "jump2.png",
        "jump3.png",
        "jump4.png",
    ]


#: Global registry mapping character IDs to their class definitions.
#: Character IDs are used in settings and save data.
#:
#: To add a new character, define your CharacterClass subclass and add it here::
#:
#:     CHARACTER_REGISTRY["my_char_id"] = MyCharacterClass
#:
CHARACTER_REGISTRY: Dict[str, Type[CharacterClass]] = {
    "character1": CharacterOne,
    "character2": CharacterTwo,
    "character3": CharacterThree,
}
