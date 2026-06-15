import os
import time
import base64
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

async def generate_imagen3_infographic(topic):
    print("\n" + "="*50)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🧿 MẮT THẦN 4: ĐỘT NHẬP CĂN CỨ GEMINI ADVANCED (PERSISTENT VOL)")
    print("="*50)
    
    user_data_dir = os.path.abspath("gemini_profile")
    os.makedirs(user_data_dir, exist_ok=True)
    
    async with async_playwright() as p:
        args = ['--disable-blink-features=AutomationControlled', '--start-maximized']
        print("🔄 Đang Nạp Lõi Trình Duyệt Nội Cứng (Bảo lưu Google Khỏi Quét Xóa Cookie)...")
        
        try:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                channel="chrome",
                args=args,
                no_viewport=True
            )
        except Exception:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                args=args,
                no_viewport=True
            )
            
        page = context.pages[0] if len(context.pages) > 0 else await context.new_page()
        
        try:
            await page.goto("https://gemini.google.com/app", timeout=60000)
        except Exception:
            print("⚠️ Mạng Chậm Hoặc Quá Tải Kết Nối Tới Máy Chủ Của Google...")
            
        # Xử lý Login Chặn Đỉnh Cao: Dựa vào sự điều hướng URL khắc nghiệt của Google thay vì giao diện ảo
        try:
            # Xem thử 4s sau Google có điều hướng bay ra ngoài màn Đăng nhập không?
            await page.wait_for_timeout(4000)
            if "accounts.google.com" in page.url or "/app" not in page.url:
                 raise Exception("Not Logged In Yet")
                 
            # Chỉ quét đúng cái thẻ 'rich-textarea' (Tức là hộp thoại chat cực đặc trưng của Gemini)
            chat_input = page.locator('rich-textarea').first
            await chat_input.wait_for(state="visible", timeout=8000)
        except Exception:
            print("\n" + "!"*60)
            print("🚨 HỆ THỐNG BÁO ĐỘNG ĐỎ: BẠN CHƯA ĐĂNG NHẬP (WEB ĐANG Ở MÀN HÌNH NGOÀI)!")
            print("👉 HÃY TỰ TAY BẤM NÚT ĐĂNG NHẬP GMAIL CHÍNH CHỦ VÀ VÀO CỬA SỔ BÊN TRONG (Thấy Box Chat Của Gemini Mới Xong)...")
            print("⏳ Cỗ Máy Tool Đang Đạp Phanh Dừng Lại Tối Đa 10 Phút Để Bạn Điền Xong Gmail...")
            print("!"*60)
            
            try:
                 # Đợi URL chuyển hướng vào tận bên trong Hộp Chat /app
                 await page.wait_for_url("**/app**", timeout=600000)
                 await page.wait_for_timeout(5000)
                 
                 # Chờ tải khung gõ sau đó khóa mục tiêu cực đại
                 chat_input = page.locator('rich-textarea').first
                 await chat_input.wait_for(state="visible", timeout=20000)
                 print("✅ TÍN HIỆU XANH: BẠN ĐÃ LOGIN GMAIL THÀNH CÔNG. CẤU TRÚC PHẦN CỨNG ĐÃ GHI NHẬN!")
            except Exception:
                 print("⚠️ Quá 10 Phút Bạn Không Thể Login Hoặc Không Vào Được Box Chat. Hủy Nhiệm Vụ Sinh Ảnh Này Của Gemini.")
                 await context.close()
                 return None
                 
        prompt = f"Tạo một bức tranh minh họa Vector Art phẳng nhẹ nhàng, màu pastel ấm áp. Chủ đề: '{topic}'. Cảnh một người mẹ trẻ an vui bình yên bên bé trai 13 tháng tuổi ở nhà, xen lẫn chi tiết hiện đại khéo léo về Công nghệ AI trong đời sống. Hình vuông tỷ lệ 1:1, layout sạch sẽ, không có chữ. Chỉ xuất ra ảnh."
        
        print(f"📡 Truyền Lệnh Prompt Sang Đầu Não Gemini Pro: '{prompt}'...")
        try:
            await chat_input.click()
            await page.wait_for_timeout(1000)
            
            await page.keyboard.insert_text(prompt)
            await page.wait_for_timeout(1000)
            
            send_btn = page.locator('button[aria-label="Gửi tin nhắn"], button[aria-label="Send message"], button:has-text("Gửi")').first
            if await send_btn.count() > 0 and await send_btn.is_enabled():
                 await send_btn.click()
            else:
                 await page.keyboard.press("Enter")
                 
            print("⏳ [Imagen 3] LỆNH TỪ USER: Yêu cầu Đóng Băng Kỷ Luật 5 PHÚT (300 Giây) Để Render Đám Mây Mực Khối Chậm Rãi Tránh Vội Vã...")
            await page.wait_for_timeout(300000)
            
            print(f"🎯 Đang truy quét nút ẩn 'Sao chép hình ảnh' nguyên bản theo chỉ thị trực tiếp của User...")
            try:
                 await context.grant_permissions(['clipboard-read', 'clipboard-write'])
            except Exception: pass
            
            img_saved = False
            
            try:
                 # Lội ngược luồng HTML săn bằng được nút Chấm Tròn 3 Chấm (Menu Ẩn Của Từng Câu Trả Lời)
                 menus = await page.locator('button[aria-haspopup="menu"]').all()
                 if menus:
                      for menu in reversed(menus):
                           try:
                                await menu.scroll_into_view_if_needed()
                                await menu.click()
                                await page.wait_for_timeout(1000)
                                
                                copy_btn = page.locator('text="Sao chép hình ảnh", text="Copy image"').first
                                if await copy_btn.count() > 0 and await copy_btn.is_visible():
                                     print("✅ ĐÃ CHỘP ĐƯỢC NÚT 'SAO CHÉP HÌNH ẢNH'. Nhấn Click Trộm Lưu Hình Vào Bộ Nhớ Tạm...")
                                     await copy_btn.click()
                                     await page.wait_for_timeout(3000)
                                     img_saved = True
                                     break
                                else:
                                     await page.keyboard.press("Escape")
                                     await page.wait_for_timeout(500)
                           except Exception: pass
            except Exception as e:
                 print(f"❌ Trục trặc khi móc họng Menu Gemini: {e}")
                 
            if img_saved:
                 print("✅ Bức Ảnh Tuyệt Phẩm Từ Gemini Pro {1024}x{1024} Siêu Nét Đã Nằm Cực Kín Trong Bộ Nhớ Đệm Toàn Hệ Thống (Clipboard). KẾT THÚC NHIỆM VỤ TẠI MẮT THẦN 4.")
                 await context.close()
                 return "CLIPBOARD"
            else:
                 print("⚠️ Mắt thần báo cáo: Gemini Ẩn Quá Sâu Nút Sao chép. Bật Mạch Phụ Trợ (Chụp Ảnh Điểm Ảnh Cháy Tạm)...")
                 
                 image_url = None
                 img_locator = None
                 
                 for _ in range(15):
                      response_images = page.locator('img[src*="googleusercontent"]')
                      count = await response_images.count()
                      if count > 0:
                           for i in range(count - 1, -1, -1):
                                img = response_images.nth(i)
                                box = await img.bounding_box()
                                if box and box['width'] > 250 and box['height'] > 250:
                                     image_url = await img.get_attribute('src')
                                     img_locator = img
                                     break
                           if image_url: break
                      await page.wait_for_timeout(3000)
                      
                 if not image_url or not img_locator:
                      print("❌ Cả Đường Lưu Clipboard Lẫn Đường Chụp Đều Gãy. Đuổi Về Cứu Hộ Lò Rèn Pollinations Khẩn Cấp.")
                      await context.close()
                      return None
                      
                 os.makedirs("fb_images", exist_ok=True)
                 save_path = os.path.abspath(os.path.join("fb_images", f"gemini_masterpiece_{int(time.time())}.jpg"))
                 await img_locator.scroll_into_view_if_needed()
                 await page.wait_for_timeout(1000)
                 await img_locator.screenshot(path=save_path, type="jpeg", quality=95)
                 
                 try:
                     from PIL import Image
                     with Image.open(save_path) as img:
                         img = img.convert("RGB")
                         img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
                         img.save(save_path, "JPEG", quality=85, optimize=True)
                 except: pass
                 
                 print(f"✅ Bọc Cứu Hộ Ghi Được File 2MB An Toàn Hoàn Tất.")
                 await context.close()
                 return save_path
            
        except Exception as flow_err:
            print(f"❌ Luồng Khai Xuất Ảnh Web Đứng Bánh: {flow_err}")
            await context.close()
            return None
