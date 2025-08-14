@echo off
echo ========================================
echo CASI Installer Build Script
echo ========================================
echo.

REM Check if required files exist
echo Checking required files...

REM Check if PyInstaller build exists
if not exist "dist\chatbot_ui.exe" (
    echo ERROR: PyInstaller build not found!
    echo Please run 'build.bat' first to create the executable.
    pause
    exit /b 1
)

REM Check if icon files exist
if not exist "CASInew-nbg.ico" (
    echo ERROR: CASInew-nbg.ico not found!
    pause
    exit /b 1
)

if not exist "CASInew-nbg.png" (
    echo ERROR: CASInew-nbg.png not found!
    pause
    exit /b 1
)

REM Check if Inno Setup is installed
where iscc >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Inno Setup Compiler (iscc) not found!
    echo Please install Inno Setup from: https://jrsoftware.org/isinfo.php
    pause
    exit /b 1
)

echo All required files found.
echo.

REM Create installer output directory
if not exist "installer_output" mkdir "installer_output"

REM Build the installer
echo Building CASI installer...
echo.

iscc CASI_Installer.iss

if %errorLevel% == 0 (
    echo.
    echo ========================================
    echo Installer built successfully!
    echo ========================================
    echo.
    echo Installer location: installer_output\CASI_Installer_v1.2.2.exe
    echo.
    echo Installer includes:
    echo - Main executable (chatbot_ui.exe)
    echo - All required assets and images
    echo - Configuration files (config.py, backend.py)
    echo - Documentation and troubleshooting guides
    echo - Troubleshooting scripts
    echo.
    echo Features:
    echo - Checks if CASI is running before install
    echo - Creates desktop and start menu shortcuts
    echo - Installs documentation and troubleshooting tools
    echo - Creates configuration directory
    echo - Registry entries for easy uninstall
    echo.
) else (
    echo.
    echo ========================================
    echo Installer build failed!
    echo ========================================
    echo.
    echo Please check:
    echo 1. Inno Setup is installed correctly
    echo 2. All required files are present
    echo 3. File paths in CASI_Installer.iss are correct
    echo.
)

pause
