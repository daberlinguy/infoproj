"""Level Editor for the Parkour Game.

This editor uses a shared texture configuration (textures.json) that is
automatically synced between the game and the editor. To add new textures,
simply edit textures.json and they will appear in both applications.
"""

import copy
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "code"))
try:
    from utils.level_codec import encode as _plvl_encode, decode as _plvl_decode
    _CODEC_AVAILABLE = True
except ImportError:
    _CODEC_AVAILABLE = False

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QPen, QBrush, QPainter, QPixmap, QKeySequence, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QSpinBox,
    QTabWidget,
    QTextEdit,
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
            "page_positions": {"1": {"x": 0, "y": 0}},
            "texts": [],
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

        self.tab_widget = QTabWidget()
        
        self.platform_list = QListWidget()
        self.platform_list.setSelectionMode(
            QListWidget.SelectionMode.ExtendedSelection
        )
        self.platform_list.currentRowChanged.connect(self._load_platform_into_form)
        self.tab_widget.addTab(self.platform_list, "Platforms")
        
        self.text_list = QListWidget()
        self.text_list.currentRowChanged.connect(self._load_text_into_form)
        self.tab_widget.addTab(self.text_list, "Texts")
        
        splitter.addWidget(self.tab_widget)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        right_panel = QWidget()
        right = QVBoxLayout()
        right_panel.setLayout(right)
        scroll.setWidget(right_panel)
        splitter.addWidget(scroll)
        splitter.setSizes([500, 200, 300])

        right.addLayout(self._build_level_form())
        right.addSpacing(10)
        right.addLayout(self._build_page_controls())
        right.addLayout(self._build_mode_controls())
        right.addLayout(self._build_platform_form())
        right.addSpacing(10)
        right.addLayout(self._build_buttons())
        right.addSpacing(10)
        right.addWidget(self._build_text_form())
        right.addStretch()

        self.status_label = QLabel("")
        right.addWidget(self.status_label)
        self._set_mode("add")
        self._refresh_platform_list()
        self._refresh_text_list()
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

        # Platform types with checkboxes
        types_group = QGroupBox("Platform Types")
        types_layout = QGridLayout()
        self.type_checkboxes = {}
        for i, ptype in enumerate(PLATFORM_TYPES):
            checkbox = QCheckBox(ptype)
            self.type_checkboxes[ptype] = checkbox
            types_layout.addWidget(checkbox, i // 3, i % 3)
        types_group.setLayout(types_layout)
        form.addRow(types_group)

        self.texture_search = QLineEdit()
        self.texture_search.setPlaceholderText("Search textures...")
        self.texture_search.textChanged.connect(self._filter_textures)
        form.addRow("Search", self.texture_search)

        self.texture_type = QComboBox()
        self.texture_type.addItems(TEXTURE_TYPES)
        form.addRow("Texture", self.texture_type)

        self.layer = QSpinBox()
        self.layer.setRange(-10, 10)
        self.layer.setValue(0)
        self.layer.setToolTip(
            "Layer depth: negative = background (darker), positive = foreground (brighter)"
        )
        form.addRow("Layer", self.layer)

        values_group = QGroupBox("Platform Values")
        values_layout = QFormLayout()
        
        self.boost_power = QSpinBox()
        self.boost_power.setRange(-2000, -100)
        self.boost_power.setValue(-900)
        self.boost_power.setSingleStep(50)
        self.boost_power.setToolTip("Jump velocity for BOOST_UP platforms (more negative = higher jump)")
        values_layout.addRow("Boost Power", self.boost_power)
        
        self.speed_mult = QDoubleSpinBox()
        self.speed_mult.setRange(0.1, 5.0)
        self.speed_mult.setValue(1.5)
        self.speed_mult.setSingleStep(0.1)
        self.speed_mult.setDecimals(1)
        self.speed_mult.setToolTip("Speed multiplier for SPEED_UP platforms")
        values_layout.addRow("Speed Mult", self.speed_mult)
        
        self.slow_mult = QDoubleSpinBox()
        self.slow_mult.setRange(0.1, 1.0)
        self.slow_mult.setValue(0.5)
        self.slow_mult.setSingleStep(0.1)
        self.slow_mult.setDecimals(1)
        self.slow_mult.setToolTip("Speed multiplier for SLOW_DOWN platforms")
        values_layout.addRow("Slow Mult", self.slow_mult)
        
        values_group.setLayout(values_layout)
        form.addRow(values_group)

        self.apply_selected_btn = QPushButton("Apply All to Selected")
        self.apply_selected_btn.clicked.connect(self._apply_to_selected)
        form.addRow(self.apply_selected_btn)

        quick_update_layout = QHBoxLayout()
        self.apply_type_btn = QPushButton("Update Type Only")
        self.apply_type_btn.clicked.connect(self._apply_type_to_selected)
        self.apply_texture_btn = QPushButton("Update Texture Only")
        self.apply_texture_btn.clicked.connect(self._apply_texture_to_selected)
        quick_update_layout.addWidget(self.apply_type_btn)
        quick_update_layout.addWidget(self.apply_texture_btn)
        form.addRow(quick_update_layout)

        return form

    def _build_page_controls(self):
        layout = QVBoxLayout()
        top_row = QHBoxLayout()
        self.page_label = QLabel("Page")
        self.page_select = QSpinBox()
        self.page_select.setRange(1, 999)
        self.page_select.setValue(int(self.current_page))
        self.page_select.valueChanged.connect(self._on_page_change)
        top_row.addWidget(self.page_label)
        top_row.addWidget(self.page_select)

        buttons = QGridLayout()
        self.add_page_up_btn = QPushButton("Add Up")
        self.add_page_down_btn = QPushButton("Add Down")
        self.add_page_left_btn = QPushButton("Add Left")
        self.add_page_right_btn = QPushButton("Add Right")
        self.add_page_up_btn.clicked.connect(lambda: self._add_page_relative(0, -1))
        self.add_page_down_btn.clicked.connect(lambda: self._add_page_relative(0, 1))
        self.add_page_left_btn.clicked.connect(lambda: self._add_page_relative(-1, 0))
        self.add_page_right_btn.clicked.connect(lambda: self._add_page_relative(1, 0))
        buttons.addWidget(self.add_page_up_btn, 0, 1)
        buttons.addWidget(self.add_page_left_btn, 1, 0)
        buttons.addWidget(self.add_page_right_btn, 1, 2)
        buttons.addWidget(self.add_page_down_btn, 2, 1)

        layout.addLayout(top_row)
        layout.addLayout(buttons)
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
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self._load_level)
        save_btn = QPushButton("Save JSON")
        save_btn.clicked.connect(self._save_json)
        save_plvl_btn = QPushButton("Save .plvl")
        save_plvl_btn.clicked.connect(self._save_plvl)
        save_plvl_btn.setToolTip("Save in compact binary format (~90% smaller)")

        layout.addWidget(add_btn)
        layout.addWidget(update_btn)
        layout.addWidget(remove_btn)
        layout.addWidget(load_btn)
        layout.addWidget(save_btn)
        layout.addWidget(save_plvl_btn)
        return layout

    def _build_text_form(self):
        group = QGroupBox("Text Objects")
        layout = QFormLayout()
        
        pos_layout = QGridLayout()
        self.text_x = QSpinBox()
        self.text_y = QSpinBox()
        self.text_page = QSpinBox()
        self.text_x.setRange(-9999, 9999)
        self.text_y.setRange(-9999, 9999)
        self.text_page.setRange(1, 999)
        self.text_page.setValue(1)
        pos_layout.addWidget(QLabel("X"), 0, 0)
        pos_layout.addWidget(self.text_x, 0, 1)
        pos_layout.addWidget(QLabel("Y"), 0, 2)
        pos_layout.addWidget(self.text_y, 0, 3)
        pos_layout.addWidget(QLabel("Page"), 1, 0)
        pos_layout.addWidget(self.text_page, 1, 1)
        layout.addRow("Position", pos_layout)
        
        self.text_content = QTextEdit()
        self.text_content.setPlaceholderText("Enter text here...")
        self.text_content.setMaximumHeight(60)
        layout.addRow("Text", self.text_content)
        
        color_layout = QGridLayout()
        self.text_r = QSpinBox()
        self.text_g = QSpinBox()
        self.text_b = QSpinBox()
        for spin in (self.text_r, self.text_g, self.text_b):
            spin.setRange(0, 255)
        self.text_r.setValue(255)
        self.text_g.setValue(255)
        self.text_b.setValue(255)
        color_layout.addWidget(QLabel("R"), 0, 0)
        color_layout.addWidget(self.text_r, 0, 1)
        color_layout.addWidget(QLabel("G"), 0, 2)
        color_layout.addWidget(self.text_g, 0, 3)
        color_layout.addWidget(QLabel("B"), 0, 4)
        color_layout.addWidget(self.text_b, 0, 5)
        layout.addRow("Color", color_layout)
        
        size_font_layout = QHBoxLayout()
        self.text_size = QSpinBox()
        self.text_size.setRange(8, 99)
        self.text_size.setValue(24)
        self.text_font = QLineEdit("Minecraft")
        self.text_font.setPlaceholderText("Font name (empty = default)")
        size_font_layout.addWidget(QLabel("Size"))
        size_font_layout.addWidget(self.text_size)
        size_font_layout.addWidget(QLabel("Font"))
        size_font_layout.addWidget(self.text_font)
        layout.addRow("Style", size_font_layout)
        
        btn_layout = QHBoxLayout()
        add_text_btn = QPushButton("Add Text")
        add_text_btn.clicked.connect(self._add_text)
        update_text_btn = QPushButton("Update Text")
        update_text_btn.clicked.connect(self._update_text)
        remove_text_btn = QPushButton("Remove Text")
        remove_text_btn.clicked.connect(self._remove_text)
        btn_layout.addWidget(add_text_btn)
        btn_layout.addWidget(update_text_btn)
        btn_layout.addWidget(remove_text_btn)
        layout.addRow(btn_layout)
        
        group.setLayout(layout)
        return group

    def _add_text(self):
        self._record_undo()
        text_obj = {
            "x": self.text_x.value(),
            "y": self.text_y.value(),
            "page": self.text_page.value(),
            "text": self.text_content.toPlainText(),
            "color": [self.text_r.value(), self.text_g.value(), self.text_b.value()],
            "size": self.text_size.value(),
            "font": self.text_font.text().strip(),
        }
        self.level_data.setdefault("texts", []).append(text_obj)
        self._refresh_text_list()
        self.canvas.render_scene()
        self._set_status("Text added.")

    def _update_text(self):
        index = self.text_list.currentRow()
        if index < 0:
            QMessageBox.warning(self, "No selection", "Select a text to update.")
            return
        self._record_undo()
        text_obj = {
            "x": self.text_x.value(),
            "y": self.text_y.value(),
            "page": self.text_page.value(),
            "text": self.text_content.toPlainText(),
            "color": [self.text_r.value(), self.text_g.value(), self.text_b.value()],
            "size": self.text_size.value(),
            "font": self.text_font.text().strip(),
        }
        self.level_data["texts"][index] = text_obj
        self._refresh_text_list()
        self.text_list.setCurrentRow(index)
        self.canvas.render_scene()
        self._set_status("Text updated.")

    def _remove_text(self):
        index = self.text_list.currentRow()
        if index < 0:
            QMessageBox.warning(self, "No selection", "Select a text to remove.")
            return
        self._record_undo()
        self.level_data["texts"].pop(index)
        self._refresh_text_list()
        self.canvas.render_scene()
        self._set_status("Text removed.")

    def _load_text_into_form(self, index):
        texts = self.level_data.get("texts", [])
        if index < 0 or index >= len(texts):
            return
        text_obj = texts[index]
        self.text_x.setValue(text_obj.get("x", 0))
        self.text_y.setValue(text_obj.get("y", 0))
        self.text_page.setValue(text_obj.get("page", 1))
        self.text_content.setPlainText(text_obj.get("text", ""))
        color = text_obj.get("color", [255, 255, 255])
        self.text_r.setValue(color[0] if len(color) > 0 else 255)
        self.text_g.setValue(color[1] if len(color) > 1 else 255)
        self.text_b.setValue(color[2] if len(color) > 2 else 255)
        self.text_size.setValue(text_obj.get("size", 24))
        self.text_font.setText(text_obj.get("font", ""))

    def _refresh_text_list(self):
        self.text_list.blockSignals(True)
        self.text_list.clear()
        texts = self.level_data.get("texts", [])
        for idx, text_obj in enumerate(texts):
            preview = text_obj.get("text", "")[:20]
            if len(text_obj.get("text", "")) > 20:
                preview += "..."
            page = text_obj.get("page", 1)
            label = f"{idx + 1}: [P{page}] ({text_obj.get('x')},{text_obj.get('y')}) {preview}"
            self.text_list.addItem(label)
        self.text_list.blockSignals(False)

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
        selected_types = [
            ptype
            for ptype, checkbox in self.type_checkboxes.items()
            if checkbox.isChecked()
        ]
        if not selected_types:
            selected_types = ["NORMAL"]

        platform = {
            "x1": self.x1.value(),
            "y1": self.y1.value(),
            "x2": self.x2.value(),
            "y2": self.y2.value(),
            "grid_size": 32,
            "types": selected_types,
            "layer": self.layer.value(),
            "color": [120, 120, 120],
            "boost_power": self.boost_power.value(),
            "speed_multiplier": self.speed_mult.value(),
            "slow_multiplier": self.slow_mult.value(),
        }
        texture = self.texture_type.currentText()
        if texture:
            platform["texture"] = texture
        return platform

    def _load_platform_into_form(self, index):
        cells = self._current_cells()
        if index < 0 or index >= len(cells):
            return
        cell = cells[index]

        cell_types = cell.get("types", [])
        if not cell_types:
            old_type = cell.get("type", "NORMAL")
            cell_types = [old_type] if old_type else ["NORMAL"]

        platform = {
            "x1": cell.get("x", 0),
            "y1": cell.get("y", 0),
            "x2": cell.get("x", 0),
            "y2": cell.get("y", 0),
            "grid_size": cell.get("grid_size", 32),
            "types": cell_types,
            "texture": cell.get("texture", ""),
            "color": cell.get("color", [0, 0, 0]),
        }
        self.x1.setValue(platform.get("x1", 0))
        self.y1.setValue(platform.get("y1", 0))
        self.x2.setValue(platform.get("x2", 0))
        self.y2.setValue(platform.get("y2", 0))

        # Update type checkboxes
        for ptype, checkbox in self.type_checkboxes.items():
            checkbox.setChecked(ptype in platform.get("types", []))

        self.texture_type.setCurrentText(platform.get("texture", ""))

        self.layer.setValue(cell.get("layer", 0))
        
        self.boost_power.setValue(cell.get("boost_power", -900))
        self.speed_mult.setValue(cell.get("speed_multiplier", 1.5))
        self.slow_mult.setValue(cell.get("slow_multiplier", 0.5))

        self.canvas.select_platform_index(index)

    def _refresh_platform_list(self):
        self.platform_list.clear()
        for idx, cell in enumerate(self._current_cells()):
            # Handle both old "type" and new "types" format
            cell_types = cell.get("types", [])
            if not cell_types:
                old_type = cell.get("type", "NORMAL")
                cell_types = [old_type] if old_type else ["NORMAL"]
            types_str = "+".join(cell_types)

            # Add layer info to label
            layer = cell.get("layer", 0)
            layer_str = f" [L{layer:+d}]" if layer != 0 else ""

            label = (
                f"{idx + 1}: ({cell.get('x')},{cell.get('y')}) {types_str}{layer_str}"
            )
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
        # Check if there are multiple selections from the canvas or list
        selected_indices = self.canvas.get_selected_indices()

        # If no canvas selection, check list widget for multi-selection
        if not selected_indices:
            list_items = self.platform_list.selectedItems()
            if list_items:
                selected_indices = [self.platform_list.row(item) for item in list_items]

        if selected_indices and len(selected_indices) > 1:
            # Update multiple platforms
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
        else:
            # Fall back to single platform update
            index = self.platform_list.currentRow()
            if index < 0:
                QMessageBox.warning(
                    self, "No selection", "Select a platform to update."
                )
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
        # Check if there are multiple selections from the canvas or list
        selected_indices = self.canvas.get_selected_indices()

        # If no canvas selection, check list widget for multi-selection
        if not selected_indices:
            list_items = self.platform_list.selectedItems()
            if list_items:
                selected_indices = [self.platform_list.row(item) for item in list_items]

        if selected_indices:
            # Remove multiple platforms
            self._record_undo()
            # Sort in reverse to avoid index shifting during removal
            for index in sorted(selected_indices, reverse=True):
                if 0 <= index < len(self._current_cells()):
                    self._current_cells().pop(index)
            self._refresh_platform_list()
            self._set_status(f"Removed {len(selected_indices)} platform(s).")
        else:
            # Fall back to single platform removal
            index = self.platform_list.currentRow()
            if index < 0:
                QMessageBox.warning(
                    self, "No selection", "Select a platform to remove."
                )
                return
            self._record_undo()
            self._current_cells().pop(index)
            self._refresh_platform_list()
            self._set_status("Platform removed.")

    def _load_level(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Level", "", "Level Files (*.json *.plvl);;JSON (*.json);;Binary Level (*.plvl)"
        )
        if not path:
            return
        try:
            if path.endswith(".plvl"):
                if not _CODEC_AVAILABLE:
                    QMessageBox.critical(self, "Codec unavailable", "level_codec module not found.")
                    return
                with open(path, "rb") as f:
                    self.level_data = _plvl_decode(f.read())
            else:
                with open(path, "r", encoding="utf-8") as f:
                    self.level_data = json.load(f)
            self.current_path = path
            self.level_data.setdefault("page_width_cells", DEFAULT_GRID_COLUMNS)
            self.level_data.setdefault("page_height_cells", DEFAULT_GRID_ROWS)
            self._ensure_pages()
            self._ensure_page_positions()
            self._expand_platforms_to_cells()
            self._apply_level_to_form()
            self._refresh_platform_list()
            self._refresh_text_list()
            self.undo_stack.clear()
            self.redo_stack.clear()
            self._set_status(f"Loaded {os.path.basename(path)}")
        except Exception as exc:
            QMessageBox.critical(self, "Load failed", str(exc))

    # keep old name as alias so any external calls still work
    _load_json = _load_level

    def _save_json(self):
        self._sync_level_fields()
        if not self.current_path or self.current_path.endswith(".plvl"):
            path, _ = QFileDialog.getSaveFileName(
                self, "Save Level JSON", "", "JSON Files (*.json)"
            )
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

    def _save_plvl(self):
        if not _CODEC_AVAILABLE:
            QMessageBox.critical(self, "Codec unavailable", "level_codec module not found.")
            return
        self._sync_level_fields()
        # Suggest the same base name but with .plvl extension
        default_path = ""
        if self.current_path:
            default_path = os.path.splitext(self.current_path)[0] + ".plvl"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Binary Level (.plvl)", default_path, "Binary Level (*.plvl)"
        )
        if not path:
            return
        try:
            payload = self._build_save_payload()
            with open(path, "wb") as f:
                f.write(_plvl_encode(payload))
            json_size = len(json.dumps(payload).encode())
            plvl_size = os.path.getsize(path)
            ratio = (1 - plvl_size / json_size) * 100 if json_size else 0
            self._set_status(
                f"Saved {os.path.basename(path)}  "
                f"({plvl_size // 1024} KB vs {json_size // 1024} KB JSON, {ratio:.0f}% smaller)"
            )
        except Exception as exc:
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

                platform_types = platform.get("types", [])
                if not platform_types:
                    old_type = platform.get("type", "NORMAL")
                    platform_types = [old_type] if old_type else ["NORMAL"]

                for y in range(min(y1, y2), max(y1, y2) + 1):
                    for x in range(min(x1, x2), max(x1, x2) + 1):
                        cell = {
                            "x": x,
                            "y": y,
                            "grid_size": platform.get("grid_size", 32),
                            "types": platform_types,
                            "color": platform.get("color", [120, 120, 120]),
                            "layer": platform.get("layer", 0),
                        }
                        if platform.get("boost_power"):
                            cell["boost_power"] = platform["boost_power"]
                        if platform.get("speed_multiplier"):
                            cell["speed_multiplier"] = platform["speed_multiplier"]
                        if platform.get("slow_multiplier"):
                            cell["slow_multiplier"] = platform["slow_multiplier"]
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
            "page_width_cells": self.level_data.get(
                "page_width_cells", DEFAULT_GRID_COLUMNS
            ),
            "page_height_cells": self.level_data.get(
                "page_height_cells", DEFAULT_GRID_ROWS
            ),
            "pages": {},
        }
        page_positions = self._get_page_positions()
        if page_positions:
            payload["page_positions"] = {
                str(page_key): {"x": pos[0], "y": pos[1]}
                for page_key, pos in page_positions.items()
            }
        for page_key, page in self.level_data.get("pages", {}).items():
            cells = page.get("cells", [])
            platforms = self._cells_to_platforms(cells)
            payload["pages"][str(page_key)] = {"platforms": platforms}
        
        texts = self.level_data.get("texts", [])
        if texts:
            payload["texts"] = texts
        return payload

    def _cells_to_platforms(self, cells):
        platforms = []
        for cell in cells:
            platform_types = cell.get("types", [])
            if not platform_types:
                old_type = cell.get("type", "NORMAL")
                platform_types = [old_type] if old_type else ["NORMAL"]

            platform = {
                "x1": cell.get("x", 0),
                "y1": cell.get("y", 0),
                "x2": cell.get("x", 0),
                "y2": cell.get("y", 0),
                "grid_size": cell.get("grid_size", 32),
                "types": platform_types,
                "color": cell.get("color", [120, 120, 120]),
                "layer": cell.get("layer", 0),
            }
            
            boost_power = cell.get("boost_power")
            speed_mult = cell.get("speed_multiplier")
            slow_mult = cell.get("slow_multiplier")
            
            if boost_power is not None and boost_power != -900:
                platform["boost_power"] = boost_power
            if speed_mult is not None and speed_mult != 1.5:
                platform["speed_multiplier"] = speed_mult
            if slow_mult is not None and slow_mult != 0.5:
                platform["slow_multiplier"] = slow_mult
            
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

    def _ensure_page_positions(self):
        pages = self.level_data.get("pages", {})
        positions = self.level_data.get("page_positions")
        if not isinstance(positions, dict):
            positions = {}

        normalized = {}
        for key, pos in positions.items():
            if not isinstance(pos, dict):
                continue
            try:
                x = int(pos.get("x", 0))
                y = int(pos.get("y", 0))
            except (TypeError, ValueError):
                continue
            normalized[str(key)] = {"x": x, "y": y}

        if not normalized:
            page_numbers = []
            for page_key in pages.keys():
                try:
                    page_numbers.append(int(page_key))
                except (TypeError, ValueError):
                    continue
            page_numbers = sorted(page_numbers) or [1]
            for index, page_key in enumerate(page_numbers):
                normalized[str(page_key)] = {"x": index, "y": 0}

        if normalized:
            max_x = max(pos["x"] for pos in normalized.values())
        else:
            max_x = 0

        for page_key in pages.keys():
            if str(page_key) not in normalized:
                max_x += 1
                normalized[str(page_key)] = {"x": max_x, "y": 0}

        self.level_data["page_positions"] = normalized

    def _get_page_positions(self):
        self._ensure_pages()
        self._ensure_page_positions()
        positions = self.level_data.get("page_positions", {})
        return {
            str(page_key): (int(pos.get("x", 0)), int(pos.get("y", 0)))
            for page_key, pos in positions.items()
            if isinstance(pos, dict)
        }

    def _next_page_id(self):
        pages = self.level_data.get("pages", {})
        max_page = 0
        for page_key in pages.keys():
            try:
                max_page = max(max_page, int(page_key))
            except (TypeError, ValueError):
                continue
        return max_page + 1

    def _add_page_relative(self, dx, dy):
        self._record_undo()
        self._ensure_page_positions()
        positions = self.level_data.get("page_positions", {})
        current_pos = positions.get(str(self.current_page), {"x": 0, "y": 0})
        target_x = int(current_pos.get("x", 0)) + dx
        target_y = int(current_pos.get("y", 0)) + dy

        existing_page = None
        for page_key, pos in positions.items():
            if int(pos.get("x", 0)) == target_x and int(pos.get("y", 0)) == target_y:
                existing_page = str(page_key)
                break

        if existing_page:
            self.current_page = existing_page
            self.page_select.blockSignals(True)
            self.page_select.setValue(int(existing_page))
            self.page_select.blockSignals(False)
            self._refresh_platform_list()
            self.canvas.render_scene()
            return

        new_page = str(self._next_page_id())
        self.level_data.setdefault("pages", {})[new_page] = {"cells": []}
        positions[new_page] = {"x": target_x, "y": target_y}
        self.level_data["page_positions"] = positions
        self.current_page = new_page
        self.page_select.blockSignals(True)
        self.page_select.setValue(int(new_page))
        self.page_select.blockSignals(False)
        self._refresh_platform_list()
        self.canvas.render_scene()

    def _current_cells(self):
        self._ensure_pages()
        return self.level_data["pages"][self.current_page]["cells"]

    def _cells_for_page(self, page_key):
        self._ensure_pages()
        page = self.level_data.get("pages", {}).get(str(page_key), {})
        return page.get("cells", [])

    def _on_page_change(self, value):
        self.current_page = str(value)
        self._ensure_pages()
        self._ensure_page_positions()
        self._refresh_platform_list()
        self.canvas.render_scene()

    def _on_level_field_change(self):
        self._sync_level_fields()
        self.canvas.render_scene()

    def _apply_to_selected(self):
        selected_indices = self.canvas.get_selected_indices()
        if not selected_indices:
            QMessageBox.warning(
                self, "No selection", "Select platforms in the preview."
            )
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

    def _filter_textures(self, search_text):
        """Filter texture dropdown based on search text and auto-select best match."""
        self.texture_type.clear()

        search_lower = search_text.lower().strip()
        filtered_textures = [""]  # Always include empty option

        if not search_lower:
            # No search text – show all textures, select nothing
            self.texture_type.addItems(TEXTURE_TYPES)
            return

        best_match = None
        best_score = -1
        for texture in TEXTURE_TYPES[1:]:  # Skip the first empty string
            t_lower = texture.lower()
            if search_lower in t_lower:
                filtered_textures.append(texture)
                # Score: exact match > starts-with > contains
                if t_lower == search_lower:
                    score = 3
                elif t_lower.startswith(search_lower):
                    score = 2
                else:
                    score = 1
                # Among equal scores prefer shorter names (closer match)
                if score > best_score or (score == best_score and (best_match is None or len(texture) < len(best_match))):
                    best_score = score
                    best_match = texture

        self.texture_type.addItems(filtered_textures)

        # Auto-select the best match
        if best_match:
            self.texture_type.setCurrentText(best_match)

    def _apply_type_to_selected(self):
        """Update only the type for selected platforms."""
        selected_indices = self.canvas.get_selected_indices()
        if not selected_indices:
            QMessageBox.warning(
                self, "No selection", "Select platforms in the preview."
            )
            return
        self._record_undo()

        # Collect selected types
        selected_types = [
            ptype
            for ptype, checkbox in self.type_checkboxes.items()
            if checkbox.isChecked()
        ]
        if not selected_types:
            selected_types = ["NORMAL"]

        for index in selected_indices:
            cell = self._current_cells()[index]
            cell["types"] = selected_types
            # Remove old single type field if it exists
            if "type" in cell:
                del cell["type"]
        self._refresh_platform_list()
        self._set_status(f"Updated type for {len(selected_indices)} platform(s).")

    def _apply_texture_to_selected(self):
        """Update only the texture for selected platforms."""
        selected_indices = self.canvas.get_selected_indices()
        if not selected_indices:
            QMessageBox.warning(
                self, "No selection", "Select platforms in the preview."
            )
            return
        self._record_undo()
        texture = self.texture_type.currentText()
        for index in selected_indices:
            cell = self._current_cells()[index]
            if texture:
                cell["texture"] = texture
            elif "texture" in cell:
                del cell["texture"]
        self._refresh_platform_list()
        self._set_status(f"Updated texture for {len(selected_indices)} platform(s).")

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
        self._refresh_text_list()
        self.canvas.render_scene()
        self._set_status("Undo.")

    def redo(self):
        if not self.redo_stack:
            self._set_status("Nothing to redo.")
            return
        self.undo_stack.append(self._snapshot_state())
        self.level_data = self.redo_stack.pop()
        self._apply_level_to_form()
        self._refresh_platform_list()
        self._refresh_text_list()
        self.canvas.render_scene()
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
        self.columns = int(
            editor.level_data.get("page_width_cells", DEFAULT_GRID_COLUMNS)
        )
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
        self._page_positions = {"1": (0, 0)}
        self._page_key_by_position = {(0, 0): "1"}
        self._page_offset_px_by_key = {"1": (0, 0)}
        self._min_page_pos = (0, 0)
        self._current_page_offset = (0, 0)

    def set_mode(self, mode):
        self.mode = mode
        if self.mode == "select":
            self.setDragMode(self.DragMode.RubberBandDrag)
        else:
            self.setDragMode(self.DragMode.NoDrag)

    def _load_texture_atlas(self):
        candidates = [
            _resource_path(
                "resources", "assets", "sprites", "tiles", "texture_atlas.png"
            ),
            _resource_path(
                "src", "resources", "assets", "sprites", "tiles", "texture_atlas.png"
            ),
        ]
        for atlas_path in candidates:
            if os.path.exists(atlas_path):
                return QPixmap(atlas_path)
        return None

    def render_scene(self):
        self.scene.clear()
        self.columns = int(self.editor.level_data.get("page_width_cells", self.columns))
        self.rows = int(self.editor.level_data.get("page_height_cells", self.rows))
        pages = self.editor.level_data.get("pages", {})
        page_positions = self.editor._get_page_positions()
        if not page_positions:
            page_positions = {"1": (0, 0)}

        self._page_positions = page_positions
        self._page_key_by_position = {
            (pos[0], pos[1]): str(page_key)
            for page_key, pos in page_positions.items()
        }

        page_width_px = self.columns * self.grid_size
        page_height_px = self.rows * self.grid_size

        min_x = min(pos[0] for pos in page_positions.values())
        max_x = max(pos[0] for pos in page_positions.values())
        min_y = min(pos[1] for pos in page_positions.values())
        max_y = max(pos[1] for pos in page_positions.values())
        self._min_page_pos = (min_x, min_y)

        self._page_offset_px_by_key = {}
        for page_key, pos in page_positions.items():
            offset_x = (pos[0] - min_x) * page_width_px
            offset_y = (pos[1] - min_y) * page_height_px
            self._page_offset_px_by_key[str(page_key)] = (offset_x, offset_y)

        width = (max_x - min_x + 1) * page_width_px
        height = (max_y - min_y + 1) * page_height_px
        self.scene.setSceneRect(0, 0, width, height)
        self._preview_item = None

        bg = self.editor.level_data.get("background_color", {})
        bg_color = QColor(bg.get("r", 135), bg.get("g", 206), bg.get("b", 235))
        for page_key, (offset_x, offset_y) in self._page_offset_px_by_key.items():
            bg_rect = QGraphicsRectItem(
                QRectF(offset_x, offset_y, page_width_px, page_height_px)
            )
            bg_rect.setBrush(QBrush(bg_color))
            bg_rect.setPen(QPen(Qt.PenStyle.NoPen))
            bg_rect.setZValue(-3)
            self.scene.addItem(bg_rect)

        image_path = bg.get("image")
        if image_path and os.path.exists(image_path):
            for page_key, (offset_x, offset_y) in self._page_offset_px_by_key.items():
                pixmap = QPixmap(image_path).scaled(page_width_px, page_height_px)
                img_item = self.scene.addPixmap(pixmap)
                img_item.setPos(offset_x, offset_y)
                img_item.setZValue(-2)

        spawn = self.editor.level_data.get("player_spawn", {})
        spawn_x = int(spawn.get("x", 0))
        spawn_y = int(spawn.get("y", 0))
        if spawn.get("grid", True):
            spawn_x *= self.grid_size
            spawn_y *= self.grid_size
        spawn_offset = self._page_offset_px_by_key.get(
            "1", self._page_offset_px_by_key.get(self.editor.current_page, (0, 0))
        )
        spawn_rect = QRectF(
            spawn_offset[0] + spawn_x,
            spawn_offset[1] + spawn_y,
            self.grid_size,
            self.grid_size,
        )
        spawn_item = QGraphicsRectItem(spawn_rect)
        spawn_item.setBrush(QBrush(QColor(0, 255, 0, 90)))
        spawn_item.setPen(QPen(QColor(0, 120, 0), 2))
        spawn_item.setZValue(0)
        self.scene.addItem(spawn_item)

        grid_pen = QPen(QColor(80, 80, 80), 1)
        separator_pen = QPen(QColor(25, 25, 25), 3)
        for page_key, (offset_x, offset_y) in self._page_offset_px_by_key.items():
            for x in range(0, page_width_px + 1, self.grid_size):
                self.scene.addLine(
                    offset_x + x,
                    offset_y,
                    offset_x + x,
                    offset_y + page_height_px,
                    grid_pen,
                )
            for y in range(0, page_height_px + 1, self.grid_size):
                self.scene.addLine(
                    offset_x,
                    offset_y + y,
                    offset_x + page_width_px,
                    offset_y + y,
                    grid_pen,
                )
            self.scene.addRect(
                offset_x, offset_y, page_width_px, page_height_px, separator_pen
            )

        self._outline_items = {}
        for page_key, (offset_x, offset_y) in self._page_offset_px_by_key.items():
            page_cells = self.editor._cells_for_page(page_key)
            for idx, cell in enumerate(page_cells):
                rect = self._cell_rect(cell, offset_x, offset_y)
                item = QGraphicsRectItem(rect)
                item.setFlag(
                    QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable,
                    True,
                )
                item.setData(0, idx)
                item.setData(1, page_key)  # Store page key
                color = cell.get("color", [120, 120, 120])
                item.setBrush(QBrush(QColor(*color)))
                item.setPen(QPen(QColor(200, 0, 0), 2))
                item.setZValue(1)
                self.scene.addItem(item)
                texture = cell.get("texture", "")
                if texture and self._atlas and texture in TEXTURE_ATLAS:
                    x, y, w, h = TEXTURE_ATLAS[texture]
                    tile = self._atlas.copy(x, y, w, h).scaled(
                        self.grid_size, self.grid_size
                    )
                    start_x = int(rect.x())
                    start_y = int(rect.y())
                    end_x = int(rect.x() + rect.width())
                    end_y = int(rect.y() + rect.height())
                    for ty in range(start_y, end_y, self.grid_size):
                        for tx in range(start_x, end_x, self.grid_size):
                            tile_item = self.scene.addPixmap(tile)
                            tile_item.setPos(tx, ty)
                            tile_item.setZValue(2)
                            tile_item.setFlag(
                                tile_item.GraphicsItemFlag.ItemIsSelectable, False
                            )
                            tile_item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
                elif texture:
                    text = self.scene.addText(texture)
                    text.setDefaultTextColor(QColor(20, 20, 20))
                    text.setPos(rect.x() + 4, rect.y() + 4)
                    text.setZValue(3)
                    text.setFlag(text.GraphicsItemFlag.ItemIsSelectable, False)
                    text.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

                outline = QGraphicsRectItem(rect)
                outline.setBrush(QBrush(Qt.BrushStyle.NoBrush))
                outline.setPen(QPen(QColor(0, 0, 0, 0), 0))
                outline.setZValue(4)
                self.scene.addItem(outline)
                self._outline_items[(page_key, idx)] = outline

        texts = self.editor.level_data.get("texts", [])
        for text_obj in texts:
            text_page = str(text_obj.get("page", 1))
            if text_page not in self._page_offset_px_by_key:
                continue
            offset_x, offset_y = self._page_offset_px_by_key[text_page]
            x = text_obj.get("x", 0) + offset_x
            y = text_obj.get("y", 0) + offset_y
            color = text_obj.get("color", [255, 255, 255])
            size = text_obj.get("size", 24)
            font_name = text_obj.get("font", "")
            text_content = text_obj.get("text", "")
            
            font = QFont(font_name if font_name else "Arial", size)
            text_item = self.scene.addText(text_content, font)
            text_item.setDefaultTextColor(QColor(*color))
            text_item.setPos(x, y)
            text_item.setZValue(5)

        self._current_page_offset = self._page_offset_px_by_key.get(
            self.editor.current_page, (0, 0)
        )

    def _cell_rect(self, cell, x_offset=0, y_offset=0):
        x = cell.get("x", 0) * self.grid_size
        y = cell.get("y", 0) * self.grid_size
        return QRectF(x + x_offset, y + y_offset, self.grid_size, self.grid_size)

    def _to_page_cell(self, scene_x, scene_y):
        """Return (page_key, cell_x, cell_y) for the given scene coordinates."""
        page_width_px = self.columns * self.grid_size
        page_height_px = self.rows * self.grid_size
        min_x, min_y = self._min_page_pos
        grid_x = int(scene_x) // page_width_px
        grid_y = int(scene_y) // page_height_px
        page_pos = (grid_x + min_x, grid_y + min_y)
        page_key = self._page_key_by_position.get(page_pos)
        if page_key is None:
            page_key = self.editor.current_page
        offset_x, offset_y = self._page_offset_px_by_key.get(page_key, (0, 0))
        cell_x = (int(scene_x) - offset_x) // self.grid_size
        cell_y = (int(scene_y) - offset_y) // self.grid_size
        return page_key, cell_x, cell_y

    def _to_current_page_cell(self, scene_x, scene_y):
        """Legacy helper – returns (cell_x, cell_y) on the current page."""
        _, cell_x, cell_y = self._to_page_cell(scene_x, scene_y)
        return cell_x, cell_y

    def get_selected_indices(self):
        indices = []
        page_keys = set()
        for item in self.scene.selectedItems():
            index = item.data(0)
            page_key = item.data(1)
            if index is not None:
                indices.append(int(index))
                if page_key is not None:
                    page_keys.add(page_key)
        # Auto-switch to the page of the selected cells
        if page_keys and len(page_keys) == 1:
            target_page = page_keys.pop()
            if target_page != self.editor.current_page:
                self.editor.current_page = target_page
                self.editor.page_select.blockSignals(True)
                self.editor.page_select.setValue(int(target_page))
                self.editor.page_select.blockSignals(False)
                self.editor._refresh_platform_list()
        return indices

    def select_platform_index(self, index):
        for item in self.scene.items():
            if item.data(0) == index and item.data(1) == self.editor.current_page:
                item.setSelected(True)
                break

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.mapToScene(event.position().toPoint())
            page_key, cell_x, cell_y = self._to_page_cell(pos.x(), pos.y())
            # Auto-switch to the clicked page
            if page_key != self.editor.current_page:
                self.editor.current_page = page_key
                self.editor.page_select.blockSignals(True)
                self.editor.page_select.setValue(int(page_key))
                self.editor.page_select.blockSignals(False)
                self._current_page_offset = self._page_offset_px_by_key.get(
                    page_key, (0, 0)
                )
                self.editor._refresh_platform_list()
            if 0 <= cell_x < self.columns and 0 <= cell_y < self.rows:
                if (
                    self.mode == "add"
                    and event.modifiers() == Qt.KeyboardModifier.NoModifier
                ):
                    self._dragging = True
                    self._start_cell = (cell_x, cell_y)
                    if self._preview_item:
                        self._preview_item = None
                    self._preview_item = QGraphicsRectItem()
                    self._preview_item.setBrush(QBrush(QColor(255, 255, 255, 40)))
                    self._preview_item.setPen(QPen(QColor(0, 0, 0), 1))
                    self.scene.addItem(self._preview_item)
                    return  # Don't call super() for add mode
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.mode == "add" and self._dragging and self._start_cell:
            pos = self.mapToScene(event.position().toPoint())
            _, cell_x, cell_y = self._to_page_cell(pos.x(), pos.y())
            cell_x = max(0, min(self.columns - 1, cell_x))
            cell_y = max(0, min(self.rows - 1, cell_y))
            x1, y1 = self._start_cell
            x2, y2 = cell_x, cell_y
            if self._preview_item:
                rect = self._rect_for_cells(
                    x1,
                    y1,
                    x2,
                    y2,
                    self._current_page_offset[0],
                    self._current_page_offset[1],
                )
                self._preview_item.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.mode == "add" and self._dragging and self._start_cell:
            pos = self.mapToScene(event.position().toPoint())
            _, cell_x, cell_y = self._to_page_cell(pos.x(), pos.y())
            cell_x = max(0, min(self.columns - 1, cell_x))
            cell_y = max(0, min(self.rows - 1, cell_y))
            x1, y1 = self._start_cell
            x2, y2 = cell_x, cell_y
            self.editor.add_platform_from_rect(
                min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
            )
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
        selected_items = {}
        for item in self.scene.selectedItems():
            index = item.data(0)
            page_key = item.data(1)
            if index is not None and page_key is not None:
                selected_items[(page_key, int(index))] = True
        for key, outline in list(self._outline_items.items()):
            if outline is None:
                self._outline_items.pop(key, None)
                continue
            try:
                if key in selected_items:
                    outline.setPen(self.selected_outline_pen)
                else:
                    outline.setPen(QPen(QColor(0, 0, 0, 0), 0))
            except RuntimeError:
                # Item got deleted by a scene refresh; drop stale references.
                self._outline_items.pop(key, None)

    def _rect_for_cells(self, x1, y1, x2, y2, x_offset=0, y_offset=0):
        left = min(x1, x2) * self.grid_size + x_offset
        top = min(y1, y2) * self.grid_size + y_offset
        right = (max(x1, x2) + 1) * self.grid_size + x_offset
        bottom = (max(y1, y2) + 1) * self.grid_size + y_offset
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
