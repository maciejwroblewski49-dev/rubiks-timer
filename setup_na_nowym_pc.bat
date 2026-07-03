@echo off
title Rubik's Timer - Setup

echo ================================================
echo  Rubik's Timer - Instalacja na nowym PC
echo ================================================
echo.

:: Check Python
py --version >nul 2>&1
if errorlevel 1 (
    echo Python nie jest zainstalowany!
    echo Pobierz Python 3.11+ z: https://www.python.org/downloads/
    echo Zaznacz "Add Python to PATH" podczas instalacji.
    echo.
    pause & exit /b 1
)

echo [1/2] Instalowanie zaleznosci...
py -m pip install customtkinter pillow matplotlib --quiet
if errorlevel 1 (
    echo BLAD: Nie mozna zainstalowac pakietow.
    pause & exit /b 1
)

echo [2/2] Tworzenie ikony i skrotu na pulpicie...
py make_icon.py

:: Create desktop shortcut
py -c "
import os, sys
pythonw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
script  = os.path.abspath('main.py')
icon    = os.path.abspath('icon.ico')
desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
lnk     = os.path.join(desktop, \"Rubik's Timer.lnk\")

import subprocess, tempfile
ps = f'''
\$ws = New-Object -ComObject WScript.Shell
\$s  = \$ws.CreateShortcut('{lnk}')
\$s.TargetPath       = '{pythonw}'
\$s.Arguments        = '\"{script}\"'
\$s.WorkingDirectory = '{os.path.abspath('.')}'
\$s.IconLocation     = '{icon},0'
\$s.Description      = \"Rubik's Timer\"
\$s.Save()
'''
subprocess.run(['powershell','-Command', ps], check=True)
print('Skrot na pulpicie: OK')
"

echo.
echo ================================================
echo  GOTOWE! Uruchom aplikacje skrotem na pulpicie.
echo ================================================
pause
