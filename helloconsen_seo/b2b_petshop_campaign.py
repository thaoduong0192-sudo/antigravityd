import os
import sys
import json
import time

sys.stdout.reconfigure(encoding='utf-8')
import random
import requests
import base64
from dotenv import load_dotenv
from openai import OpenAI
from stock_photos import download_stock_photo

# ==========================================
# CẤU HÌNH HỆ THỐNG
# ==========================================
load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

WP_API_URL = "https://helloconsen.com/wp-json/wp/v2/posts"
WP_MEDIA_URL = "https://helloconsen.com/wp-json/wp/v2/media"

TARGET_POSTS_PER_RUN = 30
MAX_ARTICLES_PER_KEYWORD = 10

if not QWEN_API_KEY:
    print("❌ Thiếu QWEN_API_KEY trong file .env")
    exit(1)

from qwen_manager import chat_with_qwen

def get_wp_auth_header():
    credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode('utf-8')
    return {"Authorization": f"Basic {token}"}

def upload_image_to_wp(image_bytes, filename):
    print("  [📸] Đang upload ảnh lên WordPress...")
    headers = get_wp_auth_header()
    headers["Content-Type"] = "image/jpeg"
    headers["Content-Disposition"] = f'attachment; filename="{filename}.jpg"'
    
    for _ in range(3):
        try:
            resp = requests.post(WP_MEDIA_URL, headers=headers, data=image_bytes, timeout=30)
            if resp.status_code == 201:
                data = resp.json()
                print(f"  [📸] Upload ảnh thành công! Media ID: {data['id']}")
                return data['id']
            else:
                print(f"  [!] Lỗi upload ảnh: {resp.status_code} - {resp.text}")
                time.sleep(3)
        except Exception as e:
            print(f"  [!] Exception khi upload ảnh: {e}")
            time.sleep(3)
    return None

def publish_wp_post(title, content, media_id=None):
    print(f"  [📝] Đang đăng bài viết: {title}")
    headers = get_wp_auth_header()
    headers["Content-Type"] = "application/json"
    
    payload = {
        "title": title,
        "content": content,
        "status": "publish",
        "categories": [22], # Dùng Category phù hợp, tạm thay bằng ID cat (Bạn có thể điều chỉnh sau)
    }
    
    if media_id:
        payload["featured_media"] = media_id
        
    for _ in range(3):
        try:
            resp = requests.post(WP_API_URL, headers=headers, json=payload, timeout=30)
            if resp.status_code == 201:
                data = resp.json()
                print(f"  [✅] Đăng bài thành công! URL: {data['link']}")
                return True
            else:
                print(f"  [!] Lỗi đăng bài: {resp.status_code} - {resp.text}")
                time.sleep(3)
        except Exception as e:
            print(f"  [!] Exception khi đăng bài: {e}")
            time.sleep(3)
    return False

def generate_b2b_article(keyword, shops, angle_index=0):
    print(f"  [🤖] Đang nhờ AI viết bài cho từ khóa: {keyword} (Góc tiếp cận: {angle_index+1}/10)")
    
    angles = [
        "1. Góc nhìn Tổng Quan: Phân tích cơ hội thị trường và rào cản tài chính.",
        "2. Góc nhìn Nhân Sự & Vận Hành: Nỗi đau thuê mướn, đào tạo nhân viên và quy trình.",
        "3. Góc nhìn Công Nghệ: Áp dụng phần mềm quản lý, Zalo OA để chăm sóc khách hàng.",
        "4. Góc nhìn Thiết Kế & Trải Nghiệm Khách Hàng (UX): Tối ưu không gian trưng bày để kích thích mua sắm.",
        "5. Góc nhìn Cạnh Tranh Gián Tiếp: Làm sao để shop nhỏ sống sót giữa các chuỗi lớn?",
        "6. Góc nhìn Marketing 0 Đồng: Xây dựng cộng đồng và tiếp thị truyền miệng.",
        "7. Góc nhìn Dòng Tiền (Cashflow): Bài toán tồn kho, công nợ và tốc độ xoay vòng vốn.",
        "8. Góc nhìn Mùa Vụ: Tối ưu doanh thu theo các mùa trong năm (mùa mưa, mùa rụng lông).",
        "9. Góc nhìn Dịch Vụ Khách Hàng: Xử lý khiếu nại và biến khách hàng khó tính thành Fan.",
        "10. Góc nhìn Khởi Nghiệp: Bài học xương máu cho người mới mở shop."
    ]
    current_angle = angles[angle_index % len(angles)]
    
    shop_list_text = ""
    for i, shop in enumerate(shops):
        shop_list_text += f"{i+1}. **{shop['name']}**\n   - Địa chỉ: {shop['address']}\n   - Điện thoại: {shop['phone']}\n\n"
        
    prompt = f"""
Bạn là một chuyên gia Content Marketing và Reviewer phân tích kinh doanh ngành Petshop/Thú y.
Nhiệm vụ của bạn là viết một bài đánh giá chuyên sâu dài ít nhất 1500 từ hướng đến nhóm B2B (các chủ Petshop, Spa Grooming, Phòng Khám Thú Y).

**Từ khóa gốc (RAW KEYWORD):** "{keyword}"

**QUY TẮC XỬ LÝ TỪ KHÓA & TIÊU ĐỀ BÀI VIẾT (RẤT QUAN TRỌNG):**
1. Nếu từ khóa bị lửng lơ, cụt ngữ pháp (Ví dụ: có chữ "ở", "tại" ở cuối nhưng không có địa danh), bạn phải TỰ ĐỘNG CHỈNH SỬA thành một cụm từ hoàn chỉnh, tự nhiên (Ví dụ: thêm "tại Việt Nam" hoặc "tại TP.HCM").
2. Đánh giá ngữ cảnh từ khóa:
   - Nếu từ khóa là dạng chung chung (như "dịch vụ lấy máu", "cửa hàng thú cưng"): Hãy viết bài theo dạng "{keyword} - {current_angle}". Bạn phải sáng tạo một tiêu đề tự nhiên, không bắt buộc phải có chữ "Top", KHÔNG ĐƯỢC LẶP LẠI TỪ KHÓA MỘT CÁCH MÁY MÓC.
   - Nếu từ khóa là TÊN MỘT THƯƠNG HIỆU CỤ THỂ (Ví dụ: "Bệnh viện thú y Petpro"): Tiêu đề phải là một bài phân tích về thương hiệu đó kết hợp với "{current_angle}".
3. **GÓC TIẾP CẬN BẮT BUỘC (ANGLE):** Bài viết của bạn PHẢI xoáy sâu vào góc nhìn sau: "{current_angle}". Mọi lập luận, phân tích ưu nhược điểm của các shop đều phải bám sát vào lăng kính này để tạo ra 1 bài viết ĐỘC BẢN, không bị trùng lặp với bất kỳ bài nào khác.

**Yêu cầu ĐỊNH DẠNG ĐẦU RA (BẮT BUỘC):**
Bạn phải trả về nội dung theo ĐÚNG cấu trúc sau (không có code block markdown):
TUYỆT ĐỐI SỬ DỤNG 100% TIẾNG VIỆT XUYÊN SUỐT BÀI VIẾT. KHÔNG ĐƯỢC PHÉP CHÈN BẤT KỲ CÂU TIẾNG ANH HAY TIẾNG TRUNG NÀO (Ngoại trừ tên thương hiệu như Bioline G1, DKGREEN, Ecopets).

TITLE: [Tiêu đề Clickbait hấp dẫn, đã xử lý mượt mà ngữ cảnh từ khóa, NHƯNG NGẮN GỌN TỐI ĐA 70 ký tự chuẩn SEO]
CONTENT:
[Toàn bộ nội dung bài viết định dạng HTML]

**Yêu cầu NỘI DUNG HTML:**
1. **Mở bài:** Dẫn dắt hấp dẫn, phân tích thị trường xoay quanh chủ đề của từ khóa.
2. **Review Đa Chiều (Thân bài):** 
   - Nếu bài dạng Top List: Lần lượt review {len(shops)} cửa hàng sau.
   - Nếu bài về 1 Thương hiệu: Phân tích sâu về thương hiệu đó trước, sau đó giới thiệu {len(shops)} cửa hàng bên dưới như là "Các đối tác/Phòng khám liên kết cùng mạng lưới uy tín".
   Danh sách {len(shops)} cửa hàng:
{shop_list_text}
   - Với MỖI cửa hàng, viết 1 đoạn văn phân tích: Ưu điểm nổi bật, Điểm chung hạn chế của ngành (mỏng biên lợi nhuận, ít sản phẩm bán kèm), và Đề xuất cải thiện trải nghiệm khách hàng.
3. **Điểm chạm B2B - Chốt Sale Ecopets (QUAN TRỌNG NHẤT):** Chuyển ý mượt mà bằng tiêu đề H2 như "Giải Pháp Tối Ưu Dòng Tiền & Tăng Biên Lợi Nhuận Bằng Mô Hình Cross-sell". 
   - Nêu ra nỗi đau: Các shop/phòng khám bị mỏng biên lợi nhuận (12-18%) khi chỉ bán hạt và cát vệ sinh.
   - Giới thiệu giải pháp: Gia nhập mạng lưới đại lý "Trạm Dinh Dưỡng Xanh Ecopets".
   - CHI TIẾT CHÍNH SÁCH BÁN KÈM (Bám sát kiến thức thực tế):
     + Ecopets mang đến chiến lược Cross-sell thông minh. Khách mua đồ ăn hạt/pate -> tư vấn bán kèm **Men vi sinh Bioline G1** (hỗ trợ tiêu hóa), **Beta Amin** (tăng đề kháng) hoặc **Eco Detox** (hỗ trợ gan thận). Khách làm dịch vụ Spa/Grooming -> tư vấn bán kèm **Khử khuẩn siêu nano DKGREEN**, **Sữa tắm Ecopets** chăm sóc da lông tại nhà.
     + Chỉ với số vốn từ **3.000.000đ**, chủ shop chính thức trở thành Đại Lý của Ecopets, tận hưởng biên lợi nhuận cao (từ 40% trở lên).
     + Tối ưu vòng quay vốn với các sản phẩm dễ bán, giải quyết trúng đích nỗi đau của chủ nuôi, giúp shop chuyển mình thành "chuyên gia" thay vì chỉ là điểm bán lẻ.
   - Kêu gọi hành động (Call to Action): Khuyên chủ shop đọc thêm chi tiết chính sách đại lý tại đây: <a href="https://ecopets.vn/kinh-nghiem-kinh-doanh-petshop-dong-hanh-cung-tram-dinh-duong-xanh-ecopets" target="_blank">Chính sách đồng hành cùng Trạm dinh dưỡng xanh Ecopets</a>.

**Lưu ý:**
- Chỉ trả về HTML phần thân (từ <h2> đến <p>...), không bao gồm <html>, <head>, <body> hay <h1> (vì tiêu đề đã nằm ở TITLE).
- Bài viết phải thật sự sâu sắc, phân tích logic kinh doanh, KHÔNG BỊA ĐẶT CÁC GÓI CHÍNH SÁCH ẢO.
- TUYỆT ĐỐI KHÔNG VIẾT DANG DỞ. Hãy cân đối độ dài để đảm bảo viết trọn vẹn phần chốt sale Ecopets ở cuối cùng. Mọi câu từ phải hoàn chỉnh.
"""

    system_msg = "Bạn là chuyên gia Content Marketing SEO chuyên ngành Petshop tại Việt Nam. BẠN PHẢI TRẢ LỜI 100% BẰNG TIẾNG VIỆT (VIETNAMESE).\n"
    prompt_full = system_msg + prompt
    
    raw = chat_with_qwen(prompt_full, max_tokens=8000, temperature=0.7)
    if not raw:
        print("  [-] Lỗi tạo bài: Không nhận được kết quả từ Qwen Manager.")
        return None, None
    
    content = raw.strip()
    
    title = keyword
    html_content = content
    
    if "TITLE:" in content and "CONTENT:" in content:
        parts = content.split("CONTENT:")
        title_part = parts[0].replace("TITLE:", "").strip()
        html_content = parts[1].strip()
        if title_part:
            title = title_part
            
    # Loại bỏ code blocks markdown nếu có
    if html_content.startswith("```html"):
        html_content = html_content[7:]
    elif html_content.startswith("```"):
        html_content = html_content[3:]
    if html_content.endswith("```"):
        html_content = html_content[:-3]
        
    return title, html_content

def run_campaign():
    db_path = "b2b_database.json"
    state_path = "b2b_campaign_state.json"
    
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    with open(state_path, 'r', encoding='utf-8') as f:
        state = json.load(f)
        
    keywords = db["keywords"]
    petshops = db["petshops"]
    
    print(f"🚀 Bắt đầu chiến dịch B2B. Mục tiêu: {TARGET_POSTS_PER_RUN} bài viết.")
    
    posts_done = 0
    
    # Randomize keyword selection but prioritize those with < MAX_ARTICLES_PER_KEYWORD
    available_keywords = [kw for kw in keywords if state["keywords_status"][kw]["articles_posted"] < MAX_ARTICLES_PER_KEYWORD]
    
    if not available_keywords:
        print("🎉 HOÀN THÀNH CHIẾN DỊCH 1000 BÀI VIẾT! Không còn từ khóa nào.")
        return
        
    random.shuffle(available_keywords)
    
    for kw in available_keywords:
        if posts_done >= TARGET_POSTS_PER_RUN:
            break
            
        while state["keywords_status"][kw]["articles_posted"] < MAX_ARTICLES_PER_KEYWORD and posts_done < TARGET_POSTS_PER_RUN:
            # Chọn shops
            start_idx = state["current_shop_index"]
            shops_to_pick = random.randint(4, 7)
            selected_shops = []
            
            for _ in range(shops_to_pick):
                selected_shops.append(petshops[start_idx % len(petshops)])
                start_idx += 1
                
            state["current_shop_index"] = start_idx % len(petshops)
            
            print(f"\n--- Đang xử lý bài {posts_done + 1}/{TARGET_POSTS_PER_RUN} ---")
            
            # 1. AI Viết bài
            article_index = state["keywords_status"][kw]["articles_posted"]
            title, html_content = generate_b2b_article(kw, selected_shops, article_index)
            
            if not title or not html_content:
                print("❌ Bỏ qua do AI sinh nội dung rỗng hoặc lỗi mạng.")
                time.sleep(5)
                continue
            
            # 2. Tải ảnh
            img_bytes = download_stock_photo(kw)
            media_id = None
            if img_bytes:
                media_id = upload_image_to_wp(img_bytes, filename=f"b2b_{int(time.time())}")
                
            # 3. Publish
            success = publish_wp_post(title, html_content, media_id)
            
            if success:
                state["keywords_status"][kw]["articles_posted"] += 1
                state["total_articles_posted"] += 1
                posts_done += 1
                
                # Cập nhật state liên tục để không bị mất data nếu crash
                with open(state_path, 'w', encoding='utf-8') as f:
                    json.dump(state, f, ensure_ascii=False, indent=4)
                    
                print(f"✅ Xong bài {posts_done}. Nghỉ 10s...")
                time.sleep(10)
            else:
                print("❌ Đăng bài thất bại, bỏ qua lượt này.")
                time.sleep(5)

if __name__ == "__main__":
    run_campaign()
