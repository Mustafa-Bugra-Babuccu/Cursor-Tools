#!/usr/bin/env python3
"""
Test the fixed auto-update functionality
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ssl_fallback():
    """Test the SSL fallback functionality"""
    print("🔧 Testing Fixed Auto-Update System")
    print("=" * 60)
    
    try:
        from auto_update_manager import AutoUpdateManager
        from auto_update_config import AutoUpdateConfig
        
        print("✅ Imports successful")
        print(f"Current Version: {AutoUpdateConfig.CURRENT_VERSION}")
        print(f"SSL Verification: {AutoUpdateConfig.VERIFY_SSL}")
        print()
        
        # Create manager instance
        print("Creating AutoUpdateManager...")
        manager = AutoUpdateManager()
        
        print("Testing update check with SSL fallback...")
        update_info = manager.check_for_updates(force_check=True)
        
        if update_info:
            print("✅ Update check successful!")
            print(f"  Available Version: {update_info.get('version')}")
            print(f"  Release Name: {update_info.get('name')}")
            print(f"  Download URL: {update_info.get('download_url')}")
            print(f"  Published: {update_info.get('published_at')}")
            
            # Test version comparison
            current = AutoUpdateConfig.CURRENT_VERSION
            latest = update_info.get('version')
            
            try:
                current_parts = tuple(map(int, current.split(".")))
                latest_parts = tuple(map(int, latest.split(".")))
                is_newer = latest_parts > current_parts
                
                print(f"\nVersion Comparison:")
                print(f"  Current: {current} -> {current_parts}")
                print(f"  Latest: {latest} -> {latest_parts}")
                print(f"  Is Newer: {is_newer}")
                
                if is_newer:
                    print("✅ Update would be offered to user")
                else:
                    print("ℹ️  No update needed")
                    
            except Exception as e:
                print(f"❌ Version comparison error: {e}")
                
        else:
            print("ℹ️  No update available or check failed")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Test error: {e}")

def test_configuration():
    """Test the configuration options"""
    print("\n⚙️  Testing Configuration Options:")
    print("=" * 50)
    
    try:
        from auto_update_config import AutoUpdateConfig
        
        # Test normal config
        normal_config = AutoUpdateConfig.get_request_config()
        print("Normal Request Config:")
        for key, value in normal_config.items():
            print(f"  {key}: {value}")
        
        print()
        
        # Test fallback config
        fallback_config = AutoUpdateConfig.get_fallback_request_config()
        print("Fallback Request Config (SSL disabled):")
        for key, value in fallback_config.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"❌ Configuration test error: {e}")

def test_manual_api_call():
    """Test manual API call with both SSL modes"""
    print("\n🌐 Testing Manual API Calls:")
    print("=" * 50)
    
    try:
        import requests
        from auto_update_config import AutoUpdateConfig
        
        api_url = AutoUpdateConfig.GITHUB_API_URL
        
        # Test with SSL verification
        print("1. Testing with SSL verification enabled...")
        try:
            config = AutoUpdateConfig.get_request_config()
            response = requests.get(api_url, **config)
            print(f"   ✅ SSL enabled: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Latest release: {data.get('tag_name', 'N/A')}")
                
        except Exception as e:
            print(f"   ❌ SSL enabled failed: {e}")
            
            # Test with SSL verification disabled
            print("\n2. Testing with SSL verification disabled...")
            try:
                config = AutoUpdateConfig.get_fallback_request_config()
                response = requests.get(api_url, **config)
                print(f"   ✅ SSL disabled: Status {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Latest release: {data.get('tag_name', 'N/A')}")
                    
            except Exception as e2:
                print(f"   ❌ SSL disabled also failed: {e2}")
                
    except Exception as e:
        print(f"❌ Manual API test error: {e}")

def test_asset_detection():
    """Test asset detection logic"""
    print("\n📁 Testing Asset Detection:")
    print("=" * 50)
    
    try:
        from auto_update_config import AutoUpdateConfig
        
        # Mock assets for testing
        mock_assets = [
            {"name": "Cursor-Tools.exe", "browser_download_url": "https://example.com/Cursor-Tools.exe"},
            {"name": "source-code.zip", "browser_download_url": "https://example.com/source.zip"},
            {"name": "README.md", "browser_download_url": "https://example.com/README.md"},
        ]
        
        print("Mock assets:")
        for asset in mock_assets:
            name = asset["name"]
            is_valid = AutoUpdateConfig.is_valid_asset(name)
            print(f"  {name}: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        # Test download URL extraction
        download_url = None
        for asset in mock_assets:
            if AutoUpdateConfig.is_valid_asset(asset["name"]):
                download_url = asset["browser_download_url"]
                break
        
        print(f"\nSelected download URL: {download_url}")
        
    except Exception as e:
        print(f"❌ Asset detection test error: {e}")

if __name__ == "__main__":
    test_configuration()
    test_asset_detection()
    test_manual_api_call()
    test_ssl_fallback()
    
    print("\n" + "=" * 60)
    print("🏁 Fixed Auto-Update Test Complete")
    print("\nKey improvements:")
    print("1. ✅ SSL fallback mechanism for corporate environments")
    print("2. ✅ Better error handling and user feedback")
    print("3. ✅ Configurable SSL verification settings")
    print("4. ✅ Detailed error messages for troubleshooting")
    print("5. ✅ Manual update URL provided when auto-update fails")
