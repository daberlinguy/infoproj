"""Compact binary level format codec for Parkour levels.

File extension: ``.plvl``
Magic bytes:    ``PLVL`` (4 bytes)
Version:        1 (uint8)

Format overview
---------------
[Header]
  4 bytes  magic "PLVL"
  1 byte   version (currently 1)
  2 bytes  number of strings in string-table (uint16)

[String table]
  For each string:
    2 bytes  length (uint16)
    N bytes  UTF-8 encoded string

[Level header]
  2 bytes  name string-table index (uint16)
  1 byte   spawn_grid  (bool 0/1)
  2 bytes  spawn_grid_size (uint16)
  2 bytes  spawn_x (int16)
  2 bytes  spawn_y (int16)
  1 byte   bg_r, bg_g, bg_b
  2 bytes  bg_image string-table index (0 = none)
  2 bytes  page_width_cells  (uint16)
  2 bytes  page_height_cells (uint16)

[Pages]
  2 bytes  number of pages (uint16)
  For each page:
    2 bytes  page_key string-table index
    2 bytes  pos_x (int16)
    2 bytes  pos_y (int16)
    2 bytes  platform_count (uint16)
    For each platform:
      2 bytes  x1 (int16)
      2 bytes  y1 (int16)
      2 bytes  x2 (int16)
      2 bytes  y2 (int16)
      1 byte   grid_size  (uint8)  stored as grid_size/8, so 32→4, 16→2
      1 byte   layer (int8, signed)
      3 bytes  r, g, b (color)
      1 byte   type_flags  bitmask (bits 0-7 → NORMAL/DEATH/CHECKPOINT/FINISH/
                            SLIPPERY/NOCLIP/BOOST_UP/SPEED_UP)
      1 byte   type_flags2 bitmask (bit 0 → SLOW_DOWN; bits 1-7 reserved)
      2 bytes  texture string-table index (0 = none)
      -- optional extras present only when type_flags has BOOST_UP / SPEED_UP /
         SLOW_DOWN bits set --
      4 bytes  boost_power  (float32, only when BOOST_UP bit set)
      4 bytes  speed_mult   (float32, only when SPEED_UP bit set)
      4 bytes  slow_mult    (float32, only when SLOW_DOWN bit set)

[Texts]
  2 bytes  number of text objects (uint16)
  For each text:
    2 bytes  page string-table index
    2 bytes  x (int16)   -- pixel position
    2 bytes  y (int16)
    3 bytes  r, g, b
    1 byte   size (uint8)
    2 bytes  font string-table index (0 = none)
    2 bytes  text string-table index

End of file.

Typical size reduction: ~90 % vs. pretty-printed JSON.
"""

from __future__ import annotations

import struct
from typing import Any, Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────
MAGIC = b"PLVL"
VERSION = 1

# Canonical type-flag bit positions
_TYPE_BITS: Dict[str, int] = {
    "NORMAL":     0,
    "DEATH":      1,
    "CHECKPOINT": 2,
    "FINISH":     3,
    "SLIPPERY":   4,
    "NOCLIP":     5,
    "BOOST_UP":   6,
    "SPEED_UP":   7,
}
_TYPE_BITS2: Dict[str, int] = {
    "SLOW_DOWN": 0,
}
_BIT_TYPE: Dict[int, str] = {v: k for k, v in _TYPE_BITS.items()}
_BIT_TYPE2: Dict[int, str] = {v: k for k, v in _TYPE_BITS2.items()}

# ─────────────────────────────────────────────────────────────
# String-table helpers
# ─────────────────────────────────────────────────────────────

class _StringTable:
    """Bidirectional mapping between strings and compact uint16 indices.

    Index 0 is always the empty string / "not present" sentinel.
    """

    def __init__(self) -> None:
        self._list: List[str] = [""]          # index 0 == empty
        self._index: Dict[str, int] = {"": 0}

    def intern(self, s: str) -> int:
        """Return the index for *s*, registering it if new."""
        if s not in self._index:
            self._index[s] = len(self._list)
            self._list.append(s)
        return self._index[s]

    def get(self, idx: int) -> str:
        return self._list[idx] if idx < len(self._list) else ""

    def __len__(self) -> int:
        return len(self._list)

    # ── serialise ──────────────────────────────────────────────

    def pack(self) -> bytes:
        out = bytearray()
        out += struct.pack(">H", len(self._list))
        for s in self._list:
            encoded = s.encode("utf-8")
            out += struct.pack(">H", len(encoded))
            out += encoded
        return bytes(out)

    @classmethod
    def unpack(cls, data: bytes, offset: int = 0) -> Tuple["_StringTable", int]:
        tbl = cls()
        tbl._list = []
        tbl._index = {}
        count, = struct.unpack_from(">H", data, offset)
        offset += 2
        for i in range(count):
            slen, = struct.unpack_from(">H", data, offset)
            offset += 2
            s = data[offset: offset + slen].decode("utf-8")
            offset += slen
            tbl._list.append(s)
            tbl._index[s] = i
        return tbl, offset


# ─────────────────────────────────────────────────────────────
# Encode
# ─────────────────────────────────────────────────────────────

def encode(level_data: Dict[str, Any]) -> bytes:
    """Convert a level data dict to compact binary .plvl bytes."""

    st = _StringTable()

    # ── pre-pass: intern all strings ──────────────────────────
    name = level_data.get("name", "")
    st.intern(name)

    bg = level_data.get("background_color", {})
    bg_image = bg.get("image", "") if isinstance(bg, dict) else ""
    st.intern(bg_image)

    pages_raw = level_data.get("pages", {})
    page_positions_raw = level_data.get("page_positions", {})

    for page_key in pages_raw:
        st.intern(str(page_key))

    for page_key, page_data in pages_raw.items():
        platforms = page_data.get("platforms", [])
        for p in platforms:
            st.intern(p.get("texture") or "")

    texts = level_data.get("texts", [])
    for t in texts:
        st.intern(str(t.get("page", 1)))
        st.intern(t.get("font") or "")
        st.intern(t.get("text", ""))

    # ── header ────────────────────────────────────────────────
    buf = bytearray()
    buf += MAGIC
    buf += struct.pack("B", VERSION)
    buf += st.pack()        # string table (written before body, offsets known)

    # ── level header ──────────────────────────────────────────
    spawn = level_data.get("player_spawn", {})
    spawn_grid = 1 if spawn.get("grid", True) else 0
    spawn_grid_size = int(spawn.get("grid_size", 32))
    spawn_x = int(spawn.get("x", 0))
    spawn_y = int(spawn.get("y", 0))

    bg_r = bg.get("r", 135) if isinstance(bg, dict) else 135
    bg_g = bg.get("g", 206) if isinstance(bg, dict) else 206
    bg_b = bg.get("b", 235) if isinstance(bg, dict) else 235

    pw = int(level_data.get("page_width_cells", 60))
    ph = int(level_data.get("page_height_cells", 34))

    buf += struct.pack(">H", st.intern(name))
    buf += struct.pack("B", spawn_grid)
    buf += struct.pack(">H", spawn_grid_size)
    buf += struct.pack(">hh", spawn_x, spawn_y)
    buf += struct.pack("BBB", bg_r, bg_g, bg_b)
    buf += struct.pack(">H", st.intern(bg_image))
    buf += struct.pack(">HH", pw, ph)

    # ── pages ─────────────────────────────────────────────────
    buf += struct.pack(">H", len(pages_raw))

    for page_key, page_data in pages_raw.items():
        page_key_str = str(page_key)
        pos = page_positions_raw.get(page_key_str, page_positions_raw.get(page_key, {}))
        pos_x = int(pos.get("x", 0)) if isinstance(pos, dict) else 0
        pos_y = int(pos.get("y", 0)) if isinstance(pos, dict) else 0

        platforms = page_data.get("platforms", [])

        buf += struct.pack(">H", st.intern(page_key_str))
        buf += struct.pack(">hh", pos_x, pos_y)
        buf += struct.pack(">H", len(platforms))

        for p in platforms:
            x1 = int(p.get("x1", p.get("x", 0)))
            y1 = int(p.get("y1", p.get("y", 0)))
            x2 = int(p.get("x2", x1))
            y2 = int(p.get("y2", y1))
            grid_size = int(p.get("grid_size", 32))
            layer = int(p.get("layer", 0))

            color = p.get("color", [120, 120, 120])
            r, g, b = (int(color[0]), int(color[1]), int(color[2])) if color and len(color) >= 3 else (120, 120, 120)

            types_raw = p.get("types", [p.get("type", "NORMAL")])
            types = [str(t).upper() for t in (types_raw if types_raw else ["NORMAL"])]

            flags1 = 0
            for t in types:
                if t in _TYPE_BITS:
                    flags1 |= (1 << _TYPE_BITS[t])
            flags2 = 0
            for t in types:
                if t in _TYPE_BITS2:
                    flags2 |= (1 << _TYPE_BITS2[t])

            # grid_size stored as grid_size//8 to fit in uint8 (32→4, 16→2 …)
            gs_byte = max(1, min(255, grid_size // 8))

            texture_idx = st.intern(p.get("texture") or "")

            buf += struct.pack(">hhhh", x1, y1, x2, y2)
            buf += struct.pack("Bb", gs_byte, layer)
            buf += struct.pack("BBB", r, g, b)
            buf += struct.pack("BB", flags1, flags2)
            buf += struct.pack(">H", texture_idx)

            if flags1 & (1 << _TYPE_BITS["BOOST_UP"]):
                buf += struct.pack(">f", float(p.get("boost_power", -900.0)))
            if flags1 & (1 << _TYPE_BITS["SPEED_UP"]):
                buf += struct.pack(">f", float(p.get("speed_multiplier", 1.5)))
            if flags2 & (1 << _TYPE_BITS2["SLOW_DOWN"]):
                buf += struct.pack(">f", float(p.get("slow_multiplier", 0.5)))

    # ── texts ─────────────────────────────────────────────────
    buf += struct.pack(">H", len(texts))
    for t in texts:
        page_idx = st.intern(str(t.get("page", 1)))
        tx = int(t.get("x", 0))
        ty = int(t.get("y", 0))
        col = t.get("color", [255, 255, 255])
        tr, tg, tb = (int(col[0]), int(col[1]), int(col[2])) if col and len(col) >= 3 else (255, 255, 255)
        size = int(t.get("size", 24))
        font_idx = st.intern(t.get("font") or "")
        text_idx = st.intern(t.get("text", ""))

        buf += struct.pack(">H", page_idx)
        buf += struct.pack(">hh", tx, ty)
        buf += struct.pack("BBB", tr, tg, tb)
        buf += struct.pack("B", size)
        buf += struct.pack(">HH", font_idx, text_idx)

    return bytes(buf)


# ─────────────────────────────────────────────────────────────
# Decode
# ─────────────────────────────────────────────────────────────

def decode(data: bytes) -> Dict[str, Any]:
    """Convert .plvl binary bytes back to a level data dict."""

    if data[:4] != MAGIC:
        raise ValueError("Not a .plvl file (bad magic bytes)")
    version = data[4]
    if version != VERSION:
        raise ValueError(f"Unsupported .plvl version {version}")

    offset = 5  # past magic + version

    st, offset = _StringTable.unpack(data, offset)

    # ── level header ──────────────────────────────────────────
    name_idx, = struct.unpack_from(">H", data, offset); offset += 2
    spawn_grid_byte, = struct.unpack_from("B", data, offset); offset += 1
    spawn_grid_size, = struct.unpack_from(">H", data, offset); offset += 2
    spawn_x, spawn_y = struct.unpack_from(">hh", data, offset); offset += 4
    bg_r, bg_g, bg_b = struct.unpack_from("BBB", data, offset); offset += 3
    bg_image_idx, = struct.unpack_from(">H", data, offset); offset += 2
    pw, ph = struct.unpack_from(">HH", data, offset); offset += 4

    bg_image = st.get(bg_image_idx)

    level: Dict[str, Any] = {
        "name": st.get(name_idx),
        "player_spawn": {
            "x": spawn_x,
            "y": spawn_y,
            "grid": bool(spawn_grid_byte),
            "grid_size": spawn_grid_size,
        },
        "background_color": {
            "r": bg_r,
            "g": bg_g,
            "b": bg_b,
            "a": 255,
            **({"image": bg_image} if bg_image else {}),
        },
        "page_width_cells": pw,
        "page_height_cells": ph,
        "pages": {},
        "page_positions": {},
        "texts": [],
    }

    # ── pages ─────────────────────────────────────────────────
    num_pages, = struct.unpack_from(">H", data, offset); offset += 2

    for _ in range(num_pages):
        page_key_idx, = struct.unpack_from(">H", data, offset); offset += 2
        pos_x, pos_y = struct.unpack_from(">hh", data, offset); offset += 4
        num_platforms, = struct.unpack_from(">H", data, offset); offset += 2

        page_key = st.get(page_key_idx)
        level["page_positions"][page_key] = {"x": pos_x, "y": pos_y}

        platforms: List[Dict[str, Any]] = []
        for _ in range(num_platforms):
            x1, y1, x2, y2 = struct.unpack_from(">hhhh", data, offset); offset += 8
            gs_byte, layer = struct.unpack_from("Bb", data, offset); offset += 2
            r, g, b = struct.unpack_from("BBB", data, offset); offset += 3
            flags1, flags2 = struct.unpack_from("BB", data, offset); offset += 2
            texture_idx, = struct.unpack_from(">H", data, offset); offset += 2

            grid_size = gs_byte * 8

            types = []
            for bit, tname in _BIT_TYPE.items():
                if flags1 & (1 << bit):
                    types.append(tname)
            for bit, tname in _BIT_TYPE2.items():
                if flags2 & (1 << bit):
                    types.append(tname)
            if not types:
                types = ["NORMAL"]

            plat: Dict[str, Any] = {
                "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                "grid_size": grid_size,
                "types": types,
                "color": [r, g, b],
                "layer": int(layer),
            }
            texture = st.get(texture_idx)
            if texture:
                plat["texture"] = texture

            if flags1 & (1 << _TYPE_BITS["BOOST_UP"]):
                val, = struct.unpack_from(">f", data, offset); offset += 4
                plat["boost_power"] = val
            if flags1 & (1 << _TYPE_BITS["SPEED_UP"]):
                val, = struct.unpack_from(">f", data, offset); offset += 4
                plat["speed_multiplier"] = val
            if flags2 & (1 << _TYPE_BITS2["SLOW_DOWN"]):
                val, = struct.unpack_from(">f", data, offset); offset += 4
                plat["slow_multiplier"] = val

            platforms.append(plat)

        level["pages"][page_key] = {"platforms": platforms}

    # ── texts ─────────────────────────────────────────────────
    num_texts, = struct.unpack_from(">H", data, offset); offset += 2
    for _ in range(num_texts):
        page_idx, = struct.unpack_from(">H", data, offset); offset += 2
        tx, ty = struct.unpack_from(">hh", data, offset); offset += 4
        tr, tg, tb = struct.unpack_from("BBB", data, offset); offset += 3
        tsize, = struct.unpack_from("B", data, offset); offset += 1
        font_idx, text_idx = struct.unpack_from(">HH", data, offset); offset += 4

        text_obj: Dict[str, Any] = {
            "page": st.get(page_idx),
            "x": tx,
            "y": ty,
            "color": [tr, tg, tb],
            "size": tsize,
            "text": st.get(text_idx),
        }
        font = st.get(font_idx)
        if font:
            text_obj["font"] = font
        level["texts"].append(text_obj)

    return level


# ─────────────────────────────────────────────────────────────
# Unified load (handles both .plvl and .json)
# ─────────────────────────────────────────────────────────────

def load_level(file_path: str):
    """Load a level from either a ``.plvl`` or ``.json`` file.

    Returns the level data dict, or None on error.
    """
    import json as _json

    if not file_path or not __import__("os").path.exists(file_path):
        return None

    try:
        if file_path.endswith(".plvl"):
            with open(file_path, "rb") as f:
                return decode(f.read())
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                return _json.load(f)
    except Exception as e:
        print(f"[level_codec] Error loading '{file_path}': {e}")
        return None


def save_level(file_path: str, level_data: dict) -> None:
    """Save level data to a ``.plvl`` binary file."""
    with open(file_path, "wb") as f:
        f.write(encode(level_data))
