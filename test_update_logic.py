#!/usr/bin/env python3
"""
Test script to verify auto-update logic with mock data
"""

import json
from auto_update_config import AutoUpdateConfig

def test_version_comparison():
    """Test version comparison logic"""
    print("🔄 Testing Version Comparison Logic:")
    print("=" * 50)
    
    test_cases = [
        ("1.2.0", "1.1.0", True),   # Newer version
        ("1.1.1", "1.1.0", True),   # Patch update
        ("2.0.0", "1.1.0", True),   # Major update
        ("1.1.0", "1.1.0", False),  # Same version
        ("1.0.0", "1.1.0", False),  # Older version
        ("1.1.0", "1.2.0", False),  # Current is older
    ]
    
    for latest, current, expected in test_cases:
        try:
            latest_parts = tuple(map(int, latest.split(".")))
            current_parts = tuple(map(int, current.split(".")))
            result = latest_parts > current_parts
            
            status = "✅" if result == expected else "❌"
            print(f"{status} {latest} > {current} = {result} (expected: {expected})")
            
        except Exception as e:
            print(f"❌ Error comparing {latest} vs {current}: {e}")

def test_asset_validation():
    """Test asset name validation"""
    print("\n🧪 Testing Asset Validation:")
    print("=" * 50)
    
    test_assets = [
        ("Cursor-Tools.exe", True),
        ("cursor-tools.exe", True),
        ("Cursor-Tools-v1.1.0.exe", True),
        ("cursor-tools-v1.1.0.exe", True),
        ("Cursor-Tools-1.1.0.exe", True),
        ("SomeOtherApp.exe", True),  # Current logic accepts any .exe
        ("Cursor-Tools.zip", False),
        ("README.md", False),
        ("setup.msi", False),
    ]
    
    for asset_name, expected in test_assets:
        result = AutoUpdateConfig.is_valid_asset(asset_name)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{asset_name}' -> {result} (expected: {expected})")

def test_mock_release_processing():
    """Test processing of mock release data"""
    print("\n📦 Testing Release Data Processing:")
    print("=" * 50)
    
    # Mock release data that simulates different scenarios
    mock_releases = [
        {
            "name": "Valid release with assets",
            "data": {
                "tag_name": "v1.2.0",
                "name": "Version 1.2.0",
                "published_at": "2025-05-29T12:00:00Z",
                "draft": False,
                "prerelease": False,
                "assets": [
                    {
                        "name": "Cursor-Tools.exe",
                        "size": 15728640,
                        "browser_download_url": "https://github.com/test/repo/releases/download/v1.2.0/Cursor-Tools.exe"
                    }
                ]
            }
        },
        {
            "name": "Release without 'v' prefix",
            "data": {
                "tag_name": "1.2.0",
                "name": "Version 1.2.0",
                "published_at": "2025-05-29T12:00:00Z",
                "draft": False,
                "prerelease": False,
                "assets": [
                    {
                        "name": "cursor-tools-v1.2.0.exe",
                        "size": 15728640,
                        "browser_download_url": "https://github.com/test/repo/releases/download/1.2.0/cursor-tools-v1.2.0.exe"
                    }
                ]
            }
        },
        {
            "name": "Release with no assets",
            "data": {
                "tag_name": "v1.2.0",
                "name": "Version 1.2.0",
                "published_at": "2025-05-29T12:00:00Z",
                "draft": False,
                "prerelease": False,
                "assets": []
            }
        },
        {
            "name": "Same version as current",
            "data": {
                "tag_name": "v1.1.0",
                "name": "Version 1.1.0",
                "published_at": "2025-05-29T10:00:00Z",
                "draft": False,
                "prerelease": False,
                "assets": [
                    {
                        "name": "Cursor-Tools.exe",
                        "size": 15728640,
                        "browser_download_url": "https://github.com/test/repo/releases/download/v1.1.0/Cursor-Tools.exe"
                    }
                ]
            }
        }
    ]
    
    current_version = AutoUpdateConfig.CURRENT_VERSION
    
    for test_case in mock_releases:
        print(f"\n--- {test_case['name']} ---")
        release_data = test_case['data']
        
        # Extract version
        latest_version = release_data.get("tag_name", "").lstrip("v")
        print(f"Tag Name: {release_data.get('tag_name')}")
        print(f"Extracted Version: '{latest_version}'")
        print(f"Current Version: {current_version}")
        
        # Test version comparison
        try:
            latest_parts = tuple(map(int, latest_version.split(".")))
            current_parts = tuple(map(int, current_version.split(".")))
            is_newer = latest_parts > current_parts
            print(f"Is Newer: {is_newer}")
        except Exception as e:
            print(f"Version comparison error: {e}")
            is_newer = False
        
        # Test asset processing
        assets = release_data.get('assets', [])
        print(f"Assets Count: {len(assets)}")
        
        if assets:
            for i, asset in enumerate(assets, 1):
                asset_name = asset.get('name', 'Unknown')
                is_valid = AutoUpdateConfig.is_valid_asset(asset_name)
                print(f"  Asset {i}: {asset_name} (valid: {is_valid})")
        
        # Test download URL extraction
        download_url = None
        for asset in assets:
            asset_name = asset.get("name", "")
            if AutoUpdateConfig.is_valid_asset(asset_name):
                download_url = asset.get("browser_download_url")
                break
        
        print(f"Download URL: {download_url or 'Not found'}")
        
        # Simulate update decision
        if is_newer and download_url:
            print("✅ Update would be offered")
        elif not is_newer:
            print("ℹ️  No update needed (same or older version)")
        elif not download_url:
            print("⚠️  Update available but no valid download found")
        else:
            print("❌ Update check would fail")

def test_configuration():
    """Test configuration values"""
    print("\n⚙️  Testing Configuration:")
    print("=" * 50)
    
    print(f"Current Version: {AutoUpdateConfig.CURRENT_VERSION}")
    print(f"GitHub Owner: {AutoUpdateConfig.GITHUB_OWNER}")
    print(f"GitHub Repo: {AutoUpdateConfig.GITHUB_REPO}")
    print(f"API URL: {AutoUpdateConfig.GITHUB_API_URL}")
    print(f"Repo URL: {AutoUpdateConfig.GITHUB_REPO_URL}")
    print(f"Force Update: {AutoUpdateConfig.FORCE_UPDATE_POLICY}")
    print(f"Check on Startup: {AutoUpdateConfig.CHECK_ON_STARTUP}")
    print(f"Timeout: {AutoUpdateConfig.UPDATE_CHECK_TIMEOUT}s")
    
    # Test version format validation
    print(f"\nVersion Format Valid: {AutoUpdateConfig.validate_version_format(AutoUpdateConfig.CURRENT_VERSION)}")
    
    # Test headers
    headers = AutoUpdateConfig.get_api_headers()
    print(f"API Headers: {headers}")

if __name__ == "__main__":
    print("🔍 CURSOR-TOOLS AUTO-UPDATE LOGIC TEST")
    print("=" * 60)
    
    test_configuration()
    test_version_comparison()
    test_asset_validation()
    test_mock_release_processing()
    
    print("\n" + "=" * 60)
    print("🏁 Test Complete")
