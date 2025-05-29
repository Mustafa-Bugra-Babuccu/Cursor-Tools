#!/usr/bin/env python3
"""
Debug script for Cursor-Tools auto-update functionality
This script helps diagnose issues with the GitHub API integration and update detection
"""

import requests
import json
import sys
from datetime import datetime
from auto_update_config import AutoUpdateConfig

def test_github_api():
    """Test GitHub API connectivity and response"""
    print("=" * 60)
    print("🔍 CURSOR-TOOLS AUTO-UPDATE DIAGNOSTIC")
    print("=" * 60)
    print()
    
    # Test configuration
    print("📋 Configuration Check:")
    print(f"   Current Version: {AutoUpdateConfig.CURRENT_VERSION}")
    print(f"   GitHub Owner: {AutoUpdateConfig.GITHUB_OWNER}")
    print(f"   GitHub Repo: {AutoUpdateConfig.GITHUB_REPO}")
    print(f"   API URL: {AutoUpdateConfig.GITHUB_API_URL}")
    print(f"   Timeout: {AutoUpdateConfig.UPDATE_CHECK_TIMEOUT}s")
    print()
    
    # Test API headers
    print("📡 API Headers:")
    headers = AutoUpdateConfig.get_api_headers()
    for key, value in headers.items():
        print(f"   {key}: {value}")
    print()
    
    # Test GitHub API connectivity
    print("🌐 Testing GitHub API connectivity...")
    try:
        response = requests.get(
            AutoUpdateConfig.GITHUB_API_URL,
            headers=headers,
            timeout=AutoUpdateConfig.UPDATE_CHECK_TIMEOUT
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers:")
        for key, value in response.headers.items():
            if key.lower() in ['content-type', 'x-ratelimit-limit', 'x-ratelimit-remaining', 'x-ratelimit-reset']:
                print(f"     {key}: {value}")
        print()
        
        if response.status_code == 200:
            print("✅ API Request Successful!")
            
            # Parse response
            try:
                release_data = response.json()
                print()
                print("📦 Latest Release Information:")
                print(f"   Tag Name: {release_data.get('tag_name', 'N/A')}")
                print(f"   Name: {release_data.get('name', 'N/A')}")
                print(f"   Published At: {release_data.get('published_at', 'N/A')}")
                print(f"   Draft: {release_data.get('draft', 'N/A')}")
                print(f"   Prerelease: {release_data.get('prerelease', 'N/A')}")
                
                # Extract version
                latest_version = release_data.get("tag_name", "").lstrip("v")
                print(f"   Extracted Version: '{latest_version}'")
                
                # Test version comparison
                print()
                print("🔄 Version Comparison Test:")
                print(f"   Current: {AutoUpdateConfig.CURRENT_VERSION}")
                print(f"   Latest: {latest_version}")
                
                is_newer = test_version_comparison(latest_version, AutoUpdateConfig.CURRENT_VERSION)
                print(f"   Is Newer: {is_newer}")
                
                # Test assets
                print()
                print("📁 Release Assets:")
                assets = release_data.get('assets', [])
                if assets:
                    for i, asset in enumerate(assets, 1):
                        asset_name = asset.get('name', 'Unknown')
                        asset_size = asset.get('size', 0)
                        download_url = asset.get('browser_download_url', 'N/A')
                        is_valid = AutoUpdateConfig.is_valid_asset(asset_name)
                        
                        print(f"   Asset {i}:")
                        print(f"     Name: {asset_name}")
                        print(f"     Size: {asset_size:,} bytes ({asset_size / (1024*1024):.1f} MB)")
                        print(f"     Download URL: {download_url}")
                        print(f"     Valid Asset: {is_valid}")
                        print()
                else:
                    print("   ⚠️  No assets found in release!")
                
                # Test download URL extraction
                download_url = get_download_url(assets)
                print(f"📥 Download URL: {download_url or 'Not found'}")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parse Error: {e}")
                print(f"   Raw Response: {response.text[:500]}...")
                
        elif response.status_code == 403:
            print("❌ API Rate Limit Exceeded!")
            print("   Try again later or check if you need authentication.")
            
        elif response.status_code == 404:
            print("❌ Repository Not Found!")
            print("   Check if the repository name and owner are correct.")
            
        else:
            print(f"❌ API Request Failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print("❌ Request Timeout!")
        print("   Check your internet connection or increase timeout.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error!")
        print("   Check your internet connection.")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def test_version_comparison(latest: str, current: str) -> bool:
    """Test version comparison logic"""
    try:
        print(f"   Parsing '{latest}' -> ", end="")
        latest_parts = tuple(map(int, latest.split(".")))
        print(f"{latest_parts}")
        
        print(f"   Parsing '{current}' -> ", end="")
        current_parts = tuple(map(int, current.split(".")))
        print(f"{current_parts}")
        
        result = latest_parts > current_parts
        print(f"   Comparison: {latest_parts} > {current_parts} = {result}")
        return result
        
    except (ValueError, AttributeError) as e:
        print(f"   ❌ Version parsing error: {e}")
        return False

def get_download_url(assets: list) -> str:
    """Test download URL extraction"""
    for asset in assets:
        asset_name = asset.get("name", "")
        if AutoUpdateConfig.is_valid_asset(asset_name):
            return asset.get("browser_download_url")
    return None

def test_asset_validation():
    """Test asset name validation"""
    print()
    print("🧪 Asset Validation Tests:")
    
    test_names = [
        "Cursor-Tools.exe",
        "cursor-tools.exe", 
        "Cursor-Tools-v1.1.0.exe",
        "cursor-tools-v1.1.0.exe",
        "SomeOtherFile.exe",
        "Cursor-Tools.zip",
        "README.md"
    ]
    
    for name in test_names:
        is_valid = AutoUpdateConfig.is_valid_asset(name)
        print(f"   '{name}' -> {is_valid}")

if __name__ == "__main__":
    test_github_api()
    test_asset_validation()
    
    print()
    print("=" * 60)
    print("🏁 Diagnostic Complete")
    print("=" * 60)
