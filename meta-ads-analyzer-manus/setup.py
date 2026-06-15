"""
setup.py
--------
Script kiểm tra môi trường và hướng dẫn lấy Access Token.
Chạy lần đầu: python setup.py
"""

import json
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def check_python_version():
    if sys.version_info < (3, 8):
        print("❌ Cần Python 3.8+. Phiên bản hiện tại:", sys.version)
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")


def install_requirements():
    req_file = PROJECT_ROOT / "requirements.txt"
    print(f"\n📦 Cài đặt thư viện từ {req_file}...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("✅ Cài đặt thư viện thành công")
    else:
        print("❌ Lỗi cài đặt:")
        print(result.stderr[-500:])


def check_credentials():
    creds_file = PROJECT_ROOT / "config" / "credentials.json"
    example_file = PROJECT_ROOT / "config" / "credentials.json.example"

    if creds_file.exists():
        with open(creds_file, "r") as f:
            creds = json.load(f)
        if creds.get("access_token") != "YOUR_LONG_LIVED_USER_ACCESS_TOKEN":
            print("✅ credentials.json đã được cấu hình")
            return True
        else:
            print("⚠️  credentials.json chưa điền thông tin thật")
    else:
        print(f"⚠️  Chưa có credentials.json")
        print(f"   Copy từ example: copy config\\credentials.json.example config\\credentials.json")

    return False


def print_token_guide():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           HƯỚNG DẪN LẤY META ACCESS TOKEN                       ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  BƯỚC 1: Tạo Meta App (nếu chưa có)                             ║
║  → https://developers.facebook.com/apps/                         ║
║  → "Create App" → "Business" → Điền tên app                     ║
║                                                                  ║
║  BƯỚC 2: Thêm "Marketing API" product vào app                   ║
║  → App Dashboard → "Add Product" → "Marketing API"              ║
║                                                                  ║
║  BƯỚC 3: Lấy Short-lived Token                                   ║
║  → Graph API Explorer: https://developers.facebook.com/tools/explorer
║  → Chọn app của bạn                                              ║
║  → "Generate Access Token"                                       ║
║  → Tick permissions: ads_read, ads_management                    ║
║                                                                  ║
║  BƯỚC 4: Đổi thành Long-lived Token (60 ngày)                   ║
║  → Gọi API:                                                      ║
║  https://graph.facebook.com/oauth/access_token                   ║
║    ?grant_type=fb_exchange_token                                 ║
║    &client_id={APP_ID}                                           ║
║    &client_secret={APP_SECRET}                                   ║
║    &fb_exchange_token={SHORT_LIVED_TOKEN}                        ║
║                                                                  ║
║  BƯỚC 5: Tìm Ad Account ID                                       ║
║  → https://business.facebook.com/adsmanager                      ║
║  → URL sẽ có: /adsmanager/manage/accounts?act=XXXXXXXXXX        ║
║  → Thêm "act_" vào đầu: act_XXXXXXXXXX                          ║
║                                                                  ║
║  BƯỚC 6: Điền vào config/credentials.json                        ║
╚══════════════════════════════════════════════════════════════════╝
""")


def create_reports_dir():
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    print(f"✅ Thư mục reports/: {reports_dir}")


def main():
    print("🔧 Meta Ads Optimizer — Setup")
    print("=" * 40)

    check_python_version()
    install_requirements()
    create_reports_dir()

    has_creds = check_credentials()

    if not has_creds:
        print_token_guide()
    else:
        print("\n🧪 Test kết nối API...")
        try:
            from core.auth import setup_connection
            setup_connection()
            print("\n✅ Setup hoàn tất! Chạy: python run_daily.py")
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
            print_token_guide()


if __name__ == "__main__":
    main()
