@echo off
setlocal enabledelayedexpansion

:: Get the root directory relative to this script
pushd "%~dp0.."

echo [INFO] Building Editor...
.\parkour\Scripts\python.exe -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --name ParkuhrEditor ^
  --onefile ^
  --windowed ^
  --add-data "src/resources;resources" ^
  editor/main.py

echo [INFO] Editor build finished.
popd
