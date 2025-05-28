"""
Account Information Module for Cursor-Tools
Extracted and simplified from cursor_acc_info.py
"""

import os
import json
import requests
import sqlite3
from typing import Dict, Optional
import logging
import re
from config import config

# Setup logger - only show errors by default
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress urllib3 debug messages
logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

# Enable debug logging if environment variable is set
if os.environ.get('CURSOR_DEBUG', '').lower() in ('1', 'true', 'yes'):
    logger.setLevel(logging.DEBUG)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.DEBUG)

class CursorConfig:
    """Cursor Configuration"""
    NAME_LOWER = "cursor"
    NAME_CAPITALIZE = "Cursor"
    BASE_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

class CursorUsageManager:
    """Cursor Usage Manager"""

    @staticmethod
    def get_proxy():
        """Get proxy settings"""
        proxy = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
        if proxy:
            return {"http": proxy, "https": proxy}
        return None

    @staticmethod
    def get_usage(token: str) -> Optional[Dict]:
        """Get usage information"""
        url = f"https://www.{CursorConfig.NAME_LOWER}.com/api/usage"
        headers = CursorConfig.BASE_HEADERS.copy()

        # Try multiple cookie formats
        cookie_formats = [
            f"Workos{CursorConfig.NAME_CAPITALIZE}SessionToken=user_01OOOOOOOOOOOOOOOOOOOOOOOO%3A%3A{token}",
            f"WorkosCursorSessionToken={token}",
            f"session_token={token}",
            f"auth_token={token}"
        ]

        for cookie_format in cookie_formats:
            headers_copy = headers.copy()
            headers_copy.update({"Cookie": cookie_format})

            try:
                proxies = CursorUsageManager.get_proxy()
                response = requests.get(url, headers=headers_copy, timeout=10, proxies=proxies)

                if response.status_code == 200:
                    data = response.json()

                    # Get Premium usage and limit
                    gpt4_data = data.get("gpt-4", {})
                    premium_usage = gpt4_data.get("numRequestsTotal", 0)
                    max_premium_usage = gpt4_data.get("maxRequestUsage", 999)

                    # Get Basic usage, but set limit to "No Limit"
                    gpt35_data = data.get("gpt-3.5-turbo", {})
                    basic_usage = gpt35_data.get("numRequestsTotal", 0)

                    return {
                        'premium_usage': premium_usage,
                        'max_premium_usage': max_premium_usage,
                        'basic_usage': basic_usage,
                        'max_basic_usage': "No Limit"
                    }
                elif response.status_code == 401:
                    continue
                else:
                    response.raise_for_status()

            except requests.RequestException:
                continue
            except Exception:
                continue

        logger.error("Get usage info failed: All cookie formats failed with 401 Unauthorized")
        return None

    @staticmethod
    def get_stripe_profile(token: str) -> Optional[Dict]:
        """Get user subscription info"""
        url = f"https://api2.{CursorConfig.NAME_LOWER}.sh/auth/full_stripe_profile"
        headers = CursorConfig.BASE_HEADERS.copy()

        # Try multiple authorization formats
        auth_formats = [
            f"Bearer {token}",
            f"Token {token}",
            token  # Raw token
        ]

        for auth_format in auth_formats:
            headers_copy = headers.copy()
            headers_copy.update({"Authorization": auth_format})

            try:
                proxies = CursorUsageManager.get_proxy()
                response = requests.get(url, headers=headers_copy, timeout=10, proxies=proxies)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    continue
                else:
                    response.raise_for_status()

            except requests.RequestException:
                continue
            except Exception:
                continue

        logger.error("Get subscription info failed: All authorization formats failed with 401 Unauthorized")
        return None

def get_default_paths():
    """Get default Cursor paths for Windows (using centralized config)"""
    return config.cursor_paths

def get_token_from_storage(storage_path):
    """Get token from storage.json"""
    if not os.path.exists(storage_path):
        return None

    try:
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Try to get accessToken (primary method)
            if 'cursorAuth/accessToken' in data:
                token = data['cursorAuth/accessToken']
                return token

            # Try other possible token keys
            token_keys = [
                'cursorAuth/token',
                'auth/accessToken',
                'auth/token',
                'accessToken',
                'token'
            ]

            for key in token_keys:
                if key in data and isinstance(data[key], str) and len(data[key]) > 20:
                    return data[key]

            # Try any key containing 'token'
            for key in data:
                if 'token' in key.lower() and isinstance(data[key], str) and len(data[key]) > 20:
                    return data[key]

    except Exception as e:
        logger.error(f"Get token from storage.json failed: {str(e)}")

    return None

def get_token_from_sqlite(sqlite_path):
    """Get token from sqlite"""
    if not os.path.exists(sqlite_path):
        return None

    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()

        # Try multiple queries to find tokens
        queries = [
            "SELECT key, value FROM ItemTable WHERE key LIKE '%token%'",
            "SELECT key, value FROM ItemTable WHERE key LIKE '%cursorAuth%'",
            "SELECT key, value FROM ItemTable WHERE key LIKE '%auth%'",
            "SELECT key, value FROM ItemTable WHERE value LIKE '%token%'"
        ]

        for query in queries:
            try:
                cursor.execute(query)
                rows = cursor.fetchall()

                for row in rows:
                    try:
                        _, value = row[0], row[1]

                        # Direct string token
                        if isinstance(value, str) and len(value) > 20:
                            # Check if it looks like a JWT or access token
                            if '.' in value or value.startswith('ey') or 'Bearer' in value:
                                conn.close()
                                return value.replace('Bearer ', '').strip()

                        # Try to parse JSON
                        try:
                            data = json.loads(value)
                            if isinstance(data, dict):
                                # Look for token fields
                                for token_field in ['token', 'accessToken', 'access_token', 'authToken']:
                                    if token_field in data and isinstance(data[token_field], str) and len(data[token_field]) > 20:
                                        conn.close()
                                        return data[token_field]
                        except:
                            pass
                    except:
                        continue
            except Exception:
                continue

        conn.close()
    except Exception as e:
        logger.error(f"Get token from sqlite failed: {str(e)}")

    return None

def get_token_from_session(session_path):
    """Get token from session"""
    if not os.path.exists(session_path):
        return None

    try:
        # Try to find all possible session files
        for file in os.listdir(session_path):
            if file.endswith(('.log', '.ldb', '.json')):
                file_path = os.path.join(session_path, file)
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read().decode('utf-8', errors='ignore')

                        # Multiple token patterns to search for
                        patterns = [
                            r'"token":"([^"]+)"',
                            r'"accessToken":"([^"]+)"',
                            r'"authToken":"([^"]+)"',
                            r'"cursorAuth/accessToken":"([^"]+)"',
                            r'Bearer\s+([A-Za-z0-9\-_\.]+)',
                            r'token["\s]*[:=]["\s]*([A-Za-z0-9\-_\.]{20,})'
                        ]

                        for pattern in patterns:
                            token_match = re.search(pattern, content, re.IGNORECASE)
                            if token_match:
                                token = token_match.group(1)
                                if len(token) > 20:  # Ensure it's a reasonable token length
                                    return token
                except:
                    continue

    except Exception as e:
        logger.error(f"Get token from session failed: {str(e)}")

    return None

def validate_token(token):
    """Validate if token looks like a valid Cursor token"""
    if not token or not isinstance(token, str):
        return False

    # Remove any Bearer prefix
    token = token.replace('Bearer ', '').strip()

    # Basic length check
    if len(token) < 20:
        return False

    # Check for common token patterns
    # JWT tokens typically have 3 parts separated by dots
    if token.count('.') >= 2:
        return True

    # Check for base64-like characters
    if re.match(r'^[A-Za-z0-9\-_\.]+$', token):
        return True

    return False

def get_cursor_token():
    """Get Cursor token"""
    # Get default paths
    paths = get_default_paths()
    if not paths:
        return None

    # Try to get token from different locations
    sources = [
        lambda: get_token_from_storage(paths['storage_path']),
        lambda: get_token_from_sqlite(paths['sqlite_path']),
        lambda: get_token_from_session(paths['session_path'])
    ]

    for source_func in sources:
        try:
            token = source_func()
            if token and validate_token(token):
                return token.replace('Bearer ', '').strip()
        except Exception:
            continue

    return None

def format_subscription_type(subscription_data: Dict) -> str:
    """Format subscription type"""
    if not subscription_data:
        return "Free"

    # Handle new API response format
    if "membershipType" in subscription_data:
        membership_type = subscription_data.get("membershipType", "").lower()
        subscription_status = subscription_data.get("subscriptionStatus", "").lower()

        if subscription_status == "active":
            if membership_type == "pro":
                return "Pro"
            elif membership_type == "free_trial":
                return "Free Trial"
            elif membership_type == "pro_trial":
                return "Pro Trial"
            elif membership_type == "team":
                return "Team"
            elif membership_type == "enterprise":
                return "Enterprise"
            elif membership_type:
                return membership_type.capitalize()
            else:
                return "Active Subscription"
        elif subscription_status:
            return f"{membership_type.capitalize()} ({subscription_status})"

    # Compatible with old API response format
    subscription = subscription_data.get("subscription")
    if subscription:
        plan = subscription.get("plan", {}).get("nickname", "Unknown")
        status = subscription.get("status", "unknown")

        if status == "active":
            if "pro" in plan.lower():
                return "Pro"
            elif "pro_trial" in plan.lower():
                return "Pro Trial"
            elif "free_trial" in plan.lower():
                return "Free Trial"
            elif "team" in plan.lower():
                return "Team"
            elif "enterprise" in plan.lower():
                return "Enterprise"
            else:
                return plan
        else:
            return f"{plan} ({status})"

    return "Free"

def get_email_from_storage(storage_path):
    """Get email from storage.json"""
    if not os.path.exists(storage_path):
        return None

    try:
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Try to get email
            if 'cursorAuth/cachedEmail' in data:
                return data['cursorAuth/cachedEmail']

            # Try other possible keys
            for key in data:
                if 'email' in key.lower() and isinstance(data[key], str) and '@' in data[key]:
                    return data[key]
    except Exception as e:
        logger.error(f"Get email from storage.json failed: {str(e)}")

    return None

def get_email_from_sqlite(sqlite_path):
    """Get email from sqlite"""
    if not os.path.exists(sqlite_path):
        return None

    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        # Try to query records containing email
        cursor.execute("SELECT value FROM ItemTable WHERE key LIKE '%email%' OR key LIKE '%cursorAuth%'")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            try:
                value = row[0]
                # If it's a string and contains @, it might be an email
                if isinstance(value, str) and '@' in value:
                    return value

                # Try to parse JSON
                try:
                    data = json.loads(value)
                    if isinstance(data, dict):
                        # Check if there's an email field
                        if 'email' in data:
                            return data['email']
                        # Check if there's a cachedEmail field
                        if 'cachedEmail' in data:
                            return data['cachedEmail']
                except:
                    pass
            except:
                continue
    except Exception as e:
        logger.error(f"Get email from sqlite failed: {str(e)}")

    return None

def get_cursor_account_info():
    """Get comprehensive Cursor account information"""
    # Get token
    token = get_cursor_token()
    if not token:
        return {"error": "Token not found. Please login to Cursor first."}

    # Get paths
    paths = get_default_paths()
    if not paths:
        return {"error": "Could not determine Cursor paths for this operating system."}

    # Get email info - try multiple sources
    email = get_email_from_storage(paths['storage_path'])

    # If not found in storage, try from sqlite
    if not email:
        email = get_email_from_sqlite(paths['sqlite_path'])

    # Get subscription info
    try:
        subscription_info = CursorUsageManager.get_stripe_profile(token)
    except Exception as e:
        logger.error(f"Get subscription info failed: {str(e)}")
        subscription_info = None

    # If not found in storage and sqlite, try from subscription info
    if not email and subscription_info:
        # Try to get email from subscription info
        if 'customer' in subscription_info and 'email' in subscription_info['customer']:
            email = subscription_info['customer']['email']

    # Get usage info
    try:
        usage_info = CursorUsageManager.get_usage(token)
    except Exception as e:
        logger.error(f"Get usage info failed: {str(e)}")
        usage_info = None

    # Compile results
    result = {
        "email": email,
        "subscription_info": subscription_info,
        "usage_info": usage_info,
        "subscription_type": format_subscription_type(subscription_info) if subscription_info else "Free"
    }

    # Add trial days if available
    if subscription_info:
        days_remaining = subscription_info.get("daysRemainingOnTrial")
        if days_remaining is not None and days_remaining > 0:
            result["trial_days_remaining"] = days_remaining

    return result

def debug_cursor_authentication():
    """Debug function to help troubleshoot authentication issues"""
    print("=== Cursor Authentication Debug ===")

    # Check paths
    paths = get_default_paths()
    if not paths:
        print("❌ Could not get default paths")
        return

    print(f"✅ Paths found:")
    for key, path in paths.items():
        exists = "✅" if os.path.exists(path) else "❌"
        print(f"  {key}: {exists} {path}")

    # Check token sources
    print("\n=== Token Sources ===")

    # Storage
    storage_token = get_token_from_storage(paths['storage_path'])
    if storage_token:
        print(f"✅ Storage token found: {storage_token[:20]}...")
        print(f"   Valid: {'✅' if validate_token(storage_token) else '❌'}")
    else:
        print("❌ No token found in storage.json")

    # SQLite
    sqlite_token = get_token_from_sqlite(paths['sqlite_path'])
    if sqlite_token:
        print(f"✅ SQLite token found: {sqlite_token[:20]}...")
        print(f"   Valid: {'✅' if validate_token(sqlite_token) else '❌'}")
    else:
        print("❌ No token found in SQLite")

    # Session
    session_token = get_token_from_session(paths['session_path'])
    if session_token:
        print(f"✅ Session token found: {session_token[:20]}...")
        print(f"   Valid: {'✅' if validate_token(session_token) else '❌'}")
    else:
        print("❌ No token found in session files")

    # Final token
    final_token = get_cursor_token()
    if final_token:
        print(f"\n✅ Final token selected: {final_token[:20]}...")
        print(f"   Length: {len(final_token)}")
        print(f"   Valid: {'✅' if validate_token(final_token) else '❌'}")

        # Test API calls
        print("\n=== API Tests ===")

        # Test subscription API
        print("Testing subscription API...")
        subscription_info = CursorUsageManager.get_stripe_profile(final_token)
        if subscription_info:
            print("✅ Subscription API successful")
        else:
            print("❌ Subscription API failed")

        # Test usage API
        print("Testing usage API...")
        usage_info = CursorUsageManager.get_usage(final_token)
        if usage_info:
            print("✅ Usage API successful")
        else:
            print("❌ Usage API failed")
    else:
        print("\n❌ No valid token found")
        print("\nTroubleshooting suggestions:")
        print("1. Make sure Cursor is installed and you're logged in")
        print("2. Try logging out and logging back into Cursor")
        print("3. Check if Cursor is running")
        print("4. Verify the Cursor installation path")

if __name__ == "__main__":
    # Run debug when script is executed directly
    debug_cursor_authentication()
