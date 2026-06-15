import os
import json
import requests
import re
from dotenv import load_dotenv
from openai import OpenAI
from stock_photos import download_stock_photo
from fully_auto_system import upload_image_bytes_to_wp, strip_markdown_to_html

load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
WP_USERNAME = "aivietbai"
WP_APP_PASSWORD = "kNZG 0aEW 1iy0 tTcT Degh pTR4"
WP_API_URL = "https://ecopets.vn/wp-json/wp/v2/posts"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "b2b_campaign_db.json")

from qwen_manager import chat_with_qwen

SUB_INSIGHTS = [
    "Tập trung vào phân tích các sai lầm cơ bản khiến chủ shop mất vốn, rủi ro tồn kho và giải pháp quản lý tài chính an toàn.",
    "Tập trung vào các chiến thuật Marketing 0 đồng, cách xây dựng phễu khách hàng và kịch bản tăng tỷ lệ chuyển đổi tại cửa hàng.",
    "Tập trung vào việc tối ưu chi phí vận hành hàng tháng (nhân sự, mặt bằng) và cách gia tăng biên lợi nhuận ròng.",
    "Tập trung vào nghệ thuật tư vấn của nhân viên, cách Upsell/Cross-sell các mặt hàng phụ trợ để tăng giá trị đơn hàng (AOV).",
    "Tập trung vào khâu thiết kế không gian (Setup), tối ưu quầy thu ngân và tạo trải nghiệm khác biệt để giữ chân khách hàng.",
    "Tập trung vào quản lý vòng đời sản phẩm, giải quyết bài toán hàng cận date, hàng thanh lý và tối ưu dòng tiền nhập hàng.",
    "Tập trung vào việc xây dựng thương hiệu cá nhân của chủ shop, uy tín phòng khám và tạo sự trung thành thông qua chất lượng cốt lõi.",
    "Tập trung vào việc áp dụng phần mềm, công nghệ, hệ thống tự động để chủ shop được giải phóng thời gian.",
    "Tập trung vào việc lựa chọn ngách sản phẩm sinh lời cao, ít cạnh tranh thay vì lao vào cuộc chiến giá rẻ của hạt/cát.",
    "Tập trung vào các mô hình nhượng quyền, đại lý ít vốn, dễ thu hồi vốn và khả năng nhân bản cửa hàng nhanh chóng."
]

def generate_fixed_content(keyword_data, post_index, old_title):
    keyword = keyword_data["keyword"]
    core_insight = keyword_data["insight"]
    sub_insight = SUB_INSIGHTS[post_index % 10]
    
    print(f"\n[AI] Đang viết lại bài: '{old_title}'...")
    print(f"     -> Sub-insight: {sub_insight[:80]}...")

    prompt = f"""Bạn là CHUYÊN GIA TƯ VẤN VẬN HÀNH & KINH DOANH NGÀNH PET.
Nhiệm vụ: Viết lại phần nội dung (body content) cho bài viết có tiêu đề "{old_title}".

TỪ KHÓA CHÍNH: "{keyword}"
ĐỐI TƯỢNG ĐỌC: Chủ Pet Shop, chủ Spa Grooming, Bác sĩ thú y mở phòng khám, người khởi nghiệp Pet Hotel.
GÓC NHÌN CHÍNH CỦA NHÓM TỪ KHÓA: {core_insight}
GÓC NHÌN ĐẶC THÙ CHO BÀI VIẾT NÀY (Bắt buộc xoáy sâu): {sub_insight}

CẤU TRÚC BÀI BẮT BUỘC:
<h1>{old_title}</h1>
<p>[Mở đầu thẳng vào vấn đề, đánh trúng 'nỗi đau' theo góc nhìn đặc thù. Ngay trong đoạn đầu, chèn một câu tự nhiên có chứa link này: <a href="https://ecopets.vn/category/kinh-doanh-petshop">kinh doanh petshop</a> để xây dựng cấu trúc Silo SEO]</p>

<h2>[Tiêu đề H2 số 1: Phân tích thực trạng / Nỗi đau. BẮT BUỘC có chứa từ khóa địa phương: "tại TP.HCM" hoặc "Quận 2" để tối ưu GEO Local]</h2>
<p>...</p>
<!-- ILLUSTRATION_1 -->

<h2>[Tiêu đề H2 số 2: Phân tích sâu vào góc nhìn đặc thù đã giao]</h2>
<p>...</p><ul>...</ul>
<!-- ILLUSTRATION_2 -->

<h2>[Tiêu đề H2 số 3: Giải pháp chiến lược]</h2>
<h3>[Ý 1]</h3>... <h3>[Ý 2]</h3>...

<h2>Giải Pháp Bứt Phá Lợi Nhuận Cùng Trạm Dinh Dưỡng Xanh Ecopets</h2>
<p>Giữa thời điểm chi phí vận hành ngày càng tăng cao, việc phụ thuộc vào thức ăn hạt hay cát vệ sinh khiến biên lợi nhuận mỏng. Để giải quyết, dự án "Trạm Dinh Dưỡng Xanh Ecopets" (Địa chỉ: 36 Đường 27A, Phường Bình Trưng, Quận 2, TP.HCM) mang đến gói Starter Pack chỉ với số vốn 1 triệu đồng.</p>
<p>Thay vì ôm lô hàng lớn, cửa hàng chỉ cần 1 triệu để nhận 11 hũ viên nhai dinh dưỡng (Beta Amin, Bioline G1, Viên tăng cân). Tổng thu về gần 1.7 triệu đồng, biên lợi nhuận hơn 40%. Đặc biệt, tặng kèm 3 hũ sample Full-size để nhân viên cho thú cưng ăn thử tại quầy thu ngân - tự động chốt sale mà không cần chèo kéo.</p>
<p>Tìm hiểu chi tiết và đăng ký trở thành đại lý ngay tại bài viết: <a href="https://ecopets.vn/kinh-nghiem-kinh-doanh-petshop-dong-hanh-cung-tram-dinh-duong-xanh-ecopets" target="_blank">Kinh nghiệm kinh doanh petshop: Đồng hành cùng Trạm dinh dưỡng xanh Ecopets</a>.</p>

<h2>Kết Luận</h2>
<p>[Tóm tắt + kêu gọi hợp tác kinh doanh. Bắt buộc nhắc lại địa chỉ Ecopets tại Quận 2, TP.HCM để tối ưu Local SEO GEO]</p>

LUẬT BẮT BUỘC:
1. Tối thiểu 1500 chữ thực chất.
2. CHỈ dùng HTML thuần, KHÔNG dùng Markdown.
3. TUYỆT ĐỐI không dùng văn phong y khoa chữa bệnh cho thú cưng. Phải dùng từ ngữ kinh tế: dòng tiền, biên lợi nhuận, chi phí, tồn kho, khách hàng, up-sale.
4. LUẬT KHÔNG BỊA ĐẶT: Tuyệt đối KHÔNG sáng tác, bịa đặt thêm bất kỳ tên phần mềm, chính sách thanh toán, chương trình khuyến mãi hay dịch vụ nào có gắn tên thương hiệu "Ecopets" (như Ecopets ERP, Clearance Hub, Credit Cycle...). CHỈ ĐƯỢC PHÉP nhắc đến gói "Trạm Dinh Dưỡng Xanh Starter Pack 1 triệu đồng" như đã cung cấp. Các giải pháp quản lý khác chỉ được nói chung chung, KHÔNG gán mác là sản phẩm của Ecopets.
"""

    raw = chat_with_qwen(prompt, max_tokens=8000, temperature=0.8)
    if not raw:
        return None

    html_text = strip_markdown_to_html(raw)
    
    # Loại bỏ H1 vì WP tự render H1 từ title
    html_text = re.sub(r'<h1.*?>.*?</h1>', '', html_text, flags=re.IGNORECASE | re.DOTALL).strip()
    
    print("  -> Đang lấy ảnh minh họa B2B mới...")
    img1 = download_stock_photo(keyword + " store", width=800, height=500)
    img2 = download_stock_photo(keyword + " business", width=800, height=501)
    
    _, url1 = upload_image_bytes_to_wp(img1, alt_text=f"Kinh doanh {keyword[:40]}") if img1 else (None, "")
    _, url2 = upload_image_bytes_to_wp(img2, alt_text=f"Giải pháp {keyword[:40]}") if img2 else (None, "")
    
    fig1 = f'<figure class="wp-block-image size-large aligncenter"><img src="{url1}" alt="Mô hình {keyword[:40]} tại Việt Nam" width="800" height="500" loading="lazy"/></figure>' if url1 else ""
    fig2 = f'<figure class="wp-block-image size-large aligncenter"><img src="{url2}" alt="Giải pháp {keyword[:40]} tối ưu" width="800" height="501" loading="lazy"/></figure>' if url2 else ""
    
    html_text = html_text.replace("<!-- ILLUSTRATION_1 -->", fig1)
    html_text = html_text.replace("<!-- ILLUSTRATION_2 -->", fig2)

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
    return html_text + schema_block

def update_wp_post(post_id, content):
    payload = {
        "content": content,
        "categories": [503]
    }
    url = f"{WP_API_URL}/{post_id}"
    resp = requests.post(url, json=payload, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=30)
    if resp.status_code in (200, 201):
        print(f"  [+] Cập nhật thành công Post ID {post_id}!")
        return True
    else:
        print(f"  [-] Lỗi cập nhật Post ID {post_id}:", resp.text)
        return False

def main():
    if not os.path.exists(DB_PATH):
        print("[-] Không tìm thấy Database!")
        return
        
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    published_titles = [item["title"].strip().lower() for item in db.get("published_articles", [])]
    if not published_titles:
        print("[-] Chưa có bài nào được đăng.")
        return
        
    print(f"[*] Tìm thấy {len(published_titles)} bài đã đăng trong DB. Bắt đầu lấy danh sách từ WordPress...")
    
    # Lấy 50 bài viết gần nhất (Category 22 hoặc 503 nếu đã bị đổi)
    resp = requests.get(f"{WP_API_URL}?per_page=50", auth=(WP_USERNAME, WP_APP_PASSWORD))
    if resp.status_code != 200:
        print("[-] Lỗi lấy bài từ WP!")
        return
        
    wp_posts = resp.json()
    
    # Gom nhóm bài viết theo keyword để lấy keyword_data
    kw_dict = {kw["keyword"]: kw for kw in db["keywords"]}
    
    count_fixed = 0
    for item in db.get("published_articles", []):
        t = item["title"]
        k = item["keyword"]
        
        # Tìm bài viết tương ứng trên WP
        target_post = next((p for p in wp_posts if p["title"]["rendered"].strip().replace('&#8211;', '-').lower() == t.strip().lower() or t.strip().lower() in p["title"]["rendered"].strip().lower()), None)
        
        if not target_post:
            # Fallback API search
            search_resp = requests.get(f"{WP_API_URL}?search={t}&per_page=1", auth=(WP_USERNAME, WP_APP_PASSWORD))
            if search_resp.status_code == 200 and len(search_resp.json()) > 0:
                target_post = search_resp.json()[0]
                
        if not target_post:
            print(f"[-] Không tìm thấy bài '{t}' trên WP để sửa.")
            continue
            
        post_id = target_post["id"]
        
        # Generate new content
        kw_data = kw_dict.get(k)
        if not kw_data:
            continue
            
        # Tính index bài viết (để lấy sub_insight).
        # Giả sử ta tìm ra các bài viết thuộc keyword này trong published_articles
        # để đếm index.
        kw_articles = [a for a in db.get("published_articles", []) if a["keyword"] == k]
        post_idx = next((i for i, a in enumerate(kw_articles) if a["title"] == t), 0)
        
        new_content = generate_fixed_content(kw_data, post_idx, target_post["title"]["rendered"])
        if new_content:
            update_wp_post(post_id, new_content)
            count_fixed += 1
            
    print(f"\n[+] Đã sửa thành công {count_fixed}/{len(published_titles)} bài viết.")

if __name__ == "__main__":
    main()
