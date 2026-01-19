#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

./parkour/bin/python -m PyInstaller \
  --noconfirm \
  --clean \
  --name ParkourGame \
  --onefile \
  --windowed \
  --paths src/code \
  --add-data "src/resources:resources" \
  --add-data "data:data" \
  --add-data "levels:levels" \
  src/code/main.py
