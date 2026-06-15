import os
import time
import json
import random
from playwright.sync_api import sync_playwright
from ai_generator import generate_comment
from playwright_stealth import stealth_sync
from logger import log_interaction

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_channels():
    if not os.path.exists('channels.txt'):
        print("Không tìm thấy file channels.txt")
        return []
    with open('channels.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def run_bot_for_account(account_index, channel_name):
    profile_dir = os.path.join(os.getcwd(), 'profiles', f'profile_{account_index}')
    if not os.path.exists(profile_dir):
        print(f"Profile {account_index} chưa tồn tại. Vui lòng chạy run_setup.py trước!")
        return

    print(f"--- Bắt đầu chạy TÀI KHOẢN {account_index} trên kênh @{channel_name} ---")
    
    with sync_playwright() as p:
        browser_context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False, # Hiện trình duyệt để xem cho vui
            viewport={"width": 1280, "height": 720},
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = browser_context.pages[0]
        stealth_sync(page) # Kích hoạt chế độ chống nhận diện bot
        
        try:
            # 1. Truy cập kênh
            print(f"Đang truy cập kênh: https://www.tiktok.com/@{channel_name}")
            page.goto(f"https://www.tiktok.com/@{channel_name}", wait_until="domcontentloaded")
            time.sleep(5) # Đợi tải trang
            
            # 2. Click vào video đầu tiên (mới nhất)
            video_selector = "a[href*='/video/']"
            page.wait_for_selector(video_selector, timeout=15000)
            page.locator(video_selector).first.click()
            print("Đã mở video đầu tiên.")
            
            # Lấy caption video để làm ngữ cảnh cho AI
            caption = ""
            try:
                time.sleep(2) # Đợi modal video tải nội dung
                caption_elem = page.locator('[data-e2e="browse-video-desc"]').first
                if caption_elem.is_visible(timeout=3000):
                    caption = caption_elem.inner_text()
                    print(f"Đã lấy được caption: {caption[:50]}...")
            except Exception:
                print("Không lấy được caption.")
            
            # 3. Giả lập thời gian xem video (10-25 giây)
            watch_time = random.randint(10, 25)
            print(f"Đang xem video trong {watch_time} giây...")
            time.sleep(watch_time)
            
            # 4. Like video
            try:
                like_btn = page.locator('[data-e2e="like-icon"]').first
                if like_btn.is_visible():
                    like_btn.click()
                    print("-> Đã Like video.")
                    log_interaction(account_index, channel_name, "Like")
                    time.sleep(1)
            except Exception as e:
                print("Không tìm thấy nút Like hoặc đã Like rồi.")
                
            # 5. Share video (chỉ cần bấm nút Share mở menu)
            try:
                share_btn = page.locator('[data-e2e="share-icon"]').first
                if share_btn.is_visible():
                    share_btn.click()
                    print("-> Đã nhấn nút Share.")
                    log_interaction(account_index, channel_name, "Share")
                    time.sleep(2)
                    # Click ra ngoài để tắt menu share
                    page.mouse.click(10, 10)
            except Exception as e:
                print("Không click được Share.")
                
            # 6. Comment
            try:
                print("Đang gọi AI để sinh bình luận (dựa trên caption)...")
                comment_text = generate_comment(channel_name, caption=caption)
                print(f"Bình luận AI sinh ra: '{comment_text}'")
                
                # Tìm ô nhập comment bằng nhiều cách (đề phòng TikTok đổi giao diện)
                comment_box = page.locator('.public-DraftEditor-content, [data-e2e="comment-input"], div[contenteditable="true"]').first
                
                # Có thể cần click vào vùng comment trước
                try:
                    page.locator('[data-e2e="comment-icon"]').first.click()
                    time.sleep(1)
                except:
                    pass
                    
                if comment_box.is_visible(timeout=5000):
                    comment_box.click()
                    time.sleep(1)
                    # Gõ từng phím như người thật
                    page.keyboard.type(comment_text, delay=random.randint(50, 150))
                    time.sleep(1)
                    # Nhấn Enter để gửi
                    page.keyboard.press("Enter")
                    print("-> Đã gửi Comment thành công!")
                    log_interaction(account_index, channel_name, "Comment", comment_text)
                else:
                    print("Không tìm thấy ô nhập comment (Có thể video khóa comment).")
            except Exception as e:
                print(f"Lỗi khi comment: {e}")
                
            # Nghỉ 1 chút trước khi đóng
            time.sleep(3)
            
        except Exception as e:
            print(f"Lỗi trong quá trình chạy kênh {channel_name}: {e}")
        finally:
            browser_context.close()
            print(f"--- Đã đóng trình duyệt TÀI KHOẢN {account_index} ---")

def main_loop():
    config = load_config()
    num_accounts = config.get("num_accounts", 5)
    wait_min = config.get("wait_min_seconds", 45)
    wait_max = config.get("wait_max_seconds", 90)
    
    while True:
        channels = load_channels()
        if not channels:
            print("Danh sách kênh trống! Vui lòng thêm kênh vào file channels.txt")
            time.sleep(10)
            continue
            
        # Chọn ngẫu nhiên 1 tài khoản và 1 kênh
        account_idx = random.randint(1, num_accounts)
        channel = random.choice(channels)
        
        run_bot_for_account(account_idx, channel)
        
        wait_time = random.randint(wait_min, wait_max)
        print(f"=== Đang nghỉ {wait_time} giây trước vòng lặp tiếp theo ===\n")
        time.sleep(wait_time)

if __name__ == "__main__":
    print("KHỞI ĐỘNG TIKTOK AUTO BOT...")
    main_loop()
