"""
convert_levels.py — Batch-convert level JSON files to the compact .plvl binary format.

Usage:
    python packaging/convert_levels.py              # dry-run (shows stats only)
    python packaging/convert_levels.py --write       # write .plvl files next to the .json files
    python packaging/convert_levels.py --replace     # write .plvl AND delete the original .json files

Run from the project root:
    .\\parkour\\Scripts\\python.exe packaging\\convert_levels.py [--write] [--replace]
"""

import argparse
import json
import os
import sys

# Locate level_codec relative to this script's location
_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC_CODE = os.path.join(_HERE, "..", "src", "code")
if _SRC_CODE not in sys.path:
    sys.path.insert(0, _SRC_CODE)

from utils.level_codec import encode as _encode, decode as _decode  # noqa: E402


def _fmt_size(n: int) -> str:
    if n >= 1024 * 1024:
        return f"{n / (1024 * 1024):.2f} MB"
    if n >= 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n} B"


def convert_all(worlds_dir: str, write: bool, replace: bool) -> None:
    total_json = 0
    total_plvl = 0
    converted = 0
    errors = 0

    for root, _dirs, files in os.walk(worlds_dir):
        for fname in sorted(files):
            if not fname.endswith(".json"):
                continue
            json_path = os.path.join(root, fname)
            plvl_path = os.path.splitext(json_path)[0] + ".plvl"

            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    level_data = json.load(f)

                encoded = _encode(level_data)
                json_size = os.path.getsize(json_path)
                plvl_size = len(encoded)

                ratio = (1 - plvl_size / json_size) * 100 if json_size else 0
                rel_path = os.path.relpath(json_path, worlds_dir)
                print(
                    f"  {rel_path:55s}  {_fmt_size(json_size):>10s}  →  {_fmt_size(plvl_size):>8s}"
                    f"  ({ratio:.0f}% smaller)"
                )

                total_json += json_size
                total_plvl += plvl_size
                converted += 1

                if write or replace:
                    with open(plvl_path, "wb") as f:
                        f.write(encoded)

                    # Verify round-trip
                    recovered = _decode(encoded)
                    # Basic sanity check: same platform count
                    orig_count = sum(
                        len(page.get("platforms", []))
                        for page in level_data.get("pages", {}).values()
                        if isinstance(page, dict)
                    )
                    rec_count = sum(
                        len(page.get("platforms", []))
                        for page in recovered.get("pages", {}).values()
                        if isinstance(page, dict)
                    )
                    if orig_count != rec_count:
                        print(
                            f"    ⚠  Round-trip mismatch: {orig_count} platforms → {rec_count}"
                        )

                    if replace:
                        os.remove(json_path)
                        print(f"    ✓  Removed {fname}")

            except Exception as exc:
                print(f"  ERROR converting {fname}: {exc}")
                errors += 1

    print()
    print("=" * 70)
    if converted:
        overall_ratio = (1 - total_plvl / total_json) * 100 if total_json else 0
        print(
            f"  Converted : {converted} file(s)"
            + (f"  |  {errors} error(s)" if errors else "")
        )
        print(f"  Total JSON : {_fmt_size(total_json)}")
        print(f"  Total .plvl: {_fmt_size(total_plvl)}")
        print(f"  Savings    : {_fmt_size(total_json - total_plvl)}  ({overall_ratio:.0f}%)")
        if not write and not replace:
            print()
            print("  (Dry-run — no files written.  Use --write or --replace to save.)")
    else:
        print("  No JSON level files found.")
    print("=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert level JSON files to compact binary .plvl format."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--write",
        action="store_true",
        help="Write .plvl files alongside the .json files (keeps originals).",
    )
    group.add_argument(
        "--replace",
        action="store_true",
        help="Write .plvl files and DELETE the original .json files.",
    )
    parser.add_argument(
        "--worlds-dir",
        default=os.path.join(_HERE, "..", "data", "worlds"),
        help="Path to the worlds directory (default: data/worlds).",
    )
    args = parser.parse_args()

    worlds_dir = os.path.abspath(args.worlds_dir)
    if not os.path.isdir(worlds_dir):
        print(f"Error: worlds directory not found: {worlds_dir}")
        sys.exit(1)

    mode = "REPLACE (write .plvl + delete .json)" if args.replace else \
           "WRITE (keep .json + write .plvl)" if args.write else \
           "DRY-RUN (no files changed)"

    print(f"convert_levels.py — mode: {mode}")
    print(f"Scanning: {worlds_dir}")
    print()
    convert_all(worlds_dir, write=args.write, replace=args.replace)


if __name__ == "__main__":
    main()
