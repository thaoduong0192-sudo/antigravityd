import os
import json
from playwright.sync_api import sync_playwright

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def setup_profiles():
    config = load_config()
    num_accounts = config.get("num_accounts", 5)
    
    # Tạo thư mục profiles nếu chưa có
    os.makedirs('profiles', exist_ok=True)
    
    with sync_playwright() as p:
        for i in range(1, num_accounts + 1):
            profile_dir = os.path.join(os.getcwd(), 'profiles', f'profile_{i}')
            print(f"[{i}/{num_accounts}] Đang mở trình duyệt cho TÀI KHOẢN {i}...")
            print("==> Vui lòng đăng nhập vào TikTok (Quét QR hoặc nhập mật khẩu).")
            print("==> SAU KHI ĐĂNG NHẬP THÀNH CÔNG VÀ THẤY TRANG CHỦ, HÃY TỰ TẮT CỬA SỔ TRÌNH DUYỆT ĐỂ LƯU LẠI VÀ CHUYỂN SANG NICK TIẾP THEO.")
            
            # Khởi chạy trình duyệt với user_data_dir để lưu lại cookies/session
            browser_context = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=False,
                viewport={"width": 1280, "height": 720},
                args=["--disable-blink-features=AutomationControlled"]
            )
            
            page = browser_context.pages[0]
            page.goto("https://www.tiktok.com/login")
            
            # Đợi người dùng tự đóng trình duyệt
            try:
                page.wait_for_event("close", timeout=0)
            except Exception:
                pass
            
            browser_context.close()
            print(f"Đã lưu phiên đăng nhập cho TÀI KHOẢN {i}.\n")
            
if __name__ == "__main__":
    print("--- CHƯƠNG TRÌNH LƯU PHIÊN ĐĂNG NHẬP (LÀM 1 LẦN DUY NHẤT) ---")
    setup_profiles()
    print("Hoàn tất thiết lập! Bây giờ bạn có thể chạy file tiktok_bot.py")
