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
            
        # Xử lý Login
        try:
            await page.wait_for_timeout(4000)
            if "accounts.google.com" in page.url or "/app" not in page.url:
                raise Exception("Not Logged In Yet")
                
            chat_input = page.locator('rich-textarea').first
            await chat_input.wait_for(state="visible", timeout=8000)
        except Exception:
            print("\n" + "!"*60)
            print("🚨 HỆ THỐNG BÁO ĐỘNG ĐỎ: BẠN CHƯA ĐĂNG NHẬP!")
            print("👉 HÃY TỰ TAY BẤM NÚT ĐĂNG NHẬP GMAIL VÀ VÀO CỬA SỔ GEMINI...")
            print("⏳ Đang đợi tối đa 10 phút...")
            print("!"*60)
            
            try:
                await page.wait_for_url("**/app**", timeout=600000)
                await page.wait_for_timeout(5000)
                chat_input = page.locator('rich-textarea').first
                await chat_input.wait_for(state="visible", timeout=20000)
                print("✅ TÍN HIỆU XANH: ĐÃ LOGIN GMAIL THÀNH CÔNG.")
            except Exception:
                print("⚠️ Quá 10 Phút Không Login Được. Hủy Nhiệm Vụ Sinh Ảnh.")
                await context.close()
                return None
                
        prompt = f"Tạo cho tôi 1 bức ảnh Infographic cực sắc nét, vuông tỷ lệ 1:1. Chủ đề: '{topic}'. Yêu cầu nội dung: Chuyên nghiệp, số liệu trực quan, thiết kế Modern Corporate B2B, layout sạch phẳng gọn gàng sạch sẽ. Chỉ xuất ra 1 ảnh duy nhất, không thêm hội thoại thừa."
        
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
                
            print("⏳ [Imagen 3] Đang đợi Gemini render ảnh (5 phút)...")
            await page.wait_for_timeout(300000)
            
            print(f"🎯 Đang tìm nút 'Sao chép hình ảnh' qua menu 3 chấm...")
            try:
                await context.grant_permissions(['clipboard-read', 'clipboard-write'])
            except Exception: pass
            
            img_saved = False
            
            # CHIẾN LƯỢC CHÍNH: Click menu 3 chấm → "Sao chép hình ảnh"
            try:
                menus = await page.locator('button[aria-haspopup="menu"]').all()
                if menus:
                    for menu in reversed(menus):
                        try:
                            await menu.scroll_into_view_if_needed()
                            await menu.click()
                            await page.wait_for_timeout(1000)
                            
                            copy_btn = page.locator('text="Sao chép hình ảnh", text="Copy image"').first
                            if await copy_btn.count() > 0 and await copy_btn.is_visible():
                                print("✅ ĐÃ CHỘP ĐƯỢC NÚT 'SAO CHÉP HÌNH ẢNH'. Đang click...")
                                await copy_btn.click()
                                await page.wait_for_timeout(3000)
                                img_saved = True
                                break
                            else:
                                await page.keyboard.press("Escape")
                                await page.wait_for_timeout(500)
                        except Exception: pass
            except Exception as e:
                print(f"❌ Trục trặc khi tìm Menu Gemini: {e}")
                
            if img_saved:
                print("✅ Ảnh đã vào Clipboard qua menu 3 chấm. Sẵn sàng Paste vào Facebook!")
                await context.close()
                return "CLIPBOARD"
            
            # CHIẾN LƯỢC FALLBACK 1: Right-click thẳng vào hình → Copy image
            print("⚠️ Không tìm được nút qua menu 3 chấm. Thử right-click trực tiếp vào hình...")
            
            # TÌM MỌI ẢNH LỚN TRÊN TRANG (Không cần phân biệt googleusercontent)
            image_url = None
            img_locator = None
            for _ in range(15):
                response_images = page.locator('img')
                count = await response_images.count()
                if count > 0:
                    for i in range(count - 1, -1, -1):
                        img_elem = response_images.nth(i)
                        
                        # Kiểm tra kích thước tự nhiên để tránh lấy nhầm icon
                        is_large = await page.evaluate('''el => {
                            return el && el.naturalWidth > 300 && el.naturalHeight > 300;
                        }''', await img_elem.element_handle())
                        
                        if is_large:
                            image_url = await img_elem.get_attribute('src')
                            img_locator = img_elem
                            break
                    if image_url: break
                await page.wait_for_timeout(3000)
                
            if not image_url or not img_locator:
                print("❌ Không tìm thấy ảnh từ Gemini. Đuổi về Pollinations dự phòng.")
                await context.close()
                return None
                
            os.makedirs("fb_images", exist_ok=True)
            save_path = os.path.abspath(os.path.join("fb_images", f"gemini_{int(time.time())}.jpg"))

            print("⏳ Đang tải ảnh NGUYÊN BẢN từ URL gốc (chất lượng cao nhất)...")
            try:
                import requests as req_lib
                cookies_list = await context.cookies()
                cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in cookies_list])
                
                dl_headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                    "Cookie": cookie_header,
                    "Referer": "https://gemini.google.com/",
                }
                resp = req_lib.get(image_url, headers=dl_headers, timeout=60)
                if resp.status_code == 200 and len(resp.content) > 10000:
                    with open(save_path, 'wb') as f:
                        f.write(resp.content)
                    file_size = os.path.getsize(save_path)
                    print(f"✅ Đã tải ảnh NGUYÊN VẸN từ URL gốc ({file_size//1024} KB).")
                    
                    try:
                        import subprocess
                        print("💉 Đang dùng PowerShell ép ảnh vào Clipboard...")
                        abs_save_path = os.path.abspath(save_path).replace('\\', '\\\\')
                        ps_script = f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::SetImage([System.Drawing.Image]::FromFile('{abs_save_path}'))"
                        subprocess.run(["powershell", "-c", ps_script], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        print("✅ Đã bơm ảnh thành công vào Clipboard! Sẵn sàng sang Facebook bấm Ctrl+V.")
                        
                        await context.close()
                        return "CLIPBOARD"
                    except Exception as ps_err:
                        print(f"⚠️ Lỗi ép Clipboard bằng PowerShell: {ps_err}")
                else:
                    print(f"⚠️ Tải URL gốc thất bại (status={resp.status_code}).")
            except Exception as dl_err:
                print(f"⚠️ Lỗi tải URL: {dl_err}.")
                
            print("❌ Tất cả chiến lược tải ảnh đều thất bại. Đuổi về Pollinations dự phòng.")
            await context.close()
            return None
            
        except Exception as flow_err:
            print(f"❌ Luồng Khai Xuất Ảnh Web Đứng Bánh: {flow_err}")
            await context.close()
            return None
