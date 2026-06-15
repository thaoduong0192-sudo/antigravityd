import os
import random
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import re
import schedule
import time
import requests
import urllib.parse
from datetime import datetime
import fb_auto_comment
import gemini_image_generator
import openpyxl

# Load cấu hình
load_dotenv()

# Cấu hình Gemini API
GEMINI_API_KEY_FB = os.getenv("GEMINI_API_KEY_FB")
GEMINI_API_KEY = GEMINI_API_KEY_FB if GEMINI_API_KEY_FB else os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("❌ Lỗi: Vui lòng thêm GEMINI_API_KEY_FB (hoặc GEMINI_API_KEY) vào file .env")
    exit(1)

def get_history():
    if os.path.exists("posted_history.txt"):
        with open("posted_history.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            return "".join(lines[-15:])
    return ""

def save_history(topic):
    with open("posted_history.txt", "a", encoding="utf-8") as f:
        f.write(f"- {topic}\n")

def generate_post_content():
    history = get_history()
    current_date = datetime.now().strftime('%d/%m/%Y')
    
    hook_types = [
        "Kiểu A (Storytelling Khác Biệt): Kể 1 câu chuyện CỰC KỲ KHÁC BIỆT VÀ MỚI LẠ về 1 chủ petshop/thú y ngẫu nhiên. (TUYỆT ĐỐI KHÔNG dùng lại văn mẫu 'Hôm qua mình ghé một petshop...', hãy bịa ra bối cảnh mới 100% như đang cà phê, đang lướt mạng, đang xem báo cáo tài chính, có ông anh từ Nhật bay về...)",
        "Kiểu B (Tuyên bố Gây Sốc): Đưa ra 1 Tuyên Bố đi ngược hoàn toàn số đông hiện tại hoặc Phản Biện thẳng mặt một định kiến/sai lầm phổ biến nhất trong ngành Pet đang làm khổ dân kinh doanh.",
        "Kiểu C (Tiêm Nỗi Đau): Đặt ra MỘT câu hỏi ngắn cực mạnh xoáy sâu tận Tâm Can vào nỗi đau Ngầm Nhất của dân kinh doanh Pet khiến họ giật mình nhận ra vấn đề.",
        "Kiểu D (Số liệu Tương Lai): Đưa ra và phân tích 1 Con số Báo Cáo Data Thị trường Châu Á/Quốc tế Mới Nhất (Tự tổng hợp/Tính toán) làm mồi nhử chết người buộc phải đọc tiếp."
    ]
    chosen_hook = random.choice(hook_types)
    
    print(f"\n📝 Khởi tạo Trục Kịch Bản Mới Nhất ({current_date}). Chống Trùng Lặp bằng [{chosen_hook}]...")
    
    prompt = f"""
[CƠ CHẾ KỸ THUẬT AUTO - BẮT BUỘC]
1. Bạn KHÔNG dùng lại các ngách chủ đề cũ sau đây:
{history}
2. Dòng TIÊN QUYẾT ĐẦU TIÊN của file kết quả trả về BẮT BUỘC LÀ:
"TOPIC: [Từ 5 đến 10 từ khóa tìm kiếm Google về xu hướng đó, cách nhau bằng dấu phẩy]" (Đây là lệnh nạp tự động vào NotebookLM).
3. Từ dòng thứ 2 trở xuống, là bài viết Facebook theo sát nguyên tắc bên dưới.

[LỆNH TỐI CẤP VỀ SỰ KHÁC BIỆT - CHỐNG NHÀM CHÁN VÀ LẶP LẠI (CHẾ ĐỘ TÀN BẠO)]
- Lần Nhả Chữ Này, BẮT BUỘC BẠN PHẢI SỬ DỤNG {chosen_hook} ĐỂ LÀM ĐOẠN HOOK MỞ ĐẦU BAO GỒM 3-5 DÒNG TÓ TÉM ĐẦU TIÊN CỦA BÀI VIẾT!!!
- TUYỆT ĐỐI KHÔNG LẶP LẠI CÁCH VIẾT NHƯ: "Hôm qua mình ghé thăm...", "Câu chuyện của chị này không cá biệt...". Nếu tôi bắt được bạn dùng mẫu câu cũ sáo rỗng vô hồn này, bạn sẽ bị Đình Chỉ Vĩnh Viễn. HÃY THA THÚ SÁNG TẠO!
==============================

# PROMPT VIẾT CONTENT FACEBOOK CÁ NHÂN — NGÀNH THÚ CƯNG B2B

## Dùng cho: AI hoặc copywriter viết bài Facebook cá nhân, nhắm đến chủ doanh nghiệp sỉ lẻ / thú y / đại lý B2B ngành pet ngày hôm nay {current_date}.

## 1. BỐI CẢNH & MỤC TIÊU
Bạn là Cố Vấn Tối Cao Thực Chiến Chiến Lược Mạng Lưới Sỉ ngành Thú Cưng tại VN với hơn 20 năm máu mặt kinh nghiệm.
Bài viết đánh thẳng vào TẦM NHÌN, TIỀN TÀI, HOẠT ĐỘNG của:
- Chủ petshop
- Chủ phòng khám thú y
- Người mở xưởng phụ kiện, bán buôn thức ăn.

## 2. PHONG CÁCH VIẾT — "BỤI BẶM THỰC CHIẾN + DATA"
### Giọng văn:
- Nói như đang uống Cafe với đàn em trong nghề — KHÔNG thuyết trình sân khấu.
- Tự tin, đôi lúc xắt xéo thẳng tay, gãi đúng chỗ ngứa.
- Dùng "Mình/Bạn" hoặc "Bác/Shop". KHÔNG dùng "Quý vị, Các Báo Đối tác Tiên Phong".

### CẤU TRÚC 5 PHẦN SIÊU TỐC TRÊN ĐIỆN THOẠI
Phần 1: HOOK (Chính là Cái Lệnh Bắt Buộc Dùng Phía Trên Được Chọn). Sốc & Ngắn gọn. Sau đó Cách 1 Dòng.
Phần 2: Nỗi đau/Bối cảnh đang bủa vây Dân Petshop (Rất Đồng Cảm).
Phần 3: Insight Khác Biệt & Data Dẫn Lối (VD Mars Petcare / Phân Tích Thực Tiễn Kho Bãi).
Phần 4: Giải pháp Chốt Hạ Khôn Ngoan làm ngay ngày mai (Gạch đầu dòng bằng Dấu Mũi Tên -> Lôi Kéo Sức Mua Khách Sỉ).
Phần 5: KẾT bằng 1 Câu Đinh Đóng Cột (IN HOA) và 1 Câu Mở Nhờ Tương Tác Của Cả Làng Nhảy Vào Comment Cho Xôm Tụ. Kèm 3 Tag Đặc Sắc Dân Buôn Pet.

## QUY TẮC RĂN ĐE TRÌNH BÀY HÌNH ẢNH FACEBOOK THUẦN TÚY:
- Câu Rất Ngắn (Tối đa 15 Từ 1 câu, Ngắt Ý Nhanh).
- Tường Facebook là chữ thuần tĩnh Plain Text. Gạch Đầu dòng bằng Dấu Trừ (-) HOẶC 1 Số Emoji Cơ Bản Lịch Sự. 
- KHÔNG BAO GIỜ VIẾT ĐÁNH DẤU MARKDOWN (Lỗi Bôi Đậm Facebook Sẽ Xóa Trắng!). KHÔNG dùng dấu Bôi đậm **.
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            result = response.text.strip()
            
            topic_match = re.search(r"TOPIC:\s*(.+)", result)
            topic_str = topic_match.group(1) if topic_match else "xu hướng kinh doanh thú cưng chiến lược petshop"
            
            final_content = re.sub(r"TOPIC:\s*(.+)\n*", "", result)
            
            final_content = final_content.replace('**', '')
            final_content = final_content.replace('*', '')
            final_content = final_content.replace('###', '')
            final_content = final_content.replace('##', '')
            
            save_history(topic_str)
            return final_content.strip(), topic_str.strip()
            
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "retry" in error_msg or "429" in error_msg:
                print(f"⏳ Hết Token do Free Tier. Đợi 60s hồi sinh lực (Lần {attempt+1}/{max_retries})...")
                time.sleep(65)
            else:
                print(f"Lỗi Sinh Content: {e}")
                return None, None
                
    print("❌ Lỗi mạng AI Generator.")
    return None, None


def generate_self_comments(post_content, count=10):
    print(f"\n💬 Đang chuẩn bị {count} bình luận bổ trợ để tăng tương tác và giá trị cho bài viết...")
    current_date = datetime.now().strftime('%d/%m/%Y')
    
    prompt = f"""
[LỆNH TỐI CẤP: SINH BÌNH LUẬN TỰ TƯƠNG TÁC (SELF-ENGAGEMENT B2B)]
Bạn là "Tuệ Đan" - Một chuyên gia lão luyện trong ngành sỉ Petshop và Thú y. Hãy viết {count} bình luận bổ trợ để tự đăng dưới bài viết của mình.

NỘI DUNG BÀI VIẾT CHÍNH:
"{post_content}"

[YÊU CẦU VỀ NỘI DUNG BÌNH LUẬN - MỞ RỘNG GIÁ TRỊ TỐI ĐA]
1. Mang tính mở rộng: Mỗi bình luận PHẢI đào sâu thêm một khía cạnh mà bài viết chính chưa có. Giúp người đọc hiểu sâu tận gốc vấn đề và thấy rõ giải pháp mang lại tiền bạc/sức khỏe cho thú cưng như thế nào.
2. Đa dạng góc nhìn (Thực chiến): 
   - 4 câu "Đào sâu kỹ thuật/Y khoa": Phân tích tại sao vấn đề đó lại xảy ra, cơ chế sinh học hoặc sai lầm trong chăm sóc.
   - 4 câu "Đào sâu kinh doanh/Sỉ": Phân tích tại sao chủ shop nên nhập hàng này, biên độ lợi nhuận, cách tư vấn khách lẻ để chốt đơn nhanh.
   - 2 câu "Kết nối & Cam kết": Khẳng định chất lượng và sự đồng hành của Tuệ Đan với anh em trong nghề.
3. Phong cách: Thẳng thắn, sâu sắc, kiến thức chuyên sâu nhưng dễ hiểu. Tông giọng của một người "đã từng trải" và muốn giúp đỡ đàn em.
4. Quy tắc trình bày: 
   - KHÔNG markdown (**), không hashtags (#).
   - Tuyệt đối không có câu chào hỏi sáo rỗng. Vào thẳng vấn đề bổ sung.
   - TRẢ VỀ DƯỚI DẠNG DANH SÁCH, mỗi bình luận trên một dòng, bắt đầu bằng [CMT].
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        raw_res = response.text.strip()
        
        comments = []
        for line in raw_res.split('\n'):
            if '[CMT]' in line:
                comment = line.replace('[CMT]', '').strip()
                if comment:
                    comments.append(comment)
        
        # Đảm bảo đủ số lượng, nếu không đủ thì lấy subset hoặc clone
        if len(comments) < count:
             print(f"⚠️ Chỉ sinh được {len(comments)}/10 comment. AI có vẻ đang tiết kiệm lời.")
        
        return comments[:count]
        
    except Exception as e:
        print(f"Lỗi Sinh Bình Luận Tự Động: {e}")
        return []


def generate_infographic_image(content, topic):
    print("\n🎨 KÍCH HOẠT MÁY CHỦ ÁNH SÁNG POLLINATIONS AI (SẢN XUẤT INFOGRAPHIC B2B NÉT CAO)...")
    
    prompt_gen = f"Translate the core idea of this topic into exactly 5-8 descriptive English keywords (alphabet only, no punctuation, focus on business or animals): '{topic}'"
    
    image_prompt = ""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt_gen)
            raw = response.text.strip()
            image_prompt = re.sub(r'[^a-zA-Z0-9 ]', '', raw)
            break
        except Exception:
             time.sleep(60)
                 
    if not image_prompt:
         image_prompt = "veterinary pet shop management business"

    save_path = os.path.abspath(os.path.join("fb_images", f"infographic_{int(time.time())}.jpg"))
    os.makedirs("fb_images", exist_ok=True)
    
    prompts_to_try = [
        f"A highly professional vector infographic about {image_prompt}. Clean modern data visualization, icons, minimalist corporate layout, white background, high quality, flat design mockup, B2B pet industry",
        f"Petshop business concept flat vector illustration, {image_prompt}. UI UX dashboard style, pastel colors, white background, professional infographics layout",
        f"Veterinary clinic and pet care business flat vector infographic, clean minimalist layout, data charts, modern icons, {image_prompt}"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    }
    
    for i, pt in enumerate(prompts_to_try):
        random_seed = random.randint(1, 999999)
        safe_pt = urllib.parse.quote(pt)
        image_url = f"https://image.pollinations.ai/prompt/{safe_pt}?nologo=true&seed={random_seed}"
        
        try:
            print(f"⌛ [Tầng {i+1}/3] Đang kiên nhẫn đợi rèn ảnh Sinh Học (Cho phép chờ tối đa 5 phút)...")
            response = requests.get(image_url, headers=headers, timeout=310)
            if response.status_code == 200:
                img_data = response.content
                if img_data.startswith(b'\xff\xd8') or img_data.startswith(b'\x89PNG') or img_data[8:12] == b'WEBP':
                    with open(save_path, 'wb') as handler:
                        handler.write(img_data)
                        
                    print("🔪 Quá trình Render hoàn tất. Bắt đầu kích hoạt Cỗ Máy Nén Pillow Ép Ảnh Infographic Chuẩn Format Facebook...")
                    try:
                        from PIL import Image
                    except ImportError:
                        import subprocess, sys
                        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"], stdout=subprocess.DEVNULL)
                        from PIL import Image
                        
                    with Image.open(save_path) as img:
                        img = img.convert("RGB")
                        # Đảm bảo ảnh Vuông Tỷ Lệ Đẹp với Dung lượng Cực Thấp (Dưới 2MB theo lệnh User)
                        img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
                        img.save(save_path, "JPEG", quality=85, optimize=True)
                        
                    file_size = os.path.getsize(save_path)
                    print(f"✅ Bức Ảnh Infographic Chuẩn 1024x1024 siêu nét và cực nhẹ: {file_size//1024} KB. Sẵn sàng lên sóng!")
                    return save_path
        except Exception as e:
            print(f"⚠️ Tranh vẽ văng lỗi (Từ chối mạng): {e}")
            pass
        
        print(f"⚠️ Server mất quá hạn chưa xong. Hạ cấp xuống Tầng {i+2}...")
        time.sleep(1)
        
    print("❌ API Ảnh AI đang sập mạng cục bộ. Đang dùng phương án Cứu Hộ API Thú cưng Quốc Tế...")
    try:
        res = requests.get("https://api.thecatapi.com/v1/images/search", headers=headers, timeout=10).json()
        img_data = requests.get(res[0]['url'], headers=headers, timeout=15).content
        if img_data.startswith(b'\xff\xd8') or img_data.startswith(b'\x89PNG') or img_data[8:12] == b'WEBP':
             with open(save_path, 'wb') as handler:
                  handler.write(img_data)
             print("✅ Đã lấy thành công ảnh thật Cat/Dog để chữa cháy Bài Viết!")
             return save_path
    except Exception as e:
        print(f"❌ Cứu hộ thú cưng cũng gãy: {e}")

    return None


async def post_to_facebook(browser, content, image_path=None, comments=None):
    print("\n🚀 [4/4] BẮT ĐẦU CHIẾN DỊCH FACEBOOK AUTO CHỐT ĐĂNG MẠNH MẼ...")
    session_file = "fb_session.json"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    if os.path.exists(session_file):
        context = await browser.new_context(storage_state=session_file, no_viewport=True, user_agent=user_agent)
        print("🔄 Đã Nhận Thẻ Căn Cước Facebook Trọn Đời (Không Bắt Login Lại)...")
    else:
        print("⚠️ HỆ THỐNG PHÁT HIỆN LẦN ĐẦU CHẠY FACEBOOK! HÃY ĐĂNG NHẬP (Chỉ Cần Làm 1 Lần Duy Nhất).")
        context = await browser.new_context(no_viewport=True, user_agent=user_agent)
            
    page = await context.new_page()
    
    print("Đang bẻ lái vào Tường Facebook...")
    try:
        await page.goto("https://www.facebook.com/", timeout=120000)
    except Exception:
        pass
    
    feed_ready = False
    try:
        feed_box_check = page.locator('div[role="button"]:has-text("Bạn đang nghĩ gì"), div[role="button"]:has-text("What\'s on your mind")').first
        await feed_box_check.wait_for(state="visible", timeout=20000)
        feed_ready = True
    except Exception:
        pass

    if not feed_ready:
        print("\n" + "!"*55)
        print("🚨 KHÔNG THẤY TƯỜNG (HOẶC VƯỚNG BỘ LỌC BẢO MẬT FB - CẦN ĐĂNG NHẬP)!")
        
        fb_email = os.getenv("FB_EMAIL")
        fb_pass = os.getenv("FB_PASSWORD")
        email_input = page.locator('input[name="email"], input[id="email"], input[type="text"]')
        pass_input = page.locator('input[name="pass"], input[id="pass"], input[type="password"]')
        
        if fb_email and fb_pass and await email_input.count() > 0:
            print(f"🤖 HỆ THỐNG PHÁT HIỆN TÀI KHOẢN TRONG .ENV: TỰ ĐỘNG TIÊM MẬT KHẨU CHO [{fb_email}]...")
            await email_input.first.click()
            await page.keyboard.insert_text(fb_email)
            await page.wait_for_timeout(500)
            if await pass_input.count() > 0:
                await pass_input.first.click()
                await page.keyboard.insert_text(fb_pass)
                await page.wait_for_timeout(500)
            await page.keyboard.press("Enter")
            print("⏳ Đã tự động nạp Mật Khẩu và Gõ Enter! Cắm Chốt Bẻ Khóa...")
            print("⚠️ LƯU Ý: NẾU BỊ FACEBOOK HỎI MÃ XÁC NHẬN 2FA TỪ ĐIỆN THOẠI, ANH PHẢI TỰ COPY MÃ VÀO VÀ BẤM TIẾP TỤC!")
        else:
            print("👉 LƯU Ý KỸ: Tool chưa được anh cấp FB_EMAIL và FB_PASSWORD ở file .env (Để hệ thống tự Login).")
            print("👉 VUI LÒNG TỰ CLICK CHUỘT TRÊN MÀN HÌNH BẬT LÊN NÀY ĐỂ ĐĂNG NHẬP BẰNG TAY VÀO LÚC NÀY.")
            
        print("⚠️ Đang Bật Đồng Hồ Chờ FB Mở Tường (Tối đa 15 Phút Không Xong Sẽ Hủy Bỏ Lược Phím Này).")
        
        try:
            feed_box_wait = page.locator('div[role="button"]:has-text("Bạn đang nghĩ gì"), div[role="button"]:has-text("What\'s on your mind")').first
            # Đợi lên tới 15 Phút
            await feed_box_wait.wait_for(state="visible", timeout=900000)
            await page.wait_for_timeout(5000)
        except Exception:
            print("⚠️ Quá hạn chờ tài khoản FB! Phiên sẽ tự Hủy. Tiến hành xóa tệp Session cũ để làm mới lần sau...")
            try:
                if os.path.exists(session_file):
                    os.remove(session_file)
            except: pass
            await context.close()
            return
        
        await context.storage_state(path=session_file)
        print("💾 Đã khóa Cookie Facebook vĩnh viễn vào tệp tin!")
    
    await page.wait_for_timeout(3000)
    
    # 1. Bật Bảng Nhập Liệu Chữ FB
    try:
        post_box = page.locator('div[role="button"]:has-text("Bạn đang nghĩ gì"), div[role="button"]:has-text("What\'s on your mind")').first
        if await post_box.count() > 0:
            await post_box.click(timeout=10000)
            await page.wait_for_timeout(3000)
        else:
             await page.mouse.click(640, 600)
             await page.wait_for_timeout(4000)
             
        # BƯỚC QUAN TRỌNG TỐI THƯỢNG: ÉP LẮP ẢNH TỰ ĐỘNG
        if image_path == "CLIPBOARD":
            print(f"🔗 Đang Dán Bức Ảnh Tuyệt Phẩm Trực Tiếp TỪ BỘ NHỚ ĐỆM (Ctrl+V) Theo Mật Lệnh User...")
            await page.keyboard.press("Control+V")
            print("⏳ Chờ 10 giây cho Khối Ảnh Tải Lên Thành Công Từ Clipboard vào máy chủ Facebook...")
            await page.wait_for_timeout(10000)
        elif image_path and os.path.exists(image_path):
            print(f"🔗 Đang Ép Tệp Ảnh Cứng Vào Bảng Mạch Clipboard Của Windows Để Chạy Dán Trực Tiếp (Ctrl+V)...")
            try:
                import subprocess
                abs_save_path = os.path.abspath(image_path).replace('\\', '\\\\')
                ps_script = f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::SetImage([System.Drawing.Image]::FromFile('{abs_save_path}'))"
                subprocess.run(["powershell", "-c", ps_script], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                print("✅ Đã Bơm Ảnh Thành Công Vào Clipboard! Đang Dán Ctrl+V vào bảng tin...")
                await page.keyboard.press("Control+V")
                print("⏳ Chờ 15 giây cho Khối Ảnh Tải Lên Thành Công Từ Clipboard vào máy chủ Facebook...")
                await page.wait_for_timeout(15000)
            except Exception as ev:
                print(f"⚠️ Bị Kẹt Lỗi Bơm Clipboard ({ev}). Đang Chuyển Sang Ép Mã Định Dạng Xuyên Màn Chìm Vào Thẻ Gốc!")
                try:
                    # Cách 2: Tiêm thẳng thẻ DOM Input Cứng Đội Mũ
                    await page.locator('input[type="file"]').last.set_input_files(image_path)
                    print("✅ Tiêm Cứng Nền Thẻ Mở Chéo Trực Diện Hoàn Tất.")
                    print("⏳ Chờ Mạng Đám Mây Của Hệ Thống Meta Render Và Cắt Ảnh Trực Quan... (Nín Thở Khoảng 15s)")
                    await page.wait_for_timeout(15000)
                except Exception as ef:
                    print(f"❌ XÚC ĐỘNG MẠNH: FB Không cho Load Tệp Ảnh Gửi: {ef}")

        # 2. XONG CAMERA RỒI MỚI CHUẨN BỊ BÚT VIẾT! ĐỂ BÀI ĐĂNG KHÔNG BỊ TRỐNG CHỮ HAY F5 LOẠN XẠ!
        print("⏳ Ảnh Vừa Vào Chuồng An Toàn! Đang Đổ Mực Cấy Ghép Từng Nét Chữ B2B Trọng Liên Lên Đỉnh Khung Bài Đăng...")
        textbox = page.locator('div[contenteditable="true"][role="textbox"], div[aria-label*="Bạn đang nghĩ gì"], div[aria-label*="What\'s on your mind"]').first
        
        if await textbox.count() > 0:
            await textbox.click(force=True)
            await page.keyboard.insert_text(content)
        else:
            await page.keyboard.insert_text(content)
            
        await page.wait_for_timeout(4000)
                
        print("📤 Truyền Lệnh Kích Chốt Đăng Dữ Liệu Tường...")
        next_btn = page.locator('div[aria-label="Tiếp"][role="button"], div[aria-label="Next"][role="button"], div[role="button"]:text-is("Tiếp"), div[role="button"]:text-is("Next")').first
        if await next_btn.count() > 0 and await next_btn.is_visible():
            print("⚠️ Bước Tùy chọn đối tượng phụ: Kích hoạt Nút [Tiếp]...")
            try:
                await next_btn.click(timeout=15000)
                await page.wait_for_timeout(3000)
            except Exception:
                await next_btn.click(force=True)
            
        post_btn = page.locator('div[aria-label="Đăng"][role="button"], div[aria-label="Post"][role="button"], div[role="button"]:text-is("Đăng"), div[role="button"]:text-is("Post")').first
        if await post_btn.count() == 0:
            post_btn = page.get_by_role("button", name=re.compile(r"^(Đăng|Post)$", re.IGNORECASE))
        
        if await post_btn.count() > 0:
            try: 
                print("⏳ Máy Quét Trí Tuệ Facebook Đang Rà Soát (Vui Lòng Im Lặng Chờ FB Mở Khóa Nút Đăng Lên)..")
                await post_btn.click(timeout=40000)
                print("✅ [ĐÃ XUYÊN THỦNG HỆ THỐNG] NÚT ĐĂNG ĐÃ KÍCH! Đồng hồ bắt đầu xoay 15s cho Facebook lưu vào máy chủ Mã Hóa...")
                await page.wait_for_timeout(15000) 
            except Exception as post_err:
                print(f"Lỗi Kháng Cự Nút Đăng (bị che lấp): {post_err}")
                await page.wait_for_timeout(60000)
        else:
             print("🔴 Cứu hộ Vỡ Trận: DOM Không thấy Nút Đăng, Bạn phải tự Bấm Nút Bằng Chuột Nhé!")
             await page.wait_for_timeout(60000)
        
        # --- PHẦN MỚI: TỰ BÌNH LUẬN 10 TIN NHẮN ---
        if comments and len(comments) > 0:
            print(f"\n💬 Đã kích hoạt chế độ Tự Gợn Sóng: Đang chuẩn bị rải {len(comments)} bình luận giá trị...")
            await page.wait_for_timeout(10000) # Đợi 10s cho FB ổn định bài đăng
            
            print("🏠 Đang di chuyển vào Trang Cá Nhân để tìm bài viết vừa đăng...")
            try:
                await page.goto("https://www.facebook.com/me", timeout=60000)
                await page.wait_for_timeout(5000)
                
                # Cố gắng tìm bài viết vừa đăng (bài đầu tiên trên profile)
                for attempt in range(1, 4):
                    print(f"🔍 [Lần {attempt}] Đang truy quét bài viết mới nhất trên tường...")
                    # Cuộn xuống một chút để kích hoạt load
                    await page.mouse.wheel(0, 300)
                    await page.wait_for_timeout(2000)
                    
                    post_article = page.locator('div[role="article"]').first
                    if await post_article.count() > 0:
                        await post_article.scroll_into_view_if_needed()
                        print("✅ Đã xác định được khối bài viết. Đang tìm ô nhập liệu...")
                        
                        # Nhấn bộ phím tắt J + C là cách an toàn nhất Facebook luôn hỗ trợ
                        await page.keyboard.press("Escape")
                        await page.wait_for_timeout(500)
                        
                        await page.keyboard.press("j")
                        await page.wait_for_timeout(2000)
                        await page.keyboard.press("c")
                        await page.wait_for_timeout(2000)

                        active_is_textbox = await page.evaluate('''() => {
                            const active = document.activeElement;
                            if (active && (active.getAttribute('contenteditable') === 'true' || active.getAttribute('role') === 'textbox')) {
                                return true;
                            }
                            return false;
                        }''')
                        
                        if not active_is_textbox:
                            print("🖱️ Phím tắt chưa ăn, rà tìm nút Bình Luận vật lý...")
                            comment_btn = post_article.locator('div[role="button"]:has-text("Bình luận"), div[role="button"]:has-text("Comment")').first
                            if await comment_btn.count() > 0:
                                await comment_btn.click(force=True)
                                await page.wait_for_timeout(2000)
                                
                            textboxes = post_article.locator('div[role="textbox"][contenteditable="true"]')
                            if await textboxes.count() > 0:
                                await textboxes.last.click(force=True)
                                await page.wait_for_timeout(1000)
                                active_is_textbox = True
                        
                        if active_is_textbox:
                            print(f"🚀 Bắt đầu đổ bộ {len(comments)} comment...")
                            for idx, cmt in enumerate(comments, 1):
                                try:
                                    print(f"👉 [{idx}/{len(comments)}] Gửi: {cmt[:50]}...")
                                    
                                    # Gõ trực tiếp bằng bàn phím
                                    await page.keyboard.insert_text(cmt)
                                    await page.wait_for_timeout(1500)
                                    await page.keyboard.press("Enter")
                                    
                                    # Nghỉ ngơi giữa các comment (1-3 phút)
                                    sleep_time = random.randint(60000, 180000)
                                    print(f"⏳ Nghỉ ngơi {sleep_time//1000} giây trước khi rải tiếp...")
                                    await page.wait_for_timeout(sleep_time)
                                    
                                    # Kích hoạt lại Focus để sãn sàng bình luận tiếp...
                                    await page.keyboard.press("c")
                                    await page.wait_for_timeout(2000)
                                except Exception as eidx:
                                    print(f"⚠️ Lỗi ở comment {idx}: {eidx}")
                            
                            print("✨ NHIỆM VỤ HOÀN THÀNH: Đã rải đủ 10 bình luận 'Tăng Reach'!")
                            break
                        else:
                            print("❌ Vẫn không tìm thấy ô nhập bình luận. Đang thử lại...")
                    else:
                        print(f"⚠️ Chưa thấy bài viết nào. Chờ thêm 5s...")
                        await page.wait_for_timeout(5000)
                        
            except Exception as ecmt:
                print(f"⚠️ Gặp lỗi nghiêm trọng khi đang tự comment: {ecmt}")

    except Exception as e:
        print(f"❌ Khúc mắc Màn Cấu Rỉa Dom FB: {e}")
        
    await context.close()


def get_next_reel():
    import os, csv, re
    folder_path = r"D:\Antigravity\ecopets_seo\video"
    csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.csv')]
    if not csv_files:
        print(f"❌ Không tìm thấy file CSV trong {folder_path}")
        return None, None, None
    csv_path = os.path.join(folder_path, csv_files[0])
    
    posted_log_path = os.path.join(folder_path, "posted_reels.txt")
    posted_videos = set()
    if os.path.exists(posted_log_path):
        with open(posted_log_path, "r", encoding="utf-8") as f:
            posted_videos = set(line.strip().lower() for line in f)

    video_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp4')]
    
    def extract_num(filename):
        m = re.search(r'\d+', filename)
        return int(m.group()) if m else 9999
    video_files.sort(key=extract_num)

    for video_file in video_files:
        if video_file.lower() not in posted_videos:
            num = extract_num(video_file)
            if num != 9999:
                 video_path = os.path.join(folder_path, video_file)
                 caption = ""
                 try:
                     with open(csv_path, 'r', encoding='utf-8-sig') as f:
                         reader = csv.reader(f)
                         rows = list(reader)
                         if num - 1 < len(rows):
                             row_data = rows[num - 1]
                             if len(row_data) >= 12: 
                                 caption = row_data[11]
                 except Exception as e:
                     print(f"Lỗi đọc file CSV: {e}")
                 
                 return video_path, str(caption).strip(), video_file
                 
    return None, None, None


def mark_reel_as_posted(video_filename):
    import os
    folder_path = r"D:\Antigravity\ecopets_seo\video"
    posted_log_path = os.path.join(folder_path, "posted_reels.txt")
    with open(posted_log_path, "a", encoding="utf-8") as f:
        f.write(str(video_filename) + "\n")


async def post_reel_to_facebook(browser, video_path, caption):
    import os
    print(f"\n🚀 BẮT ĐẦU CHIẾN DỊCH ĐĂNG REEL TỰ ĐỘNG: {video_path}")
    session_file = "fb_session.json"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    if os.path.exists(session_file):
        context = await browser.new_context(storage_state=session_file, no_viewport=True, user_agent=user_agent)
    else:
        print("⚠️ CHƯA CÓ SESSION ĐĂNG NHẬP! Reel không thể dùng account rỗng. Hãy chạy Đăng Bài trước để Login.")
        return False
        
    page = await context.new_page()
    try:
        print("Đang điều hướng đến trang tạo Thước Phim (Reels)...")
        await page.goto("https://www.facebook.com/reels/create", timeout=60000)
        await page.wait_for_timeout(5000)
        
        print("Đang tải lên Video MP4 vào thẻ ẩn Browser...")
        file_input = page.locator('input[type="file"][accept*="video"]').first
        if await file_input.count() > 0:
            await file_input.set_input_files(video_path)
            print("✅ Đã tiêm video vào DOM.")
            await page.wait_for_timeout(10000)
        else:
             print("❌ Không tìm thấy thẻ Input tải video Reel. Giao diện FB thay đổi hoặc mạng đang chậm!")
             await context.close()
             return False
             
        print("Đang cài cắm nội dung Caption vào Reel...")
        # Ấn nút [Tiếp] (Next) sau khi upload xong video (Trang 1: Chỉnh sửa cơ bản)
        next_btn = page.locator('div[aria-label="Tiếp"][role="button"], div[aria-label="Next"][role="button"], div[role="button"]:has-text("Tiếp"), div[role="button"]:has-text("Next")').first
        if await next_btn.count() > 0:
             await next_btn.click()
             await page.wait_for_timeout(3000)
             
        # Ấn nút [Tiếp] (Next) lần 2 (Trang 2: Chỉnh sửa âm thanh / Trim)
        if await next_btn.count() > 0 and await next_btn.is_visible():
             await next_btn.click()
             await page.wait_for_timeout(3000)

        # Chèn văn bản vào hộp textbox (Trang cuối: Mô tả & Đăng)
        textbox = page.locator('div[contenteditable="true"][role="textbox"], div[aria-label*="Mô tả"], div[aria-label*="mô tả"], div[aria-label*="Describe"]').first
        if await textbox.count() > 0:
            await textbox.click(force=True)
            if caption:
                await page.keyboard.insert_text(caption)
                print("✅ Đã chèn Caption thành công!")
            await page.wait_for_timeout(3000)
        else:
            print("⚠️ Không tìm thấy ô nhập mô tả Reel. Bỏ qua bước Caption.")

        # Nút Đăng (Publish)
        publish_btn = page.locator('div[aria-label="Đăng"][role="button"], div[aria-label="Publish"][role="button"], div[role="button"]:has-text("Đăng"), div[role="button"]:has-text("Publish")').first
        if await publish_btn.count() > 0:
             print("⏳ Đang chuẩn bị xả nút Đăng cuối cùng...")
             await publish_btn.click(timeout=30000)
             print("✅ [THƯỚC PHIM ĐÃ KÍCH HOẠT] Chờ Facebook Render Reel mới (15s)...")
             await page.wait_for_timeout(15000)
             await context.close()
             return True
        else:
             print("❌ Không thấy Nút Đăng Thước Phim. DOM Mạng gặp vấn đề.")
    except Exception as e:
         print(f"❌ Xảy ra lỗi khi đăng Reel: {e}")
         
    await context.close()
    return False


async def core_ecosystem_pipeline():
    print(f"\n=================================================")
    print(f"🕒 [{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] KÍCH HOẠT HỆ SINH THÁI TỰ ĐỘNG B2B V8 (MẮT THẦN IMAGEN 3 TỐI TÂN).")
    print(f"=================================================")
    
    content, topic = generate_post_content()
    if not content:
        return
        
    print("\n" + "="*50)
    print(" 🎨 GIAI ĐOẠN 1: MỞ CỔNG SINH ẢNH GOOGLE GEMINI ADVANCED WEB")
    print("="*50)
    # Tách biệt tiến trình Gemini với FB, sử dụng bộ nhớ thư mục vật lý để chống Google quét Cookie Ảo
    image_path = await gemini_image_generator.generate_imagen3_infographic(topic)
    
    if not image_path or not os.path.exists(image_path):
         print("\n⚠️ Đột Nhập Gemini Pro Không Có Khối Ảnh. Khởi động Lò Rèn Hình Học Trực Tiếp Pollinations AI Dự Phòng Cho Tường...")
         image_path = generate_infographic_image(content, topic)
             
    print("\n" + "="*50)
    print(" 🎯 GIAI ĐOẠN 2: DỘI BOM NỘI DUNG LÊN BẢNG TIN TƯỜNG CÁ NHÂN")
    print("="*50)
    
    async with async_playwright() as p:
        args = ['--disable-blink-features=AutomationControlled', '--start-maximized', '--window-size=1600,1000']
        try:
            browser = await p.chromium.launch(headless=False, channel="chrome", args=args)
        except Exception:
            # Fallback nếu máy không cài sẵn Google Chrome gốc
            browser = await p.chromium.launch(headless=False, args=args)
            
        # SINH BÌNH LUẬN TRƯỚC KHI VÀO TRẬN FB
        comments = generate_self_comments(content, count=10)
        
        await post_to_facebook(browser, content, image_path, comments)
        await browser.close()
        
    print(f"✅ HOÀN LỚP VÒNG LẶP ĐĂNG BÀI. Hệ Thống Dịch Chuyển Theo Khung Hẹn Định Tự Vào Giấc Ngủ...")

def execute_daily_posting():
    asyncio.run(core_ecosystem_pipeline())

def execute_random_comment():
    print(f"\n[🕒 HÊ THỐNG NHẮC VIỆC] Đã đến giờ Lên Đạn Đi Tuần - Bắt đầu Dạo Chơi Facebok Tracking...")
    try:
        asyncio.run(fb_auto_comment.run_auto_comment())
    except Exception as e:
        print(f"❌ Lỗi Nhiệm vụ Rải Thính: {e}")

def execute_fanpage_care():
    print(f"\n[🕒 HÊ THỐNG NHẮC VIỆC] Đã đến Chu Kỳ 3 Ngày - Bắt đầu Chăm Sóc Fanpage Sân Nhà Ecopets...")
    try:
        asyncio.run(fb_auto_comment.run_fanpage_comment())
    except Exception as e:
        print(f"❌ Lỗi Nhiệm vụ Chăm Fanpage: {e}")


async def core_reels_pipeline():
    print(f"\n=================================================")
    print(f"🕒 [{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] KÍCH HOẠT LÒ ĐĂNG REELS TỰ ĐỘNG B2B.")
    print(f"=================================================")
    video_path, caption, row_idx = get_next_reel()
    
    if not video_path:
        print("ℹ️ Kho Reels đã hết video mới hoặc không tìm thấy theo danh sách.")
        return
        
    async with async_playwright() as p:
        args = ['--disable-blink-features=AutomationControlled', '--start-maximized']
        try:
            browser = await p.chromium.launch(headless=False, channel="chrome", args=args)
        except Exception:
            browser = await p.chromium.launch(headless=False, args=args)
            
        success = await post_reel_to_facebook(browser, video_path, caption)
        await browser.close()
        
        if success:
             mark_reel_as_posted(row_idx)
             print(f"✅ Reel ở dòng {row_idx} ({os.path.basename(video_path)}) đã được đổi trạng thái DONE trên File Excel!")


def execute_daily_reels():
    asyncio.run(core_reels_pipeline())

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "="*80)
    print(" 🌟 SOCIAL MEDIA BOT V6.0 (Tương Tác Nghệ Thuật - Nắm Cán Toàn Bộ B2B) 🌟")
    print("="*80 + "\n")
    
    schedule.every().day.at("08:00").do(execute_daily_posting)
    schedule.every().day.at("20:00").do(execute_daily_posting)
    
    # Quy trình 2: Rải bom bình luận dạo mỗi 30 phút rải rác
    schedule.every(30).minutes.do(execute_random_comment)
    
    # Quy trình 3: Chăm sóc Fanpage 3 ngày/lần
    schedule.every(3).days.do(execute_fanpage_care)
    
    # Quy trình 4: Đăng Reel mỗi trưa và tối muộn
    schedule.every().day.at("11:30").do(execute_daily_reels)
    schedule.every().day.at("21:30").do(execute_daily_reels)
    
    print("[HỆ THỐNG TRUYỀN LỆNH]: ÉP MẠCH GIAO TRANH CHO CHUỲ DUYỆT BÀI ĐĂNG CỦA BOT...")
    execute_daily_posting()
    
    print("\n" + "="*80)
    print("🟢 TIẾN TRÌNH LÕI TRONG NHÂN (BACKGROUND PROCESS RUNNING)")
    print("🚨 Tool Mổ Não Đang Ngủ Ngầm Bám Đuôi Facebook Liên Tục - Phá Vòng Lặp. Tuyệt đối không Tắt Màn Hình Này.")
    print("="*80 + "\n")
    
    while True:
        schedule.run_pending()
        time.sleep(30)
