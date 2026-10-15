"""
Cross-platform build script for Brand Engine
Creates executables for Windows, macOS, and Linux
"""
import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

class BrandEngineBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.installer_dir = self.project_root / "installer"
        
    def clean(self):
        """Clean previous builds"""
        for dir_path in [self.dist_dir, self.build_dir, self.installer_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
        self.dist_dir.mkdir(exist_ok=True)
        self.installer_dir.mkdir(exist_ok=True)
    
    def install_dependencies(self):
        """Install required packages"""
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        # Install PyInstaller
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        
        # Install additional packages for specific platforms
        if platform.system() == "Windows":
            subprocess.run([sys.executable, "-m", "pip", "install", "pypiwin32"], check=True)
    
    def build_exe(self):
        """Build executable using PyInstaller"""
        system = platform.system()
        
        # PyInstaller arguments
        args = [
            sys.executable, "-m", "PyInstaller",
            "main.py",
            "--name=BrandEngine",
            "--onefile",
            "--windowed" if system == "Windows" else "--console",
            f"--icon=assets/icon.ico" if system == "Windows" else "",
            "--add-data=assets:assets",
            "--add-data=database:database",
            "--hidden-import=customtkinter",
            "--hidden-import=PIL",
            "--hidden-import=whois",
            "--hidden-import=requests",
            "--hidden-import=python-Levenshtein",
            "--hidden-import=openpyxl",
            "--hidden-import=pandas",
            "--collect-all=customtkinter",
            "--collect-all=PIL",
            "--noconfirm",
        ]
        
        # Filter out empty args
        args = [arg for arg in args if arg]
        
        # Run PyInstaller
        subprocess.run(args, check=True)
        
        # Get output filename
        if system == "Windows":
            exe_name = "BrandEngine.exe"
        elif system == "Darwin":
            exe_name = "BrandEngine"
        else:  # Linux
            exe_name = "BrandEngine"
        
        return self.dist_dir / exe_name
    
    def create_installer(self, exe_path):
        """Create platform-specific installer"""
        system = platform.system()
        
        if system == "Windows":
            self._create_windows_installer(exe_path)
        elif system == "Darwin":
            self._create_macos_app(exe_path)
        else:
            self._create_linux_package(exe_path)
    
    def _create_windows_installer(self, exe_path):
        """Create Windows installer"""
        # Check if Inno Setup is available
        inno_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        ]
        
        inno_path = None
        for path in inno_paths:
            if Path(path).exists():
                inno_path = path
                break
        
        if inno_path:
            # Generate Inno Setup script
            iss_content = self._generate_inno_script()
            iss_path = self.project_root / "BrandEngine.iss"
            iss_path.write_text(iss_content)
            
            # Run Inno Setup
            subprocess.run([inno_path, str(iss_path)], check=True)
            print(f"✅ Windows installer created in {self.installer_dir}")
        else:
            # Fallback to creating a ZIP file
            self._create_zip_package(exe_path)
    
    def _generate_inno_script(self):
        """Generate Inno Setup script content"""
        return """
[Setup]
AppId={{F8B3F1E8-5E3A-4B8C-9D1E-2F4A6B8C0D1E}}
AppName=Brand Engine
AppVersion=1.0.0
AppPublisher=Yavotu Team
DefaultDirName={pf64}\\BrandEngine
DefaultGroupName=BrandEngine
OutputDir=installer
OutputBaseFilename=BrandEngine_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\\BrandEngine.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\\*"; DestDir: "{app}\\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "database\\*"; DestDir: "{app}\\database"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\\Brand Engine"; Filename: "{app}\\BrandEngine.exe"
Name: "{group}\\{cm:UninstallProgram,Brand Engine}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\Brand Engine"; Filename: "{app}\\BrandEngine.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\\BrandEngine.exe"; Description: "{cm:LaunchProgram,Brand Engine}"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
"""
    
    def _create_macos_app(self, exe_path):
        """Create macOS application bundle"""
        app_name = "BrandEngine.app"
        app_path = self.installer_dir / app_name
        
        # Create app bundle structure
        contents_path = app_path / "Contents"
        macos_path = contents_path / "MacOS"
        resources_path = contents_path / "Resources"
        
        for path in [contents_path, macos_path, resources_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Copy executable
        shutil.copy(exe_path, macos_path / "BrandEngine")
        os.chmod(macos_path / "BrandEngine", 0o755)
        
        # Copy resources
        for src in ["assets", "database"]:
            src_path = self.project_root / src
            if src_path.exists():
                dst_path = resources_path / src
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
        
        # Create Info.plist
        plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Brand Engine</string>
    <key>CFBundleDisplayName</key>
    <string>Brand Engine</string>
    <key>CFBundleIdentifier</key>
    <string>com.brandengine.app</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleExecutable</key>
    <string>BrandEngine</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
</dict>
</plist>"""
        (contents_path / "Info.plist").write_text(plist_content)
        
        print(f"✅ macOS app created in {app_path}")
        print("📦 To create a DMG, use: create-dmg --volname 'BrandEngine' BrandEngine.dmg BrandEngine.app")
    
    def _create_linux_package(self, exe_path):
        """Create Linux package"""
        # Create AppImage directory structure
        app_dir = self.installer_dir / "BrandEngine.AppDir"
        usr_dir = app_dir / "usr"
        bin_dir = usr_dir / "bin"
        
        for path in [usr_dir, bin_dir]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Copy executable
        shutil.copy(exe_path, bin_dir / "brandengine")
        os.chmod(bin_dir / "brandengine", 0o755)
        
        # Create .desktop file
        desktop_content = """[Desktop Entry]
Name=Brand Engine
Comment=AI-Powered Brand Name Generator
Exec=brandengine
Icon=brandengine
Terminal=false
Type=Application
Categories=Utility;Development;
"""
        (app_dir / "brandengine.desktop").write_text(desktop_content)
        
        # Create AppRun script
        apprun_content = """#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin/:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib/:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/brandengine" "$@"
"""
        (app_dir / "AppRun").write_text(apprun_content)
        os.chmod(app_dir / "AppRun", 0o755)
        
        print(f"✅ Linux AppDir created in {app_dir}")
        print("📦 To create AppImage, use: appimagetool BrandEngine.AppDir")
    
    def _create_zip_package(self, exe_path):
        """Create ZIP package as fallback"""
        zip_path = self.installer_dir / "BrandEngine.zip"
        shutil.make_archive(
            str(zip_path).replace('.zip', ''),
            'zip',
            self.dist_dir
        )
        print(f"✅ ZIP package created in {zip_path}")
    
    def build(self):
        """Main build process"""
        print("🚀 Building Brand Engine")
        print("=" * 50)
        
        # Clean previous builds
        self.clean()
        
        # Install dependencies
        print("\n📦 Installing dependencies...")
        self.install_dependencies()
        
        # Build executable
        print("\n🔨 Building executable...")
        exe_path = self.build_exe()
        
        # Create installer
        print("\n📦 Creating installer...")
        self.create_installer(exe_path)
        
        print("\n✅ Build complete!")
        print(f"📁 Output directory: {self.installer_dir}")

if __name__ == "__main__":
    builder = BrandEngineBuilder()
    builder.build()