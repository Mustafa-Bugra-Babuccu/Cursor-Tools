@echo off
REM Cursor-Tools Build Script
REM Simple batch wrapper for the Python build script

echo ============================================================
echo  Cursor-Tools Build Script
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher and try again
    pause
    exit /b 1
)

REM Check if build_script.py exists
if not exist "build_script.py" (
    echo ERROR: build_script.py not found
    echo Please make sure you're running this from the correct directory
    pause
    exit /b 1
)

REM Parse command line arguments
set BUILD_TYPE=both
if "%1"=="onefile" set BUILD_TYPE=onefile
if "%1"=="onefolder" set BUILD_TYPE=onefolder
if "%1"=="both" set BUILD_TYPE=both
if "%1"=="help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="--help" goto :show_help

echo Building Cursor-Tools (%BUILD_TYPE%)...
echo.

REM Run the Python build script
python build_script.py %BUILD_TYPE%

REM Check if build was successful
if errorlevel 1 (
    echo.
    echo ============================================================
    echo  BUILD FAILED
    echo ============================================================
    echo Check the error messages above for details
    pause
    exit /b 1
) else (
    echo.
    echo ============================================================
    echo  BUILD COMPLETED SUCCESSFULLY
    echo ============================================================
    echo Check the 'dist' folder for the built executables
    echo.
)

pause
exit /b 0

:show_help
echo Usage: build.bat [onefile^|onefolder^|both^|help]
echo.
echo Options:
echo   onefile   - Build only one-file executable (slower startup, single file)
echo   onefolder - Build only one-folder distribution (faster startup, multiple files)
echo   both      - Build both configurations (default)
echo   help      - Show this help message
echo.
echo Examples:
echo   build.bat              (builds both configurations)
echo   build.bat onefile      (builds only one-file executable)
echo   build.bat onefolder    (builds only one-folder distribution)
echo.
pause
exit /b 0
