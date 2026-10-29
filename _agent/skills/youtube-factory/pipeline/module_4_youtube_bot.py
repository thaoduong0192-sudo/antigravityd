import os
import json
import shutil
import time
import sys
import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Constants
LONG_DIR = "output_factory/long_videos"
SHORT_DIR = "output_factory/short_videos"
META_DIR = "output_factory/metadata"
UPLOAD_DIR = "output_factory/uploaded"
USER_DATA_DIR = os.path.abspath("chrome_profile_bot")

def upload_video_playwright(page, video_path, metadata_path, schedule_date, schedule_time_str, is_short=False):
    print(f"[*] Đang tải lên: {os.path.basename(video_path)}")
    
    # 1. Click Create -> Upload video
    page.goto("https://studio.youtube.com")
    time.sleep(3)
    try:
        # Nút Upload trực tiếp (mũi tên hướng lên)
        page.locator("#upload-icon").first.click(timeout=5000)
    except:
        try:
            # Nhấn vào chữ Tạo
            page.locator("text=Tạo").first.click(timeout=5000)
            time.sleep(1)
            page.locator("text=Tải video lên").first.click(timeout=5000)
        except:
            # Nhấn vào chữ Create
            page.locator("text=Create").first.click(timeout=5000)
            time.sleep(1)
            page.locator("text=Upload videos").first.click(timeout=5000)
    time.sleep(2)
    
    # 2. Upload file
    page.set_input_files("input[type='file']", os.path.abspath(video_path))
    
    print("  + Chờ YouTube xử lý file (10-15s)...")
    time.sleep(10)
    
    # 3. Fill Title & Description
    with open(metadata_path, 'r', encoding='utf-8') as f:
        meta_content = f.read()
    
    # Giả định metadata bắt đầu bằng "TITLE:" và có "HOOK:" hoặc "DESCRIPTION:"
    title = os.path.basename(video_path)
    description = meta_content
    for line in meta_content.split('\n'):
        if line.startswith('TITLE:'):
            title = line.replace('TITLE:', '').strip()
            break
            
    # Xử lý độ dài tiêu đề (Shorts cần có #shorts)
    if is_short and "#shorts" not in title.lower():
        title += " #shorts"
    if len(title) > 95:
        title = title[:95]
        
    print(f"  + Tiêu đề: {title}")
    
    textboxes = page.locator("#textbox")
    textboxes.nth(0).fill(title)
    time.sleep(1)
    textboxes.nth(1).fill(description)
    time.sleep(1)
    
    # Khai báo không dành cho trẻ em
    try:
        page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").click()
    except:
        pass
    
    # 4. Next qua các tab
    for _ in range(3):
        page.click("#next-button")
        time.sleep(1)
        
    # Bước 5a: Click vào #second-container để mở phần "Lên lịch"
    print("  + Mở phần Lên lịch...")
    page.locator("#second-container").click(timeout=5000)
    time.sleep(2)
    
    # Bước 5b: Kiểm tra xem second-container đã được chọn chưa
    parent = page.locator("ytcp-video-visibility-select")
    style = parent.get_attribute("second-container-style")
    print(f"  + second-container-style = '{style}'")
    
    # Nếu vẫn chưa selected, thử click expand button
    if style != "selected":
        print("  + Chưa selected, thử click expand button...")
        try:
            page.locator("#second-container-expand-button").click(timeout=3000)
            time.sleep(2)
            style = parent.get_attribute("second-container-style")
            print(f"  + Sau expand: second-container-style = '{style}'")
        except:
            pass
    
    # Bước 5c: Đặt ngày và giờ bằng cách tương tác trực tiếp với Calendar Popup
    try:
        picker_visible = page.locator("ytcp-datetime-picker").is_visible()
    except:
        picker_visible = False
    
    if picker_visible:
        print(f"  + Đặt ngày: {schedule_date.strftime('%d/%m/%Y')} | Giờ: {schedule_time_str}")
        
        # 1. Click mở Calendar Popup
        date_btn = page.locator("#second-container ytcp-datetime-picker #datepicker-trigger").first
        date_btn.click()
        time.sleep(1.5)
        
        # 2. Click ngày tương ứng trong Calendar Popup
        target_day = schedule_date.day
        js_click_day = """(targetDay) => {
            const picker = document.querySelector('ytcp-date-picker');
            if (!picker) return false;
            
            // Tìm tất cả phần tử hiển thị số ngày trong calendar
            const allElements = Array.from(picker.querySelectorAll('*'));
            for (let el of allElements) {
                // Chỉ chọn phần tử lá (không chứa tag con) có text đúng bằng targetDay
                if (el.children.length === 0 && el.textContent.trim() === String(targetDay)) {
                    el.click();
                    return true;
                }
            }
            return false;
        }"""
        
        clicked = page.evaluate(js_click_day, target_day)
        time.sleep(1)
        
        if not clicked:
            # Fallback: dùng Playwright locator tìm text ngày
            try:
                page.locator("ytcp-date-picker").locator(f"text='{target_day}'").first.click()
                time.sleep(1)
            except:
                pass
                
        print(f"  + Nút ngày sau khi chọn: '{date_btn.inner_text()}'")
        
        # 3. Đặt giờ (08:00, 12:00, 19:00)
        try:
            time_input = page.locator("#second-container ytcp-datetime-picker #time-of-day-container input").first
            time_input.focus()
            time_input.click(click_count=3, force=True)
            time.sleep(0.3)
            page.keyboard.type(schedule_time_str)
            time.sleep(0.3)
            page.keyboard.press("Enter")
            time.sleep(1)
            print(f"  + Đã nhập giờ: {schedule_time_str}")
        except Exception as e_time:
            print(f"  [!] Không thể nhập giờ: {e_time}")
        
        # 4. Kiểm tra second-container vẫn selected
        style2 = parent.get_attribute("second-container-style")
        if style2 != "selected":
            print("  + Re-select schedule section...")
            page.locator("#second-container").click(timeout=5000)
            time.sleep(2)
    
    # Bước 5d: Kiểm tra nút done-button có text gì
    done_btn = page.locator("#done-button")
    done_text = done_btn.inner_text()
    print(f"  + Nút submit hiện tại: '{done_text}'")
    
    # Chụp ảnh trước khi bấm
    page.screenshot(path="before_done_click.png", full_page=True)
    
    # Bước 5e: Chờ YouTube auto-save xong (chữ "Đang lưu..." phải biến mất)
    print("  + Chờ YouTube auto-save xong...")
    for i in range(15):
        try:
            saving_text = page.locator("ytcp-video-upload-progress").inner_text()
            if "Đang lưu" in saving_text or "Saving" in saving_text:
                time.sleep(1)
                continue
        except:
            pass
        break
    time.sleep(2)
    
    # Xóa overlay Google Feedback (chặn click)
    print(f"  + Xóa overlay...")
    page.evaluate("document.querySelector('#google-feedback')?.remove()")
    page.evaluate("document.querySelectorAll('tp-yt-iron-overlay-backdrop').forEach(e => e.remove())")
    time.sleep(1)
    
    # Chụp ảnh ngay trước khi bấm
    page.screenshot(path="before_done_click.png", full_page=True)
    
    # Bấm nút bằng Playwright click THẬT
    print(f"  + Bấm nút '{done_text}' (real click)...")
    done_btn.click(timeout=10000)
    time.sleep(5)
    
    # Chụp ảnh SAU khi bấm để xem kết quả
    page.screenshot(path="after_done_click.png", full_page=True)
    
    # Bước 5f: Bấm nút "Đã hiểu" trong popup cảnh báo kiểm tra nội dung
    try:
        got_it_btn = page.locator("ytcp-button:has-text('Đã hiểu'), button:has-text('Đã hiểu'), button:has-text('Got it')")
        got_it_btn.first.click(timeout=10000)
        print("  + Đã bấm 'Đã hiểu' để xác nhận lên lịch!")
        time.sleep(3)
    except:
        print("  + Không thấy popup 'Đã hiểu', bỏ qua...")
    
    # Đợi popup chia sẻ xuất hiện rồi đóng
    try:
        page.wait_for_selector("ytcp-video-share-dialog", state="visible", timeout=15000)
        page.click("ytcp-button#close-button")
    except:
        # Có thể popup share không hiện, thử đóng bất kỳ dialog nào
        try:
            page.locator("ytcp-button#close-button").click(timeout=5000)
        except:
            pass
        
    print(f"  => Lên lịch thành công vào: {schedule_date.strftime('%Y-%m-%d')} {schedule_time_str}")
    return True

def auto_schedule_upload(start_date=None):
    print("=== YOUTUBE BATCH UPLOAD & SCHEDULE BẮT ĐẦU ===")
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    longs = sorted([f for f in os.listdir(LONG_DIR) if f.endswith(".mp4")]) if os.path.exists(LONG_DIR) else []
    shorts = sorted([f for f in os.listdir(SHORT_DIR) if f.endswith(".mp4")]) if os.path.exists(SHORT_DIR) else []
    
    if not longs and not shorts:
        print("Hàng đợi rỗng. Không có video nào cần upload.")
        return
        
    print(f"Hàng đợi còn lại: {len(longs)} Long Videos, {len(shorts)} Short Videos.")
    
    if start_date is None:
        start_date = datetime.date(2026, 8, 16)
    
    # === XÂY DỰNG LỊCH ĐĂNG ===
    # Mỗi ngày: 1 video dài (19:00) + 2 video ngắn (08:00 và 12:00)
    # Tổng: 3 video/ngày
    schedule = []  # List of (video_path, meta_path, date, time, is_short)
    
    short_idx = 0
    for day_idx, lv in enumerate(longs):
        sched_date = start_date + datetime.timedelta(days=day_idx)
        
        # 2 Shorts buổi sáng và trưa (trước video dài)
        for time_slot in ["08:00", "12:00"]:
            if short_idx < len(shorts):
                sv = shorts[short_idx]
                sv_path = os.path.join(SHORT_DIR, sv)
                sv_base = sv.replace('.mp4', '')
                
                # Resolve metadata path
                sv_meta = os.path.join(META_DIR, f"{sv_base}_meta.txt")
                if not os.path.exists(sv_meta):
                    s_num = int(sv_base.replace('S', ''))
                    adjusted = s_num - 3
                    lesson = (adjusted + 2) // 5 + 1
                    short_in_lesson = (adjusted + 2) % 5 + 1
                    sv_meta = os.path.join(META_DIR, f"L{lesson:02d}_S{short_in_lesson}_meta.txt")
                
                if os.path.exists(sv_meta):
                    schedule.append((sv_path, sv_meta, sched_date, time_slot, True))
                else:
                    print(f"  [!] Không tìm thấy metadata cho {sv}, bỏ qua...")
                    shutil.move(sv_path, os.path.join(UPLOAD_DIR, sv))
                short_idx += 1
        
        # 1 Long video buổi tối
        lv_path = os.path.join(LONG_DIR, lv)
        lv_base = lv.replace('.mp4', '')
        lv_meta = os.path.join(META_DIR, f"{lv_base}_meta.txt")
        schedule.append((lv_path, lv_meta, sched_date, "19:00", False))
    
    # Shorts còn lại (nếu có nhiều shorts hơn longs)
    extra_day_offset = len(longs)
    while short_idx < len(shorts):
        day_offset = (short_idx - len(longs) * 2) // 2
        sched_date = start_date + datetime.timedelta(days=extra_day_offset + day_offset)
        time_slot = "08:00" if (short_idx % 2 == 0) else "12:00"
        
        sv = shorts[short_idx]
        sv_path = os.path.join(SHORT_DIR, sv)
        sv_base = sv.replace('.mp4', '')
        sv_meta = os.path.join(META_DIR, f"{sv_base}_meta.txt")
        if not os.path.exists(sv_meta):
            s_num = int(sv_base.replace('S', ''))
            adjusted = s_num - 3
            lesson = (adjusted + 2) // 5 + 1
            short_in_lesson = (adjusted + 2) % 5 + 1
            sv_meta = os.path.join(META_DIR, f"L{lesson:02d}_S{short_in_lesson}_meta.txt")
        
        if os.path.exists(sv_meta):
            schedule.append((sv_path, sv_meta, sched_date, time_slot, True))
        else:
            print(f"  [!] Không tìm thấy metadata cho {sv}, bỏ qua...")
            shutil.move(sv_path, os.path.join(UPLOAD_DIR, sv))
        short_idx += 1
    
    # In lịch đăng
    print(f"\n=== LỊCH ĐĂNG ({len(schedule)} video) ===")
    current_day = None
    for v_path, m_path, sched_date, sched_time, is_short in schedule:
        if sched_date != current_day:
            current_day = sched_date
            print(f"\n📅 {sched_date.strftime('%d/%m/%Y')}:")
        vtype = "🎬 Short" if is_short else "📹 Long "
        print(f"   {vtype} | {sched_time} | {os.path.basename(v_path)}")
    print()
    
    with sync_playwright() as p:
        print("[*] Đang khởi động Playwright với Chrome Profile...")
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR, 
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = browser.new_page()
            
            # Check login
            page.goto("https://studio.youtube.com")
            time.sleep(5)
            if "accounts.google.com" in page.url or "signin" in page.url:
                print("[!] LỖI: Trình duyệt chưa đăng nhập YouTube. Vui lòng mở Chrome Profile và đăng nhập bằng tay trước.")
                return
                
            upload_count = 0
            
            for v_path, m_path, sched_date, sched_time, is_short in schedule:
                if upload_count >= 15:
                    print("\n[!] Đã đạt giới hạn an toàn (15 video/lần chạy) để tránh dính Spam. Vui lòng chạy lại sau.")
                    break
                
                try:
                    upload_video_playwright(page, v_path, m_path, sched_date, sched_time, is_short=is_short)
                    shutil.move(v_path, os.path.join(UPLOAD_DIR, os.path.basename(v_path)))
                    upload_count += 1
                except Exception as e:
                    page.screenshot(path="playwright_error_screenshot.png", full_page=True)
                    print(f"  [!] Lỗi khi upload {os.path.basename(v_path)}: {e}")
                    print("  => Đã lưu ảnh chụp màn hình lỗi tại playwright_error_screenshot.png")
                    print("  => Dừng đợt upload hiện tại.")
                    break
            
            remaining_longs = len([f for f in os.listdir(LONG_DIR) if f.endswith(".mp4")])
            remaining_shorts = len([f for f in os.listdir(SHORT_DIR) if f.endswith(".mp4")])
            print(f"\n[✓] Đã upload {upload_count} video. Còn lại: {remaining_longs} Long + {remaining_shorts} Short.")
            
        except Exception as e:
            print(f"[!] Lỗi Playwright: {e}")
            print("GỢI Ý: Hãy chắc chắn bạn đã TẮT HẲN trình duyệt Chrome trước khi chạy script.")
        finally:
            try:
                browser.close()
            except:
                pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YouTube Bot Upload & Schedule")
    parser.add_argument("--channel-dir", type=str, default="", help="Đường dẫn thư mục riêng của kênh")
    parser.add_argument("--topic-dir", type=str, default="", help="Đường dẫn thư mục riêng của topic")
    parser.add_argument("--chrome-profile", type=str, default="", help="Đường dẫn Chrome profile")
    parser.add_argument("--start-date", type=str, default="2026-08-16", help="Ngày bắt đầu lên lịch (YYYY-MM-DD)")
    args = parser.parse_args()
    
    if args.channel_dir and os.path.exists(args.channel_dir):
        LONG_DIR = os.path.join(args.channel_dir, "long_videos")
        SHORT_DIR = os.path.join(args.channel_dir, "short_videos")
        META_DIR = os.path.join(args.channel_dir, "metadata")
        UPLOAD_DIR = os.path.join(args.channel_dir, "uploaded")
        
    if args.topic_dir and os.path.exists(args.topic_dir):
        LONG_DIR = os.path.join(args.topic_dir, "long_videos")
        SHORT_DIR = os.path.join(args.topic_dir, "short_videos")
        META_DIR = os.path.join(args.topic_dir, "metadata")
        UPLOAD_DIR = os.path.join(args.topic_dir, "uploaded")
        
    if args.chrome_profile:
        USER_DATA_DIR = os.path.abspath(args.chrome_profile)
        
    try:
        parts = [int(p) for p in args.start_date.split("-")]
        custom_start_date = datetime.date(parts[0], parts[1], parts[2])
    except:
        custom_start_date = datetime.date(2026, 8, 16)
        
    auto_schedule_upload(start_date=custom_start_date)
