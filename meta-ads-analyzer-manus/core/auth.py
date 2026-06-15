"""
auth.py
-------
Quản lý xác thực với Meta Graph API.
- Load credentials từ config/credentials.json
- Validate access token
- Lấy danh sách Ad Accounts có quyền truy cập
"""

import json
import os
import sys
from pathlib import Path

try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.user import User
    from facebook_business.exceptions import FacebookRequestError
except ImportError:
    print("❌ Thiếu thư viện facebook-business. Chạy: pip install -r requirements.txt")
    sys.exit(1)

# Đường dẫn gốc của project
PROJECT_ROOT = Path(__file__).parent.parent
CREDENTIALS_FILE = PROJECT_ROOT / "config" / "credentials.json"
CREDENTIALS_EXAMPLE = PROJECT_ROOT / "config" / "credentials.json.example"


def load_credentials() -> dict:
    """Load credentials từ config/credentials.json."""
    if not CREDENTIALS_FILE.exists():
        print(f"\n❌ Không tìm thấy file credentials: {CREDENTIALS_FILE}")
        print(f"   Hãy copy file example và điền thông tin thật:")
        print(f"   copy config\\credentials.json.example config\\credentials.json\n")
        sys.exit(1)

    with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
        creds = json.load(f)

    required = ["app_id", "app_secret", "access_token", "ad_accounts"]
    for key in required:
        if key not in creds or not creds[key]:
            print(f"❌ Thiếu trường '{key}' trong credentials.json")
            sys.exit(1)

    if creds.get("access_token") == "YOUR_LONG_LIVED_USER_ACCESS_TOKEN":
        print("❌ credentials.json chưa được điền thông tin thật!")
        print("   Hãy chạy: python setup.py --help để xem hướng dẫn lấy token.")
        sys.exit(1)

    return creds


def init_api(creds: dict = None) -> dict:
    """
    Khởi tạo Meta API connection.
    Returns: credentials dict với api đã được init.
    """
    if creds is None:
        creds = load_credentials()

    try:
        FacebookAdsApi.init(
            app_id=creds["app_id"],
            app_secret=creds["app_secret"],
            access_token=creds["access_token"],
        )
        print("✅ Kết nối Meta API thành công")
        return creds
    except Exception as e:
        print(f"❌ Lỗi khởi tạo Meta API: {e}")
        sys.exit(1)


def validate_token(creds: dict) -> bool:
    """Kiểm tra token còn hợp lệ và có quyền ads_read."""
    try:
        me = User(fbid="me")
        me_data = me.api_get(fields=["name", "id"])
        print(f"✅ Token hợp lệ — User: {me_data.get('name', 'Unknown')} (ID: {me_data.get('id', '?')})")
        return True
    except FacebookRequestError as e:
        error_code = e.api_error_code()
        if error_code == 190:
            print("❌ Access token đã hết hạn. Cần lấy token mới.")
        elif error_code == 200:
            print("❌ Token thiếu quyền ads_read.")
        else:
            print(f"❌ Lỗi token (code {error_code}): {e.api_error_message()}")
        return False
    except Exception as e:
        print(f"❌ Lỗi validate token: {e}")
        return False


def get_accessible_accounts(creds: dict) -> list:
    """
    Lấy danh sách Ad Accounts có trong credentials.
    Returns list of dict: [{id, name, currency, account_status}]
    """
    accounts_info = []
    ad_account_ids = creds.get("ad_accounts", [])

    if not ad_account_ids:
        print("⚠️  Không có ad_account nào trong credentials.json")
        return []

    print(f"\n📋 Đang kiểm tra {len(ad_account_ids)} Ad Account(s)...")
    for account_id in ad_account_ids:
        try:
            account = AdAccount(account_id)
            data = account.api_get(fields=["name", "currency", "account_status", "id"])
            status_map = {
                1: "✅ Active",
                2: "⚠️  Disabled",
                3: "⚠️  Unsettled",
                7: "🚫 Pending risk review",
                8: "🚫 Pending closure",
                9: "⚠️  In grace period",
                100: "⚠️  Pending",
                101: "⚠️  Pending",
                201: "🚫 Closed",
            }
            status_code = data.get("account_status", 0)
            status_label = status_map.get(status_code, f"Unknown ({status_code})")

            info = {
                "id": data.get("id", account_id),
                "name": data.get("name", "Unknown"),
                "currency": data.get("currency", "VND"),
                "account_status": status_code,
                "status_label": status_label,
            }
            accounts_info.append(info)
            print(f"   {status_label} — {info['name']} ({info['id']}) [{info['currency']}]")
        except FacebookRequestError as e:
            print(f"   ❌ Lỗi account {account_id}: {e.api_error_message()}")
        except Exception as e:
            print(f"   ❌ Lỗi không xác định cho {account_id}: {e}")

    return accounts_info


def setup_connection():
    """Full setup: load creds → init API → validate token → get accounts."""
    creds = load_credentials()
    init_api(creds)
    is_valid = validate_token(creds)
    if not is_valid:
        sys.exit(1)
    accounts = get_accessible_accounts(creds)
    return creds, accounts
