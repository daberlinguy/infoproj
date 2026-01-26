---
title: Paths API
description: API reference for project and resource path helpers
---

# Paths API Reference

Helper functions for resolving paths in both normal and bundled (frozen) builds.

## Module Location

```python
from utils.paths import (
    bundle_root,
    project_root,
    resources_root,
    resources_path,
    assets_root,
    assets_path,
    data_root,
    levels_root,
    bundled_data_root,
    bundled_levels_root,
)
```

## Overview

These helpers:
- Resolve paths relative to the project root in development
- Resolve paths inside a bundled app (PyInstaller) using `sys._MEIPASS`

## Functions

### bundle_root()

Returns the root of the bundled app if frozen, otherwise the source root.

**Returns:** `str`

---

### project_root()

Returns the project root in development, or the executable directory when frozen.

**Returns:** `str`

---

### resources_root()

Path to the `resources` directory.

**Returns:** `str`

---

### resources_path(*parts)

Build a path inside `resources`.

```python
config_path = resources_path("textures.json")
```

**Returns:** `str`

---

### assets_root()

Path to `resources/assets`.

**Returns:** `str`

---

### assets_path(*parts)

Build a path inside `resources/assets`.

```python
image_path = assets_path("backgrounds", "title.jpg")
```

**Returns:** `str`

---

### data_root()

Path to the project `data` folder.

**Returns:** `str`

---

### levels_root()

Legacy path to the `levels` folder (if present).

**Returns:** `str`

---

### bundled_data_root()

Path to bundled `data` folder.

**Returns:** `str`

---

### bundled_levels_root()

Path to bundled legacy `levels` folder.

**Returns:** `str`

## Usage Example

```python
from utils.paths import assets_path, data_root

bg_path = assets_path("backgrounds", "title.jpg")
settings_dir = data_root()
```

## Related Links

- [Assets API](../api/assets)
- [Storage API](../api/storage)
