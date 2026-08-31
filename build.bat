@echo off
echo Building RealmsLauncher...
pyinstaller --onefile --windowed --name RealmsLauncher --icon=NONE realmslauncher.py
echo Build complete! Check the 'dist' folder for RealmsLauncher.exe
pause
