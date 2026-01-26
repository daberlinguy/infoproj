"""Level Editor for the Parkour Game.

This editor uses a shared texture configuration (textures.json) that is
automatically synced between the game and the editor. To add new textures,
simply edit textures.json and they will appear in both applications.
"""

import copy
import json
import os
import sys

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QPen, QBrush, QPainter, QPixmap, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


def _resource_path(*parts):
    """Get path to a resource file, works both in development and packaged app."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, *parts)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(project_root, *parts)


def _load_texture_config():
    """Load texture configuration from textures.json.

    Returns:
        dict: The texture configuration containing textures and platform_types.
    """
    config_paths = [
        _resource_path("resources", "textures.json"),
        _resource_path("src", "resources", "textures.json"),
    ]
    for path in config_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

    # Fallback to hardcoded defaults if config not found
    return {
        "textures": {
            "GRASS": {"x": 352, "y": 576, "width": 16, "height": 16},
            "ICE": {"x": 112, "y": 576, "width": 16, "height": 16},
            "STONE": {"x": 640, "y": 640, "width": 16, "height": 16},
            "GOLD_BLOCK": {"x": 288, "y": 576, "width": 16, "height": 16},
            "LAVA": {"x": 400, "y": 592, "width": 16, "height": 16},
        },
        "platform_types": [
            {"name": "NORMAL"},
            {"name": "DEATH"},
            {"name": "CHECKPOINT"},
            {"name": "FINISH"},
            {"name": "SLIPPERY"},
            {"name": "NOCLIP"},
        ],
    }


# Load configuration dynamically
_CONFIG = _load_texture_config()

# Extract platform types from config
PLATFORM_TYPES = [pt["name"] for pt in _CONFIG.get("platform_types", [])]

# Build texture list with empty string as first option (no texture)
TEXTURE_TYPES = [""] + list(_CONFIG.get("textures", {}).keys())

# Build texture atlas coordinates from config
TEXTURE_ATLAS = {
    name: (data["x"], data["y"], data.get("width", 16), data.get("height", 16))
    for name, data in _CONFIG.get("textures", {}).items()
}

# Global grid defaults (in cells)
DEFAULT_GRID_COLUMNS = 60
DEFAULT_GRID_ROWS = 34


class LevelEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Level Editor")
        self.resize(900, 600)

        self.level_data = {
            "name": "New Level",
            "player_spawn": {"x": 0, "y": 0, "grid": True, "grid_size": 32},
            "background_color": {"r": 135, "g": 206, "b": 235, "a": 255},
            "page_width_cells": DEFAULT_GRID_COLUMNS,
            "page_height_cells": DEFAULT_GRID_ROWS,
            "pages": {"1": {"cells": []}},
        }
        self.current_path = None
        self.current_page = "1"
        self.undo_stack = []
        self.redo_stack = []

        root = QWidget()
        layout = QHBoxLayout()
        root.setLayout(layout)
        self.setCentralWidget(root)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        self.canvas = LevelCanvas(self)
        splitter.addWidget(self.canvas)

        self.platform_list = QListWidget()
        self.platform_list.currentRowChanged.connect(self._load_platform_into_form)
        splitter.addWidget(self.platform_list)

        right_panel = QWidget()
        right = QVBoxLayout()
        right_panel.setLayout(right)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 200, 300])

        right.addLayout(self._build_level_form())
        right.addSpacing(10)
        right.addLayout(self._build_page_controls())
        right.addLayout(self._build_mode_controls())
        right.addLayout(self._build_platform_form())
        right.addSpacing(10)
        right.addLayout(self._build_buttons())
        right.addStretch()

        self.status_label = QLabel("")
        right.addWidget(self.status_label)
        self._set_mode("add")
        self._refresh_platform_list()
        self.canvas.render_scene()

    def _build_level_form(self):
        form = QFormLayout()

        self.level_name = QLineEdit(self.level_data["name"])
        form.addRow("Level Name", self.level_name)

        spawn_layout = QGridLayout()
        self.spawn_x = QSpinBox()
        self.spawn_y = QSpinBox()
        self.spawn_grid = QCheckBox("Grid")
        self.spawn_grid_size = QSpinBox()
        self.spawn_x.setRange(-9999, 9999)
        self.spawn_y.setRange(-9999, 9999)
        self.spawn_grid_size.setRange(1, 512)
        self.spawn_grid.setChecked(True)
        self.spawn_grid_size.setValue(32)
        self.spawn_x.valueChanged.connect(self._on_level_field_change)
        self.spawn_y.valueChanged.connect(self._on_level_field_change)
        self.spawn_grid.stateChanged.connect(self._on_level_field_change)
        self.spawn_grid_size.valueChanged.connect(self._on_level_field_change)
        spawn_layout.addWidget(QLabel("X"), 0, 0)
        spawn_layout.addWidget(self.spawn_x, 0, 1)
        spawn_layout.addWidget(QLabel("Y"), 0, 2)
        spawn_layout.addWidget(self.spawn_y, 0, 3)
        spawn_layout.addWidget(self.spawn_grid, 1, 0)
        spawn_layout.addWidget(QLabel("Grid Size"), 1, 2)
        spawn_layout.addWidget(self.spawn_grid_size, 1, 3)
        form.addRow("Player Spawn", spawn_layout)

        bg_layout = QGridLayout()
        self.bg_r = QSpinBox()
        self.bg_g = QSpinBox()
        self.bg_b = QSpinBox()
        for spin in (self.bg_r, self.bg_g, self.bg_b):
            spin.setRange(0, 255)
        self.bg_r.setValue(135)
        self.bg_g.setValue(206)
        self.bg_b.setValue(235)
        self.bg_image = QLineEdit("")
        self.bg_image.textChanged.connect(self._on_level_field_change)
        bg_layout.addWidget(QLabel("R"), 0, 0)
        bg_layout.addWidget(self.bg_r, 0, 1)
        bg_layout.addWidget(QLabel("G"), 0, 2)
        bg_layout.addWidget(self.bg_g, 0, 3)
        bg_layout.addWidget(QLabel("B"), 0, 4)
        bg_layout.addWidget(self.bg_b, 0, 5)
        bg_layout.addWidget(QLabel("Image"), 1, 0)
        bg_layout.addWidget(self.bg_image, 1, 1, 1, 5)
        form.addRow("Background", bg_layout)

        return form

    def _build_platform_form(self):
        form = QFormLayout()

        coord_layout = QGridLayout()
        self.x1 = QSpinBox()
        self.y1 = QSpinBox()
        self.x2 = QSpinBox()
        self.y2 = QSpinBox()
        for spin in (self.x1, self.y1, self.x2, self.y2):
            spin.setRange(-9999, 9999)
            spin.setReadOnly(True)
        coord_layout.addWidget(QLabel("x1"), 0, 0)
        coord_layout.addWidget(self.x1, 0, 1)
        coord_layout.addWidget(QLabel("y1"), 0, 2)
        coord_layout.addWidget(self.y1, 0, 3)
        coord_layout.addWidget(QLabel("x2"), 1, 0)
        coord_layout.addWidget(self.x2, 1, 1)
        coord_layout.addWidget(QLabel("y2"), 1, 2)
        coord_layout.addWidget(self.y2, 1, 3)
        form.addRow("Grid Coords", coord_layout)

        self.grid_size = QSpinBox()
        self.grid_size.setRange(1, 512)
        self.grid_size.setValue(32)
        self.grid_size.setReadOnly(True)
        form.addRow("Grid Size", self.grid_size)

        self.platform_type = QComboBox()
        self.platform_type.addItems(PLATFORM_TYPES)
        form.addRow("Type", self.platform_type)

        self.texture_type = QComboBox()
        self.texture_type.addItems(TEXTURE_TYPES)
        form.addRow("Texture", self.texture_type)

        color_layout = QGridLayout()
        self.color_r = QSpinBox()
        self.color_g = QSpinBox()
        self.color_b = QSpinBox()
        for spin in (self.color_r, self.color_g, self.color_b):
            spin.setRange(0, 255)
        color_layout.addWidget(QLabel("R"), 0, 0)
        color_layout.addWidget(self.color_r, 0, 1)
        color_layout.addWidget(QLabel("G"), 0, 2)
        color_layout.addWidget(self.color_g, 0, 3)
        color_layout.addWidget(QLabel("B"), 0, 4)
        color_layout.addWidget(self.color_b, 0, 5)
        form.addRow("Color", color_layout)

        self.apply_selected_btn = QPushButton("Apply to Selected")
        self.apply_selected_btn.clicked.connect(self._apply_to_selected)
        form.addRow(self.apply_selected_btn)

        return form

    def _build_page_controls(self):
        layout = QHBoxLayout()
        self.page_label = QLabel("Page")
        self.page_select = QSpinBox()
        self.page_select.setRange(1, 999)
        self.page_select.setValue(int(self.current_page))
        self.page_select.valueChanged.connect(self._on_page_change)
        layout.addWidget(self.page_label)
        layout.addWidget(self.page_select)
        return layout

    def _build_mode_controls(self):
        layout = QHBoxLayout()
        self.mode_label = QLabel("Mode: Select")
        self.mode_select_btn = QPushButton("Select")
        self.mode_add_btn = QPushButton("Add")
        self.mode_select_btn.clicked.connect(lambda: self._set_mode("select"))
        self.mode_add_btn.clicked.connect(lambda: self._set_mode("add"))
        layout.addWidget(self.mode_label)
        layout.addWidget(self.mode_select_btn)
        layout.addWidget(self.mode_add_btn)
        return layout

    def _build_buttons(self):
        layout = QHBoxLayout()

        add_btn = QPushButton("Add Platform")
        add_btn.clicked.connect(self._add_platform)
        update_btn = QPushButton("Update Platform")
        update_btn.clicked.connect(self._update_platform)
        remove_btn = QPushButton("Remove Platform")
        remove_btn.clicked.connect(self._remove_platform)
        merge_btn = QPushButton("Merge Platforms")
        merge_btn.clicked.connect(self._merge_platforms)
        load_btn = QPushButton("Load JSON")
        load_btn.clicked.connect(self._load_json)
        save_btn = QPushButton("Save JSON")
        save_btn.clicked.connect(self._save_json)

        layout.addWidget(add_btn)
        layout.addWidget(update_btn)
        layout.addWidget(remove_btn)
        layout.addWidget(merge_btn)
        layout.addWidget(load_btn)
        layout.addWidget(save_btn)
        return layout

    def _set_status(self, text):
        self.status_label.setText(text)

    def _snapshot_state(self):
        return copy.deepcopy(self.level_data)

    def _record_undo(self):
        self.undo_stack.append(self._snapshot_state())
        self.redo_stack.clear()

    def _sync_level_fields(self):
        self.level_data["name"] = self.level_name.text().strip() or "New Level"
        self.level_data["player_spawn"] = {
            "x": self.spawn_x.value(),
            "y": self.spawn_y.value(),
            "grid": self.spawn_grid.isChecked(),
            "grid_size": self.spawn_grid_size.value(),
        }
        self.level_data["background_color"] = {
            "r": self.bg_r.value(),
            "g": self.bg_g.value(),
            "b": self.bg_b.value(),
            "a": 255,
        }
        image_path = self.bg_image.text().strip()
        if image_path:
            self.level_data["background_color"]["image"] = image_path

    def _collect_platform_fields(self):
        platform = {
            "x1": self.x1.value(),
            "y1": self.y1.value(),
            "x2": self.x2.value(),
            "y2": self.y2.value(),
            "grid_size": self.grid_size.value(),
            "type": self.platform_type.currentText(),
        }
        texture = self.texture_type.currentText()
        if texture:
            platform["texture"] = texture
        platform["color"] = [self.color_r.value(), self.color_g.value(), self.color_b.value()]
        return platform

    def _load_platform_into_form(self, index):
        cells = self._current_cells()
        if index < 0 or index >= len(cells):
            return
        cell = cells[index]
        platform = {
            "x1": cell.get("x", 0),
            "y1": cell.get("y", 0),
            "x2": cell.get("x", 0),
            "y2": cell.get("y", 0),
            "grid_size": cell.get("grid_size", 32),
            "type": cell.get("type", "NORMAL"),
            "texture": cell.get("texture", ""),
            "color": cell.get("color", [0, 0, 0]),
        }
        self.x1.setValue(platform.get("x1", 0))
        self.y1.setValue(platform.get("y1", 0))
        self.x2.setValue(platform.get("x2", 0))
        self.y2.setValue(platform.get("y2", 0))
        self.grid_size.setValue(platform.get("grid_size", 32))
        self.platform_type.setCurrentText(platform.get("type", "NORMAL"))
        self.texture_type.setCurrentText(platform.get("texture", ""))
        color = platform.get("color", [0, 0, 0])
        if len(color) >= 3:
            self.color_r.setValue(color[0])
            self.color_g.setValue(color[1])
            self.color_b.setValue(color[2])
        self.canvas.select_platform_index(index)

    def _refresh_platform_list(self):
        self.platform_list.clear()
        for idx, cell in enumerate(self._current_cells()):
            label = f"{idx + 1}: ({cell.get('x')},{cell.get('y')}) {cell.get('type', '')}"
            self.platform_list.addItem(label)
        self.canvas.render_scene()

    def _add_platform(self):
        self._record_undo()
        self._sync_level_fields()
        cell = self._collect_platform_fields()
        cell["x"] = cell.pop("x1")
        cell["y"] = cell.pop("y1")
        cell.pop("x2", None)
        cell.pop("y2", None)
        self._current_cells().append(cell)
        self._refresh_platform_list()
        self._set_status("Platform added.")

    def _update_platform(self):
        index = self.platform_list.currentRow()
        if index < 0:
            QMessageBox.warning(self, "No selection", "Select a platform to update.")
            return
        self._record_undo()
        self._sync_level_fields()
        cell = self._collect_platform_fields()
        cell["x"] = cell.pop("x1")
        cell["y"] = cell.pop("y1")
        cell.pop("x2", None)
        cell.pop("y2", None)
        self._current_cells()[index] = cell
        self._refresh_platform_list()
        self.platform_list.setCurrentRow(index)
        self._set_status("Platform updated.")

    def _remove_platform(self):
        index = self.platform_list.currentRow()
        if index < 0:
            QMessageBox.warning(self, "No selection", "Select a platform to remove.")
            return
        self._record_undo()
        self._current_cells().pop(index)
        self._refresh_platform_list()
        self._set_status("Platform removed.")

    def _load_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Level JSON", "", "JSON Files (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.level_data = json.load(f)
            self.current_path = path
            self.level_data.setdefault("page_width_cells", DEFAULT_GRID_COLUMNS)
            self.level_data.setdefault("page_height_cells", DEFAULT_GRID_ROWS)
            self._ensure_pages()
            self._expand_platforms_to_cells()
            self._apply_level_to_form()
            self._refresh_platform_list()
            self.undo_stack.clear()
            self.redo_stack.clear()
            self._set_status(f"Loaded {os.path.basename(path)}")
        except (OSError, json.JSONDecodeError) as exc:
            QMessageBox.critical(self, "Load failed", str(exc))

    def _save_json(self):
        self._sync_level_fields()
        if not self.current_path:
            path, _ = QFileDialog.getSaveFileName(self, "Save Level JSON", "", "JSON Files (*.json)")
            if not path:
                return
            self.current_path = path
        try:
            payload = self._build_save_payload()
            with open(self.current_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            self._set_status(f"Saved {os.path.basename(self.current_path)}")
        except OSError as exc:
            QMessageBox.critical(self, "Save failed", str(exc))

    def _apply_level_to_form(self):
        self.level_name.setText(self.level_data.get("name", "New Level"))
        spawn = self.level_data.get("player_spawn", {})
        self.spawn_x.setValue(spawn.get("x", 0))
        self.spawn_y.setValue(spawn.get("y", 0))
        self.spawn_grid.setChecked(spawn.get("grid", True))
        self.spawn_grid_size.setValue(spawn.get("grid_size", 32))
        bg = self.level_data.get("background_color", {})
        self.bg_r.setValue(bg.get("r", 135))
        self.bg_g.setValue(bg.get("g", 206))
        self.bg_b.setValue(bg.get("b", 235))
        self.bg_image.setText(bg.get("image", ""))
        self.canvas.render_scene()

    def _merge_platforms(self):
        platforms = self._cells_to_platforms(self._current_cells())
        if not platforms:
            QMessageBox.information(self, "No platforms", "No platforms to merge.")
            return
        self._record_undo()
        merged = self._merge_platforms_internal(platforms)
        self.level_data["pages"][self.current_page]["platforms"] = merged
        self._refresh_platform_list()
        self._set_status("Platforms merged.")

    def _merge_platforms_internal(self, platforms):
        cell_groups = {}
        for platform in platforms:
            x1 = int(platform.get("x1", 0))
            y1 = int(platform.get("y1", 0))
            x2 = int(platform.get("x2", 0))
            y2 = int(platform.get("y2", 0))
            grid_size = int(platform.get("grid_size", 32))
            key = (
                platform.get("type", "NORMAL"),
                platform.get("texture"),
                tuple(platform.get("color", [120, 120, 120])),
                grid_size,
            )
            cells = cell_groups.setdefault(key, set())
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    cells.add((x, y))

        merged_platforms = []
        for key, cells in cell_groups.items():
            remaining = set(cells)
            while remaining:
                x, y = min(remaining)
                width = 1
                while (x + width, y) in remaining:
                    width += 1
                height = 1
                while True:
                    next_row = [(x + dx, y + height) for dx in range(width)]
                    if all(cell in remaining for cell in next_row):
                        height += 1
                    else:
                        break
                for dy in range(height):
                    for dx in range(width):
                        remaining.discard((x + dx, y + dy))
                platform_type, texture, color, grid_size = key
                entry = {
                    "x1": x,
                    "y1": y,
                    "x2": x + width - 1,
                    "y2": y + height - 1,
                    "grid_size": grid_size,
                    "type": platform_type,
                    "color": list(color),
                }
                if texture:
                    entry["texture"] = texture
                merged_platforms.append(entry)

        return merged_platforms

    def _expand_platforms_to_cells(self):
        pages = self.level_data.get("pages", {})
        for page_key, page in pages.items():
            platforms = page.get("platforms", [])
            if not platforms and "cells" in page:
                continue
            cells = []
            for platform in platforms:
                x1 = int(platform.get("x1", 0))
                y1 = int(platform.get("y1", 0))
                x2 = int(platform.get("x2", 0))
                y2 = int(platform.get("y2", 0))
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    for x in range(min(x1, x2), max(x1, x2) + 1):
                        cell = {
                            "x": x,
                            "y": y,
                            "grid_size": platform.get("grid_size", 32),
                            "type": platform.get("type", "NORMAL"),
                            "color": platform.get("color", [120, 120, 120]),
                        }
                        if platform.get("texture"):
                            cell["texture"] = platform["texture"]
                        cells.append(cell)
            page["cells"] = cells
            if "platforms" in page:
                page.pop("platforms")

    def _build_save_payload(self):
        payload = {
            "name": self.level_data.get("name", "New Level"),
            "player_spawn": self.level_data.get("player_spawn", {}),
            "background_color": self.level_data.get("background_color", {}),
            "page_width_cells": self.level_data.get("page_width_cells", DEFAULT_GRID_COLUMNS),
            "page_height_cells": self.level_data.get("page_height_cells", DEFAULT_GRID_ROWS),
            "pages": {},
        }
        for page_key, page in self.level_data.get("pages", {}).items():
            cells = page.get("cells", [])
            platforms = self._merge_platforms_internal(self._cells_to_platforms(cells))
            payload["pages"][str(page_key)] = {"platforms": platforms}
        return payload

    def _cells_to_platforms(self, cells):
        platforms = []
        for cell in cells:
            platform = {
                "x1": cell.get("x", 0),
                "y1": cell.get("y", 0),
                "x2": cell.get("x", 0),
                "y2": cell.get("y", 0),
                "grid_size": cell.get("grid_size", 32),
                "type": cell.get("type", "NORMAL"),
                "color": cell.get("color", [120, 120, 120]),
            }
            if cell.get("texture"):
                platform["texture"] = cell["texture"]
            platforms.append(platform)
        return platforms

    def _ensure_pages(self):
        pages = self.level_data.get("pages")
        if not pages:
            platforms = self.level_data.pop("platforms", [])
            self.level_data["pages"] = {"1": {"cells": []}}
            pages = self.level_data["pages"]
        if str(self.current_page) not in pages:
            pages[str(self.current_page)] = {"cells": []}

    def _current_cells(self):
        self._ensure_pages()
        return self.level_data["pages"][self.current_page]["cells"]

    def _on_page_change(self, value):
        self.current_page = str(value)
        self._ensure_pages()
        self._refresh_platform_list()

    def _on_level_field_change(self):
        self._sync_level_fields()
        self.canvas.render_scene()

    def _apply_to_selected(self):
        selected_indices = self.canvas.get_selected_indices()
        if not selected_indices:
            QMessageBox.warning(self, "No selection", "Select platforms in the preview.")
            return
        self._record_undo()
        self._sync_level_fields()
        payload = self._collect_platform_fields()
        for index in selected_indices:
            cell = self._current_cells()[index]
            cell.update(payload)
            cell["x"] = cell.pop("x1")
            cell["y"] = cell.pop("y1")
            cell.pop("x2", None)
            cell.pop("y2", None)
        self._refresh_platform_list()
        self._set_status(f"Updated {len(selected_indices)} platform(s).")

    def add_platform_from_rect(self, x1, y1, x2, y2):
        self._record_undo()
        self._sync_level_fields()
        base = self._collect_platform_fields()
        base.pop("x2", None)
        base.pop("y2", None)
        cells = self._current_cells()
        existing = {(cell.get("x"), cell.get("y")) for cell in cells}
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if (x, y) in existing:
                    continue
                cell = dict(base)
                cell["x"] = x
                cell["y"] = y
                cells.append(cell)
                existing.add((x, y))
        self._refresh_platform_list()
        self._set_status("Platform drawn.")

    def remove_platform_at_cell(self, cell_x, cell_y):
        self._record_undo()
        cells = self._current_cells()
        for index in range(len(cells) - 1, -1, -1):
            cell = cells[index]
            if cell.get("x") == cell_x and cell.get("y") == cell_y:
                cells.pop(index)
                self._refresh_platform_list()
                self._set_status("Platform removed.")
                return
        self._set_status("No platform at cell.")

    def remove_selected_platforms(self):
        selected_indices = sorted(self.canvas.get_selected_indices(), reverse=True)
        if not selected_indices:
            self._set_status("No selection to remove.")
            return
        self._record_undo()
        cells = self._current_cells()
        for index in selected_indices:
            if 0 <= index < len(cells):
                cells.pop(index)
        self._refresh_platform_list()
        self._set_status(f"Removed {len(selected_indices)} platform(s).")

    def _set_mode(self, mode):
        self.canvas.set_mode(mode)
        self.mode_label.setText(f"Mode: {mode.capitalize()}")
        self._set_status(f"Mode set to {mode}.")

    def undo(self):
        if not self.undo_stack:
            self._set_status("Nothing to undo.")
            return
        self.redo_stack.append(self._snapshot_state())
        self.level_data = self.undo_stack.pop()
        self._apply_level_to_form()
        self._refresh_platform_list()
        self._set_status("Undo.")

    def redo(self):
        if not self.redo_stack:
            self._set_status("Nothing to redo.")
            return
        self.undo_stack.append(self._snapshot_state())
        self.level_data = self.redo_stack.pop()
        self._apply_level_to_form()
        self._refresh_platform_list()
        self._set_status("Redo.")


class LevelCanvas(QGraphicsView):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        self.setDragMode(self.DragMode.RubberBandDrag)
        self.grid_size = 32
        self.columns = int(editor.level_data.get("page_width_cells", DEFAULT_GRID_COLUMNS))
        self.rows = int(editor.level_data.get("page_height_cells", DEFAULT_GRID_ROWS))
        self._zoom = 1.0
        self._min_zoom = 0.25
        self._max_zoom = 4.0
        self._dragging = False
        self._start_cell = None
        self._preview_item = None
        self._atlas = self._load_texture_atlas()
        self.mode = "select"
        self.selected_outline_pen = QPen(QColor(255, 255, 0), 3)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.scene.selectionChanged.connect(self.selectionChanged)
        self._outline_items = {}
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

    def set_mode(self, mode):
        self.mode = mode
        if self.mode == "select":
            self.setDragMode(self.DragMode.RubberBandDrag)
        else:
            self.setDragMode(self.DragMode.NoDrag)

    def _load_texture_atlas(self):
        candidates = [
            _resource_path("resources", "assets", "sprites", "tiles", "texture_atlas.png"),
            _resource_path("src", "resources", "assets", "sprites", "tiles", "texture_atlas.png"),
        ]
        for atlas_path in candidates:
            if os.path.exists(atlas_path):
                return QPixmap(atlas_path)
        return None

    def render_scene(self):
        self.scene.clear()
        self.columns = int(self.editor.level_data.get("page_width_cells", self.columns))
        self.rows = int(self.editor.level_data.get("page_height_cells", self.rows))
        width = self.columns * self.grid_size
        height = self.rows * self.grid_size
        self.scene.setSceneRect(0, 0, width, height)
        self._preview_item = None

        bg = self.editor.level_data.get("background_color", {})
        bg_color = QColor(bg.get("r", 135), bg.get("g", 206), bg.get("b", 235))
        bg_rect = QGraphicsRectItem(QRectF(0, 0, width, height))
        bg_rect.setBrush(QBrush(bg_color))
        bg_rect.setPen(QPen(Qt.PenStyle.NoPen))
        bg_rect.setZValue(-3)
        self.scene.addItem(bg_rect)

        image_path = bg.get("image")
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(width, height)
            img_item = self.scene.addPixmap(pixmap)
            img_item.setZValue(-2)

        spawn = self.editor.level_data.get("player_spawn", {})
        spawn_x = int(spawn.get("x", 0))
        spawn_y = int(spawn.get("y", 0))
        if spawn.get("grid", True):
            spawn_x *= self.grid_size
            spawn_y *= self.grid_size
        spawn_rect = QRectF(spawn_x, spawn_y, self.grid_size, self.grid_size)
        spawn_item = QGraphicsRectItem(spawn_rect)
        spawn_item.setBrush(QBrush(QColor(0, 255, 0, 90)))
        spawn_item.setPen(QPen(QColor(0, 120, 0), 2))
        spawn_item.setZValue(0)
        self.scene.addItem(spawn_item)

        grid_pen = QPen(QColor(80, 80, 80), 1)
        for x in range(0, width + 1, self.grid_size):
            self.scene.addLine(x, 0, x, height, grid_pen)
        for y in range(0, height + 1, self.grid_size):
            self.scene.addLine(0, y, width, y, grid_pen)

        self._outline_items = {}
        for idx, cell in enumerate(self.editor._current_cells()):
            rect = self._cell_rect(cell)
            item = QGraphicsRectItem(rect)
            item.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
            item.setData(0, idx)
            color = cell.get("color", [120, 120, 120])
            item.setBrush(QBrush(QColor(*color)))
            item.setPen(QPen(QColor(200, 0, 0), 2))
            item.setZValue(1)
            self.scene.addItem(item)
            texture = cell.get("texture", "")
            if texture and self._atlas and texture in TEXTURE_ATLAS:
                x, y, w, h = TEXTURE_ATLAS[texture]
                tile = self._atlas.copy(x, y, w, h).scaled(self.grid_size, self.grid_size)
                start_x = int(rect.x())
                start_y = int(rect.y())
                end_x = int(rect.x() + rect.width())
                end_y = int(rect.y() + rect.height())
                for ty in range(start_y, end_y, self.grid_size):
                    for tx in range(start_x, end_x, self.grid_size):
                        tile_item = self.scene.addPixmap(tile)
                        tile_item.setPos(tx, ty)
                        tile_item.setZValue(2)
            elif texture:
                text = self.scene.addText(texture)
                text.setDefaultTextColor(QColor(20, 20, 20))
                text.setPos(rect.x() + 4, rect.y() + 4)
                text.setZValue(3)
            outline = QGraphicsRectItem(rect)
            outline.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            outline.setPen(QPen(QColor(0, 0, 0, 0), 0))
            outline.setZValue(4)
            self.scene.addItem(outline)
            self._outline_items[idx] = outline

    def _cell_rect(self, cell):
        x = cell.get("x", 0) * self.grid_size
        y = cell.get("y", 0) * self.grid_size
        return QRectF(x, y, self.grid_size, self.grid_size)

    def get_selected_indices(self):
        indices = []
        for item in self.scene.selectedItems():
            index = item.data(0)
            if index is not None:
                indices.append(int(index))
        return indices

    def select_platform_index(self, index):
        for item in self.scene.items():
            if item.data(0) == index:
                item.setSelected(True)
                break

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.modifiers() == Qt.KeyboardModifier.NoModifier:
            pos = self.mapToScene(event.position().toPoint())
            cell_x = int(pos.x()) // self.grid_size
            cell_y = int(pos.y()) // self.grid_size
            if 0 <= cell_x < self.columns and 0 <= cell_y < self.rows:
                if self.mode == "add":
                    self._dragging = True
                    self._start_cell = (cell_x, cell_y)
                    if self._preview_item:
                        self._preview_item = None
                    self._preview_item = QGraphicsRectItem()
                    self._preview_item.setBrush(QBrush(QColor(255, 255, 255, 40)))
                    self._preview_item.setPen(QPen(QColor(0, 0, 0), 1))
                    self.scene.addItem(self._preview_item)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.mode == "add" and self._dragging and self._start_cell:
            pos = self.mapToScene(event.position().toPoint())
            cell_x = int(pos.x()) // self.grid_size
            cell_y = int(pos.y()) // self.grid_size
            cell_x = max(0, min(self.columns - 1, cell_x))
            cell_y = max(0, min(self.rows - 1, cell_y))
            x1, y1 = self._start_cell
            x2, y2 = cell_x, cell_y
            if self._preview_item:
                rect = self._rect_for_cells(x1, y1, x2, y2)
                self._preview_item.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.mode == "add" and self._dragging and self._start_cell:
            pos = self.mapToScene(event.position().toPoint())
            cell_x = int(pos.x()) // self.grid_size
            cell_y = int(pos.y()) // self.grid_size
            cell_x = max(0, min(self.columns - 1, cell_x))
            cell_y = max(0, min(self.rows - 1, cell_y))
            x1, y1 = self._start_cell
            x2, y2 = cell_x, cell_y
            self.editor.add_platform_from_rect(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
            self._dragging = False
            self._start_cell = None
            if self._preview_item:
                try:
                    self.scene.removeItem(self._preview_item)
                finally:
                    self._preview_item = None
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Undo):
            self.editor.undo()
            return
        if event.matches(QKeySequence.StandardKey.Redo):
            self.editor.redo()
            return
        if event.key() == Qt.Key.Key_Delete:
            self.editor.remove_selected_platforms()
            return
        super().keyPressEvent(event)

    def selectionChanged(self):
        selected = set(self.get_selected_indices())
        for index, outline in list(self._outline_items.items()):
            if outline is None:
                self._outline_items.pop(index, None)
                continue
            try:
                if index in selected:
                    outline.setPen(self.selected_outline_pen)
                else:
                    outline.setPen(QPen(QColor(0, 0, 0, 0), 0))
            except RuntimeError:
                # Item got deleted by a scene refresh; drop stale references.
                self._outline_items.pop(index, None)

    def _rect_for_cells(self, x1, y1, x2, y2):
        left = min(x1, x2) * self.grid_size
        top = min(y1, y2) * self.grid_size
        right = (max(x1, x2) + 1) * self.grid_size
        bottom = (max(y1, y2) + 1) * self.grid_size
        return QRectF(left, top, right - left, bottom - top)

    def _zoom_by(self, factor):
        new_zoom = max(self._min_zoom, min(self._zoom * factor, self._max_zoom))
        if abs(new_zoom - self._zoom) < 1e-6:
            return
        scale_factor = new_zoom / self._zoom
        self.scale(scale_factor, scale_factor)
        self._zoom = new_zoom

    def wheelEvent(self, event):
        angle = event.angleDelta().y()
        if angle == 0:
            super().wheelEvent(event)
            return
        if angle > 0:
            self._zoom_by(1.15)
        else:
            self._zoom_by(1 / 1.15)
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = LevelEditor()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


def merge_platforms(platforms):
    cell_groups = {}
    for platform in platforms:
        x1 = int(platform.get("x1", 0))
        y1 = int(platform.get("y1", 0))
        x2 = int(platform.get("x2", 0))
        y2 = int(platform.get("y2", 0))
        grid_size = int(platform.get("grid_size", 32))
        key = (
            platform.get("type", "NORMAL"),
            platform.get("texture"),
            tuple(platform.get("color", [120, 120, 120])),
            grid_size,
        )
        cells = cell_groups.setdefault(key, set())
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                cells.add((x, y))

    merged_platforms = []
    for key, cells in cell_groups.items():
        remaining = set(cells)
        while remaining:
            x, y = min(remaining)
            width = 1
            while (x + width, y) in remaining:
                width += 1
            height = 1
            while True:
                next_row = [(x + dx, y + height) for dx in range(width)]
                if all(cell in remaining for cell in next_row):
                    height += 1
                else:
                    break
            for dy in range(height):
                for dx in range(width):
                    remaining.discard((x + dx, y + dy))
            platform_type, texture, color, grid_size = key
            entry = {
                "x1": x,
                "y1": y,
                "x2": x + width - 1,
                "y2": y + height - 1,
                "grid_size": grid_size,
                "type": platform_type,
                "color": list(color),
            }
            if texture:
                entry["texture"] = texture
            merged_platforms.append(entry)

    return merged_platforms
