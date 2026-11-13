@echo off
rem Builds everything: FinSafe.exe and then the installer.
call build_exe.bat
if errorlevel 1 exit /b 1
call build_installer.bat
