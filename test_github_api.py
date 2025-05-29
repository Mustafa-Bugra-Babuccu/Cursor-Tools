#!/usr/bin/env python3
"""
Test GitHub API connectivity and response
"""

import requests
import json
import sys
from auto_update_config import AutoUpdateConfig

def test_basic_connectivity():
    """Test basic internet connectivity"""
    print("🌐 Testing Basic Internet Connectivity:")
    print("=" * 50)
    
    test_urls = [
        "https://httpbin.org/get",
        "https://api.github.com",
        "https://github.com"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {url} - Status: {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"⏰ {url} - Timeout")
        except requests.exceptions.ConnectionError:
            print(f"❌ {url} - Connection Error")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")

def test_github_api_direct():
    """Test GitHub API directly"""
    print("\n📡 Testing GitHub API Direct:")
    print("=" * 50)
    
    api_url = AutoUpdateConfig.GITHUB_API_URL
    headers = AutoUpdateConfig.get_api_headers()
    
    print(f"URL: {api_url}")
    print(f"Headers: {headers}")
    print()
    
    try:
        print("Making request...")
        response = requests.get(api_url, headers=headers, timeout=15)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"Content-Length: {response.headers.get('content-length', 'N/A')}")
        
        if 'x-ratelimit-remaining' in response.headers:
            print(f"Rate Limit Remaining: {response.headers['x-ratelimit-remaining']}")
        
        if response.status_code == 200:
            print("✅ API Request Successful!")
            
            try:
                data = response.json()
                print(f"\nRelease Info:")
                print(f"  Tag: {data.get('tag_name', 'N/A')}")
                print(f"  Name: {data.get('name', 'N/A')}")
                print(f"  Published: {data.get('published_at', 'N/A')}")
                print(f"  Draft: {data.get('draft', 'N/A')}")
                print(f"  Prerelease: {data.get('prerelease', 'N/A')}")
                print(f"  Assets: {len(data.get('assets', []))}")
                
                # Show assets
                assets = data.get('assets', [])
                if assets:
                    print(f"\nAssets:")
                    for i, asset in enumerate(assets, 1):
                        name = asset.get('name', 'Unknown')
                        size = asset.get('size', 0)
                        url = asset.get('browser_download_url', 'N/A')
                        print(f"  {i}. {name} ({size:,} bytes)")
                        print(f"     URL: {url}")
                else:
                    print("\n⚠️  No assets found!")
                
                # Test version extraction and comparison
                tag_name = data.get('tag_name', '')
                latest_version = tag_name.lstrip('v')
                current_version = AutoUpdateConfig.CURRENT_VERSION
                
                print(f"\nVersion Comparison:")
                print(f"  Tag Name: '{tag_name}'")
                print(f"  Extracted: '{latest_version}'")
                print(f"  Current: '{current_version}'")
                
                try:
                    latest_parts = tuple(map(int, latest_version.split(".")))
                    current_parts = tuple(map(int, current_version.split(".")))
                    is_newer = latest_parts > current_parts
                    print(f"  Is Newer: {is_newer}")
                    
                    if is_newer:
                        print("✅ Update should be detected!")
                    else:
                        print("ℹ️  No update needed")
                        
                except Exception as e:
                    print(f"❌ Version parsing error: {e}")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print(f"Raw response (first 500 chars): {response.text[:500]}")
                
        elif response.status_code == 404:
            print("❌ Repository not found!")
            print("Check if the repository exists and is public.")
            
        elif response.status_code == 403:
            print("❌ API rate limit exceeded or access forbidden!")
            print("Try again later or check authentication.")
            
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out!")
        print("Try increasing the timeout or check your connection.")
        
    except requests.exceptions.ConnectionError as e:
        print("❌ Connection error!")
        print(f"Details: {e}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_alternative_endpoints():
    """Test alternative GitHub endpoints"""
    print("\n🔄 Testing Alternative Endpoints:")
    print("=" * 50)
    
    base_url = f"https://api.github.com/repos/{AutoUpdateConfig.GITHUB_OWNER}/{AutoUpdateConfig.GITHUB_REPO}"
    
    endpoints = [
        f"{base_url}",  # Repository info
        f"{base_url}/releases",  # All releases
        f"{base_url}/releases/latest",  # Latest release (our main endpoint)
    ]
    
    headers = AutoUpdateConfig.get_api_headers()
    
    for endpoint in endpoints:
        print(f"\nTesting: {endpoint}")
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'releases' in endpoint and isinstance(data, list):
                    print(f"  Releases found: {len(data)}")
                    if data:
                        latest = data[0]
                        print(f"  Latest: {latest.get('tag_name', 'N/A')}")
                elif 'tag_name' in data:
                    print(f"  Tag: {data.get('tag_name', 'N/A')}")
                elif 'name' in data:
                    print(f"  Repo: {data.get('name', 'N/A')}")
                    
        except Exception as e:
            print(f"  Error: {e}")

def test_auto_update_manager():
    """Test the actual AutoUpdateManager"""
    print("\n🔧 Testing AutoUpdateManager:")
    print("=" * 50)
    
    try:
        from auto_update_manager import AutoUpdateManager
        
        print("Creating AutoUpdateManager instance...")
        manager = AutoUpdateManager()
        
        print(f"Current version: {manager.current_version}")
        print(f"API URL: {manager.github_api_url}")
        
        print("\nCalling check_for_updates()...")
        update_info = manager.check_for_updates(force_check=True)
        
        if update_info:
            print("✅ Update detected!")
            print(f"  Version: {update_info.get('version')}")
            print(f"  Name: {update_info.get('name')}")
            print(f"  Download URL: {update_info.get('download_url')}")
        else:
            print("ℹ️  No update detected or check failed")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔍 GITHUB API CONNECTIVITY TEST")
    print("=" * 60)
    
    test_basic_connectivity()
    test_github_api_direct()
    test_alternative_endpoints()
    test_auto_update_manager()
    
    print("\n" + "=" * 60)
    print("🏁 Test Complete")
    print("\nIf the GitHub API test fails, possible causes:")
    print("1. No internet connection")
    print("2. GitHub API rate limiting")
    print("3. Repository doesn't exist or is private")
    print("4. No releases published in the repository")
    print("5. Firewall blocking GitHub API access")
