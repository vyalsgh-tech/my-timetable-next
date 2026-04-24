@echo off
setlocal EnableExtensions

REM ============================================================
REM MyTimetableNext PC build script v2
REM Save this file as: build\build_pc_release.bat
REM Run from repository root:
REM     build\build_pc_release.bat
REM ============================================================

cd /d "%~dp0.."

echo.
echo ============================================================
echo  MyTimetableNext PC Build
echo ============================================================
echo Current folder:
echo %CD%
echo.

if not exist "desktop\timetable.pyw" (
    echo [ERROR] desktop\timetable.pyw not found.
    pause
    exit /b 1
)

if not exist "build\timetable.spec" (
    echo [ERROR] build\timetable.spec not found.
    pause
    exit /b 1
)

if not exist "data\timetable.csv" (
    echo [ERROR] data\timetable.csv not found.
    pause
    exit /b 1
)

if not exist "data\academic_calendar.csv" (
    echo [ERROR] data\academic_calendar.csv not found.
    pause
    exit /b 1
)

echo [1/4] Check Python
python --version
if errorlevel 1 (
    echo [ERROR] python command failed.
    pause
    exit /b 1
)

echo.
echo [2/4] Check PyInstaller
python -m PyInstaller --version > nul 2>&1
if errorlevel 1 (
    echo PyInstaller is not installed. Installing now...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] PyInstaller install failed.
        pause
        exit /b 1
    )
)

echo.
echo [3/4] Build EXE with PyInstaller
python -m PyInstaller "build\timetable.spec" --noconfirm
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)

echo.
echo [OK] PyInstaller build completed.
echo Dist folder:
dir "dist"

echo.
echo [4/4] Try Inno Setup compiler

set "ISCC_EXE="

if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC_EXE=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
)

if not defined ISCC_EXE (
    if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
        set "ISCC_EXE=%ProgramFiles%\Inno Setup 6\ISCC.exe"
    )
)

if not defined ISCC_EXE (
    echo [INFO] Inno Setup compiler not found.
    echo [INFO] EXE build is done. Installer build skipped.
    echo [INFO] If you need installer, install Inno Setup 6 and run this script again.
    goto END
)

echo Inno Setup compiler:
echo %ISCC_EXE%

"%ISCC_EXE%" "build\installer.iss"
if errorlevel 1 (
    echo [ERROR] Inno Setup build failed.
    pause
    exit /b 1
)

echo [OK] Installer build completed.

:END
echo.
echo ============================================================
echo  Build script finished
echo ============================================================
echo Next checks:
echo  1. Run the EXE in dist folder.
echo  2. If installer was created, install and run it.
echo  3. In PC app, use Settings - Update/Data refresh.
echo.
pause
endlocal
