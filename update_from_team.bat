@echo off
title Team RIP - Update from Team
echo ========================================================
echo       FETCHING LATEST UPDATES FROM TEAM RIP
echo ========================================================
git fetch --all
git merge origin/main --no-edit
echo.
echo Done! Your local workspace is now up to date with main.
pause
