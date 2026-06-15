import os
import json
import time
import requests
import random
import schedule
import smtplib
import unicodedata
import re
import urllib.parse
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from googlesearch import search
from openai import OpenAI
from plyer import notification
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATIONS ---
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_API_URL = "https://ecopets.vn/wp-json/wp/v2/posts"
WP_MEDIA_URL = "https://ecopets.vn/wp-json/wp/v2/media"

WC_KEY = os.getenv("WC_CONSUMER_KEY")
WC_SECRET = os.getenv("WC_CONSUMER_SECRET")
WC_MAIN_URL = "https://ecopets.vn/wp-json/wc/v3"
WC_ORDERS_URL = "https://ecopets.vn/wp-json/wc/v3/reports/sales"

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASS = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# ──────────────────────────────
ECOPETS_USPS = "Ecopets Việt Nam cung cấp nguồn hàng thức ăn chó mèo hữu cơ sinh học, cam kết lợi nhuận tối đa cho đại lý. Hỗ trợ đào tạo kiến thức dinh dưỡng thú y chuyên sâu."
from qwen_manager import chat_with_qwen
from stock_photos import download_stock_photo
from b2b_nutrition_campaign import upload_image_bytes_to_wp, strip_markdown_to_html
from google_indexer import request_indexing

def pop_target_keyword():
    try:
        with open("keyword_clusters.json", "r", encoding="utf-8") as f:
            clusters = json.load(f)
            
        target_kw = None
        target_insight = None
        
        for kw, insights in clusters.items():
            if isinstance(insights, list) and len(insights) > 0:
                target_kw = kw
                target_insight = insights.pop(0)
                break
                
        if not target_kw:
            print("[-] Đã quét sạch ma trận keyword_clusters.json! Vui lòng đổ thêm từ khóa hoặc sinh thêm insight.")
            return None, None
            
        with open("keyword_clusters.json", "w", encoding="utf-8") as f:
            json.dump(clusters, f, ensure_ascii=False, indent=4)
            
        print(f"[*] Từ khóa rút từ Ma trận: {target_kw}")
        print(f"[*] Góc nhìn (Insight) hôm nay: {target_insight}")
        return target_kw, target_insight
    except Exception as e:
        print(f"[-] Lỗi đọc file keyword_clusters.json: {e}")
        return None, None

def research_competitors(keyword):
    print("Đang phân tích bài đối thủ...")
    competitor_contents = []
    try:
        urls = list(search(keyword, num=3, stop=3, pause=2.0))
        for url in urls:
            if "ecopets.vn" not in url:
                try:
                    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                    soup = BeautifulSoup(res.content, 'html.parser')
                    text = " ".join([p.get_text().strip() for p in soup.find_all(['p', 'h2'])])
                    competitor_contents.append(f"Đối thủ ({url}):\n{text[:800]}")
                except:
                    pass
    except:
        pass
    return "\n---\n".join(competitor_contents)

def generate_sales_article(keyword, insight, competitor_data, sale_info):
    print(f"Đang viết bài chuyên gia với Mật Nhãn Insight: {insight}...")

    db_path = "database.json"
    internal_links_context = ""
    past_titles = []

    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
                published = [a for a in db.get("articles", []) if a.get("status") == "Published"]
                past_titles = [a.get("title", "") for a in published]
                
                current_silo_prefix = keyword.split()[0].lower() if keyword else ""
                silo_posts = [a for a in published if a.get("keyword", "").split()[0].lower() == current_silo_prefix]
                other_posts = [a for a in published if a.get("keyword", "").split()[0].lower() != current_silo_prefix]
                selected_posts = (silo_posts[-3:] + other_posts[-2:])[-5:]

                if selected_posts:
                    internal_links_context = "DANH SÁCH BACKLINK BẮT BUỘC CHÈN TỰ NHIÊN VÀO BÀI (anchor text):\n"
                    for a in selected_posts:
                        href_url = f"https://ecopets.vn/{slugify(a['keyword'])}"
                        internal_links_context += f"- '{a['title']}' -> Link: {href_url}\n"
        except:
            pass

    past_titles_text = "\n- ".join(filter(None, past_titles[-15:])) or "Chưa có"

    sale_context = ""
    if sale_info and sale_info.get('discount_percent', 0) > 0:
        sale_context = (
            f"Flash Sale hôm nay: '{sale_info['name']}' giảm {sale_info['discount_percent']}%, "
            f"chỉ còn {sale_info['sale']:,.0f}đ (Gốc: {sale_info['regular']:,.0f}đ). "
            f"Link mua: {sale_info['link']}. Lồng kêu gọi mua hàng vào thân bài."
        )
    elif sale_info:
        sale_context = f"Đề xuất '{sale_info['name']}' của Ecopets. Link: {sale_info['link']}"

    print("  -> Đang lấy ảnh stock Pexels và upload vào WP...")
    img_data1 = download_stock_photo(keyword, width=800, height=500)
    img_data2 = download_stock_photo(keyword, width=800, height=501)

    body1_mid, img_body1_url = upload_image_bytes_to_wp(img_data1, alt_text=f"Chăm sóc thú cưng - {keyword[:40]}") if img_data1 else (None, "")
    body2_mid, img_body2_url = upload_image_bytes_to_wp(img_data2, alt_text=f"Hướng dẫn Ecopets - {keyword[:40]}") if img_data2 else (None, "")

    img_product_url = sale_info.get("image", "") if sale_info else ""
    img_product_name = sale_info.get("name", "") if sale_info else ""
    img_product_link = sale_info.get("link", "https://ecopets.vn") if sale_info else "https://ecopets.vn"

    prompt = f"""Viết bài SEO chuyên sâu cho từ khóa: "{keyword}" theo đúng cấu trúc dưới đây.
ĐẶC BIỆT: Bài viết BẮT BUỘC phải KHAI THÁC MẠNH VÀO INSIGHT / GÓC NHÌN SAU ĐÂY: "{insight}".

ĐÓNG VAI BIÊN TẬP VIÊN KHÓ TÍNH (ONPAGE KỸ):
Bạn không chỉ là người viết, mà còn là một Biên tập viên SEO xuất sắc. Hãy đảm bảo:
- Văn phong tự nhiên, mạch lạc, CÓ CẢM XÚC NHƯ NGƯỜI THẬT viết (không được có cảm giác máy móc, rập khuôn của AI).
- TUYỆT ĐỐI không dùng những từ ngữ sáo rỗng, filler như: "Tuyệt vời", "Dưới đây là", "Bài viết này sẽ", "Hãy nhớ rằng", "Chúc bạn thành công".
- Câu văn phải ngắn gọn, súc tích, đi thẳng vào giải quyết nỗi đau của khách hàng.

PHÂN TÍCH ĐỐI TƯỢNG ĐỘC GIẢ (RẤT QUAN TRỌNG):
- Nếu từ khóa liên quan đến kinh doanh, đại lý, vốn, sỉ lẻ, chính sách -> Viết theo văn phong CHUYÊN GIA KINH DOANH B2B, nói về giải pháp kinh doanh, tối ưu chi phí, thị trường.
- Nếu từ khóa liên quan đến bệnh lý, chăm sóc, thức ăn chó mèo -> Viết theo văn phong CHUYÊN GIA THÚ Y B2C, hướng tới người nuôi thú cưng, nói về triệu chứng, nguyên nhân, cách chữa trị.
TUYỆT ĐỐI KHÔNG dùng văn phong thú y/chữa bệnh cho các từ khóa B2B và ngược lại.

YÊU CẦU CHO TIÊU ĐỀ H1 (QUAN TRỌNG NHẤT):
1. Phải CHỨA từ khóa "{keyword}".
2. Phải thể hiện RÕ RÀNG góc nhìn/insight: "{insight}".
3. Sáng tạo, thu hút, độ dài khoảng 50-70 ký tự.
4. TUYỆT ĐỐI KHÔNG ĐƯỢC GIỐNG hoặc lặp lại mô-típ của các tiêu đề đã dùng bên dưới:
- {past_titles_text}

{internal_links_context}

CẤU TRÚC BÀI BẮT BUỘC:
<h1>[Tiêu đề SEO ngắn]</h1>
<p>[Mở đầu thẳng vào vấn đề, đánh trúng 'nỗi đau' của đúng đối tượng đọc]</p>

<h2>[Tiêu đề H2 số 1: Tùy biến phù hợp ngữ cảnh. VD: Dấu hiệu bệnh lý (B2C) hoặc Thực trạng thị trường (B2B)]</h2>
<p>...</p>
<!-- ILLUSTRATION_1 -->

<h2>[Tiêu đề H2 số 2: Tùy biến. VD: Nguyên nhân (B2C) hoặc Rủi ro & Cơ hội (B2B)]</h2>
<p>...</p><ul>...</ul>
<!-- ILLUSTRATION_2 -->

<h2>[Tiêu đề H2 số 3: Giải pháp thực tế. VD: Các bước xử lý (B2C) hoặc Chiến lược kinh doanh (B2B)]</h2>
<h3>[Ý 1]</h3>... <h3>[Ý 2]</h3>...

<h2>Giải Pháp/Đồng Hành Cùng Ecopets</h2>
<p>[{ECOPETS_USPS}]</p>
<p>[{sale_context}]</p>
<!-- PRODUCT_IMAGE_1 -->

<h2>Câu Hỏi Thường Gặp (FAQ)</h2>
<h3>1. ...?</h3><p>...</p>
<h3>2. ...?</h3><p>...</p>

<h2>Kết Luận</h2>
<p>[Tóm tắt + kêu gọi đọc thêm bài Ecopets]</p>

PHÂN TÍCH ĐỐI THỦ (viết sâu hơn, khác biệt hơn đối thủ):
{competitor_data}

LUẬT BẮT BUỘC KHÁC:
1. Tối thiểu 2000 chữ thực chất.
2. Bắt đầu ngay từ thẻ <h1>. KHÔNG có câu filler rào đón.
3. PHẢI chèn tự nhiên các Internal Link (anchor text) vào các đoạn văn.
4. PHẢI có link mua sản phẩm Ecopets.
5. CHỈ dùng HTML thuần, KHÔNG dùng Markdown (**bold**, ##heading, -bullet, ```html).
"""

    raw = chat_with_qwen(prompt, max_tokens=4000, temperature=0.8)
    if not raw:
        print("  [-] Lỗi Qwen API: Không nhận được phản hồi.")
        return None

    html_text = strip_markdown_to_html(raw)

    h1_idx = html_text.find("<h1")
    if h1_idx > 0:
        html_text = html_text[h1_idx:]

    fig_ai_1 = f'<figure class="wp-block-image size-large aligncenter"><img src="{img_body1_url}" alt="Minh họa triệu chứng {keyword[:40]}" width="800" height="500" style="max-width:100%; height:auto; border-radius: 8px;" loading="lazy"/></figure>'
    fig_ai_2 = f'<figure class="wp-block-image size-large aligncenter"><img src="{img_body2_url}" alt="Thú y điều trị {keyword[:40]}" width="800" height="501" style="max-width:100%; height:auto; border-radius: 8px;" loading="lazy"/></figure>'
    fig_prod = ''
    if img_product_url:
        fig_prod = (
            f'<figure class="wp-block-image size-large aligncenter">'
            f'<a href="{img_product_link}" target="_blank">'
            f'<img src="{img_product_url}" alt="{img_product_name}" width="500" height="500" style="max-width:100%; height:auto; border-radius:10px; border:2px solid #5ab034;" loading="lazy"/>'
            f'</a>'
            f'<figcaption><strong>{img_product_name}</strong> – '
            f'<a href="{img_product_link}" target="_blank">Mua Ngay tại Ecopets</a></figcaption>'
            f'</figure>'
        )

    html_text = html_text.replace("<!-- ILLUSTRATION_1 -->", fig_ai_1)
    html_text = html_text.replace("<!-- ILLUSTRATION_2 -->", fig_ai_2)
    html_text = html_text.replace("<!-- PRODUCT_IMAGE_1 -->", fig_prod)

    # Thêm schema JSON-LD cơ bản như HelloConsen (tuỳ chọn)
    schema_block = f"""
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{keyword[:110].replace(chr(34), '')}",
  "author": {{"@type": "Person", "name": "Chuyên gia Thú y", "worksFor": {{"@type": "Organization", "name": "Ecopets"}}}},
  "publisher": {{"@type": "Organization", "name": "Ecopets", "url": "https://ecopets.vn"}},
  "datePublished": "{datetime.now().strftime('%Y-%m-%d')}"
}}
</script>"""
    html_text = html_text + schema_block

    return html_text

def get_woo_products():
    try:
        import requests
        resp = requests.get(
            f"{WC_MAIN_URL}/products",
            auth=(WC_KEY, WC_SECRET),
            params={"status": "publish", "per_page": 50}
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"  [-] Lỗi lấy sản phẩm Woo: {e}")
    return []

def upload_image_to_wp(url, alt_text=""):
    try:
        import requests
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return upload_image_bytes_to_wp(resp.content, alt_text)
    except Exception as e:
        print(f"  [-] Lỗi tải ảnh từ URL: {e}")
    return None, None

def auto_discount_product(products):
    if not products: return None
    import random
    prod = random.choice(products)
    
    img_url = ""
    if prod.get("images") and len(prod["images"]) > 0:
        img_url = prod["images"][0].get("src", "")
        
    price = float(prod.get("price") or 0)
    regular_price = float(prod.get("regular_price") or price)
    
    discount = 0
    if regular_price > price and regular_price > 0:
        discount = round((regular_price - price) / regular_price * 100)
        
    return {
        "name": prod.get("name"),
        "link": prod.get("permalink"),
        "image": img_url,
        "sale": price,
        "regular": regular_price,
        "discount_percent": discount
    }

def get_woo_revenue():
    try:
        from datetime import datetime, timedelta
        import requests
        
        # Get past 7 days range
        date_min = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        date_max = datetime.now().strftime('%Y-%m-%d')
        
        # Fetch WooCommerce sales report
        response = requests.get(
            WC_ORDERS_URL,
            auth=(WC_KEY, WC_SECRET),
            params={"date_min": date_min, "date_max": date_max}
        )
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                # The total_sales field usually contains the revenue
                return float(data[0].get("total_sales", 0.0))
    except Exception as e:
        print(f"  [-] Lỗi lấy doanh thu WooCommerce: {e}")
    return 0.0

def track_seo_ranking(keyword):
    try:
        urls = list(search(keyword, num=30, stop=30, pause=2.0))
        for rank, url in enumerate(urls, start=1):
            if "ecopets.vn" in url:
                return rank
    except:
        pass
    return 100

def post_to_wordpress(title, content, featured_media_id=None, category_id=1):
    headers = {"Content-Type": "application/json"}
    data = {
        "title": title,
        "content": content,
        "status": "publish",
        "categories": [category_id],
    }
    if featured_media_id:
        data["featured_media"] = featured_media_id

    print(f"🚀 Đăng bài: {title[:60]}...")
    try:
        response = requests.post(
            WP_API_URL,
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            headers=headers,
            json=data
        )
        if response.status_code == 201:
            post_url = response.json().get('link', '')
            print(f"  [+] Live: {post_url}")
            request_indexing(post_url)
            return True
        else:
            print(f"  [-] Lỗi WP: {response.status_code} – {response.text[:200]}")
    except Exception as e:
        print(f"  [-] Lỗi kết nối WP: {e}")
    return False

def run_daily_job():
    keyword, insight = pop_target_keyword()
    if not keyword or not insight:
        print("  [-] Dừng chu kỳ. Đã hết danh sách các Cụm từ khóa hoặc Insight.")
        return
        
    comp_data = research_competitors(keyword)
    products = get_woo_products()
    sale_info = auto_discount_product(products) if products else None
    
    html_content = generate_sales_article(keyword, insight, comp_data, sale_info)

    if not html_content:
        print("  [-] Dừng chu kỳ do không tạo được nội dung.")
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    title = keyword.capitalize()
    h1 = soup.find('h1')
    if h1:
        title = h1.get_text().strip()
        h1.decompose()
    clean_content = str(soup).strip()

    print("  -> Đang thiết lập Hình Đại Diện bằng Pexels...")
    img_featured_data = download_stock_photo(keyword, width=1200, height=630)
    featured_media_id, _ = upload_image_bytes_to_wp(img_featured_data, alt_text=title) if img_featured_data else (None, "")
        
    if not featured_media_id and sale_info and sale_info.get("image"):
        print("  [!] Kích hoạt Fallback: Dùng ảnh thực WooCommerce làm Hình Đại Diện!")
        featured_media_id, _ = upload_image_to_wp(sale_info["image"], alt_text=title)
        
    success = post_to_wordpress(title, clean_content, featured_media_id=featured_media_id)

    rank = track_seo_ranking(keyword)
    revenue = get_woo_revenue()

    db_path = "database.json"
    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
        except:
            db = {"revenue": 0, "keywords": [], "articles": []}
    else:
        db = {"revenue": 0, "keywords": [], "articles": []}

    db["revenue"] = revenue
    db["articles"].append({
        "title": title,
        "keyword": keyword,
        "status": "Published" if success else "Failed",
        "date": datetime.now().strftime("%Y-%m-%d")
    })

    kw_idx = next((i for i, k in enumerate(db.get("keywords", [])) if k.get("keyword") == keyword), None)
    if kw_idx is not None:
        db["keywords"][kw_idx]["history"].append(rank)
    else:
        db.setdefault("keywords", []).append({"keyword": keyword, "history": [rank]})

    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"Ecopets – Đăng bài xong! Bài '{title[:40]}...' đã live!")

def run_weekly_job():
    print("\n[🕒] Đang khởi chạy Module Báo Cáo Từ Khóa Qua Email...")
    revenue = get_woo_revenue()

    db_path = "database.json"
    keywords_status = ""
    total_top10 = 0
    total_tracked = 0
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            db = json.load(f)
            kws = db.get("keywords", [])
            total_tracked = len(kws)
            for k in kws:
                hist = k.get("history", [])
                rank_now = hist[-1] if hist else None
                rank_prev = hist[-2] if len(hist) >= 2 else None

                if rank_now is not None and rank_prev is not None:
                    delta = rank_prev - rank_now
                    if delta > 0:
                        delta_str = f"<span style='color:#2e7d32'>▲{delta}</span>"
                    elif delta < 0:
                        delta_str = f"<span style='color:#c62828'>▼{abs(delta)}</span>"
                    else:
                        delta_str = "<span style='color:#888'>–</span>"
                else:
                    delta_str = "<span style='color:#aaa'>Mới</span>"

                rank_display = rank_now if rank_now else "N/A"
                if isinstance(rank_now, int) and rank_now <= 10:
                    total_top10 += 1

                keywords_status += f"<tr><td>{k['keyword']}</td><td><b>{rank_display}</b> {delta_str}</td></tr>"
    except:
        keywords_status = "<tr><td colspan='2'>Chưa có dữ liệu theo dõi</td></tr>"

    html_email = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #2e7d32; border-bottom: 2px solid #2e7d32; padding-bottom: 5px;">BÁO CÁO SEO & DOANH THU ECOPETS</h2>
        
        <h3>1. Tổng Quan Hiệu Suất</h3>
        <ul style="font-size: 16px;">
          <li><b>Doanh thu WooCommerce (7 ngày qua):</b> <span style="color: #d32f2f; font-size: 18px;">{revenue:,.0f} VND</span></li>
          <li><b>Số từ khóa lọt Top 10 Google:</b> {total_top10} / {total_tracked} từ khóa</li>
        </ul>

        <h3>2. Biến Động Thứ Hạng Từ Khóa</h3>
        <table style="width: 100%; border-collapse: collapse;">
          <tr style="background-color: #f5f5f5; text-align: left;">
            <th style="padding: 10px; border: 1px solid #ddd;">Từ khóa</th>
            <th style="padding: 10px; border: 1px solid #ddd;">Thứ hạng & Biến động</th>
          </tr>
          {keywords_status}
        </table>
        
        <p style="margin-top: 20px; font-size: 12px; color: #888;">Email tạo tự động bởi Hệ thống AI Ecopets.</p>
      </body>
    </html>
    """
    
    try:
        msg = MIMEText(html_email, 'html')
        msg['Subject'] = f"Báo Cáo Tự Động Ecopets – Doanh thu: {revenue:,.0f} VND"
        msg['From'] = f"Hệ Thống AI Ecopets <{SENDER_EMAIL}>"
        msg['To'] = RECEIVER_EMAIL

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASS)
            server.send_message(msg)
        print("  [+] Đã gửi báo cáo Weekly qua Email thành công!")
        notification.notify(
            title="Ecopets Báo Cáo Hàng Tuần",
            message=f"Đã gửi báo cáo! Doanh thu: {revenue:,.0f}đ",
            app_name="Ecopets Auto System",
            timeout=10
        )
    except Exception as e:
        print(f"  [-] Lỗi gửi email báo cáo: {e}")

import time
from datetime import datetime

if __name__ == "__main__":
    print("=============================================================")
    print("     HE THONG VAN HANH SEO TU DONG (ROBUST SCHEDULER)")
    print("=============================================================")
    print(f"Kich hoat he thong tu dong dang bai! (Moi { 86400 } giay 1 bai)")

    last_daily_run = 0
    last_order_check = time.time()
    last_weekly_report = None

    while True:
        now_ts = time.time()
        now_dt = datetime.now()

        # Check orders every 5 minutes (300 seconds)
        if False:
            if now_ts - last_order_check >= 300:
                run_safe(check_new_orders) if "run_safe" in globals() else check_new_orders()
                last_order_check = now_ts

        # Run daily job
        if now_ts - last_daily_run >= 86400:
            print(f"\n[+] Dang chay tien trinh dang bai luc: {now_dt.strftime('%H:%M:%S')}")
            try:
                run_safe(run_daily_job) if "run_safe" in globals() else run_daily_job()
            except Exception as e:
                try:
                    run_daily_job()
                except Exception as ex:
                    print(f"Loi: {ex}")
            last_daily_run = now_ts

        # Check weekly report (Sunday after 10:00)
        if now_dt.weekday() == 6 and now_dt.hour >= 10 and (last_weekly_report is None or last_weekly_report.date() != now_dt.date()):
            try:
                run_safe(run_weekly_job) if "run_safe" in globals() else run_weekly_job()
            except Exception as e:
                try:
                    run_weekly_job()
                except Exception as ex:
                    print(f"Loi: {ex}")
            last_weekly_report = now_dt

        time.sleep(60)
