import json
import os
import shutil

from utils.paths import data_root, levels_root, bundled_data_root, bundled_levels_root

data_dir = data_root()
settings_path = os.path.join(data_dir, "settings.json")
worlds_dir = os.path.join(data_dir, "worlds")
legacy_levels_dir = levels_root()

_cached_worlds = None


def ensure_data_dirs():
    os.makedirs(worlds_dir, exist_ok=True)


def _maybe_seed_bundle_data():
    if os.listdir(worlds_dir):
        return
    bundled_worlds = os.path.join(bundled_data_root(), "worlds")
    if os.path.isdir(bundled_worlds):
        shutil.copytree(bundled_worlds, worlds_dir, dirs_exist_ok=True)


def _default_settings():
    return {
        "debug_mode": False,
        "character": "character1",
        "selected_world": None,
        "selected_level": None,
        "progress": {"worlds": {}},
        "controls": {
            "move_down": ["s"],
            "move_left": ["a"],
            "move_right": ["d"],
            "jump": ["space", "w"],
            "attack": ["k"],
        },
    }


def load_settings():
    ensure_data_dirs()
    _maybe_seed_bundle_data()
    if not os.path.exists(settings_path):
        settings = _default_settings()
        save_settings(settings)
        return settings
    with open(settings_path, "r", encoding="utf-8") as f:
        settings = json.load(f)
    for key, value in _default_settings().items():
        settings.setdefault(key, value)
    settings.setdefault("progress", {"worlds": {}})
    settings["progress"].setdefault("worlds", {})
    return settings


def save_settings(settings):
    ensure_data_dirs()
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def _maybe_migrate_legacy_levels():
    legacy_sources = []
    if os.path.isdir(legacy_levels_dir):
        legacy_sources.append(legacy_levels_dir)
    bundled_legacy = bundled_levels_root()
    if os.path.isdir(bundled_legacy):
        legacy_sources.append(bundled_legacy)
    if not legacy_sources:
        return
    if os.listdir(worlds_dir):
        return
    for source in legacy_sources:
        for world_name in os.listdir(source):
            world_path = os.path.join(source, world_name)
            if not os.path.isdir(world_path):
                continue
            dest_path = os.path.join(worlds_dir, world_name)
            shutil.copytree(world_path, dest_path, dirs_exist_ok=True)


def load_worlds(force_reload=False):
    global _cached_worlds
    if _cached_worlds is not None and not force_reload:
        return _cached_worlds

    ensure_data_dirs()
    _maybe_migrate_legacy_levels()
    worlds = {}
    if not os.path.isdir(worlds_dir):
        return worlds
    for world_name in sorted(os.listdir(worlds_dir)):
        world_path = os.path.join(worlds_dir, world_name)
        if not os.path.isdir(world_path):
            continue
        levels = []
        for entry in sorted(os.listdir(world_path)):
            if not entry.endswith(".json"):
                continue
            level_path = os.path.join(world_path, entry)
            level_name = entry
            try:
                with open(level_path, "r", encoding="utf-8") as f:
                    level_data = json.load(f)
                level_name = level_data.get("name", entry)
            except (OSError, json.JSONDecodeError):
                level_data = {}
            levels.append(
                {
                    "id": entry,
                    "name": level_name,
                    "path": level_path,
                    "data": level_data,
                }
            )
        worlds[world_name] = {"name": world_name, "path": world_path, "levels": levels}

    _cached_worlds = worlds
    return worlds
