@echo off
setlocal enabledelayedexpansion
title CyberGame Installer

REM ── Resolve zip root ──────────────────────────────────────────────────────
if exist "%~dp0run_game.py" (
  set "ZIPROOT=%~dp0"
) else (
  set "ZIPROOT=%~dp0..\"
)
pushd "%ZIPROOT%"
set "ZIPROOT=%CD%"
popd

set "PYDIR=%ZIPROOT%\runtime\python"
set "PYEXE=%PYDIR%\python.exe"
set "PYWEXE=%PYDIR%\pythonw.exe"
set "PTHFILE=%PYDIR%\python313._pth"
set "WHL=%ZIPROOT%\wheelhouse"
set "GETPIP=%ZIPROOT%\runtime\get-pip.py"

cls
echo.
echo  =============================================
echo   CYBERGAME INSTALLER
echo  =============================================
echo.
echo  This will:
echo    - Install required game libraries
echo    - Register the game to start on boot
echo    - Launch the game
echo.
echo  =============================================
echo.
set /p CONFIRM= Install and launch CyberGame? (Y/N): 
if /i not "%CONFIRM%"=="Y" (
  echo.
  echo  Cancelled. No changes were made.
  echo.
  pause
  exit /b 0
)

echo.
echo  [1/4] Checking Python runtime...
if exist "%PYEXE%" (
  echo        Python ready.
  goto :patch_pth
)
set "PYZIP=%ZIPROOT%\runtime\python-embed.zip"
if not exist "%PYZIP%" (
  echo  ERROR: python-embed.zip not found.
  pause & exit /b 1
)
echo        Extracting Python, please wait...
powershell -NoProfile -Command "Expand-Archive -Path '!PYZIP!' -DestinationPath '!PYDIR!' -Force"
if not exist "%PYEXE%" (
  echo  ERROR: Extraction failed.
  pause & exit /b 1
)
echo        Python ready.

:patch_pth
if exist "%PTHFILE%" (
  powershell -NoProfile -Command "(Get-Content '%PTHFILE%') -replace '#import site','import site' | Set-Content '%PTHFILE%'"
)

echo.
echo  [2/4] Checking pip...
"%PYEXE%" -m pip --version >nul 2>&1
if %errorlevel% equ 0 (
  echo        pip ready.
  goto :check_pygame
)
if not exist "%GETPIP%" (
  echo  ERROR: runtime\get-pip.py not found.
  pause & exit /b 1
)
echo        Installing pip...
"%PYEXE%" "%GETPIP%" --no-index --find-links "%WHL%" -q
if %errorlevel% neq 0 (
  echo  ERROR: pip install failed.
  pause & exit /b 1
)
echo        pip ready.

:check_pygame
echo.
echo  [3/4] Checking pygame...
"%PYEXE%" -c "import pygame" >nul 2>&1
if %errorlevel% equ 0 (
  echo        pygame ready.
  goto :launch
)
echo        Installing pygame...
"%PYEXE%" -m pip install --no-index --find-links "%WHL%" pygame -q
if %errorlevel% neq 0 (
  echo  ERROR: pygame install failed.
  pause & exit /b 1
)
echo        pygame ready.

:launch
echo.
echo  [4/4] Launching game...
if exist "%PYWEXE%" (
  start "" "%PYWEXE%" "%ZIPROOT%\run_game.py" --yes
) else (
  start "" "%PYEXE%" "%ZIPROOT%\run_game.py" --yes
)
echo        Done.
echo.
echo  The game is now running. You can close this window.
echo.
timeout /t 3 /nobreak >nul
