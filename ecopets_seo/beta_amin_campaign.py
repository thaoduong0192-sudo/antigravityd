import os
import json
import time
import random
import schedule
import re
from datetime import datetime
from qwen_model_rotator import chat_with_qwen_rotated
from fully_auto_system import get_woo_products, download_stock_photo, upload_image_to_wp, post_to_wordpress, track_seo_ranking
from b2b_nutrition_campaign import upload_image_bytes_to_wp

DB_FILE = "beta_amin_db.json"
BETA_AMIN_PRODUCT_ID = 6615  # Sốt đạm thủy phân sấy Beta Amin ID

def get_next_target():
    if not os.path.exists(DB_FILE):
        return None
        
    with open(DB_FILE, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    for idx, kw in enumerate(db.get("keywords", [])):
        if kw.get("articles_written", 0) < kw.get("target_articles", 0):
            # Clean up escape characters from markdown
            keyword = kw["keyword"].replace("\\[", "[").replace("\\]", "]")
            kw["keyword"] = keyword
            return idx, kw
            
    return None, None

def update_target(idx):
    with open(DB_FILE, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    db["keywords"][idx]["articles_written"] += 1
    
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

def generate_beta_amin_article(keyword, core_insight, article_index):
    perspectives = [
        "Góc nhìn Tập tính học (Behavioral): Rào cản tâm lý, thói quen sai lầm của chủ",
        "Góc nhìn Sinh hóa (Biochemical): Phân tích khứu giác, kích thích thụ thể umami",
        "Góc nhìn Bệnh lý học (Pathological): Chớm viêm ruột, viêm nướu, đau răng, mệt mỏi",
        "Góc nhìn Tuổi tác (Geriatric/Pediatric): Lão hóa suy giảm enzym hoặc mới cai sữa",
        "Góc nhìn Môi trường (Environmental): Stress do thời tiết, chuyển nhà, có thú cưng mới",
        "Góc nhìn Dinh dưỡng (Nutritional): Thức ăn cũ mất độ ẩm, oxy hóa lipid, dinh dưỡng rỗng"
    ]
    
    selected_perspective = perspectives[article_index % len(perspectives)]
    
    print(f"[*] Góc nhìn Y khoa được chọn: {selected_perspective}")
    
    prompt = f"""
Bạn là một BÁC SĨ THÚ Y VÀ CHUYÊN GIA DINH DƯỠNG THÚ CƯNG.
Hãy viết một bài đăng blog B2C chuẩn SEO (độ dài trên 1200 chữ) cho từ khóa: "{keyword}".

Insight Cốt Lõi: {core_insight}
Góc nhìn Y Khoa yêu cầu: {selected_perspective}

Mục tiêu chốt sale: Phân tích sâu sắc vấn đề theo góc nhìn Y khoa trên, sau đó BẮT BUỘC chốt sale bằng sản phẩm "Sốt Đạm Thủy Phân Sấy Beta Amin Ecopets" (giá siêu rẻ 25.000đ/gói 10gr). 
Lưu ý về sản phẩm: Chứa đạm thủy phân <3kDa (hấp thu 95%), Taurine, Arginine, kháng dị ứng, kích thích vị giác umami cực mạnh từ đạm nấm men và phô mai. Rất dễ sử dụng: rắc lên hạt hoặc pha nước ấm thành súp.

Sản phẩm giải pháp (BẮT BUỘC PHẢI CHÈN VÀO BÀI NHƯ MỘT PHÁC ĐỒ ĐIỀU TRỊ/LỜI KHUYÊN):
Tên: Sốt Đạm Thủy Phân Sấy Beta Amin Ecopets - Kích Thích Ăn, Phục Hồi Thể Trạng
Link mua: <a href="https://ecopets.vn/products/beta-amin-ecopets-sot-dam-thuy-phan-say-cho-cho-meo-ken-an-bung-yeu">Sốt Đạm Thủy Phân Sấy Beta Amin</a>

Yêu cầu kỹ thuật BẮT BUỘC (Nếu vi phạm sẽ bị lỗi hệ thống):
1. Cấu trúc: Thẻ H1 (Tiêu đề, bắt đầu bằng <h1> và kết thúc bằng </h1>), H2, H3 phân chia rõ ràng.
2. TUYỆT ĐỐI KHÔNG SỬ DỤNG MARKDOWN. CHỈ ĐƯỢC PHÉP DÙNG HTML.
   - LỖI THƯỜNG GẶP 1: Không dùng dấu `**` hoặc `__` để in đậm. Thay vào đó, PHẢI dùng thẻ `<strong>`.
   - LỖI THƯỜNG GẶP 2: TUYỆT ĐỐI KHÔNG sử dụng ký tự Unicode đặc biệt (toán học) để tạo chữ in đậm giả (ví dụ như 𝘁𝗵𝘂̛𝗼̛̣𝗻𝗴). Chỉ được dùng chữ cái bình thường bọc trong thẻ `<strong>`.
   - LỖI THƯỜNG GẶP 3: Không dùng dấu `#`, `##`, `###` cho tiêu đề. Thay vào đó, PHẢI dùng `<h2>`, `<h3>`.
3. BÀI VIẾT PHẢI 100% LÀ TIẾNG VIỆT.
   - TUYỆT ĐỐI KHÔNG chèn tiếng Trung Quốc, tiếng Nhật (ví dụ như chữ 性命, 救命), hoặc tiếng Anh (trừ các thuật ngữ y khoa quốc tế).
   - Văn phong tự nhiên, chuẩn ngôn ngữ người Việt.
4. CHỖ ĐẶT HÌNH ẢNH: Cứ sau 3-4 đoạn văn, ghi chính xác: [PEXELS_IMAGE_1] và [PEXELS_IMAGE_2]. Không bọc trong thẻ <img>.

BẮT ĐẦU VIẾT BÀI VỚI HTML THUẦN:
"""
    
    raw_html = chat_with_qwen_rotated(prompt, max_tokens=4000, temperature=0.7)
    return raw_html, selected_perspective

def run_beta_amin_job():
    print("\n=============================================================")
    print("     ECOPETS – HỆ THỐNG BETA AMIN CAMPAIGN (600 BÀI)")
    print("=============================================================")
    
    idx, target = get_next_target()
    if target is None:
        print("[!] Đã hoàn thành toàn bộ 600 bài viết cho chiến dịch Beta Amin!")
        return
        
    keyword = target["keyword"]
    article_index = target["articles_written"]
    target_count = target["target_articles"]
    core_insight = target["core_insight"]
    
    print(f"[*] Mục tiêu: '{keyword}' (Bài {article_index + 1}/{target_count})")
    
    raw_html, insight = generate_beta_amin_article(keyword, core_insight, article_index)
    
    if not raw_html:
        print("[-] Qwen API lỗi, bỏ qua lượt này.")
        return
        
    # Trích xuất tiêu đề (H1)
    title = keyword.capitalize()
    h1_match = re.search(r'<h1>(.*?)</h1>', raw_html, re.IGNORECASE)
    if h1_match:
        title = h1_match.group(1).strip()
        raw_html = re.sub(r'<h1>.*?</h1>', '', raw_html, count=1, flags=re.IGNORECASE)
        
    # Xử lý tàn dư Markdown (Fallback)
    raw_html = raw_html.replace('**', '')
    raw_html = re.sub(r'###\s+(.*?)\n', r'<h3>\1</h3>\n', raw_html)
    raw_html = re.sub(r'##\s+(.*?)\n', r'<h2>\1</h2>\n', raw_html)
    raw_html = raw_html.replace('```html', '').replace('```', '').strip()
        
    # Xử lý hình ảnh Pexels
    print("  -> Đang lấy ảnh stock Pexels...")
    # Dọn dẹp trường hợp AI lỡ bọc placeholder vào thẻ img
    raw_html = re.sub(r'<img[^>]*\[PEXELS_IMAGE_1\][^>]*>', '[PEXELS_IMAGE_1]', raw_html)
    raw_html = re.sub(r'<img[^>]*\[PEXELS_IMAGE_2\][^>]*>', '[PEXELS_IMAGE_2]', raw_html)
    
    for ph in ["[PEXELS_IMAGE_1]", "[PEXELS_IMAGE_2]"]:
        if ph in raw_html:
            query = "veterinary clinic" if article_index % 2 == 0 else "dog eating"
            if "mèo" in keyword.lower():
                query = "cat eating"
            
            photo_bytes = download_stock_photo(query)
            if photo_bytes:
                media_id, wp_img_url = upload_image_bytes_to_wp(photo_bytes, alt_text=keyword)
                if wp_img_url:
                    img_tag = f'<figure class="wp-block-image size-large"><img src="{wp_img_url}" alt="{keyword}"/></figure>'
                    raw_html = raw_html.replace(ph, img_tag)
                else:
                    raw_html = raw_html.replace(ph, "")
            else:
                raw_html = raw_html.replace(ph, "")
                
    # Upload hình đại diện
    featured_media_id = None
    print("  -> Đang thiết lập Hình Đại Diện...")
    feat_bytes = download_stock_photo("happy pet dog cat")
    if feat_bytes:
        media_id, _ = upload_image_bytes_to_wp(feat_bytes, alt_text=title)
        if media_id:
            featured_media_id = media_id
            
    # Post bài lên WordPress (Category ID 65: Chăm sóc)
    success = post_to_wordpress(title, raw_html, featured_media_id=featured_media_id, category_id=65)
    
    if success:
        update_target(idx)
        print(f"[+] Hoàn tất! Đã đăng bài Beta Amin cho: {keyword}")
    else:
        print("[-] Đăng bài lên WP thất bại.")

def start_daemon():
    print("[+] Beta Amin Campaign Khởi động - Tốc độ: 20 bài/ngày (~72 phút/bài)")
    print("[+] Đang chạy bài đầu tiên ngay bây giờ...")
    run_beta_amin_job()
    
    schedule.every(72).minutes.do(run_beta_amin_job)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except Exception as e:
        print(f"[-] CRITICAL ERROR in Daemon: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(100)

if __name__ == "__main__":
    start_daemon()
