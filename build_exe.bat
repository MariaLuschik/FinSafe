@echo off
rem ============================================================
rem Step 1. Build FinSafe.exe from the Python sources.
rem Run this file from the repository root (the folder with run_finsafe.py).
rem ============================================================

echo Installing PyInstaller...
python -m pip install pyinstaller
if errorlevel 1 goto error

echo Building FinSafe.exe...
rem --onefile  : pack everything into a single exe
rem --console  : the program is console based, keep the console window
rem --name     : name of the result file (dist\FinSafe.exe)
python -m PyInstaller --noconfirm --onefile --console --name FinSafe run_finsafe.py
if errorlevel 1 goto error

echo.
echo Done: dist\FinSafe.exe
goto end

:error
echo.
echo BUILD FAILED. Check the messages above.
exit /b 1

:end
