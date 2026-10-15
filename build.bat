@echo off
setlocal
echo =========================================
echo  Brand Engine Build Script
echo =========================================
echo.

echo [1/6] Cleaning previous builds...
if exist dist       rmdir /s /q dist
if exist build      rmdir /s /q build
if exist installer  rmdir /s /q installer

echo [2/6] Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo [3/6] Building executable with PyInstaller...
python build_exe.py
if errorlevel 1 (
    echo BUILD FAILED at PyInstaller step.
    exit /b 1
)
if not exist "dist\BrandEngine.exe" (
    echo ERROR: dist\BrandEngine.exe was not produced.
    exit /b 1
)

echo [4/6] Preparing installer folder...
if not exist installer mkdir installer

echo [5/6] Compiling Inno Setup installer...
set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
    echo WARNING: Inno Setup 6 not found. Skipping installer.
    echo Install from https://jrsoftware.org/isinfo.php and re-run.
    goto :done
)
%ISCC% installer_script.iss
if errorlevel 1 (
    echo INSTALLER BUILD FAILED.
    exit /b 1
)

:done
echo.
echo [6/6] Build complete!
echo   Executable : dist\BrandEngine.exe
echo   Installer  : installer\BrandEngine_Setup_1.0.0.exe
pause
endlocal