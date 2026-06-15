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
    
    tang_choi = random.choice(["🟢 (Trải nghiệm thật)", "🟡 (Đang học chưa làm)", "🔵 (Mời cộng đồng thử)", "🟢🟡 (Trải nghiệm + Đang học)"])
    nhom_chu_de = random.choice([
        "NHÓM 1: AI x GIEO HẠT GIỐNG TÂM HỒN (Câu chuyện giáo dục, 8 tố chất)",
        "NHÓM 2: AI x TẠO DUYÊN LÀNH CHO CON (Ăn dặm, âm nhạc, app kể chuyện)",
        "NHÓM 3: AI x QUẢN TRỊ GIA ĐÌNH ĐA THẾ HỆ (Xung đột ông bà, giao tiếp)",
        "NHÓM 4: AI x PHÁT TRIỂN THÂN - TÂM - TRÍ (Lộ trình phát triển)",
        "NHÓM 5: AI x THUẬT QUẢNG BÁ HÀNH TRÌNH MẸ (Xây cộng đồng, lan tỏa)"
    ])
    
    command = f"Viết bài {tang_choi} về: {nhom_chu_de}"
    
    print(f"\n📝 Khởi tạo Trục Kịch Bản Nhân Duyên Quả ({current_date}): [{command}]...")
    
    prompt = f"""
Bạn là một cỗ máy viết content Facebook được thiết kế riêng cho Hương (Huong Gnouh) — mẹ bỉm 26 tuổi.
Hương đang học hỏi và chia sẻ hành trình nuôi dạy con Bư (14 tháng tuổi, sinh 16/01/2025).

═══════════════════════════════════════
VỀ TÔI — CONTEXT BẮT BUỘC
═══════════════════════════════════════
Tên: Hương (Huong Gnouh) — sinh 16/01/1992
Trang Facebook: facebook.com/huong.thao.906
Đang học: Chương trình Nhà giáo dục gia đình tại tổ chức WIT
Đã viết sách: "Kiến Tạo Nhân Tài Từ 1 Tuổi"
Sở thích: Thư pháp Việt, thiền, đọc sách, ứng dụng AI
Phong cách sống: Tĩnh lặng, an vui, đơn giản, biết ơn
Làm online ở nhà. Chồng làm remote, đi lại HCM - Bình Dương (~40km).

═══════════════════════════════════════
VỀ BÉ BƯ — CHI TIẾT THẬT (DÙNG ĐỂ HIỂU, CHỌN LỌC KHI VIẾT — KHÔNG TÔ VẼ)
═══════════════════════════════════════
Tên: Bư. Sinh: 16/01/2025 (cùng ngày sinh với mẹ). Hiện: ~14 tháng.
Số đo: cao 76cm, nặng 10kg.
Vận động: Biết đi từ 11 tháng. Rất hiếu động. Tự học bằng cách tự luyện (đẩy ghế tập đi; xe chòi chân 1-2 ngày biết tiến lùi). Cẩn thận, đánh giá trước khi hành động, ít bị té. Thích chỗ đông người, không sợ người lạ.
Ngôn ngữ: Chủ yếu nói "ba ba", "a". Hồi 7 tháng từng nói "mama". Hiện chỉ khi khóc đòi bú hoặc ngủ mớ mới bật "mẹ ơi". Có ngữ điệu tốt nhưng không chịu bắt chước âm thanh theo yêu cầu. Không hứng thú nhìn miệng mẹ.
Ăn uống: Phải ép đút. Ăn tốt hơn khi bật kênh Ms Rachel. Mọc răng nhiều, lười ăn. Thích gặm xương sườn, cổ gà. Không chịu bú bình, không uống sữa ngoài, chỉ bú mẹ trực tiếp. Chấp nhận váng sữa.
Tính cách: Không làm theo yêu cầu người lớn — tự quyết. Bắt chước vận động (quét nhà, lau bàn, múa theo bà ngoại) nhưng không bắt chước âm thanh. Thích tháp vòng tròn hơn xếp hình. Biết nhanh nhưng chán nhanh. Ăn vạ lăn ra nhưng chấp nhận nhanh.
Lịch sinh hoạt: Sáng — ông cho đi công viên. Ban ngày — ông bà trông, bà nấu cháo. Trưa & chiều tối — ngủ với ba mẹ. Tối — ba cho ra công viên. Tối muộn — mẹ chơi tư duy ~5-10 phút rồi đòi bú. Cuối tuần — đi siêu thị, đi bơi cùng ba mẹ.
Gia đình: Sống cùng ba mẹ ruột và chồng. Bư là cháu nội ngoại duy nhất, rất được cưng chiều. Tối mẹ gọi điện nói chuyện với ông bà nội.

═══════════════════════════════════════
HỆ THỐNG TRIẾT LÝ CỐT LÕI (LỒNG GHÉP TỰ NHIÊN)
═══════════════════════════════════════
1. QUY LUẬT NHÂN DUYÊN QUẢ: (Nhân là hạt giống, Duyên là môi trường/AI, Quả là con trưởng thành).
2. THÂN GIÁO: Mẹ dạy con bằng cách mình sống mỗi ngày.
3. QUẢN TRỊ TÂM THỨC: Hành vi tự theo. Biết ơn - Ghi nhận.
4. 8 TỐ CHẤT NHÂN TÀI: Dũng cảm nhận lỗi, kiên trì, cống hiến, v.v
5. 4 YẾU TỐ: Nội tâm, Tài chính, Mối quan hệ, Sức khỏe.

═══════════════════════════════════════
CONCEPT 3 TẦNG NỘI DUNG — QUY TẮC BẮT BUỘC
═══════════════════════════════════════
🟢 TẦNG 1 — "MÌNH ĐANG LÀM" (Trải nghiệm thật với Bư 14 tháng) -> Dùng giọng đang thử, đúng với thực tế đang diễn ra.
🟡 TẦNG 2 — "MÌNH ĐANG HỌC, CHƯA TỚI GIAI ĐOẠN" (Biết nhưng chưa làm) -> Phù hợp bé lớn hơn, mời ba mẹ chia sẻ.
🔵 TẦNG 3 — "MÌNH MỜI CÁC BA MẸ CÙNG THỬ" (Mở cộng đồng) -> Trao đổi 2 chiều.
NGUYÊN TẮC: TUYỆT ĐỐI không bao giờ nói mình đã thành công. Phải thành thật.

═══════════════════════════════════════
CẤU TRÚC MỖI BÀI VIẾT — 5 BƯỚC BẮT BUỘC
═══════════════════════════════════════
BƯỚC 1: HOOK ngắn ngọn đời thường gây đồng cảm (Không triết học).
BƯỚC 2: KỂ CHUYỆN THẬT cụ thể (Bư ném đồ, bò quanh nhà...).
BƯỚC 3: LỒNG NGUYÊN LÝ kết nối tự nhiên, cực kỳ đời thường dễ hiểu.
BƯỚC 4: GIÁ TRỊ THỰC TẾ — Không nhất thiết phải là AI. Có thể chia sẻ kiến thức dinh dưỡng, sức khỏe, vận động, trí tuệ cho bé có dẫn chứng cụ thể (ví dụ: "Theo WHO, trẻ 12-18 tháng cần..."). Nếu có dùng AI thì giới thiệu ngắn gọn, nói thẳng thông tin giá trị — không cần nói dài về AI.
BƯỚC 5: CTA MỜI TRAO ĐỔI. Kết bằng câu hỏi chân thành để mời mọi người chia sẻ kinh nghiệm ngược lại — vì mình đăng bài để học hỏi chứ không phải để dạy. Kết với: "Đơn giản làm. Vui vẻ làm. Nhẹ nhàng làm." + Hashtags phù hợp mẹ bỉm.

═══════════════════════════════════════
GIỌNG VĂN — QUY TẮC TUYỆT ĐỐI (TINH THẦN KHIÊM TỐN - HỌC HỎI)
═══════════════════════════════════════
- Viết ngôi "mình". Nhẹ nhàng tâm sự. Ấm áp chân thành.
- KHÔNG CỐ GẮNG GƯỢNG ÉP ĐƯA TRI THỨC NHÂN SINH VÀO. Nếu câu chuyện không tự nhiên dẫn đến triết lý thì ĐỪNG lồng vào. Chân thành hơn giả tạo.
- Chỉ viết đúng những gì đang diễn ra thật. Không tô vẽ. Không phóng đại.
- TUYỆT ĐỐI KHÔNG DẠY ĐỜI. Mình không phải chuyên gia. Mình chỉ là người đang học và muốn chia sẻ để được nghe thêm góc nhìn của mọi người.
- Không bao giờ dùng: "bạn nên", "cần phải", "mẹ nào cũng nên", "đúng là", "đây là cách tốt nhất".
- Thay vào đó, dùng: "mình đang thử", "mình chưa chắc nhưng...", "không biết mọi người nghĩ sao", "mình học được điều này và đang áp dụng thử".
- Luôn kết thúc bằng câu hỏi hoặc lời mời chia sẻ — vì mình thật sự muốn nghe lại từ các ba mẹ khác.
- Dùng "—" để tạo nhịp văn.
- TUYỆT ĐỐI KHÔNG DÙNG DẤU MARKDOWN BÔI ĐẬM. KHÔNG GẠCH ĐẦU DÒNG DÀI. HÃY DÙNG TEXT THƯỜNG.

═══════════════════════════════════════
LỆNH VẬN HÀNH DÀNH CHO BẠN NGÀY HÔM NAY (NGÀY {current_date})
═══════════════════════════════════════
1. TRÁNH TRÙNG LẶP với quá khứ: {history}
2. BẮT BUỘC ĐƯA VÀO DÒNG ĐẦU TIÊN CỦA KẾT QUẢ ĐẦU RA Y XÌ NHƯ SAU:
TOPIC: [3-5 từ khóa tiếng việt mô tả chính xác nội dung infographic về gia đình, em bé, ngăn cách bằng dấu phẩy]
3. HÃY THỰC THI LỆNH SAU BẰNG CẢ TRÁI TIM: {command}. Nhớ lồng ghép 1 App AI đã giới thiệu như yêu cầu.
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
            tagged_content = final_content.strip() + "\n\n#ByAI"
            return tagged_content, topic_str.strip()
            
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


def generate_infographic_image(content, topic):
    print("\n🎨 KÍCH HOẠT MÁY CHỦ ÁNH SÁNG POLLINATIONS AI (SẢN XUẤT Hình Ảnh 2D Mẹ & Bé Nét Cao)...")
    
    prompt_gen = f"Translate the core idea of this topic into exactly 5-8 descriptive English keywords (alphabet only, no punctuation, focus on family, mother, baby, AI or education): '{topic}'"
    
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
         image_prompt = "mother and baby family ai education"

    save_path = os.path.abspath(os.path.join("fb_images", f"infographic_{int(time.time())}.jpg"))
    os.makedirs("fb_images", exist_ok=True)
    
    prompts_to_try = [
        f"A gentle 2D vector flat illustration about {image_prompt}. A young mother and her 13-month-old baby boy, warm pastel colors, peaceful home environment, subtle modern AI technology elements, high quality, minimalist layout, joyful family moment",
        f"Parenting and early childhood education concept flat vector art, {image_prompt}. soft pastel colors, white background, peaceful and heartwarming mother and child bonding",
        f"Family harmony and AI assistance flat vector illustration, clean minimalist layout, modern warm art style, {image_prompt}"
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
        
    print("❌ API Ảnh AI đang sập mạng cục bộ. Đang dùng phương án Cứu Hộ Hình Ảnh Mẹ Bỉm Sữa...")
    try:
        res = requests.get("https://image.pollinations.ai/prompt/cute%20happy%20baby%20infant%20mother%20family%20love%20photo?nologo=true", headers=headers, timeout=15)
        img_data = res.content
        if img_data.startswith(b'\xff\xd8') or img_data.startswith(b'\x89PNG') or img_data[8:12] == b'WEBP':
             with open(save_path, 'wb') as handler:
                  handler.write(img_data)
             print("✅ Đã lấy thành công ảnh Cấp Cứu Mẹ & Bé để chữa cháy Bài Viết!")
             return save_path
    except Exception as e:
        print(f"❌ Cứu hộ hình ảnh cũng gãy: {e}")

    return None


async def post_to_facebook(browser, content, image_path=None, drive_link=None):
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
             
        # === ĐĂNG ẢNH LÊN FACEBOOK — CHIẾN LƯỢC 3 TẦNG ===
        if image_path and os.path.exists(image_path):
            print(f"🖼️ Bắt đầu tải ảnh lên Facebook: {image_path}")
            img_uploaded = False

            # === CHIẾN LƯỢC 1: set_input_files trực tiếp vào hidden file input ===
            # (Cách đáng tin cậy nhất — không cần click nút Photo)
            if not img_uploaded:
                try:
                    # Làm hiện thị input file ẩn trước khi set
                    await page.evaluate("""
                        const inputs = document.querySelectorAll('input[type=file][accept*=image]');
                        inputs.forEach(el => {
                            el.style.display = 'block';
                            el.style.opacity = '1';
                            el.style.visibility = 'visible';
                        });
                    """)
                    await page.wait_for_timeout(500)
                    file_inputs = page.locator('input[type="file"][accept*="image"]')
                    count = await file_inputs.count()
                    if count > 0:
                        await file_inputs.first.set_input_files(image_path)
                        print(f"✅ [Chiến lược 1] set_input_files thành công ({count} input tìm thấy)!")
                        img_uploaded = True
                        await page.wait_for_timeout(8000)
                except Exception as e1:
                    print(f"⚠️ [Chiến lược 1] Thất bại: {e1}")

            # === CHIẾN LƯỢC 2: Intercept file chooser qua nút Ảnh/video ===
            if not img_uploaded:
                try:
                    photo_btn = page.locator('[aria-label*="Ảnh"], [aria-label*="Photo"], [aria-label*="video"], [aria-label*="Video"]').first
                    btn_count = await photo_btn.count()
                    if btn_count > 0:
                        async with page.expect_file_chooser(timeout=10000) as fc_info:
                            await photo_btn.click()
                        fc = await fc_info.value
                        await fc.set_files(image_path)
                        print("✅ [Chiến lược 2] file chooser intercept thành công!")
                        img_uploaded = True
                        await page.wait_for_timeout(8000)
                    else:
                        raise Exception("Không tìm thấy nút Photo/Video")
                except Exception as e2:
                    print(f"⚠️ [Chiến lược 2] Thất bại: {e2}")

            # === CHIẾN LƯỢC 3: Copy ảnh vào clipboard và Ctrl+V ===
            if not img_uploaded:
                try:
                    img_abs = os.path.abspath(image_path)
                    # Dùng PowerShell để copy file ảnh vào clipboard
                    import subprocess
                    ps_cmd = (
                        f"Add-Type -AssemblyName System.Windows.Forms; "
                        f"[System.Windows.Forms.Clipboard]::SetImage("
                        f"[System.Drawing.Image]::FromFile('{img_abs}'))"
                    )
                    subprocess.run(["powershell", "-Command", ps_cmd], check=True, timeout=10)
                    await page.keyboard.press("Control+V")
                    print("✅ [Chiến lược 3] Dán ảnh từ clipboard (Ctrl+V)!")
                    img_uploaded = True
                    await page.wait_for_timeout(10000)
                except Exception as e3:
                    print(f"⚠️ [Chiến lược 3] Clipboard thất bại: {e3}")

            if not img_uploaded:
                print("❌ Tất cả chiến lược upload ảnh đã thất bại — đăng bài không có ảnh.")
            else:
                print("⏳ Đợi Facebook render ảnh xong (15s)...")
                await page.wait_for_timeout(15000)

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
        
    except Exception as e:
        print(f"❌ Khúc mắc Màn Cấu Rỉa Dom FB: {e}")
        
    await context.close()


async def core_ecosystem_pipeline():
    print(f"\n=================================================")
    print(f"🕒 [{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] KÍCH HOẠT HỆ SINH THÁI TỰ ĐỘNG B2B V8 (MẮT THẦN IMAGEN 3 TỐI TÂN).")
    print(f"=================================================")
    
    content, topic = generate_post_content()
    if not content:
        return
        
    print("\n" + "="*50)
    print(" 🎨 GIAI ĐOẠN 1: LẤY ẢNH MINH HỌA TỪ POLLINATIONS AI")
    print("="*50)
    # Bỏ qua Gemini image gen — lấy thẳng ảnh minh họa từ Pollinations
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
            
        await post_to_facebook(browser, content, image_path, None)
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

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "="*80)
    print(" 🌟 SOCIAL MEDIA BOT V6.0 (Tương Tác Nghệ Thuật - Nắm Cán Toàn Bộ B2B) 🌟")
    print("="*80 + "\n")
    
    schedule.every().day.at("08:00").do(execute_daily_posting)
    schedule.every().day.at("20:00").do(execute_daily_posting)
    
    # Random Đi Dạo Khoảng 20 tới 40 Phút 1 Lần. Trung bình ngày ~ 50 Bài Post. (Phá Thuật Toán)
    schedule.every(20).to(40).minutes.do(execute_random_comment)
    
    print("[HỆ THỐNG TRUYỀN LỆNH]: ÉP MẠCH GIAO TRANH CHO CHUỲ DUYỆT BÀI ĐĂNG CỦA BOT...")
    execute_daily_posting()
    
    print("\n" + "="*80)
    print("🟢 TIẾN TRÌNH LÕI TRONG NHÂN (BACKGROUND PROCESS RUNNING)")
    print("🚨 Tool Mổ Não Đang Ngủ Ngầm Bám Đuôi Facebook Liên Tục - Phá Vòng Lặp. Tuyệt đối không Tắt Màn Hình Này.")
    print("="*80 + "\n")
    
    while True:
        schedule.run_pending()
        time.sleep(30)
