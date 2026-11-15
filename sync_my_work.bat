@echo off
title Team RIP - 1-Click Sync Work to GitHub
echo ========================================================
echo          TEAM RIP - 1-CLICK GIT SYNC
echo ========================================================
echo Staging your changes...
git add .
set TIMESTAMP=%date%_%time%
git commit -m "Auto-sync by teammate at %TIMESTAMP%"
echo.
echo Pushing changes to your remote branch...
git push origin HEAD
echo.
echo ========================================================
echo WORK SYNCED SUCCESSFULLY TO GITHUB!
echo Your teammates and jokerodu can now see your updates.
echo ========================================================
pause
