@echo off
title Rubik's Timer - Build

echo ================================================
echo  Budowanie standalone .exe (Rubik's Timer)
echo ================================================
echo.

:: Install PyInstaller if needed
echo [1/3] Sprawdzanie PyInstaller...
py -m pip install pyinstaller matplotlib --quiet
if errorlevel 1 (
    echo BLAD: Nie mozna zainstalowac PyInstaller.
    pause & exit /b 1
)

:: Clean previous build
if exist "dist\Rubiks Timer" rmdir /s /q "dist\Rubiks Timer"
if exist "build" rmdir /s /q "build"

echo [2/3] Budowanie .exe...
py -m PyInstaller ^
    --noconfirm ^
    --onedir ^
    --windowed ^
    --name "Rubiks Timer" ^
    --icon "icon.ico" ^
    --add-data "icon.ico;." ^
    --add-data "fonts;fonts" ^
    --collect-all customtkinter ^
    main.py

if errorlevel 1 (
    echo.
    echo BLAD podczas budowania!
    pause & exit /b 1
)

echo [3/3] Kopiowanie ikony obok .exe...
copy /y "icon.ico" "dist\Rubiks Timer\icon.ico" >nul

echo.
echo ================================================
echo  GOTOWE!
echo  Folder z aplikacja: dist\Rubiks Timer\
echo.
echo  Skopiuj caly folder "Rubiks Timer" na inne
echo  urzadzenie - nie wymaga Pythona!
echo ================================================
echo.
pause
