import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import random
import time
import requests
import re
from datetime import datetime
import schedule
from dotenv import load_dotenv

load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
WP_USERNAME = "aivietbai"
WP_APP_PASSWORD = "kNZG 0aEW 1iy0 tTcT Degh pTR4"
WP_API_URL = "https://ecopets.vn/wp-json/wp/v2/posts"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "b2b_campaign_db.json")

from qwen_manager import chat_with_qwen
from stock_photos import download_stock_photo

def strip_markdown_to_html(text):
    text = text.replace("```html", "")
    text = text.replace("```", "")
    return text.strip()

def notify_desktop(title, msg):
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(title, msg, duration=5)
    except:
        pass

def get_wp_auth_header():
    import base64
    credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode('utf-8')
    return {"Authorization": f"Basic {token}"}

def upload_image_bytes_to_wp(image_bytes, alt_text):
    print("  [📸] Đang upload ảnh lên WordPress...")
    import requests, time, io
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        out_io = io.BytesIO()
        img.save(out_io, format="WEBP", quality=80)
        image_bytes = out_io.getvalue()
        file_ext = "webp"
        mime_type = "image/webp"
        print("  [📸] Đã nén ảnh thành định dạng WebP thành công.")
    except Exception as e:
        print(f"  [!] Lỗi chuyển đổi WebP, dùng định dạng gốc: {e}")
        file_ext = "jpg"
        mime_type = "image/jpeg"

    headers = get_wp_auth_header()
    headers["Content-Type"] = mime_type
    headers["Content-Disposition"] = f'attachment; filename="b2b_{int(time.time())}.{file_ext}"'
    
    for _ in range(3):
        try:
            resp = requests.post("https://ecopets.vn/wp-json/wp/v2/media", headers=headers, data=image_bytes, timeout=30)
            if resp.status_code == 201:
                data = resp.json()
                print(f"  [📸] Upload ảnh thành công! Media ID: {data['id']}")
                return data['id'], data.get('source_url', '')
            else:
                print(f"  [!] Lỗi upload ảnh: {resp.status_code}")
                time.sleep(3)
        except Exception as e:
            time.sleep(3)
    return None, ""

def extract_json_array(text):
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    return []

def generate_longtails_for_pillar(pillar_kw):
    print(f"  [AI] Đang phân tích và sinh 9 từ khóa ngách cho Pillar: '{pillar_kw}'...")
    prompt = f"""
Nhiệm vụ: Bạn là chuyên gia SEO Research ngành thú cưng.
Tôi có 1 từ khóa gốc (Pillar): "{pillar_kw}"
Hãy sinh ra ĐÚNG 9 TỪ KHÓA NGÁCH (Long-tail keywords) để tôi viết 9 bài vệ tinh bổ trợ.
Yêu cầu:
- Phải CÓ LƯỢNG TÌM KIẾM THỰC TẾ (chứa các cụm từ như: tại tphcm, giá rẻ, uy tín, kinh nghiệm, mua ở đâu, lấy sỉ, đánh giá...).
- Dài từ 5-9 chữ. Tự nhiên như cách người dùng gõ Google.
- CHỈ TRẢ VỀ DUY NHẤT 1 MẢNG JSON (Code Block). Không có text nào khác.
Ví dụ: ["{pillar_kw} giá sỉ", "kinh nghiệm nhập {pillar_kw}"]
"""
    for _ in range(3):
        raw = chat_with_qwen(prompt, max_tokens=1500, temperature=0.7)
        if raw:
            arr = extract_json_array(raw)
            if arr and isinstance(arr, list) and len(arr) >= 5:
                return arr[:9]
        time.sleep(2)
    # Fallback
    return [f"{pillar_kw} uy tín", f"{pillar_kw} tại tphcm", f"{pillar_kw} giá rẻ", f"kinh nghiệm {pillar_kw}", f"hướng dẫn {pillar_kw}", f"cách {pillar_kw}", f"mua {pillar_kw}", f"bảng giá {pillar_kw}", f"review {pillar_kw}"]

def generate_b2b_article(keyword_data):
    pillar_kw = keyword_data["keyword"]
    core_insight = keyword_data["insight"]
    published_count = keyword_data.get("published_count", 0)
    
    # Pillar Article vs Cluster Article
    is_pillar = (published_count == 0)
    
    if is_pillar:
        target_keyword = pillar_kw
        article_type = "PILLAR (Bài Đinh)"
    else:
        # Check longtails
        if "longtails" not in keyword_data or len(keyword_data["longtails"]) < 9:
            keyword_data["longtails"] = generate_longtails_for_pillar(pillar_kw)
        
        longtail_index = published_count - 1
        if longtail_index < len(keyword_data["longtails"]):
            target_keyword = keyword_data["longtails"][longtail_index]
        else:
            target_keyword = f"{pillar_kw} phần {published_count}"
        article_type = "CLUSTER (Bài Vệ Tinh)"
        
    print(f"\n[AI] Đang viết bài B2B {article_type} ({published_count+1}/10) cho:")
    print(f"     -> Từ khóa mục tiêu: '{target_keyword}'")

    prompt = f"""Bạn là CHUYÊN GIA TƯ VẤN VẬN HÀNH & KINH DOANH NGÀNH PET.
Nhiệm vụ: Viết MỘT BÀI PHÂN TÍCH CHUYÊN SÂU mang tính thực chiến kinh doanh cao.

ĐÓNG VAI BIÊN TẬP VIÊN KHÓ TÍNH (ONPAGE KỸ):
Hãy đóng vai một Biên tập viên kinh doanh thực chiến. Đảm bảo:
- Văn phong tự nhiên, sắc sảo, KHÔNG có cảm giác máy móc của AI.
- TUYỆT ĐỐI không dùng filler words: "Tuyệt vời", "Dưới đây là", "Bài viết này sẽ", "Hãy cùng khám phá".
- Câu văn đi thẳng vào phân tích lợi nhuận, chi phí, rủi ro, vận hành.

TỪ KHÓA CHÍNH CHO BÀI NÀY: "{target_keyword}"
LOẠI BÀI: {article_type}
{"(Bài này phải cực kỳ dài, uy tín, liệt kê danh sách tổng hợp.)" if is_pillar else "(Bài này phải đi vào một ngách cụ thể, giải quyết đúng 1 vấn đề.)"}

YÊU CẦU TIÊU ĐỀ H1:
- Chứa từ khóa "{target_keyword}".
- Dài tối đa 70 ký tự. Sắc bén, kích thích sự tò mò.

CẤU TRÚC BÀI BẮT BUỘC:
<h1>[Tiêu đề SEO]</h1>
<p>[Mở đầu thẳng vào vấn đề. Ngay trong đoạn đầu, chèn một câu tự nhiên có chứa link này: <a href="https://ecopets.vn/category/kinh-doanh-petshop">kinh doanh petshop</a>]</p>

<h2>[Tiêu đề H2 số 1: Thực trạng / Vấn đề cốt lõi]</h2>
<p>...</p>
<!-- ILLUSTRATION_1 -->

<h2>[Tiêu đề H2 số 2: Phân tích sâu]</h2>
<p>...</p><ul>...</ul>
<!-- ILLUSTRATION_2 -->

<h2>[Tiêu đề H2 số 3: Giải pháp chiến lược]</h2>
<p>...</p>

<h2>Giải Pháp Bứt Phá Lợi Nhuận Cùng Trạm Dinh Dưỡng Xanh Ecopets</h2>
<p>Giữa thời điểm chi phí vận hành ngày càng tăng cao, dự án "Trạm Dinh Dưỡng Xanh Ecopets" (Địa chỉ: 36 Đường 27A, Phường Bình Trưng, Quận 2, TP.HCM) mang đến gói Starter Pack chỉ với số vốn 1 triệu đồng.</p>
<p>Thay vì ôm lô hàng lớn, cửa hàng chỉ cần 1 triệu để nhận 11 hũ viên nhai dinh dưỡng (Beta Amin, Bioline G1, Viên tăng cân). Tổng thu về gần 1.7 triệu đồng, biên lợi nhuận hơn 40%. Đặc biệt, tặng kèm 3 hũ sample Full-size để nhân viên cho thú cưng ăn thử tại quầy thu ngân - tự động chốt sale.</p>
<p>Tìm hiểu chi tiết và đăng ký trở thành đại lý ngay tại bài viết: <a href="https://ecopets.vn/kinh-nghiem-kinh-doanh-petshop-dong-hanh-cung-tram-dinh-duong-xanh-ecopets" target="_blank">Kinh nghiệm kinh doanh petshop: Đồng hành cùng Trạm dinh dưỡng xanh Ecopets</a>.</p>

<h2>Kết Luận</h2>
<p>[Tóm tắt. Bắt buộc nhắc lại địa chỉ Ecopets tại Quận 2, TP.HCM để tối ưu Local SEO GEO]</p>
"""
    
    # Inject Internal Link to Pillar if it's a Cluster Article
    pillar_url = keyword_data.get("pillar_url", "")
    if not is_pillar and pillar_url:
        prompt += f"\nLUẬT INTERNAL LINK (BẮT BUỘC): Trong bài viết, bạn PHẢI chèn 1 thẻ <a> tự nhiên trỏ về bài Pillar như sau: <a href=\"{pillar_url}\">{pillar_kw}</a>."

    prompt += """
LUẬT BẮT BUỘC:
1. Tối thiểu 1500 chữ thực chất.
2. CHỈ dùng HTML thuần, KHÔNG dùng Markdown code block (như ```html). Không có head, body.
3. TUYỆT ĐỐI KHÔNG DÙNG văn phong y khoa chữa bệnh cho thú cưng.
4. TUYỆT ĐỐI KHÔNG TỰ BỊA ĐẶT HOẶC ĐỀ XUẤT chính sách/sản phẩm Ecopets nào khác ngoài Gói Starter Pack 1 triệu đồng đã cho ở trên. Chỉ cung cấp giá trị kiến thức chuẩn xác, không làm sai lệch uy tín công ty.
"""

    raw = chat_with_qwen(prompt, max_tokens=4000, temperature=0.8)
    if not raw:
        print("  [-] Lỗi: Không nhận được phản hồi từ Qwen Manager.")
        return None, None, None

    html_text = strip_markdown_to_html(raw)
    
    title_match = re.search(r'<h1.*?>(.*?)</h1>', html_text, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else f"{target_keyword.capitalize()}"
    html_text = re.sub(r'<h1.*?>.*?</h1>', '', html_text, flags=re.IGNORECASE | re.DOTALL).strip()
    
    print("  -> Đang lấy ảnh minh họa...")
    img1 = download_stock_photo(pillar_kw + " store", width=800, height=500)
    img2 = download_stock_photo(pillar_kw + " business", width=800, height=501)
    
    media1_id, url1 = upload_image_bytes_to_wp(img1, alt_text=f"Kinh doanh {target_keyword[:40]}") if img1 else (None, "")
    media2_id, url2 = upload_image_bytes_to_wp(img2, alt_text=f"Giải pháp {target_keyword[:40]}") if img2 else (None, "")
    
    fig1 = f'<figure class="wp-block-image size-large aligncenter"><img src="{url1}" alt="Mô hình {target_keyword[:40]}" width="800" height="500" loading="lazy"/></figure>' if url1 else ""
    fig2 = f'<figure class="wp-block-image size-large aligncenter"><img src="{url2}" alt="Giải pháp {target_keyword[:40]}" width="800" height="501" loading="lazy"/></figure>' if url2 else ""
    
    html_text = html_text.replace("<!-- ILLUSTRATION_1 -->", fig1)
    html_text = html_text.replace("<!-- ILLUSTRATION_2 -->", fig2)

    return title, html_text, media1_id

def post_to_wordpress(title, content, featured_media_id=None):
    payload = {
        "title": title,
        "content": content,
        "status": "publish",
        "categories": [503], 
    }
    if featured_media_id:
        payload["featured_media"] = featured_media_id

    resp = requests.post(WP_API_URL, json=payload, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=30)
    if resp.status_code in (200, 201):
        print("  [+] Đăng bài THÀNH CÔNG!")
        return resp.json().get('link')
    else:
        print("  [-] Lỗi đăng bài WP:", resp.text)
        return None

def process_one_campaign_article():
    if not os.path.exists(DB_PATH):
        print(f"[-] Database {DB_PATH} không tồn tại!")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    active_kw = None
    kw_index = -1
    for i, kw in enumerate(db["keywords"]):
        if kw.get("published_count", 0) < 10:
            active_kw = kw
            kw_index = i
            break
            
    if not active_kw:
        print("[+] CHIẾN DỊCH B2B ĐÃ HOÀN THÀNH 1000 BÀI!")
        notify_desktop("Ecopets B2B Campaign", "Chiến dịch 1000 bài B2B đã hoàn tất!")
        return

    title, content, featured_id = generate_b2b_article(active_kw)
    if not title or not content:
        print("[-] Sinh bài viết thất bại.")
        return
        
    schema_block = f"""
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Ecopets Việt Nam",
  "address": {{
    "@type": "PostalAddress",
    "streetAddress": "36 Đường 27A",
    "addressLocality": "Phường Bình Trưng",
    "addressRegion": "Quận 2",
    "postalCode": "700000",
    "addressCountry": "VN"
  }}
}}
</script>
"""
    content += schema_block

    print(f"  -> Đang đẩy lên WordPress: {title}")
    post_link = post_to_wordpress(title, content, featured_id)
    
    if post_link:
        if active_kw.get("published_count", 0) == 0:
            db["keywords"][kw_index]["pillar_url"] = post_link
            
        db["keywords"][kw_index]["published_count"] += 1
        db.setdefault("published_articles", []).append({
            "keyword": active_kw["keyword"],
            "title": title,
            "url": post_link,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=4)
            
        print(f"  [+] Đã lưu vào {DB_PATH}. Tiến độ: {db['keywords'][kw_index]['published_count']}/10")

def run_safe():
    try:
        process_one_campaign_article()
    except Exception as e:
        print(f"[X] Lỗi tiến trình: {e}")

if __name__ == "__main__":
    print("=============================================================")
    print("     ECOPETS – CHIẾN DỊCH B2B: PILLAR & CLUSTER")
    print("=============================================================")
    
    # Kịch bản 1 bài mỗi lần chạy. Dùng Task Scheduler (hoặc .bat) để gọi tự động.
    print("\n[+] Đang tiến hành đăng 1 bài...")
    run_safe()
    print("\n[+] Hoàn tất tiến trình. (Để chạy 24/7, hãy thiết lập Windows Task Scheduler)")
