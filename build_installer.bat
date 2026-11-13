@echo off
rem ============================================================
rem Step 2. Build the installer FinSafe_Setup_<version>.exe with Inno Setup.
rem Needs dist\FinSafe.exe from build_exe.bat.
rem Result: installer\Output\FinSafe_Setup_1.0.0.exe
rem ============================================================

set ISCC=

if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe

if "%ISCC%"=="" (
    echo Inno Setup 6 was not found. Install it from https://jrsoftware.org/isdl.php
    exit /b 1
)

if not exist dist\FinSafe.exe (
    echo dist\FinSafe.exe is missing. Run build_exe.bat first.
    exit /b 1
)

"%ISCC%" installer\finsafe.iss
if errorlevel 1 (
    echo INSTALLER BUILD FAILED.
    exit /b 1
)

echo.
echo Done: installer\Output\
