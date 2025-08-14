@echo off
echo Creating CASI Installer...

REM Check if Inno Setup is installed
where iscc >nul 2>&1
if %errorlevel% neq 0 (
    echo Inno Setup not found. Please install Inno Setup first.
    echo Download from: https://jrsoftware.org/isinfo.php
    pause
    exit /b 1
)

REM Create installer
iscc "CASI_Installer.iss"

if %errorlevel% equ 0 (
    echo ✅ Installer created successfully!
    echo 📁 Check the Output folder for the installer
) else (
    echo ❌ Failed to create installer
)

pause

