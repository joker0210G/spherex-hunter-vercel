@echo off
title Team RIP - Teammate Setup
echo ========================================================
echo        WELCOME TO TEAM RIP - SPHEREx HUNTER
echo ========================================================
echo.
echo Who are you?
echo 1) jokerodu (Team Lead)
echo 2) darkodu  (Astro-Data & Backend Lead)
echo 3) coolodu  (Frontend & Blink Viewer Lead)
echo 4) iceodu   (Image Math, AI & Difference Engine)
echo 5) astrodu  (UI-UX, Citizen Science, Pitch & Demo)
echo.
set /p choice="Enter your number (1-5): "

if "%choice%"=="1" set BRANCH=main
if "%choice%"=="2" set BRANCH=darkodu/astro-backend
if "%choice%"=="3" set BRANCH=coolodu/web-frontend
if "%choice%"=="4" set BRANCH=iceodu/image-math-ai
if "%choice%"=="5" set BRANCH=astrodu/ui-story-pitch

echo.
echo Setting up your git branch: %BRANCH% ...
git checkout -b %BRANCH% 2>nul || git checkout %BRANCH%
echo.
echo ========================================================
echo Setup complete! Now open this folder in Antigravity.
echo In Antigravity chat, simply type:
echo "Hi Antigravity! I am ready. Check my memory file and start!"
echo ========================================================
pause
