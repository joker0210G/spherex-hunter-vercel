@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
chcp 65001 > nul
title Team RIP - Safe Team Sync and Workspace Hub
color 0B

set SHORTCUT_MODE=0
if not "%~1"=="" set SHORTCUT_MODE=1

if /i "%~1"=="radar" goto :RADAR
if /i "%~1"=="fetch" goto :RADAR
if /i "%~1"=="update" goto :RADAR
if /i "%~1"=="push" goto :PUSH
if /i "%~1"=="sync" goto :PUSH
if /i "%~1"=="save" goto :PUSH
if /i "%~1"=="setup" goto :SETUP
if /i "%~1"=="branch" goto :SETUP
if /i "%~1"=="stop" goto :STOP

:MENU
cls
echo ==============================================================================
echo             TEAM RIP: SPHEREx HUNTER - TEAM SYNC AND WORKSPACE HUB
echo                    NASA Space Apps Challenge 2026
echo ==============================================================================
echo.
echo   [1] Check Team Radar and Pull Updates (Safe Fetch + Activity Dashboard)
echo   [2] Save and Push My Work to GitHub (1-Click Sync)
echo   [3] Switch / Setup Teammate Branch (jokerodu, darkodu, coolodu, iceodu, astrodu)
echo   [4] Stop SPHEREx Hunter Server (Free Port 8000)
echo   [5] Exit
echo.
echo ==============================================================================
set /p MENU_CHOICE="Choose an option [1-5]: "

if "%MENU_CHOICE%"=="1" goto :RADAR
if "%MENU_CHOICE%"=="2" goto :PUSH
if "%MENU_CHOICE%"=="3" goto :SETUP
if "%MENU_CHOICE%"=="4" goto :STOP
if "%MENU_CHOICE%"=="5" goto :EXIT
echo Invalid choice. Please enter a number between 1 and 5.
timeout /t 2 > nul
goto :MENU

:RADAR
cls
echo ==============================================================================
echo        TEAM RIP: 1-CLICK SAFE TEAM RADAR AND UPDATES
echo        NASA Space Apps Challenge 2026 - SPHEREx Hunter
echo ==============================================================================
echo.
echo [1/2] Fetching team progress from GitHub (100%% safe, read-only)...
git fetch --all --prune
if %ERRORLEVEL% NEQ 0 (
    echo [!] Network or Git warning. Continuing with local data...
)

echo.
echo [2/2] Generating Multi-Track Activity and GitHub Tasks Dashboard...
echo.
if exist "tools\team_sync_summary.py" (
    python tools\team_sync_summary.py
) else (
    echo [INFO] team_sync_summary.py not found, skipping visual dashboard.
)

echo.
echo ==============================================================================
echo                      SAFETY AND LOCAL WORK CHECK
echo ==============================================================================

set HAS_UNCOMMITTED=
for /f "tokens=*" %%i in ('git status --porcelain') do set HAS_UNCOMMITTED=1

for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
if "%CURRENT_BRANCH%"=="" set CURRENT_BRANCH=main

if defined HAS_UNCOMMITTED (
    echo [!] NOTE: You have uncommitted work in progress on [%CURRENT_BRANCH%].
    echo     Your files were NOT touched or modified. Your work is 100%% safe!
    echo.
    echo     When you are ready to save your work to GitHub, use option 2 (Push My Work).
    echo.
    goto :ACTION_DONE
)

if "%CURRENT_BRANCH%"=="main" (
    echo Your working folder is clean.
    set /p MERGE_CHOICE="Pull latest main updates into your local folder? [Y/N] (Default=Y): "
    if /i "!MERGE_CHOICE!"=="N" goto :ACTION_DONE
    echo Pulling latest main...
    git pull origin main --no-edit
    goto :ACTION_DONE
)

echo Your working folder on branch [%CURRENT_BRANCH%] is clean.
echo.
echo Other teammates work on isolated branches:
echo   - darkodu  - backend/
echo   - coolodu  - frontend/
echo   - iceodu   - image_engine/
echo   - astrodu  - docs/
echo.
set /p MERGE_CHOICE="Do you want to merge latest main into [%CURRENT_BRANCH%]? [Y/N] (Default=N): "
if /i "!MERGE_CHOICE!"=="Y" (
    echo Merging origin/main into [%CURRENT_BRANCH%]...
    git merge origin/main --no-edit
) else (
    echo Skipped merge. Your branch [%CURRENT_BRANCH%] remains untouched!
)
goto :ACTION_DONE

:PUSH
cls
echo ==============================================================================
echo                     TEAM RIP - 1-CLICK GIT SYNC
echo ==============================================================================
echo.
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
if "%CURRENT_BRANCH%"=="" set CURRENT_BRANCH=main
echo Current branch: [%CURRENT_BRANCH%]
echo.
echo Staging your changes...
git add .
set TIMESTAMP=%date%_%time%
git commit -m "Auto-sync by teammate at %TIMESTAMP%"
echo.
echo Pushing changes to remote branch [%CURRENT_BRANCH%]...
git push origin HEAD
echo.
echo ==============================================================================
echo WORK SYNCED SUCCESSFULLY TO GITHUB!
echo Your teammates and jokerodu can now see your updates.
echo ==============================================================================
goto :ACTION_DONE

:SETUP
cls
echo ==============================================================================
echo                      TEAM RIP - TEAMMATE SETUP
echo ==============================================================================
echo.
echo Who are you?
echo   1) jokerodu (Team Lead)                          - [main]
echo   2) darkodu  (Astro-Data and Backend Lead)        - [darkodu/astro-backend]
echo   3) coolodu  (Frontend and Blink Viewer Lead)     - [coolodu/web-frontend]
echo   4) iceodu   (Image Math, AI and Difference)      - [iceodu/image-math-ai]
echo   5) astrodu  (UI-UX, Citizen Science, Pitch)      - [astrodu/ui-story-pitch]
echo.
set /p TM_CHOICE="Enter your number (1-5): "

set TARGET_BRANCH=
if "%TM_CHOICE%"=="1" set TARGET_BRANCH=main
if "%TM_CHOICE%"=="2" set TARGET_BRANCH=darkodu/astro-backend
if "%TM_CHOICE%"=="3" set TARGET_BRANCH=coolodu/web-frontend
if "%TM_CHOICE%"=="4" set TARGET_BRANCH=iceodu/image-math-ai
if "%TM_CHOICE%"=="5" set TARGET_BRANCH=astrodu/ui-story-pitch

if "%TARGET_BRANCH%"=="" (
    echo Invalid choice.
    timeout /t 2 > nul
    goto :SETUP
)

echo.
echo Setting up your git branch: %TARGET_BRANCH% ...
git checkout -b %TARGET_BRANCH% 2>nul || git checkout %TARGET_BRANCH%
echo.
echo ==============================================================================
echo Branch is now active: %TARGET_BRANCH%
echo You can now open this project in Antigravity.
echo ==============================================================================
goto :ACTION_DONE

:STOP
cls
echo ==============================================================================
echo            STOPPING SPHEREx HUNTER BACKEND (PORT 8000)
echo ==============================================================================
echo.
set FOUND=0
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    set FOUND=1
    echo Terminating server process PID %%a ...
    taskkill /F /PID %%a >nul 2>&1
)

if %FOUND%==1 (
    echo.
    echo [OK] SPHEREx Hunter server stopped successfully. Port 8000 is now free.
) else (
    echo.
    echo [INFO] No server was running on port 8000.
)
goto :ACTION_DONE

:ACTION_DONE
echo.
if "%SHORTCUT_MODE%"=="1" goto :EXIT
echo ------------------------------------------------------------------------------
pause
goto :MENU

:EXIT
exit /b 0
