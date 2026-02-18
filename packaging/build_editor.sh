#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

./parkour/bin/python -m PyInstaller \
  --noconfirm \
  --clean \
  --name ParkuhrEditor \
  --onefile \
  --windowed \
  --add-data "src/resources:resources" \
  editor/main.py
