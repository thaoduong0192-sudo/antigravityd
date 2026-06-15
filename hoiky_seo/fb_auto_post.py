import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import random
import asyncio
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from playwright.async_api import async_playwright

load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
if QWEN_API_KEY:
    qwen_client = OpenAI(
        api_key=QWEN_API_KEY,
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        timeout=180.0
    )
else:
    print("[-] CẢNH BÁO: KHÔNG TÌM THẤY QWEN_API_KEY trong .env!")
    exit(1)

def call_qwen_safe(model_name, prompt, retries=3):
    for i in range(retries):
        try:
            response = qwen_client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            err_str = str(e)
            print(f"  [!] Lỗi API Qwen (Caption FB). Đang thử lại sau 5s... ({i+1}/{retries}) - {err_str}")
            time.sleep(5)
    raise Exception("Qwen API call failed for Facebook Caption.")

def generate_fb_caption(keyword, wp_url):
    prompt = f"""
Đóng vai một chuyên gia tư vấn viết hồi ký, chấp bút sách gia đình từ thương hiệu BE HERITAGE.
Hãy viết một Status Facebook để chia sẻ bài báo mới với từ khóa "{keyword}".
Yêu cầu:
- Viết thân mật, chạm đến cảm xúc về giá trị của gia đình, lưu giữ kỷ niệm, ý nghĩa sống.
- Độ dài vừa phải (khoảng 3-4 câu).
- CÓ gợi sự tò mò để người đọc bấm vào link đọc bài viết.
- Tạo sẵn 3-4 hashtag phù hợp (ví dụ: #VietHoiKy #BeHeritage #LuuGiuKyNiem...)
- Trả về NỘI DUNG STATUS THUẦN TÚY (Không chứa ngoặc kép bọc ngoài, không chứa cấu trúc 'Dưới đây là status').

Đường link bài viết: {wp_url} (Không cần ghi link trong content bạn viết ra, hệ thống sẽ tự dán bên dưới cùng).
    """
    ai_text = call_qwen_safe('qwen-plus', prompt)
    
    # Gộp caption và link
    final_content = f"{ai_text}\n\n👉 Mời bạn đón đọc chi tiết tại đây: {wp_url}"
    return final_content

def generate_10_comments(keyword):
    prompt = f"""
Đóng vai chính tác giả bài viết (thương hiệu viết hồi ký BE HERITAGE) về chủ đề "{keyword}".
Thay vì đóng vai khách hàng mồi tương tác, hãy viết 10 bình luận nhằm MỞ RỘNG GIÁ TRỊ, cung cấp thêm kiến thức, trích dẫn hay, hoặc góc nhìn sâu sắc để bổ sung cho bài viết gốc.
Yêu cầu:
- Mỗi bình luận phải đứng độc lập trên 1 dòng. Không đánh số thứ tự ở đầu. Không dùng ngoặc kép bọc ngoài.
- 10 bình luận là 10 ý bổ sung khác nhau (ví dụ: 1 bình luận trích lời danh nhân về kỷ niệm, 1 bình luận đưa ra mẹo nhỏ khi bắt đầu viết, 1 bình luận chia sẻ cảm xúc nghề nghiệp của người chấp bút, v.v.).
- Lồng ghép khéo léo và mượt mà một vài từ khóa liên quan đến "{keyword}" vào còm để tối ưu SEO Facebook.
- Dài 1-2 câu mỗi bình luận. Ngôn từ chuyên gia, sâu lắng, ấm áp và truyền cảm hứng.
"""
    ai_text = call_qwen_safe('qwen-plus', prompt)
    lines = [L.strip() for L in ai_text.split('\n') if L.strip() and len(L.strip()) > 10]
    cleaned = [re.sub(r"^\d+[\.\-\)]\s*", "", L) for L in lines]
    return cleaned[:10]

async def run_facebook_posting(keyword, wp_url):
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔵 KHỞI ĐỘNG CỖ MÁY ĐĂNG FACEBOOK FANPAGE...")
    session_file = "fb_session.json"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    if not os.path.exists(session_file):
        print("⚠️ THẤT BẠI: Trạng thái Cookie FB Trống! Bạn CHƯA chạy 'login_facebook_once.py' để lưu Session.")
        return False
        
    print("🤖 Đang tư duy Caption bằng Qwen AI...")
    try:
         caption_content = generate_fb_caption(keyword, wp_url)
         print(f"💬 Nội dung chốt hạ:\n{'-'*30}\n{caption_content}\n{'-'*30}")
    except Exception as e:
         print(f"❌ Lỗi sinh AI Caption: {e}")
         return False

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--start-maximized', '--window-size=1600,900']
        )
        context = await browser.new_context(
            storage_state=session_file,
            viewport={'width': 1600, 'height': 900},
            user_agent=user_agent
        )
        page = await context.new_page()
        
        try:
            fanpage_url = "https://www.facebook.com/viethoikyonline"
            print(f"🔗 Đang bẻ lái trình duyệt về Tổng Hành Dinh: {fanpage_url}")
            await page.goto(fanpage_url, timeout=60000)
            await page.wait_for_timeout(8000)
            
            print("⏳ Xử lý pop-up và chuyển profile (nếu có)...")
            popup_locs = [
                'div[aria-label="Đóng"]',
                'div[aria-label="Close"]',
                'div[role="button"]:has-text("Lúc khác")',
                'div[role="button"]:has-text("Đóng")'
            ]
            for p_loc in popup_locs:
                btn = page.locator(p_loc).first
                if await btn.count() > 0 and await btn.is_visible():
                    try:
                        await btn.click(force=True, timeout=2000)
                        await page.wait_for_timeout(1000)
                    except: pass
            
            switch_locs = [
                'div[role="button"]:has-text("Chuyển ngay")',
                'div[role="button"]:has-text("Chuyển")'
            ]
            for sl in switch_locs:
                btn = page.locator(sl).first
                if await btn.count() > 0 and await btn.is_visible():
                    try:
                        await btn.click(force=True, timeout=2000)
                        print("✅ Đã bấm nút chuyển Profile sang Fanpage.")
                        await page.wait_for_timeout(5000)
                    except: pass
            
            # Click vào "Bạn đang nghĩ gì" / "Tạo bài viết"
            print("⏳ Đang dò tìm Box Tạo Bài Viết...")
            box_locators = [
                'div[role="button"]:has-text("Bạn đang nghĩ gì")',
                'div[role="button"]:has-text("Tạo bài viết")',
                'div[aria-label="Tạo bài viết"]',
                'span:has-text("Bạn đang nghĩ gì")'
            ]
            
            clicked = False
            for loc in box_locators:
                btn = page.locator(loc).first
                if await btn.count() > 0 and await btn.is_visible():
                    await btn.click(force=True)
                    clicked = True
                    print(f"✅ Đã tóm được Box đăng bài qua locator: {loc}")
                    break
                    
            if not clicked:
                # Vuốt chuột rà lại
                await page.mouse.wheel(0, 500)
                await page.wait_for_timeout(2000)
                for loc in box_locators:
                    btn = page.locator(loc).first
                    if await btn.count() > 0 and await btn.is_visible():
                        await btn.click(force=True)
                        clicked = True
                        print(f"✅ Đã tóm được Box đăng bài qua locator (SAU KHI CUỘN): {loc}")
                        break

            if not clicked:
                 raise Exception("KHÔNG THỂ MỞ ĐƯỢC POPUP ĐĂNG BÀI - Bị chặn layout Fanpage hoặc sai account.")

            await page.wait_for_timeout(3000)
            
            print("Mở modal thành công. Đang cắm Text...")
            # Sử dụng logic mềm mỏng theo huong_gnouh:
            textbox = page.locator('div[contenteditable="true"][role="textbox"], div[aria-label*="Bạn đang nghĩ gì"], div[aria-label*="What\'s on your mind"]').first
            
            if await textbox.count() > 0:
                await textbox.click(force=True)
                await page.keyboard.insert_text(caption_content)
            else:
                await page.keyboard.insert_text(caption_content)
                
            await page.wait_for_timeout(4000)
            
            # Chờ để Facebook fetch preview URL (thường mất 3-8s)
            print("⏳ Đang đợi FB render Link Preview (8 giây)...")
            await page.wait_for_timeout(8000)
            
            print("📤 Truyền Lệnh Kích Chốt Đăng Dữ Liệu Tường...")
            next_btn = page.locator('div[aria-label="Tiếp"][role="button"], div[aria-label="Next"][role="button"], div[role="button"]:text-is("Tiếp"), div[role="button"]:text-is("Next")').first
            if await next_btn.count() > 0 and await next_btn.is_visible():
                print("⚠️ Bước Tùy chọn Meta Suite: Kích hoạt Nút [Tiếp]...")
                try:
                    await next_btn.click(timeout=15000)
                    await page.wait_for_timeout(3000)
                except Exception:
                    await next_btn.click(force=True)
                
            post_btn = page.locator('div[aria-label="Đăng"][role="button"], div[aria-label="Post"][role="button"], div[role="button"]:has-text("Đăng"), div[role="button"]:has-text("Post")')
            
            # Select only visible post button
            visible_post_btns = []
            count = await post_btn.count()
            for i in range(count):
                if await post_btn.nth(i).is_visible():
                    visible_post_btns.append(post_btn.nth(i))
                    
            if len(visible_post_btns) > 0:
                final_post_btn = visible_post_btns[0]
                try: 
                    print("⏳ Máy Quét Facebook Đang Rà Soát Kênh Đăng...")
                    # Try to check if disabled
                    if await final_post_btn.get_attribute("aria-disabled") == "true":
                         print("⚠️ Nút Đăng đang mờ (disabled), chờ thêm 5s...")
                         await page.wait_for_timeout(5000)
                    
                    await final_post_btn.click(timeout=40000)
                    print("✅ NÚT ĐĂNG ĐÃ KÍCH! Đồng hồ 15s xoay vòng cho Facebook update Tường...")
                    await page.wait_for_timeout(15000) 
                except Exception as post_err:
                    print(f"❌ Lỗi Kháng Cự Nút Đăng (Bị đè layout): {post_err}")
                    await page.screenshot(path="debug_fb_error.png")
                    await page.wait_for_timeout(10000)
            else:
                 await page.screenshot(path="debug_fb_error_nopost.png")
                 raise Exception("Đứt Gãy: KHÔNG TÌM THẤY BẤT KỲ NÚT ĐĂNG NÀO (Lưu ảnh debug).")
            
            print("🎉 Báo Cáo Sếp: XONG NHIỆM VỤ ĐĂNG CHÉO BÀI TRÊN FACEBOOK!")
            
            # --- CHUYỂN SANG GIAI ĐOẠN LIKE & SEEDING COMMENT ---
            print("\n" + "="*40)
            print("👍 BẮT ĐẦU CHIẾN DỊCH SEEDING KÉO ENGAGEMENT TỰ ĐỘNG (10 CMT)")
            print("="*40)
            
            try:
                print("🔄 Tải lại trang Fanpage để bài viết vừa đăng dội lên đầu Feed...")
                await page.goto(fanpage_url, timeout=60000)
                await page.wait_for_timeout(5000)
                await page.mouse.wheel(0, 500)
                await page.wait_for_timeout(3000)
                
                # Bấm Like bài viết đầu tiên
                like_btn = page.locator('div[aria-label="Thích"][role="button"], div[aria-label="Like"][role="button"]').first
                if await like_btn.count() > 0:
                    try:
                        await like_btn.click(timeout=5000)
                        print("❤️ Đã click Thích (Like) cho bài viết mới!")
                    except Exception as e_like:
                        print(f"⚠️ Điểm mù - Không Like được: {str(e_like)[:100]}")
                
                await page.wait_for_timeout(2000)
                
                comments = generate_10_comments(keyword)
                if comments:
                    print(f"🤖 Trí tuệ AI đã vạch ra {len(comments)} kịch bản comments. Lên đạn xả text...")
                    
                    # Click open comment first if hidden. Check multiple Facebook variants
                    cm_start_btn = page.locator('div[aria-label="Viết bình luận"], div[aria-label="Bình luận"][role="button"], div[aria-label="Bình luận về bài viết này"][role="button"], div[role="button"]:has-text("Bình luận")')
                    visible_comment_btns = []
                    bt_cmd = await cm_start_btn.count()
                    for i in range(bt_cmd):
                         if await cm_start_btn.nth(i).is_visible():
                             visible_comment_btns.append(cm_start_btn.nth(i))
                             
                    if len(visible_comment_btns) > 0:
                         try: await visible_comment_btns[0].click(timeout=3000)
                         except: pass
                    
                    await page.wait_for_timeout(2000)

                    comment_box = page.locator('div[aria-label*="Viết bình luận"], div[aria-label*="Bình luận"], div[role="textbox"][aria-label*="bình luận"], p[data-lexical-text="true"]')
                    if await comment_box.count() > 0:
                        await comment_box.click(timeout=5000)
                        await page.wait_for_timeout(1000)
                        for idx, c_text in enumerate(comments, 1):
                            await page.keyboard.insert_text(c_text)
                            await page.wait_for_timeout(1000)
                            await page.keyboard.press("Enter")
                            print(f"  💬 Còm {idx}/10: {c_text[:50]}...")
                            delay = random.randint(4000, 7000)
                            await page.wait_for_timeout(delay)
                    else:
                        print("⚠️ Hệ thống Tường Giao Diện Mới: Box Bình luận đang đóng kính, không tìm thấy ô Input!")
                else:
                    print("⚠️ Trí tuệ nhân tạo không nhả ra còm nào.")

            except Exception as seed_err:
                 print(f"❌ Xung đột quá trình Rải Seeding do Layout FB: {str(seed_err)[:200]}")

        except Exception as flow_err:
            print(f"❌ Đứt gãy luồng FB Auto Post: {flow_err}")
            return False

        await browser.close()
        return True

def trigger_facebook_post(keyword, wp_url):
    return asyncio.run(run_facebook_posting(keyword, wp_url))

if __name__ == "__main__":
    # KHÚC NÀY CHỈ ĐỂ TEST RIÊNG BIỆT 1 FILE
    test_kw = "dịch vụ viết hồi ký cho người già"
    test_url = "https://hoiky.com.vn" 
    trigger_facebook_post(test_kw, test_url)
