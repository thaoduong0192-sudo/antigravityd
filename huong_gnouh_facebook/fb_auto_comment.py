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
[LỆNH TỐI CAO DÀNH CHO BÌNH LUẬN DẠO (AUTO MẸ BỈM SỮA & GIÁO DỤC SỚM)]
Bạn đang đóng vai Hương (Huong Gnouh), mẹ bỉm 26 tuổi, có con trai 13 tháng tên Bư, đam mê Giáo dục gia đình và ứng dụng AI nuôi dạy con.
Nhiệm vụ: Đọc Nội Dung Bài Viết trên Group/Fanpage Facebook của các mẹ bỉm khác.

NỘI DUNG BÀI VIẾT:
"{post_text}"

[QUY TẮC BẤT DI BẤT DỊCH TỪ HỆ THỐNG]
1. NẾU bài viết này đánh ghen, chửi lộn, chính trị, tiêu cực: NGAY LẬP TỨC IN RA ĐÚNG 1 TỪ DUY NHẤT: "IGNORE".
2. TRONG MỌI TRƯỜNG HỢP KHÁC (ĐẶC BIỆT LÀ BÀI CHIA SẺ NUÔI DẠY CON, ĂN DẶM, BỆNH TRẺ EM, THAN THỞ MỆT MỎI, GIÁO DỤC SỚM): Hãy viết 1 câu trả lời CỰC KỲ KHÉO LÉO để TẠO SỰ ĐỒNG CẢM.
- Độ dài: Tối đa 1 đến 2 câu. Giọng văn chân thành, ấm áp, nhún nhường.
- Mục tiêu: Hiện diện Thương hiệu cá nhân. Khen ngợi em bé đáng yêu, đồng cảm sự vất vả của mẹ, hoặc chia sẻ 1 tips nhỏ xíu mình biết từ triết lý "Nhân Duyên Quả". VD: "Trộm vía bé lanh lẹ quá mom ơi!", "Đợt Bư nhà em cũng thế, mệt phờ người nhưng ráng giữ tinh thần nhẹ nhàng thì con lại ngoan.", "Mẹ vất vả rồi, nghỉ ngơi chút nhé mom!"
- TUYỆT ĐỐI KHÔNG BÁN HÀNG, KHÔNG DẠY ĐỜI, CHỈ CHÂN THÀNH CHIA SẺ ĐỂ HỌ BẤM LIKE COMMENT.
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
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🕵️ BẬT CHẾ ĐỘ RẢI ĐỒNG CẢM BÌNH LUẬN DẠO (MẸ BỈM SỮA/GIÁO DỤC SỚM)...")
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
            "giáo dục sớm", "em bé 1 tuổi", "mẹ bỉm sữa", "ăn dặm cho bé", 
            "review bỉm sữa", "nuôi con khoa học", "khủng hoảng tuổi lên 1", "dạy con từ sớm"
        ]
        
        target_kw = random.choice(keywords)
        print(f"🔎 Đang thâm nhập Quần Thể FB với Từ Khóa Trend Ngẫu Nhiên: [{target_kw}]...")
        
        try:
            # Lọc bài viết mới nhất trong kết quả tìm kiếm Bằng Param của Desktop
            # Hoặc đi thẳng vào search base
            await page.goto(f"https://www.facebook.com/search/posts/?q={urllib.parse.quote(target_kw)}")
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
                          await comment_btn.click()
                          await page.wait_for_timeout(2500)
                          
                     comment_box = article.locator('div[aria-label="Viết bình luận"], div[aria-label="Write a comment"], div[role="textbox"]:has-text("Bình luận")').first
                     if await comment_box.count() > 0 and await comment_box.is_visible():
                          await comment_box.click(delay=200)
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

if __name__ == "__main__":
    asyncio.run(run_auto_comment())
