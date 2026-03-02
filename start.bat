@echo off
setlocal enabledelayedexpansion

:: Launcher script to start components for Parkuhr project

set START_GAME=0
set START_EDITOR=0

:: Parse arguments
if "%~1" == "" (
    :: Default behavior: Launch Game
    set START_GAME=1
    EXIT \B
    goto run_starts
)

:parse_args
if "%~1" == "" goto run_starts
if /i "%~1" == "-g" (
    set START_GAME=1
)
if /i "%~1" == "-e" (
    set START_EDITOR=1
)
shift
goto parse_args

:run_starts
:: Calculate how many components to start
set /a TOTAL_START=%START_GAME% + %START_EDITOR%

if %START_GAME% == 1 (
    if %TOTAL_START% GTR 1 (
        echo [MAIN] Starting Game in new window...
        start "" ".\parkour\Scripts\python.exe" ".\src\code\main.py"
    ) else (
        echo [MAIN] Starting Game...
        .\parkour\Scripts\python.exe .\src\code\main.py
    )
)

if %START_EDITOR% == 1 (
    if %TOTAL_START% GTR 1 (
        echo [MAIN] Starting Editor in new window...
        start "" ".\parkour\Scripts\python.exe" ".\editor\main.py"
    ) else (
        echo [MAIN] Starting Editor...
        .\parkour\Scripts\python.exe .\editor\main.py
    )
)
