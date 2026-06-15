import os
import json
import time
import random
import schedule
from datetime import datetime
from qwen_model_rotator import chat_with_qwen_rotated
from fully_auto_system import get_woo_products, download_stock_photo, upload_image_to_wp, post_to_wordpress, track_seo_ranking
from b2b_nutrition_campaign import upload_image_bytes_to_wp

DB_FILE = "pain_point_db.json"

def get_next_target():
    if not os.path.exists(DB_FILE):
        return None
        
    with open(DB_FILE, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    for idx, kw in enumerate(db.get("keywords", [])):
        if kw.get("articles_written", 0) < 5:
            # Clean up escape characters from markdown
            keyword = kw["keyword"].replace("\\[", "[").replace("\\]", "]")
            keyword = keyword.replace("[Địa phương]", "TPHCM")
            kw["keyword"] = keyword
            return idx, kw
            
    return None, None

def update_target(idx, rank=0):
    with open(DB_FILE, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    db["keywords"][idx]["articles_written"] += 1
    db["keywords"][idx]["history"].append(rank)
    
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

def select_best_product_for_pain_point(keyword, products):
    """
    Sử dụng AI để duyệt qua danh sách sản phẩm và chọn ra sản phẩm phù hợp nhất với nỗi đau.
    """
    if not products:
        return None
        
    prod_list_str = ""
    for i, p in enumerate(products[:30]): # Giới hạn 30 sản phẩm để tránh quá tải token
        prod_list_str += f"- [{i}] Tên: {p.get('name')} | Giá: {p.get('price')} VND\n"
        
    prompt = f"""
Nỗi đau của khách hàng: "{keyword}"

Dưới đây là danh sách sản phẩm Ecopets hiện có:
{prod_list_str}

Nhiệm vụ: Trả về CHỈ MỘT con số ID (trong ngoặc vuông) của sản phẩm có khả năng giải quyết tốt nhất nỗi đau trên.
KHÔNG giải thích, chỉ trả về số. Ví dụ: 5
"""
    raw = chat_with_qwen_rotated(prompt, max_tokens=10, temperature=0.1)
    
    try:
        import re
        match = re.search(r'\d+', raw)
        if match:
            idx = int(match.group(0))
            if 0 <= idx < len(products):
                prod = products[idx]
                img_url = prod.get("images")[0].get("src", "") if prod.get("images") else ""
                return {
                    "name": prod.get("name"),
                    "link": prod.get("permalink"),
                    "image": img_url,
                    "price": float(prod.get("price") or 0)
                }
    except:
        pass
        
    # Fallback to random
    prod = random.choice(products)
    img_url = prod.get("images")[0].get("src", "") if prod.get("images") else ""
    return {
        "name": prod.get("name"),
        "link": prod.get("permalink"),
        "image": img_url,
        "price": float(prod.get("price") or 0)
    }

def generate_pain_point_article(keyword, article_index, product_info):
    insight_prompt = f"""
Cho từ khóa tìm kiếm thể hiện Nỗi Đau (Pain Point) của người nuôi thú cưng: "{keyword}".
Hãy tạo ra MỘT GÓC NHÌN (Insight) MỚI LẠ VÀ ĐỘC ĐÁO ĐỂ VIẾT BÀI (đây là bài viết thứ {article_index + 1} về chủ đề này).
Hãy đảm bảo góc nhìn này không trùng lặp với các góc nhìn thông thường.
Ví dụ:
- Góc nhìn Y khoa: Phân tích cơ chế sinh lý.
- Góc nhìn Hành vi: Phân tích tâm lý học thú cưng.
- Góc nhìn Môi trường sống: Phân tích tác động từ nhà ở/chung cư.

CHỈ TRẢ VỀ CÂU INSIGHT ĐÓ, KHÔNG GIẢI THÍCH GÌ THÊM.
"""
    insight = chat_with_qwen_rotated(insight_prompt, max_tokens=100, temperature=0.8)
    if not insight: insight = "Góc nhìn chuyên gia thực chiến"
    
    print(f"[*] Góc nhìn (Insight) được chọn: {insight.strip()}")
    
    prod_text = "Không có sản phẩm."
    if product_info:
        prod_text = f"""
Sản phẩm Ecopets đề xuất giải quyết nỗi đau:
Tên: {product_info['name']}
Giá: {product_info['price']:,.0f} đ
Link mua: <a href="{product_info['link']}">{product_info['name']}</a>
Hình ảnh sản phẩm: <img src="{product_info['image']}" alt="{product_info['name']}" />
"""

    prompt = f"""
Bạn là một CHUYÊN GIA THÚ Y VÀ CHĂM SÓC THÚ CƯNG.
Hãy viết một bài đăng blog B2C chuẩn SEO, tối ưu Local SEO (GEO) cho từ khóa: "{keyword}".

Góc nhìn chuyên sâu (Insight): {insight.strip()}

Sản phẩm giải pháp (BẮT BUỘC PHẢI CHÈN VÀO BÀI NHƯ MỘT LỜI KHUYÊN):
{prod_text}

Yêu cầu kỹ thuật:
1. Độ dài: Ít nhất 1200 chữ.
2. Cấu trúc: 
   - Thẻ H1: Tiêu đề bài viết hấp dẫn, chứa từ khóa. Bắt đầu bằng <h1> và kết thúc bằng </h1>.
   - Thẻ H2, H3: Phân chia các luận điểm rõ ràng.
3. Nội dung: Đánh mạnh vào sự đồng cảm với nỗi đau/sự cố của chủ nuôi, giải thích nguyên nhân khoa học (theo Insight), sau đó đưa ra cách giải quyết. Khéo léo đề xuất sản phẩm Ecopets như giải pháp tối ưu.
4. KHÔNG DÙNG MARKDOWN. Dùng HTML thuần túy.
5. CHỖ ĐẶT HÌNH ẢNH MINH HOẠ TỪ PEXELS: Cứ sau khoảng 3-4 đoạn văn, hãy để trống một dòng và ghi chính xác văn bản: [PEXELS_IMAGE_1] và [PEXELS_IMAGE_2]. TUYỆT ĐỐI KHÔNG bọc chúng trong thẻ <img>, không thêm alt, style hay caption gì cả. Chỉ ghi đoạn văn bản đó thôi.
6. Sản phẩm: Phải chèn thẻ <a> và <img> của sản phẩm vào đoạn đề xuất giải pháp. Đừng thay đổi URL.

BẮT ĐẦU VIẾT BÀI VỚI HTML:
"""
    
    raw_html = chat_with_qwen_rotated(prompt, max_tokens=4000, temperature=0.7)
    return raw_html, insight

def run_pain_point_job():
    print("\n=============================================================")
    print("     ECOPETS – HỆ THỐNG PAIN POINT CAMPAIGN (B2C)")
    print("=============================================================")
    
    idx, target = get_next_target()
    if target is None:
        print("[!] Đã hoàn thành toàn bộ 1000 bài viết cho danh sách Pain Point!")
        return
        
    keyword = target["keyword"]
    article_index = target["articles_written"]
    print(f"[*] Mục tiêu: '{keyword}' (Bài {article_index + 1}/5)")
    
    products = get_woo_products()
    selected_product = select_best_product_for_pain_point(keyword, products)
    if selected_product:
        print(f"[*] Sản phẩm giải pháp được chọn: {selected_product['name']}")
        
    raw_html, insight = generate_pain_point_article(keyword, article_index, selected_product)
    
    if not raw_html:
        print("[-] Qwen API lỗi, bỏ qua lượt này.")
        return
        
    # Trích xuất tiêu đề (H1)
    import re
    title = keyword.capitalize()
    h1_match = re.search(r'<h1>(.*?)</h1>', raw_html, re.IGNORECASE)
    if h1_match:
        title = h1_match.group(1).strip()
        raw_html = re.sub(r'<h1>.*?</h1>', '', raw_html, count=1, flags=re.IGNORECASE)
        
    # Xử lý hình ảnh Pexels
    print("  -> Đang lấy ảnh stock Pexels...")
    # Dọn dẹp trường hợp AI lỡ bọc placeholder vào thẻ img
    raw_html = re.sub(r'<img[^>]*\[PEXELS_IMAGE_1\][^>]*>', '[PEXELS_IMAGE_1]', raw_html)
    raw_html = re.sub(r'<img[^>]*\[PEXELS_IMAGE_2\][^>]*>', '[PEXELS_IMAGE_2]', raw_html)
    
    for ph in ["[PEXELS_IMAGE_1]", "[PEXELS_IMAGE_2]"]:
        if ph in raw_html:
            query = "sad dog" if "chó" in keyword.lower() else "sad cat"
            if "môi" in keyword.lower() or "hôi" in keyword.lower() or "phòng" in keyword.lower():
                query = "messy room pet"
            
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
    feat_bytes = download_stock_photo("pet care")
    if feat_bytes:
        media_id, _ = upload_image_bytes_to_wp(feat_bytes, alt_text=title)
        if media_id:
            featured_media_id = media_id
            
    # Nếu tải pexels lỗi, lấy hình sản phẩm làm dự phòng
    if not featured_media_id and selected_product and selected_product["image"]:
        featured_media_id, _ = upload_image_to_wp(selected_product["image"], alt_text=title)
        
    # Post bài lên WordPress (Category ID 3 có thể là Kiến thức/Kinh nghiệm, điều chỉnh sau nếu cần)
    # Ecopets dùng Category ID 65 cho chuyên mục Chăm sóc
    success = post_to_wordpress(title, raw_html, featured_media_id=featured_media_id, category_id=65)
    
    if success:
        rank = track_seo_ranking(keyword)
        update_target(idx, rank)
        print(f"[+] Hoàn tất! Đã đăng bài Pain Point cho: {keyword}")
    else:
        print("[-] Đăng bài lên WP thất bại.")

def start_daemon():
    print("[+] Pain Point Campaign Khởi động - Tốc độ: ~200 bài/ngày (~7 phút/bài)")
    print("[+] Đang chạy bài đầu tiên ngay bây giờ...")
    run_pain_point_job()
    
    schedule.every(7).minutes.do(run_pain_point_job)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except Exception as e:
        print(f"[-] CRITICAL ERROR in Daemon: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(100) # Give time to read before pause

if __name__ == "__main__":
    start_daemon()
