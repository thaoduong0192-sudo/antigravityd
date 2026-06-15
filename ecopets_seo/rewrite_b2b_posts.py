import os
import requests
import json
from dotenv import load_dotenv
from openai import OpenAI
import re
from stock_photos import download_stock_photo
from fully_auto_system import upload_image_bytes_to_wp, strip_markdown_to_html

load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
WP_USERNAME = "aivietbai"
WP_APP_PASSWORD = "kNZG 0aEW 1iy0 tTcT Degh pTR4"
WP_API_URL = "https://ecopets.vn/wp-json/wp/v2/posts"





from qwen_manager import chat_with_qwen

def is_b2b_title(title: str) -> bool:
    b2b_keywords = ["sỉ", "đại lý", "pet shop", "kinh doanh", "vốn", "dropshipping", "chiết khấu", "bán buôn"]
    title_lower = title.lower()
    return any(kw in title_lower for kw in b2b_keywords)

def get_internal_links(keyword):
    db_path = "database.json"
    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
                published = [a for a in db.get("articles", []) if a.get("status") == "Published"]
                current_silo_prefix = keyword.split()[0].lower() if keyword else ""
                silo_posts = [a for a in published if a.get("keyword", "").split()[0].lower() == current_silo_prefix]
                other_posts = [a for a in published if a.get("keyword", "").split()[0].lower() != current_silo_prefix]
                return (silo_posts[-3:] + other_posts[-2:])[-5:]
        except:
            pass
    return []

def generate_rewritten_content(title, keyword):
    print(f"  -> Đang viết lại nội dung B2B cho: '{title}'...")
    
    ECOPETS_USPS = "Ecopets Việt Nam cung cấp nguồn hàng thức ăn chó mèo hữu cơ sinh học, cam kết lợi nhuận tối đa cho đại lý. Hỗ trợ đào tạo kiến thức dinh dưỡng thú y chuyên sâu."
    sale_context = "Đăng ký trở thành đại lý Ecopets ngay hôm nay để nhận chính sách chiết khấu tốt nhất. Link: https://ecopets.vn/lien-he"
    
    internal_links_context = ""
    links = get_internal_links(keyword)
    if links:
        internal_links_context = "DANH SÁCH BACKLINK BẮT BUỘC CHÈN TỰ NHIÊN VÀO BÀI (anchor text):\n"
        for a in links:
            slug = a['keyword'].replace(' ', '-')
            internal_links_context += f"- '{a['title']}' -> Link: https://ecopets.vn/{slug}\n"

    prompt = f"""Bạn là CHUYÊN GIA KINH DOANH VÀ VẬN HÀNH B2B TRONG NGÀNH PET.
Nhiệm vụ: Viết một bài viết cực kỳ chuyên sâu, mang đậm tính thực chiến kinh doanh, hướng tới đối tượng đọc là: Chủ Pet Shop, người khởi nghiệp kinh doanh thú cưng, nhà phân phối, đại lý sỉ.

TỪ KHÓA CHÍNH: "{keyword}"
TIÊU ĐỀ BÀI CŨ ĐANG BỊ SAI VĂN PHONG: "{title}"

YÊU CẦU ĐẶC BIỆT:
1. SÁNG TẠO MỘT TIÊU ĐỀ H1 HOÀN TOÀN MỚI (TỐI ĐA 65 KÝ TỰ). Tiêu đề phải cực kỳ ngắn gọn, sắc bén, đánh thẳng vào nỗi đau kinh doanh của đại lý/chủ shop. Ví dụ: "Cách Kinh Doanh Pet Shop Online: Giải Pháp Lợi Nhuận Cao"
Tuyệt đối KHÔNG giữ lại bất kỳ cấu trúc, ý nghĩa hay từ ngữ nào của tiêu đề cũ. CẤM dùng các từ: sức khỏe, dinh dưỡng, chữa bệnh, người nuôi, thú y.
2. Nội dung phải nói về giải pháp kinh doanh, tối ưu chi phí, thị trường, rủi ro nhập hàng, chiến lược bán hàng.

{internal_links_context}

CẤU TRÚC BÀI BẮT BUỘC:
<h1>[Tiêu đề SEO MỚI ngắn gọn, chuẩn B2B]</h1>
<p>[Mở đầu thẳng vào vấn đề, đánh trúng 'nỗi đau' của người kinh doanh]</p>

<h2>[Tiêu đề H2 số 1: Thực trạng thị trường/Thách thức nhập hàng]</h2>
<p>...</p>
<!-- ILLUSTRATION_1 -->

<h2>[Tiêu đề H2 số 2: Phân tích rủi ro & Cơ hội kinh doanh]</h2>
<p>...</p><ul>...</ul>
<!-- ILLUSTRATION_2 -->

<h2>[Tiêu đề H2 số 3: Chiến lược kinh doanh/Giải pháp tối ưu lợi nhuận]</h2>
<h3>[Chiến lược 1]</h3>... <h3>[Chiến lược 2]</h3>...

<h2>Giải Pháp Nhập Sỉ Đồng Hành Cùng Ecopets</h2>
<p>[{ECOPETS_USPS}]</p>
<p>[{sale_context}]</p>

<h2>Câu Hỏi Thường Gặp (FAQ) Dành Cho Đại Lý</h2>
<h3>1. ...?</h3><p>...</p>
<h3>2. ...?</h3><p>...</p>

<h2>Kết Luận</h2>
<p>[Tóm tắt + kêu gọi hợp tác kinh doanh cùng Ecopets]</p>

LUẬT BẮT BUỘC:
1. Tối thiểu 1500 chữ thực chất.
2. Bắt đầu ngay từ thẻ <h1>. KHÔNG có câu filler ("Tuyệt vời!", "Dưới đây là...", "Xin chào").
3. PHẢI chèn tự nhiên các Internal Link (anchor text) vào các đoạn văn.
4. CHỈ dùng HTML thuần, KHÔNG dùng Markdown (**bold**, ##heading, -bullet, ```html).
"""

    try:
        resp = qwen_client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8000,
            temperature=0.7
        )
        raw = resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"  [-] Lỗi Qwen API: {e}")
        return None

    html_text = strip_markdown_to_html(raw)
    
    print("  -> Đang lấy ảnh stock minh họa mới...")
    img_data1 = download_stock_photo(keyword, width=800, height=500)
    img_data2 = download_stock_photo(keyword, width=800, height=501)

    body1_mid, img_body1_url = upload_image_bytes_to_wp(img_data1, alt_text=f"Kinh doanh pet shop - {keyword[:40]}") if img_data1 else (None, "")
    body2_mid, img_body2_url = upload_image_bytes_to_wp(img_data2, alt_text=f"Đại lý thú cưng - {keyword[:40]}") if img_data2 else (None, "")
    
    fig_ai_1 = f'<figure class="wp-block-image size-large aligncenter"><img src="{img_body1_url}" alt="Minh họa {keyword[:40]}" width="800" height="500" style="max-width:100%; height:auto; border-radius: 8px;" loading="lazy"/></figure>'
    fig_ai_2 = f'<figure class="wp-block-image size-large aligncenter"><img src="{img_body2_url}" alt="Giải pháp {keyword[:40]}" width="800" height="501" style="max-width:100%; height:auto; border-radius: 8px;" loading="lazy"/></figure>'

    html_text = html_text.replace("<!-- ILLUSTRATION_1 -->", fig_ai_1)
    html_text = html_text.replace("<!-- ILLUSTRATION_2 -->", fig_ai_2)

    return html_text

def process_rewrite():
    print("Đang tải danh sách 60 bài viết mới nhất từ WordPress...")
    resp = requests.get(WP_API_URL, params={"per_page": 60, "status": "publish"}, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=15)
    if resp.status_code != 200:
        print("Lỗi API WP")
        return

    posts = resp.json()
    b2b_posts = [p for p in posts if is_b2b_title(p['title']['rendered'])]
    
    print(f"Tìm thấy {len(b2b_posts)} bài viết có tính chất B2B cần sửa.")
    
    for i, post in enumerate(b2b_posts):
        post_id = post['id']
        title = post['title']['rendered']
        print(f"\n[{i+1}/{len(b2b_posts)}] Đang xử lý Post ID {post_id}: {title}")
        
        keyword = post['slug'].replace('-', ' ')
        
        new_content = generate_rewritten_content(title, keyword)
        if not new_content:
            print("  [-] Thất bại khi sinh nội dung mới.")
            continue
            
        new_title_match = re.search(r'<h1.*?>(.*?)</h1>', new_content, re.IGNORECASE | re.DOTALL)
        new_title = new_title_match.group(1).strip() if new_title_match else title
        
        new_content = re.sub(r'<h1.*?>.*?</h1>', '', new_content, flags=re.IGNORECASE | re.DOTALL).strip()
            
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
        new_content += schema_block
        
        print(f"  -> Đang đẩy nội dung và tiêu đề mới lên WordPress: {new_title}")
        update_resp = requests.post(
            f"{WP_API_URL}/{post_id}", 
            json={"title": new_title, "content": new_content}, 
            auth=(WP_USERNAME, WP_APP_PASSWORD), 
            timeout=30
        )
        
        if update_resp.status_code == 200:
            print("  [+] Cập nhật THÀNH CÔNG bài viết B2B!")
        else:
            print("  [x] Lỗi cập nhật:", update_resp.text)

if __name__ == "__main__":
    if qwen_client:
        process_rewrite()
    else:
        print("Không thể kết nối AI")
