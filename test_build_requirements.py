#!/usr/bin/env python3
"""
Test script to verify all build requirements are met
"""

import os
import sys
from pathlib import Path

def test_build_requirements():
    """Test if all build requirements are satisfied"""
    print("🔍 Testing Build Requirements")
    print("=" * 50)

    script_dir = Path(__file__).parent.absolute()

    # Required files from build_script.py
    required_files = [
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
        "pro_features_manager.py",
        "pro_features.py",
        "auto_update_manager.py",
        "auto_update_config.py",
        "requirements.txt",
        "CHANGELOG.md",
        "LICENSE",
        "README.md"
    ]

    # Build configuration files
    build_files = [
        "build_script.py",
        "build_config.ini",
        "build.bat"
    ]

    print("📋 Checking required application files...")
    missing_files = []
    for file in required_files:
        file_path = script_dir / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)

    print(f"\n🔧 Checking build system files...")
    missing_build_files = []
    for file in build_files:
        file_path = script_dir / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_build_files.append(file)

    print(f"\n📦 Checking Python dependencies...")
    try:
        import rich
        print(f"✅ rich - INSTALLED")
    except ImportError:
        print("❌ rich - NOT INSTALLED")

    try:
        import colorama
        print(f"✅ colorama {colorama.__version__}")
    except ImportError:
        print("❌ colorama - NOT INSTALLED")

    try:
        import requests
        print(f"✅ requests {requests.__version__}")
    except ImportError:
        print("❌ requests - NOT INSTALLED")

    try:
        import urllib3
        print(f"✅ urllib3 {urllib3.__version__}")
    except ImportError:
        print("❌ urllib3 - NOT INSTALLED")

    print(f"\n🐍 Python version: {sys.version}")

    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)

    if missing_files:
        print(f"❌ Missing application files: {len(missing_files)}")
        for file in missing_files:
            print(f"   - {file}")
    else:
        print(f"✅ All {len(required_files)} application files found")

    if missing_build_files:
        print(f"❌ Missing build files: {len(missing_build_files)}")
        for file in missing_build_files:
            print(f"   - {file}")
    else:
        print(f"✅ All {len(build_files)} build files found")

    if sys.version_info >= (3, 8):
        print("✅ Python version is compatible")
    else:
        print("❌ Python 3.8+ required")

    # Test imports
    print(f"\n🧪 Testing critical imports...")
    try:
        from main import CursorToolsApp
        print("✅ Main application import successful")
    except Exception as e:
        print(f"❌ Main application import failed: {e}")

    try:
        from auto_update_manager import AutoUpdateManager
        print("✅ Auto-update manager import successful")
    except Exception as e:
        print(f"❌ Auto-update manager import failed: {e}")

    try:
        from pro_features_manager import ProUIFeaturesManager
        print("✅ Pro features manager import successful")
    except Exception as e:
        print(f"❌ Pro features manager import failed: {e}")

    # Overall status
    total_issues = len(missing_files) + len(missing_build_files)
    if total_issues == 0 and sys.version_info >= (3, 8):
        print(f"\n🎉 BUILD READY - All requirements satisfied!")
        print(f"💡 You can now run: python build_script.py")
        return True
    else:
        print(f"\n⚠️  BUILD NOT READY - {total_issues} issues found")
        print(f"💡 Fix the issues above before building")
        return False

if __name__ == "__main__":
    success = test_build_requirements()
    sys.exit(0 if success else 1)
