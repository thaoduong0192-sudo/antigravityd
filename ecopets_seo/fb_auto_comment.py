import os
import random
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import urllib.parse
import hashlib
from datetime import datetime

load_dotenv()

GEMINI_API_KEY_FB = os.getenv("GEMINI_API_KEY_FB")
GEMINI_API_KEY = GEMINI_API_KEY_FB if GEMINI_API_KEY_FB else os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("❌ Lỗi: Vui lòng thêm GEMINI_API_KEY_FB vào file .env")
    exit(1)

def is_already_commented(text):
    if not os.path.exists("commented_history.txt"):
        return False
    short_text = text[:200].strip()
    text_hash = hashlib.md5(short_text.encode('utf-8')).hexdigest()
    with open("commented_history.txt", "r") as f:
        if text_hash in f.read():
            return True
    return False

def save_comment_history(text):
    short_text = text[:200].strip()
    text_hash = hashlib.md5(short_text.encode('utf-8')).hexdigest()
    with open("commented_history.txt", "a") as f:
        f.write(text_hash + "\n")

def generate_witty_comment(post_text):
    prompt = f"""
[LỆNH TỐI CAO DÀNH CHO BÌNH LUẬN DẠO (AUTO ENGAGEMENT B2B)]
Bạn đang đóng vai Chủ Doanh Nghiệp Cung Cấp Sỉ Petshop/Thú y dày dặn kinh nghiệm, khéo léo và điềm đạm.
Nhiệm vụ: Đọc Nội Dung Bài Viết trên Group/Fanpage Facebook của người khác dưới đây.

NỘI DUNG BÀI VIẾT:
"{post_text}"

[QUY TẮC BẤT DI BẤT DỊCH TỪ HỆ THỐNG]
1. NẾU bài viết này đánh ghen, chửi lộn, chính trị, tiêu cực, đâm chém: NGAY LẬP TỨC IN RA ĐÚNG 1 TỪ DUY NHẤT: "IGNORE".
2. TRONG MỌI TRƯỜNG HỢP KHÁC (RẤT KHUYẾN KHÍCH CÁC BÀI VIẾT QUẢNG CÁO BÁN LẺ THÚ CƯNG, TÌM NGUỒN SỈ, HỎI ĐÁP, TUYỂN DỤNG, TÌM MỐI BÁN BUÔN NGÀNH PET): Hãy viết 1 câu trả lời CỰC KỲ KHÉO LÉO để TẠO SỰ CHU Ý.
- Độ dài: Tối đa 1 đến 2 câu. Mình lướt ngang thấy đúng Insight thì chêm 1 câu bình luận thôi.
- Mục tiêu: Hiện diện Thương hiệu. Dùng lời khen khách sáo, đồng cảm tình hình thị trường. Nếu thấy họ bán hàng thì chúc họ bán đắt khách. VD: "Mẫu mã đẹp quá shop ơi, chúc shop tháng này bùng nổ doanh số nhé!", "Ca này khó nhằn phết, bác xử lý mượt tay ghê!", "Công nhận đợt này hạt ế ẩm thật shop ạ. Shop châm thêm nguồn hàng mới xem sao?"
- TUYỆT ĐỐI KHÔNG BÁN HÀNG THÔ ("bên mình có...", "inbox mình..."). CHỈ XÂY DỰNG MỐI QUAN HỆ ĐỂ HỌ BẤM LIKE COMMENT VÀ LƯU TÂM PROFILE MÌNH.
- TUYỆT ĐỐI KHÔNG dùng DẤU HASHTAG (#), không dùng in đậm (**).
- Dùng tối đa 1 Emoji duy nhất cho tự nhiên.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        res = response.text.strip()
        if "IGNORE" in res:
            return None
        return res
    except Exception as e:
        print(f"Lỗi Sinh Comment AI: {e}")
        return None

async def run_auto_comment():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🕵️ BẬT CHẾ ĐỘ RẢI BOM BÌNH LUẬN DẠO (TRUY VẾT TƯƠNG TÁC NGÁCH PET)...")
    session_file = "fb_session.json"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    if not os.path.exists(session_file):
        print("⚠️ Trạng thái Cookie FB Trống (Chưa Đăng Nhập ở Tool Phá Khóa Chính). Hủy Chuyến Đi Dạo Này!")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(storage_state=session_file, no_viewport=True, user_agent=user_agent)
        page = await context.new_page()
        
        keywords = [
            "sỉ petshop", "nguồn hàng thú cưng", "thú y", "petshop", 
            "mở petshop", "kinh doanh thú cưng", "phụ kiện chó mèo giá sỉ", "thức ăn sỉ chó mèo"
        ]
        
        target_kw = random.choice(keywords)
        print(f"🔎 Đang thâm nhập Quần Thể FB với Từ Khóa Trend Ngẫu Nhiên: [{target_kw}]...")
        
        try:
            # Thay vì đi thẳng link dễ dính 404, ta đi qua trang chủ FB bảo mật cao hơn
            await page.goto("https://www.facebook.com/", timeout=60000)
            await page.wait_for_timeout(5000)
            
            print("Nhập lệnh tìm kiếm vào thanh công cụ...")
            search_input = page.locator('input[type="search"], input[aria-label*="Tìm kiếm"]').first
            if await search_input.count() > 0:
                await search_input.fill(target_kw)
                await page.keyboard.press("Enter")
            else:
                await page.goto(f"https://www.facebook.com/search/top/?q={urllib.parse.quote(target_kw)}")
            
            await page.wait_for_timeout(8000)
            
            # Vuốt nhẹ màn hình 4 Lần tạo độ trễ tải bài
            for _ in range(4):
                 await page.mouse.wheel(0, 1000)
                 await page.wait_for_timeout(3000)
                 
            # Find Facebook Post Containers
            articles = page.locator('div[role="article"]')
            count = await articles.count()
            print(f"📡 Radar Càn Quét Được {count} Khối Bài Viết Chứa Từ Khóa Trên Cung Đường Này. Đang soi Text...")
            
            success_commented = False
            
            # Quét tối đa 5 bài đầu, chỉ chấm đúng 1 bài ngon nhất để thả thính!
            for i in range(min(count, 5)):
                if success_commented: 
                     break 
                     
                article = articles.nth(i)
                try:
                    text_content = await article.inner_text()
                except Exception:
                    continue
                    
                if len(text_content) < 30: 
                     continue
                     
                if is_already_commented(text_content):
                     print("⏭️ Dấu Vết Lỗi: Chỗ này đã Thả cmt rồi. Pass!")
                     continue
                     
                print(f"🧠 Soi được 1 Post Dài [{len(text_content)} Kí tự] -> Bắn Sang Não AI Gemini Đo Lường...")
                ai_reply = generate_witty_comment(text_content)
                
                if not ai_reply:
                     save_comment_history(text_content)
                     print("🗑️ AI Ra Lệnh PASS (Rác/Quảng Cáo Trá Hình/Đấu Tố Mạng).")
                     continue
                     
                print(f"💬 PHÁN QUYẾT TỪ CHỦ TỊCH AI ĐỂ THẢ MỒI: '{ai_reply}'")
                print("⏳ Di chuyển Trỏ Chuột Mô Phỏng Viết Phản Hồi...")
                
                # Trỏ vào box comment
                try:
                     # Vuốt cái bài viết đó lọt giữa khung nhìn để click khỏi lỗi bị mép
                     await article.scroll_into_view_if_needed()
                     await page.wait_for_timeout(1000)
                     
                     comment_btn = article.locator('div[role="button"]:has-text("Bình"), div[role="button"]:has-text("Comment")').first
                     if await comment_btn.is_visible():
                          await comment_btn.click(force=True)
                          await page.wait_for_timeout(2500)
                          
                     comment_box = article.locator('div[aria-label="Viết bình luận"], div[aria-label="Write a comment"], div[role="textbox"]:has-text("Bình luận")').first
                     if await comment_box.count() > 0 and await comment_box.is_visible():
                          await comment_box.click(delay=200, force=True)
                          await page.wait_for_timeout(500)
                          
                          # Tránh bị lỗi loạn mã tiếng Việt khi type(), chèn thẳng Text qua copy-paste ẩn
                          await page.keyboard.insert_text(ai_reply)
                          await page.wait_for_timeout(random.randint(2000, 4000)) # Giả vờ ngâm nghĩ
                          
                          await page.keyboard.press("Enter")
                          print("✅ ÁM SÁT THÀNH CÔNG! BÌNH LUẬN ĐÃ GHIM CẮM KÉO TRAFFIC. NGẮT NHIỆM VỤ RÚT QUÂN.")
                          save_comment_history(text_content)
                          success_commented = True
                     else:
                          print("⚠️ Bài đăng riêng tư/Group đóng chặn quyền Vãng lai Bình Luận. Chuyển mục tiêu Lưới!")
                except Exception as e:
                     print(f"❌ Kẹt Trục Phản Kháng Của FB (DOM Click Khó Mờ Ảo): {e}")
                     
        except Exception as flow_err:
            print(f"❌ Đứt gãy luồng FB: {flow_err}")

        await browser.close()
        if not success_commented:
            print("💨 Cuốc Dạo Này Thất Bại Biển Bọt, Các Bài Xung Quanh Không Ngon Nhả Chữ Nào. Thu Quân Hẹn Lát Nữa Cày Lại!")

def generate_fanpage_comment(post_text):
    prompt = f"""
[LỆNH TỐI CAO DÀNH CHO BÌNH LUẬN CHĂM SÓC FANPAGE NHÀ (ECOPETS.VN1)]
Bạn đang đóng vai Tuệ Đan - Một chuyên gia, một khách sỉ đối tác chiến lược cực kỳ am hiểu ngành Thú y & Petshop.
Nhiệm vụ: Đọc Nội Dung Bài Viết trên Fanpage Ecopets.vn1 dưới đây và để lại 1 bình luận tung hứng, bồi đắp thêm giá trị.

NỘI DUNG BÀI VIẾT TỪ FANPAGE NHÀ:
"{post_text}"

[QUY TẮC BẤT DI BẤT DỊCH TỪ HỆ THỐNG]
1. ĐÂY LÀ SÂN NHÀ CỦA MÌNH. Hãy comment theo hướng KIẾN TẠO GIÁ TRỊ, hỏi những câu mở rộng vấn đề để mồi cho admin Page trả lời, hoặc đưa ra 1 lời khen khách quan sâu sắc về giải pháp mà Ecopets mang lại.
2. NẾU bài viết là Kiến thức: Comment bằng 1 fact chuyên sâu hoặc 1 góc nhìn thực tế bổ sung. VD: "Đúng rồi bác, phần xương khớp này nếu kết hợp thêm X nữa thì chó già nằm ổ bao khỏe luôn."
3. NẾU bài viết là Sản phẩm/Sale: Khen khen chất lượng, hỏi về chính sách sỉ. VD: "Lô đợt này date xa không shop? Tư vấn em gói sỉ 50kg về tỉnh nhé."
4. TUYỆT ĐỐI KHÔNG spam thả icon vô nghĩa.
5. Độ dài: Tối đa 2 đến 3 câu.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        res = response.text.strip()
        if "IGNORE" in res:
            return None
        return res
    except Exception as e:
        print(f"Lỗi Sinh Comment AI Fanpage: {e}")
        return None

async def run_fanpage_comment():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🏰 BẬT CHẾ ĐỘ CHĂM SÓC FANPAGE SÂN NHÀ (ECOPETS.VN1)...")
    session_file = "fb_session.json"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    if not os.path.exists(session_file):
        print("⚠️ Trạng thái Cookie FB Trống. Vui lòng quét FaceBook Login Auto Poster trước!")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(storage_state=session_file, no_viewport=True, user_agent=user_agent)
        page = await context.new_page()
        
        try:
            print("🔗 Đang di chuyển thẳng tới Đại Bản Doanh: https://www.facebook.com/Ecopets.vn1")
            await page.goto("https://www.facebook.com/Ecopets.vn1", timeout=60000)
            await page.wait_for_timeout(8000)
            
            # Cuộn 10 lần để load đủ bài
            for _ in range(10):
                 await page.mouse.wheel(0, 1500)
                 await page.wait_for_timeout(2000)
                 
            articles = page.locator('div[role="article"]')
            count = await articles.count()
            print(f"📡 Đã quét được {count} bài đăng trên tường nhà. Tiến hành bơm Comment Giá Trị...")
            
            commented_count = 0
            
            for i in range(count):
                if commented_count >= 10: 
                     print("✅ Đã hoàn thành chỉ tiêu 10 bài viết. Rút quân!")
                     break 
                     
                article = articles.nth(i)
                try:
                    text_content = await article.inner_text()
                except Exception:
                    continue
                    
                if len(text_content) < 30: continue
                     
                if is_already_commented(text_content):
                     print("⏭️ Dấu Vết Lỗi: Post này đã được Chăm Sóc. Pass!")
                     continue
                     
                print(f"🧠 Phân tích Bài [{i+1}] Dài [{len(text_content)} Kí tự] -> Gọi Não Ngành Nghề Gemini...")
                ai_reply = generate_fanpage_comment(text_content)
                
                if not ai_reply:
                     continue
                     
                print(f"💬 TUNG HỨNG ĐỒNG ĐỘI: '{ai_reply}'")
                
                # Trỏ vào box comment
                try:
                     await article.scroll_into_view_if_needed()
                     await page.wait_for_timeout(1000)
                     
                     comment_btn = article.locator('div[role="button"]:has-text("Bình"), div[role="button"]:has-text("Comment")').first
                     if await comment_btn.is_visible():
                          await comment_btn.click(force=True)
                          await page.wait_for_timeout(2500)
                          
                     comment_box = article.locator('div[aria-label="Viết bình luận"], div[aria-label="Write a comment"], div[role="textbox"]:has-text("Bình luận")').first
                     if await comment_box.count() > 0 and await comment_box.is_visible():
                          await comment_box.click(delay=200, force=True)
                          await page.wait_for_timeout(500)
                          
                          await page.keyboard.insert_text(ai_reply)
                          await page.wait_for_timeout(random.randint(4000, 8000)) # Delays ngẫu nhiên mượt hơn
                          await page.keyboard.press("Enter")
                          
                          print(f"✅ BƠM TIÊM COMMENT THÀNH CÔNG VÀO BÀI TƯỜNG NHÀ!")
                          save_comment_history(text_content)
                          commented_count += 1
                          # Đợi random 1-3 phút trước khi bình luận bài tiếp theo cho giống người
                          delay = random.randint(60, 180)
                          print(f"⏳ Nghỉ tay {delay} giây trước khi tương tác bài tiếp theo...")
                          await page.wait_for_timeout(delay * 1000)
                     else:
                          print("⚠️ Móc comment không ra. Chuyển mục tiêu!")
                except Exception as e:
                     print(f"❌ Kẹt DOM Bài Nhà: {e}")
                     
        except Exception as flow_err:
            print(f"❌ Đứt gãy luồng Fanpage: {flow_err}")

        await browser.close()
        print(f"🎌 Xong Cuốc Đi Chăm Trại Ecopets. KẾT THÚC.")

if __name__ == "__main__":
    asyncio.run(run_auto_comment())
