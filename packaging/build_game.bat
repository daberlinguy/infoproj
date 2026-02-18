@echo off
setlocal enabledelayedexpansion

:: Get the root directory relative to this script
pushd "%~dp0.."

echo [INFO] Building Game...
.\parkour\Scripts\python.exe -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --name ParkuhrGame ^
  --onefile ^
  --windowed ^
  --paths src/code ^
  --add-data "src/resources;resources" ^
  --add-data "data;data" ^
  --add-data "levels;levels" ^
  src/code/main.py

echo [INFO] Game build finished.
popd
