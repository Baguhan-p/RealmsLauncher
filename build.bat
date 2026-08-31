@echo off
chcp 65001 >nul
echo Installing dependencies...
pip install pyinstaller customtkinter requests --quiet

echo Building RealmsLauncher...
py -m PyInstaller RealmsLauncher.spec

if exist "dist\RealmsLauncher.exe" (
    echo Build successful! RealmsLauncher.exe created in dist folder.
) else (
    echo Build failed! Check for errors above.
)

echo.
echo Press any key to exit...
pause >nul
