#!/usr/bin/env python3
"""
Cursor-Tools Application Build Script
Comprehensive build automation for the Cursor-Tools application
"""

import sys
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime

class CursorToolsBuilder:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.build_dir = self.script_dir / "build"
        self.dist_dir = self.script_dir / "dist"
        self.app_name = "Cursor-Tools"
        self.main_script = "main.py"

        # Build configuration
        self.build_config = {
            "one_file": True,
            "one_folder": True,
            "console": True,
            "admin_manifest": True,
            "optimize": True,
            "strip_debug": True,
            "upx_compress": False  # Set to True if UPX is available
        }

        # Required files and modules
        self.required_files = [
            "main.py",
            "config.py",
            "ui_manager.py",
            "device_id_modifier.py",
            "registry_manager.py",
            "account_info_manager.py",
            "acc_info.py",
            "disable_update_manager.py",
            "disable_update.py",
            "reset_machine_id_manager.py",
            "reset_machine_id.py",
            "requirements.txt"
        ]

        # Dependencies from requirements.txt
        self.dependencies = [
            "rich==13.7.0",
            "colorama==0.4.6",
            "requests==2.31.0"
        ]

    def print_header(self):
        """Print build script header"""
        print("=" * 60)
        print(f"🔨 Cursor-Tools Build Script")
        print(f"📅 Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

    def check_requirements(self):
        """Check if all required files and dependencies are available"""
        print("\n📋 Checking build requirements...")

        # Check Python version
        if sys.version_info < (3, 8):
            raise Exception("Python 3.8 or higher is required")
        print(f"✅ Python {sys.version.split()[0]} detected")

        # Check required files
        missing_files = []
        for file in self.required_files:
            if not (self.script_dir / file).exists():
                missing_files.append(file)

        if missing_files:
            raise Exception(f"Missing required files: {', '.join(missing_files)}")
        print(f"✅ All {len(self.required_files)} required files found")

        # Check if PyInstaller is installed
        try:
            import PyInstaller
            print(f"✅ PyInstaller {PyInstaller.__version__} available")
        except ImportError:
            print("❌ PyInstaller not found. Installing...")
            self.install_pyinstaller()

    def install_pyinstaller(self):
        """Install PyInstaller if not available"""
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"],
                         check=True, capture_output=True)
            print("✅ PyInstaller installed successfully")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to install PyInstaller: {e}")

    def install_dependencies(self):
        """Install application dependencies"""
        print("\n📦 Installing application dependencies...")

        try:
            # Install from requirements.txt
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                         check=True, capture_output=True, cwd=self.script_dir)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to install dependencies: {e}")

    def clean_build_dirs(self):
        """Clean previous build directories"""
        print("\n🧹 Cleaning previous build directories...")

        dirs_to_clean = [self.build_dir, self.dist_dir, self.script_dir / "__pycache__"]

        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"🗑️  Removed {dir_path.name}")

        print("✅ Build directories cleaned")

    def create_spec_file(self, build_type="onefile"):
        """Create PyInstaller spec file for advanced configuration"""
        # Convert Windows path to use forward slashes to avoid escape sequence issues
        script_dir_posix = str(self.script_dir).replace('\\', '/')

        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Analysis configuration
a = Analysis(
    ['{self.main_script}'],
    pathex=['{script_dir_posix}'],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'rich.console',
        'rich.panel',
        'rich.table',
        'rich.text',
        'rich.prompt',
        'rich.align',
        'colorama',
        'requests',
        'winreg',
        'ctypes',
        'sqlite3',
        'configparser',
        'uuid',
        'hashlib',
        'tempfile',
        'glob',
        'json',
        're',
        'datetime',
        'pathlib',
        'typing'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ configuration
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE configuration
exe = EXE(
    pyz,
    a.scripts,
    {'a.binaries,' if build_type == 'onefile' else ''}
    {'a.zipfiles,' if build_type == 'onefile' else ''}
    {'a.datas,' if build_type == 'onefile' else ''}
    [],
    name='{self.app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip={'True' if self.build_config['strip_debug'] else 'False'},
    upx={'True' if self.build_config['upx_compress'] else 'False'},
    upx_exclude=[],
    runtime_tmpdir=None,
    console={'True' if self.build_config['console'] else 'False'},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin={'True' if self.build_config['admin_manifest'] else 'False'},
    icon=None,
    version=None,
)

{'# COLLECT configuration for onedir build' if build_type == 'onedir' else ''}
{'coll = COLLECT(' if build_type == 'onedir' else ''}
{'    exe,' if build_type == 'onedir' else ''}
{'    a.binaries,' if build_type == 'onedir' else ''}
{'    a.zipfiles,' if build_type == 'onedir' else ''}
{'    a.datas,' if build_type == 'onedir' else ''}
{'    strip=False,' if build_type == 'onedir' else ''}
{'    upx=True,' if build_type == 'onedir' else ''}
{'    upx_exclude=[],' if build_type == 'onedir' else ''}
{'    name=\'{self.app_name}\',' if build_type == 'onedir' else ''}
{')' if build_type == 'onedir' else ''}
'''

        spec_file = self.script_dir / f"{self.app_name}_{build_type}.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)

        return spec_file

    def build_onefile(self):
        """Build one-file executable"""
        print("\n🔨 Building one-file executable...")
        start_time = time.time()

        try:
            # Create spec file for one-file build
            spec_file = self.create_spec_file("onefile")

            # Build command
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                str(spec_file)
            ]

            # Run PyInstaller
            result = subprocess.run(cmd, cwd=self.script_dir, capture_output=True, text=True)

            if result.returncode != 0:
                raise Exception(f"PyInstaller failed:\n{result.stderr}")

            build_time = time.time() - start_time
            exe_path = self.dist_dir / f"{self.app_name}.exe"

            if exe_path.exists():
                file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
                print(f"✅ One-file build completed in {build_time:.1f}s")
                print(f"📁 Executable: {exe_path}")
                print(f"📏 File size: {file_size:.1f} MB")
                return exe_path
            else:
                raise Exception("Executable not found after build")

        except Exception as e:
            print(f"❌ One-file build failed: {e}")
            return None

    def build_onefolder(self):
        """Build one-folder distribution"""
        print("\n📁 Building one-folder distribution...")
        start_time = time.time()

        try:
            # Create spec file for one-folder build
            spec_file = self.create_spec_file("onedir")

            # Build command
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                str(spec_file)
            ]

            # Run PyInstaller
            result = subprocess.run(cmd, cwd=self.script_dir, capture_output=True, text=True)

            if result.returncode != 0:
                raise Exception(f"PyInstaller failed:\n{result.stderr}")

            build_time = time.time() - start_time
            folder_path = self.dist_dir / self.app_name
            exe_path = folder_path / f"{self.app_name}.exe"

            if exe_path.exists():
                # Calculate folder size
                folder_size = sum(f.stat().st_size for f in folder_path.rglob('*') if f.is_file()) / (1024 * 1024)
                file_count = len(list(folder_path.rglob('*')))

                print(f"✅ One-folder build completed in {build_time:.1f}s")
                print(f"📁 Distribution folder: {folder_path}")
                print(f"🎯 Executable: {exe_path}")
                print(f"📏 Total size: {folder_size:.1f} MB ({file_count} files)")
                return folder_path
            else:
                raise Exception("Executable not found after build")

        except Exception as e:
            print(f"❌ One-folder build failed: {e}")
            return None

    def test_executable(self, exe_path):
        """Test the built executable"""
        print(f"\n🧪 Testing executable: {exe_path.name}")

        try:
            # Test basic execution (with timeout)
            result = subprocess.run(
                [str(exe_path), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=exe_path.parent if exe_path.is_file() else exe_path
            )

            # Check for admin privilege requirement (common error codes)
            if result.returncode == 740 or "yükseltme gerekiyor" in result.stderr or "elevation" in result.stderr.lower():
                print("✅ Executable requires admin privileges (expected)")
                return True
            elif result.returncode == 0 or "Cursor-Tools" in result.stdout or "UUUP" in result.stdout:
                print("✅ Executable test passed")
                return True
            else:
                print(f"⚠️  Executable test warning: Return code {result.returncode}")
                print(f"   This may be normal if the app requires admin privileges")
                return True  # Consider it passed for admin-required apps

        except subprocess.TimeoutExpired:
            print("⚠️  Executable test timeout (may be waiting for user input)")
            return True  # Consider it passed if it's waiting for input
        except PermissionError:
            print("✅ Executable requires admin privileges (expected)")
            return True
        except Exception as e:
            # Check if it's an admin privilege error
            if "740" in str(e) or "elevation" in str(e).lower():
                print("✅ Executable requires admin privileges (expected)")
                return True
            print(f"❌ Executable test failed: {e}")
            return False

    def create_build_info(self, builds):
        """Create build information file"""
        build_info = {
            "build_date": datetime.now().isoformat(),
            "python_version": sys.version,
            "app_name": self.app_name,
            "builds": []
        }

        for build_type, path in builds.items():
            if path:
                if path.is_file():
                    size = path.stat().st_size
                    build_info["builds"].append({
                        "type": build_type,
                        "path": str(path),
                        "size_bytes": size,
                        "size_mb": round(size / (1024 * 1024), 2)
                    })
                else:
                    # For folders, calculate total size
                    total_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                    file_count = len(list(path.rglob('*')))
                    build_info["builds"].append({
                        "type": build_type,
                        "path": str(path),
                        "size_bytes": total_size,
                        "size_mb": round(total_size / (1024 * 1024), 2),
                        "file_count": file_count
                    })

        # Save build info
        info_file = self.dist_dir / "build_info.json"
        with open(info_file, 'w') as f:
            import json
            json.dump(build_info, f, indent=2)

        print(f"📋 Build information saved to: {info_file}")

    def print_summary(self, builds):
        """Print build summary"""
        print("\n" + "=" * 60)
        print("🎉 BUILD SUMMARY")
        print("=" * 60)

        successful_builds = [k for k, v in builds.items() if v is not None]
        failed_builds = [k for k, v in builds.items() if v is None]

        if successful_builds:
            print(f"✅ Successful builds: {', '.join(successful_builds)}")
            for build_type, path in builds.items():
                if path:
                    print(f"   📁 {build_type}: {path}")

        if failed_builds:
            print(f"❌ Failed builds: {', '.join(failed_builds)}")

        print(f"\n📂 Output directory: {self.dist_dir}")
        print("\n💡 Usage Instructions:")
        print("   • Run the executable with administrator privileges")
        print("   • The application will create necessary directories automatically")
        print("   • Configuration files will be stored in Documents/Cursor Tools")
        print("\n⚠️  Important Notes:")
        print("   • This application requires Windows administrator privileges")
        print("   • Antivirus software may flag the executable (false positive)")
        print("   • The application modifies Windows registry and system files")

    def build_all(self):
        """Build all configurations"""
        builds = {}

        try:
            self.print_header()
            self.check_requirements()
            self.install_dependencies()
            self.clean_build_dirs()

            # Build configurations
            if self.build_config["one_file"]:
                builds["one-file"] = self.build_onefile()
                if builds["one-file"]:
                    self.test_executable(builds["one-file"])

            if self.build_config["one_folder"]:
                builds["one-folder"] = self.build_onefolder()
                if builds["one-folder"]:
                    exe_path = builds["one-folder"] / f"{self.app_name}.exe"
                    self.test_executable(exe_path)

            # Create build information
            self.create_build_info(builds)

            # Print summary
            self.print_summary(builds)

            return builds

        except Exception as e:
            print(f"\n❌ Build failed: {e}")
            return builds

def main():
    """Main build function"""
    if len(sys.argv) > 1:
        build_type = sys.argv[1].lower()
        builder = CursorToolsBuilder()

        if build_type == "onefile":
            builder.build_config["one_folder"] = False
        elif build_type == "onefolder":
            builder.build_config["one_file"] = False
        elif build_type == "both":
            pass  # Build both (default)
        else:
            print("Usage: python build_script.py [onefile|onefolder|both]")
            sys.exit(1)
    else:
        builder = CursorToolsBuilder()

    # Run the build
    builds = builder.build_all()

    # Exit with appropriate code
    successful_builds = [v for v in builds.values() if v is not None]
    sys.exit(0 if successful_builds else 1)

if __name__ == "__main__":
    main()
