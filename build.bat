@echo off
setlocal enabledelayedexpansion

:: Main script to coordinate builds for Parkuhr project

set BUILD_GAME=0
set BUILD_EDITOR=0

:: Parse arguments
if "%~1"=="" goto usage

:parse_args
if "%~1"=="" goto run_builds
if /i "%~1"=="-a" (
    set BUILD_GAME=1
    set BUILD_EDITOR=1
)
if /i "%~1"=="-g" (
    set BUILD_GAME=1
)
if /i "%~1"=="-e" (
    set BUILD_EDITOR=1
)
shift
goto parse_args

:usage
echo Usage: build.bat [-a] [-g] [-e]
echo   -a  Build all components (Game and Editor)
echo   -g  Build only the Parkuhr Game
echo   -e  Build only the Parkuhr Editor
echo.
echo Example: .\build.bat -a
echo Example: .\build.bat -g -e
exit /b 1

:run_builds
if %BUILD_GAME%==1 (
    echo [MAIN] Starting Game Build...
    call ".\packaging\build_game.bat"
)

if %BUILD_EDITOR%==1 (
    echo [MAIN] Starting Editor Build...
    call ".\packaging\build_editor.bat"
)

echo [MAIN] All requested builds completed.
