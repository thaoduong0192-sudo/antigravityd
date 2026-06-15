import os
import time
import asyncio
import re

async def automate_notebook_and_drive(browser, topic_str, content_text):
    google_session_file = "google_session.json"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    
    if os.path.exists(google_session_file):
        context = await browser.new_context(storage_state=google_session_file, no_viewport=True, user_agent=user_agent)
        print("\n🔄 Đã khóa mục tiêu Phiên đăng nhập Google Workspace...")
    else:
        print("\n" + "!"*65)
        print("🚨 LẦN ĐẦU KÍCH HOẠT HỆ SINH THÁI NOTEBOOKLM!")
        print("👉 VUI LÒNG ĐĂNG NHẬP GMAIL CỦA ANH TRÊN TRÌNH DUYỆT ĐANG MỞ.")
        print("!"*65)
        
        context = await browser.new_context(no_viewport=True, user_agent=user_agent)
        page = await context.new_page()
        await page.goto("https://accounts.google.com/")
        
        print("⏳ Điểm danh: Đang đợi anh thao tác trên trình duyệt...")
        print("💡 Tự động chạy tiếp khi màn hình Google chuyển thành công (15 Phút).")
        
        try:
            await page.wait_for_url(re.compile(r"myaccount\.google\.com|myactivity\.google\.com|notebooklm", re.IGNORECASE), timeout=900000)
            await page.wait_for_timeout(5000)
            await context.storage_state(path=google_session_file)
            print("✅ Đã sao lưu chứng chỉ đăng nhập Google Vĩnh viễn!")
        except Exception as e:
            print(f"⚠️ Cảnh báo: Quá 15 phút chưa login ({e})")
            await context.storage_state(path=google_session_file)
            
        await page.close()

    await context.grant_permissions(['clipboard-read', 'clipboard-write'])
    page = await context.new_page()
    
    # --- PHASE 1: NOTEBOOKLM ---
    print("\n🚀 Cài cắm Thuật toán vào Google NotebookLM...")
    await page.goto("https://notebooklm.google.com/")
        
    print("\n--------------------------------------------------------------")
    print(" 🕹️ CHẾ ĐỘ CO-PILOT HIỆP LỰC NGƯỜI LÁI ĐƯỢC KÍCH HOẠT 🕹️ ")
    print(" 👁️ Nếu anh thấy Màn hình Chào mừng (Welcome) hay 'Dùng thử NotebookLM' (Try)...")
    print(" 👁️  Anh có thể Click 'Create New Notebook' giúp Tool luôn nhé! Cả 2 cùng Lái OK!")
    print("--------------------------------------------------------------\n")

    # Mắt Thần 1: Dò Nút Thêm Nguồn Đặc Chủng Web
    print("🔎 Đang quét tia tìm Khay Chọn Nguồn Nhập Từ Khóa Web (Chờ Tối Đa 60s)...")
    is_source_box = False
    for i in range(30): 
        try:
            try_btn = page.locator('a:has-text("Dùng thử NotebookLM"), a:has-text("Try NotebookLM")').first
            if await try_btn.count() > 0 and await try_btn.is_visible():
                 await try_btn.click()
                 await page.wait_for_timeout(4000)
        except Exception: pass
        
        try:
            add_src_btn = page.locator('div[role="button"]:has-text("Thêm nguồn"), div[role="button"]:has-text("Add source")').first
            if await add_src_btn.count() > 0 and await add_src_btn.is_visible():
                 await add_src_btn.click()
                 await page.wait_for_timeout(2000)
        except Exception: pass
        
        try:
            search_input = page.locator('input[placeholder*="Tìm nguồn mới trên web"], input[placeholder*="web"], input[type="text"]').last
            if await search_input.count() > 0 and await search_input.is_visible():
                 is_source_box = True
                 break
        except Exception: pass
             
        try:
             for txt in ["Sổ tay mới", "New Notebook", "Tạo sổ tay mới", "Create new notebook", "Notebook Mới", "Tạo mới", "New"]:
                  new_btn = page.locator(f'div[role="button"]:text-is("{txt}"), button:has-text("{txt}"), div:has-text("{txt}")').last
                  if await new_btn.count() > 0 and await new_btn.is_visible():
                       await new_btn.click()
                       await page.wait_for_timeout(3000)
                       break
        except Exception: pass
        
        await page.wait_for_timeout(2000)

    if not is_source_box:
        print("⚠️ Hết 60s dò Mắt Thần không thấy Khay Input Dò Nguồn Web.")
        print("💡 CỨU HỘ: Anh hãy tự ấn Nút Trắng 'Thêm Nguồn' Hoặc tự dán Từ khóa Web Nhé!!!")
        await page.wait_for_timeout(20000)

    # Mắt Thần 2: Nạp Từ Khóa Search Web
    print(f"✅ Đã tóm được Box Tìm Kiếm Nguồn Web. Đang xả từ khóa Nghiên Cứu Chuyên Sâu: [{topic_str}]...")
    is_searched = False
    for i in range(15):
         try:
              search_input = page.locator('input[placeholder*="Tìm nguồn mới trên web"], input[placeholder*="web"], input[type="text"]').first
              if await search_input.count() > 0 and await search_input.is_visible():
                   await search_input.click()
                   for _ in range(30):
                       await page.keyboard.press("Backspace") 
                   
                   await search_input.fill(topic_str)
                   await page.wait_for_timeout(1000)
                   
                   quick_study_btn = page.locator('div[role="button"]:has-text("Nghiên cứu nhanh"), button:has-text("Nghiên cứu nhanh"), span:has-text("Nghiên cứu nhanh")').first
                   if await quick_study_btn.count() > 0 and await quick_study_btn.is_visible():
                        await quick_study_btn.click()
                   else:
                        print("⚠️ Không thấy nút Nghiên Cứu Nhanh. Lệnh Xâm Nhập Bằng Cú Gõ Enter Cháy Cạnh...")
                        await page.keyboard.press("Enter")
                        
                   is_searched = True
                   break
         except Exception as e: 
              print(f"Lỗi Typing Phụ: {e}")
         await page.wait_for_timeout(2000)
         
    if not is_searched:
         print("❌ Không gõ được Từ Khóa Dò Web. Anh em Co-Pilot xin hỗ trợ Cú Click!")
         await page.wait_for_timeout(10000)
         
    print("⏳ Máy Quét Cổng Không Gian Đang Hoạt Động! Đang chờ Model AI Cày Nguồn Lên Ý Tưởng (Khoảng 20-30 giây)...")
    await page.wait_for_timeout(25000) 

    image_path = os.path.abspath(os.path.join("fb_images", f"notebook_info_{int(time.time())}.jpg"))
    os.makedirs("fb_images", exist_ok=True)

    # Mắt Thần 3: Đoạt Infographic & Ép Size 2MB
    print("\n📸 [2/2] Quét Tín Hiệu 'Bản Đồ Họa Thông Tin' (Ánh sáng Dữ liệu)...")
    info_clicked = False
    for i in range(20): 
         try:
             info_btn = page.locator('div[role="button"]:has-text("Bản đồ họa thông tin"), div[role="button"]:has-text("Infographic"), div[role="button"]:has-text("Timeline")').last
             if await info_btn.count() > 0 and await info_btn.is_visible():
                  await info_btn.click()
                  info_clicked = True
                  break
         except Exception: pass
         await page.wait_for_timeout(2000)
         
    if not info_clicked:
         print("⚠️ Nút Đồ Họa Cứng. Chữa cháy Auto-Gõ Bật Render Bằng Chatbot:")
         try:
             chatbox = page.locator('textarea').last
             if await chatbox.count() > 0 and await chatbox.is_visible():
                 await chatbox.fill("Hãy viết một Bản đồ họa thông tin/Infographic ngắn gọn dựa trên dữ liệu Web này.")
                 await page.keyboard.press("Enter")
                 info_clicked = True
         except Exception: pass
         
    if info_clicked:
         print("⏳ Đã Truy Lệnh Ảnh! Đang đợi AI Nội Lực Render Đồ Họa Hiện Lên Khung (Chờ 20s)...")
         await page.wait_for_timeout(20000)
         try:
             blocks = page.locator('div[data-message-author="model"]').last
             if await blocks.count() > 0 and await blocks.is_visible():
                 await blocks.screenshot(path=image_path, type="jpeg", quality=85)
                 print("✅ Đã Chụp JPEG Hoàn Mỹ Khối Infographic Chat!")
             else:
                 await page.screenshot(path=image_path, type="jpeg", quality=85)
                 print("⚠️ Đã Chụp Khối Rộng Toàn Bức Màn Cảm Biến Facebook!")
                 
             # [YÊU CẦU ĐỘC QUYỀN]: NGHÌN CÂN ÉP ẢNH DƯỚI 2MB:
             if os.path.exists(image_path):
                 file_b = os.path.getsize(image_path)
                 if file_b > 2 * 1024 * 1024:
                     print(f"⚠️ Dữ liệu Khối Lượng To: {(file_b/1024/1024):.2f} MB! Ép Code Code Pillow Thắt Hắt Nước Dưới 2MB...")
                     try:
                         from PIL import Image
                         with Image.open(image_path) as img:
                             img = img.convert("RGB")
                             w, h = img.size
                             img = img.resize((int(w * 0.8), int(h * 0.8)), Image.Resampling.LANCZOS)
                             img.save(image_path, "JPEG", quality=75, optimize=True)
                         print(f"✅ Code Siết Đỉnh: Ảnh Infographic Rút Xong, Nặng Cực Thấp: {(os.path.getsize(image_path)//1024)} KB.")
                     except Exception as pe:
                         print(f"❌ Thuật toán Cắt Lõi Bị Tự Chối (Thiếu Tín Hiệu System Pillow): {pe}")
                 else:
                     print(f"✅ Ảnh Infographic Siêu Nhẹ Nặng: {(file_b/1024):.1f} KB. Lọt Khẩu Độ Facebook Tuyệt Đối.")
                                          
         except Exception as ge:
             print(f"❌ Văng Trình Chụp Screen Cục Bộ Màn Hình Chrome! ({ge})")
             image_path = None
    else:
         image_path = None

    await context.close()
    return image_path, None
