"""
Build script for creating a standalone Windows executable
Uses PyInstaller to create a single EXE file
"""
import importlib
import io
import os
import shutil
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Force UTF-8 stdout/stderr on Windows so emoji / unicode never crashes the
# build script (Windows console defaults to cp1252).
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True
        )
    except Exception:
        # If stdout has no .buffer (e.g. running under some IDEs), just skip.
        pass


def build_windows_exe() -> int:
    """Build a Windows executable using PyInstaller. Returns exit code."""

    # Clean previous builds
    for dir_name in ("build", "dist", "__pycache__"):
        if os.path.exists(dir_name):
            print(f"[CLEAN] Removing {dir_name}/")
            shutil.rmtree(dir_name, ignore_errors=True)

    # Make sure required asset files exist so PyInstaller doesn't silently skip
    icon_path = Path("assets") / "icon.ico"
    if not icon_path.exists():
        print(f"[WARN] {icon_path} not found - building without custom icon.")
        print("       Create it with:")
        print("       python -c \"from PIL import Image; "
              "Image.open('assets/logo.png').convert('RGBA').save("
              "'assets/icon.ico', sizes=[(256,256),(128,128),(64,64),"
              "(48,48),(32,32),(16,16)])\"")
        icon_arg = None
    else:
        icon_arg = str(icon_path).replace("\\", "/")

    # -----------------------------------------------------------------------
    # PyInstaller arguments
    # -----------------------------------------------------------------------
    args = [
        "main.py",
        "--name=BrandEngine",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        # Bundle the assets folder next to the exe at runtime
        "--add-data=assets;assets",
        # NOTE: do NOT bundle `database/` - brands.db is user data that the
        # app creates at runtime via config.DATABASE_PATH. Shipping it means
        # Inno Setup (or PyInstaller) may overwrite the user's saved brands.

        # Core GUI dependencies
        "--hidden-import=customtkinter",
        "--collect-all=customtkinter",
        "--hidden-import=PIL",
        "--collect-all=PIL",
        "--hidden-import=PIL._tkinter_finder",

        # Networking / data handling
        "--hidden-import=whois",
        "--hidden-import=requests",
        "--hidden-import=openpyxl",
        "--hidden-import=pandas",
        "--hidden-import=pandas._libs.tslibs.base",
    ]

    # Only add optional deps if they are actually installed. This avoids the
    # "Hidden import 'X' not found" warnings/errors from PyInstaller.
    for optional in ("Levenshtein", "python-Levenshtein"):
        try:
            importlib.import_module(optional.replace("-", "_"))
            args.append(f"--hidden-import={optional}")
            break
        except ImportError:
            pass

    if icon_arg:
        args.insert(4, f"--icon={icon_arg}")

    print("[BUILD] Running PyInstaller with arguments:")
    print("        " + " ".join(args))

    # Run PyInstaller
    pyinstaller_main = importlib.import_module("PyInstaller.__main__")
    pyinstaller_main.run(args)

    # Verify the exe was actually produced
    exe_path = Path("dist") / "BrandEngine.exe"
    if not exe_path.exists():
        print(f"\n[FAIL] PyInstaller finished but {exe_path} was not created.")
        return 1

    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"\n[OK] Build complete! Executable created in 'dist' folder")
    print(f"     Location: {exe_path}")
    print(f"     Size    : {size_mb:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(build_windows_exe())