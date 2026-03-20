@echo off
setlocal enabledelayedexpansion
title CyberGame Remover

REM ── Auto-elevate to Administrator ────────────────────────────────────────
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -NoProfile -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit /b
)

REM ── Resolve zip root ─────────────────────────────────────────────────────
if exist "%~dp0..\run_game.py" (
  set "ZIPROOT=%~dp0..\"
) else (
  set "ZIPROOT=%~dp0"
)
pushd "%ZIPROOT%"
set "ZIPROOT=%CD%"
popd

cls
echo.
echo  =============================================
echo   CYBERGAME REMOVER
echo  =============================================
echo.
echo  This will completely remove CyberGame:
echo    - Kill all running game processes
echo    - Remove registry startup entry
echo    - Remove scheduled task
echo    - Delete %%APPDATA%%\CyberGame
echo    - Delete the extracted game folder
echo.
echo  =============================================
echo.
set /p CONFIRM= Proceed with full removal? (Y/N): 
if /i not "%CONFIRM%"=="Y" (
    echo.
    echo  Cancelled. Nothing was removed.
    echo.
    pause
    exit /b 0
)

echo.
echo  [1/5] Killing game processes...
taskkill /f /im pythonw.exe >nul 2>&1
taskkill /f /im python.exe  >nul 2>&1
timeout /t 2 /nobreak >nul
echo        Done.

echo.
echo  [2/5] Removing registry startup entry...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "CyberGameUpdater" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo        Registry key removed.
) else (
    echo        Not found - already clean.
)

echo.
echo  [3/5] Removing scheduled task...
schtasks /delete /tn "CyberGameUpdater" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo        Scheduled task removed.
) else (
    echo        Not found - already clean.
)

echo.
echo  [4/5] Deleting AppData install folder...
set "APPGAME=%APPDATA%\CyberGame"
if exist "%APPGAME%\" (
    rmdir /s /q "%APPGAME%"
    echo        Deleted: %APPGAME%
) else (
    echo        Not found - already clean.
)

echo.
echo  [5/5] Deleting extracted game folder...
for /d %%D in ("%ZIPROOT%\game" "%ZIPROOT%\runtime" "%ZIPROOT%\wheelhouse" "%ZIPROOT%\server" "%ZIPROOT%\scripts" "%ZIPROOT%\tools" "%ZIPROOT%\.venv") do (
    if exist "%%D\" (
        rmdir /s /q "%%D"
        echo        Deleted: %%D
    )
)
for %%F in ("%ZIPROOT%\run_game.py" "%ZIPROOT%\requirements.txt" "%ZIPROOT%\README.md" "%ZIPROOT%\highscore.json" "%ZIPROOT%\start.bat" "%ZIPROOT%\remove_game.bat") do (
    if exist "%%F" (
        del /f /q "%%F"
        echo        Deleted: %%F
    )
)
for /d /r "%ZIPROOT%" %%D in (__pycache__) do (
    if exist "%%D" rmdir /s /q "%%D" >nul 2>&1
)
echo        Done.

echo.
echo  =============================================
echo   REMOVAL COMPLETE
echo   CyberGame has been fully removed.
echo  =============================================
echo.
pause
