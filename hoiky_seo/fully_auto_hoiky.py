import sys
sys.stdout.reconfigure(encoding='utf-8')
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
from fb_auto_post import trigger_facebook_post

load_dotenv()

# --- CONFIGURATIONS ---
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
# --- CONFIGURATIONS HOIKY ---
WP_API_URL = "https://hoiky.com.vn/wp-json/wp/v2/posts"
WP_MEDIA_URL = "https://hoiky.com.vn/wp-json/wp/v2/media"

WC_KEY = os.getenv("WC_CONSUMER_KEY")
WC_SECRET = os.getenv("WC_CONSUMER_SECRET")
# WooCommerce removed for Hoiky
WC_MAIN_URL = None
WC_ORDERS_URL = None

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASS = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

from qwen_manager import chat_with_qwen

HOIKY_USPS = """
BE HERITAGE (hoiky.com.vn) - Dịch vụ viết hồi ký và chấp bút lưu giữ di sản vượt thời gian.
- Hóa thân vào giọng văn khách hàng, thấu cảm sâu sắc.
- Cam kết bảo mật tuyệt đối, khách hàng là tác giả duy nhất.
- Lưu truyền di sản tinh thần quý giá cho thế hệ sau.
Website: https://hoiky.com.vn
"""

last_checked_time = datetime.now()


def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')


def notify_desktop(title, message):
    try:
        notification.notify(title=title, message=message, timeout=10)
    except:
        pass


def check_new_orders():
    global last_checked_time
    if not WC_KEY or not WC_SECRET:
        return
    try:
        after_str = last_checked_time.isoformat()
        response = requests.get(
            f"{WC_MAIN_URL}/orders",
            auth=(WC_KEY, WC_SECRET),
            params={"after": after_str, "status": "processing,pending,on-hold"},
            timeout=10
        )
        if response.status_code == 200:
            orders = response.json()
            for order in orders:
                total = order.get('total', '0')
                first_name = order.get('billing', {}).get('first_name', 'Khách hàng')
                notify_desktop(
                    "🚨 CÓ ĐƠN HÀNG MỚI ECOPETS!",
                    f"Khách {first_name} vừa đặt đơn {total} VND. Xử lý ngay!"
                )
            last_checked_time = datetime.now()
    except:
        pass


def get_woo_products():
    """Lấy toàn bộ sản phẩm từ WooCommerce, trả về list dict."""
    if not WC_KEY or not WC_SECRET:
        return []
    try:
        response = requests.get(
            f"{WC_MAIN_URL}/products",
            auth=(WC_KEY, WC_SECRET),
            params={"status": "publish", "per_page": 20},
            timeout=15
        )
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []


def auto_discount_product(products):
    """Chọn 1 sản phẩm chưa sale, áp dụng giảm giá 10–20%."""
    if not products:
        return None
    not_on_sale = [p for p in products if not p.get('on_sale') and p.get('regular_price')]
    chosen = random.choice(not_on_sale) if not_on_sale else random.choice(products)

    product_id = chosen['id']
    product_name = chosen['name']
    regular_price = float(chosen.get('regular_price') or 0)
    img_url = chosen.get('images', [{}])[0].get('src', '') if chosen.get('images') else ''
    product_link = chosen.get('permalink', 'https://ecopets.vn')

    if not_on_sale and regular_price > 0:
        discount_percent = random.choice([10, 15, 20])
        sale_price = int(regular_price * (100 - discount_percent) / 100)
        date_to = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        try:
            requests.post(
                f"{WC_MAIN_URL}/products/{product_id}",
                auth=(WC_KEY, WC_SECRET),
                json={"sale_price": str(sale_price), "date_on_sale_to": date_to},
                timeout=10
            )
            print(f"  -> Flash Sale: '{product_name}' -{discount_percent}% → {sale_price:,.0f}đ")
        except:
            pass
        return {"id": product_id, "name": product_name, "discount_percent": discount_percent,
                "regular": regular_price, "sale": sale_price, "image": img_url, "link": product_link}
    else:
        return {"id": product_id, "name": product_name, "discount_percent": 0,
                "regular": regular_price, "sale": regular_price, "image": img_url, "link": product_link}


def get_english_prompt(keyword, context):
    try:
        prompt = f"Convert this Vietnamese keyword into 2-3 simple English keywords separated by space, suitable for Unsplash stock photo search. Keyword: '{keyword}'. Return ONLY the keywords without quotes. E.g. 'vietnamese family', 'old book memory'."
        return chat_with_qwen(prompt).strip()
    except Exception as e:
        print(f"  [-] Lỗi Dịch Prompt Hình Ảnh: {e}")
        return "family portrait memory"

def fetch_stock_image_url(english_keywords, width=600, height=600):
    print(f"  -> Trích xuất ảnh chân thực trên Pexels: '{english_keywords}'...")
    if not PEXELS_API_KEY:
        print("  [-] Thiếu PEXELS_API_KEY")
        return None
        
    safe_query = urllib.parse.quote(english_keywords)
    try:
        headers = {"Authorization": PEXELS_API_KEY}
        page = random.randint(1, 3)
        url = f"https://api.pexels.com/v1/search?query={safe_query}&per_page=15&page={page}"
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            photos = data.get("photos", [])
            if photos:
                chosen = random.choice(photos)
                return chosen["src"]["large"]
    except Exception as e:
        print(f"  [-] Lỗi tìm ảnh Pexels: {e}")
        
    print("  -> (Dùng ảnh dự phòng của hệ thống Flickr)")
    return f"https://loremflickr.com/{width}/{height}/{safe_query.replace('%20', ',')}"


def upload_image_to_wp(image_url, alt_text="Ecopets"):
    if not image_url:
        return None
    try:
        img_data = requests.get(image_url, timeout=20).content
        filename = f"hoiky_{random.randint(1000,9999)}.jpg"
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "image/jpeg",
        }
        resp = requests.post(
            WP_MEDIA_URL,
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            headers=headers,
            data=img_data,
            timeout=30
        )
        if resp.status_code == 201:
            media = resp.json()
            requests.post(f"{WP_MEDIA_URL}/{media['id']}", auth=(WP_USERNAME, WP_APP_PASSWORD), json={"alt_text": alt_text}, timeout=10)
            print(f"  -> Đã upload ảnh đại diện (Featured Image) lên WP Media (ID: {media['id']})")
            return media['id']
    except Exception as e:
        print(f"  [-] Lỗi upload ảnh: {e}")
    return None

def upload_image_get_url(image_url, alt_text="Hoiky"):
    if not image_url or image_url.startswith("http") is False:
        return None
    try:
        img_data = requests.get(image_url, timeout=20).content
        filename = f"hoiky_content_{random.randint(1000,9999)}.jpg"
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "image/jpeg",
        }
        resp = requests.post(
            WP_MEDIA_URL,
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            headers=headers,
            data=img_data,
            timeout=30
        )
        if resp.status_code == 201:
            media = resp.json()
            requests.post(f"{WP_MEDIA_URL}/{media['id']}", auth=(WP_USERNAME, WP_APP_PASSWORD), json={"alt_text": alt_text}, timeout=10)
            return media['source_url']
    except Exception as e:
        print(f"  [-] Lỗi upload ảnh nội dung: {e}")
    return None


def extract_json_array(text):
    import re, json
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
Nhiệm vụ: Bạn là chuyên gia SEO Research mảng tự truyện, hồi ký.
Tôi có 1 từ khóa gốc (Pillar): "{pillar_kw}"
Hãy sinh ra ĐÚNG 9 TỪ KHÓA NGÁCH (Long-tail keywords) để tôi viết 9 bài vệ tinh bổ trợ.
Yêu cầu:
- Phải CÓ LƯỢNG TÌM KIẾM THỰC TẾ (chứa các cụm từ như: tại tphcm, giá bao nhiêu, uy tín, kinh nghiệm, thuê ai viết, ý nghĩa, bảo mật...).
- Dài từ 5-9 chữ. Tự nhiên như cách người dùng gõ Google.
- CHỈ TRẢ VỀ DUY NHẤT 1 MẢNG JSON (Code Block). Không có text nào khác.
Ví dụ: ["kinh nghiệm {pillar_kw}", "dịch vụ {pillar_kw} tại tphcm"]
"""
    for _ in range(3):
        raw = chat_with_qwen(prompt)
        if raw:
            arr = extract_json_array(raw)
            if arr and isinstance(arr, list) and len(arr) >= 5:
                return arr[:9]
        import time
        time.sleep(2)
    return [f"{pillar_kw} uy tín", f"{pillar_kw} tại tphcm", f"giá {pillar_kw}", f"kinh nghiệm {pillar_kw}", f"hướng dẫn {pillar_kw}", f"cách {pillar_kw}", f"dịch vụ {pillar_kw}", f"bảo mật {pillar_kw}", f"ý nghĩa {pillar_kw}"]

def discover_daily_keyword():
    from datetime import datetime
    print(f"\n[{datetime.now().strftime('%d/%m/%Y %H:%M')}] BẮT ĐẦU CHU KỲ KIẾN TẠO HOIKY (PILLAR-CLUSTER MATRIX)")
    db_path = "database.json"
    if not os.path.exists(db_path):
        print("[-] Không tìm thấy database.json")
        return None, None, False, None, -1
        
    try:
        import json
        with open(db_path, "r", encoding="utf-8") as f:
            db = json.load(f)
            
        active_kw_obj = None
        kw_index = -1
        for i, kw_obj in enumerate(db.get("keywords", [])):
            if kw_obj.get("published_count", 0) < 10:
                active_kw_obj = kw_obj
                kw_index = i
                break
                
        if not active_kw_obj:
            print("[-] Đã chạy xong TOÀN BỘ database! Không còn từ khóa nào < 10 bài.")
            return None, None, False, None, -1
            
        pillar_kw = active_kw_obj["keyword"]
        published_count = active_kw_obj.get("published_count", 0)
        
        is_pillar = (published_count == 0)
        
        if is_pillar:
            target_keyword = pillar_kw
            print(f"[*] Viết Bài PILLAR (Bài Đinh) cho từ khóa: {target_keyword}")
        else:
            if "longtails" not in active_kw_obj or len(active_kw_obj["longtails"]) < 9:
                active_kw_obj["longtails"] = generate_longtails_for_pillar(pillar_kw)
                db["keywords"][kw_index]["longtails"] = active_kw_obj["longtails"]
                with open(db_path, "w", encoding="utf-8") as f:
                    json.dump(db, f, ensure_ascii=False, indent=2)
            
            longtail_idx = published_count - 1
            if longtail_idx < len(active_kw_obj["longtails"]):
                target_keyword = active_kw_obj["longtails"][longtail_idx]
            else:
                target_keyword = f"{pillar_kw} phần {published_count}"
                
            print(f"[*] Viết Bài CLUSTER (Vệ Tinh) cho từ khóa ngách: {target_keyword}")
            
        return target_keyword, pillar_kw, is_pillar, active_kw_obj.get("pillar_url", ""), kw_index
        
    except Exception as e:
        print(f"[-] Lỗi đọc database: {e}")
        return None, None, False, None, -1


def get_woo_revenue():
    if not WC_KEY or not WC_SECRET:
        return 0
    try:
        response = requests.get(
            WC_ORDERS_URL, auth=(WC_KEY, WC_SECRET),
            params={"date_min": datetime.now().strftime("%Y-%m-01")}, timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0].get('total_sales', 0))
    except:
        pass
    return 0


def research_competitors(keyword):
    print("Đang phân tích bài đối thủ...")
    competitor_contents = []
    try:
        urls = list(search(keyword, num=3, stop=3, pause=2.0))
        for url in urls:
            if "hoiky.com.vn" not in url:
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


def strip_markdown_to_html(text: str) -> str:
    import re
    text = re.sub(r'```[\w]*\n?', '', text)
    text = text.replace('```', '')
    text = re.sub(r'^#{4}\s+(.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^#{3}\s+(.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^#{2}\s+(.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^#{1}\s+(.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'\*{3}(.+?)\*{3}', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'_{3}(.+?)_{3}', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*{2}(.+?)\*{2}', r'<strong>\1</strong>', text)
    text = re.sub(r'_{2}(.+?)_{2}', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'^[-\*]\s+(.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'((?:<li>.*</li>\n?)+)', r'<ul>\n\1</ul>\n', text)
    text = re.sub(r'^\d+\.\s+(.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'^(---+|\*\*\*+)$', '<hr/>', text, flags=re.MULTILINE)
    text = re.sub(r'^>\s+(.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
    lines = text.split('\n')
    wrapped = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('<'):
            wrapped.append(f'<p>{stripped}</p>')
        else:
            wrapped.append(line)
    text = '\n'.join(wrapped)
    return text.strip()

def generate_sales_article(target_keyword, pillar_kw, is_pillar, pillar_url, competitor_data, sale_info):
    article_type = "PILLAR (Bài Đinh)" if is_pillar else "CLUSTER (Bài Vệ Tinh)"
    print(f"Đang viết bài chuyên gia ({article_type})...")

    db_path = "database.json"
    internal_links_context = ""
    past_titles = []
    
    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
                published = [a for a in db.get("articles", []) if a.get("status") == "Published"]
                past_titles = [a.get("title", "") for a in published]

                current_silo_prefix = pillar_kw.split()[0].lower() if pillar_kw else ""
                silo_posts = [a for a in published if a.get("keyword", "").split()[0].lower() == current_silo_prefix]
                other_posts = [a for a in published if a.get("keyword", "").split()[0].lower() != current_silo_prefix]
                selected_posts = (silo_posts[-3:] + other_posts[-2:])[-5:]

                if selected_posts:
                    internal_links_context = "DANH SÁCH BÀI VIẾT LIÊN QUAN (INTERNAL LINK - BẮT BUỘC CHÈN TỰ NHIÊN, ƯU TIÊN BÀI CÙNG NHÓM SILO):\n"
                    for a in selected_posts:
                        href_url = a.get("url", f"https://hoiky.com.vn/{slugify(a['keyword'])}")
                        internal_links_context += f"- Tiêu đề bài: '{a['title']}' -> Link đích: {href_url}\n"
        except Exception:
            pass

    STATIC_CORE_LINKS = [
        {"desc": "Hồi ký của Cha", "url": "https://hoiky.com.vn/hoi-ky-cua-cha/"},
        {"desc": "Hồi ký của Mẹ", "url": "https://hoiky.com.vn/hoi-ky-cua-me/"},
        {"desc": "Hồi ký của Ông", "url": "https://hoiky.com.vn/hoi-ky-cua-ong/"},
        {"desc": "Hồi ký của Bà", "url": "https://hoiky.com.vn/hoi-ky-cua-ba/"},
        {"desc": "Hồi ký Doanh nhân & Nhà sáng lập", "url": "https://hoiky.com.vn/hoi-ky-doanh-nhan-nha-sang-lap-luu-giu-di-san-khoi-nghiep"}
    ]
    
    selected_static_links = random.sample(STATIC_CORE_LINKS, k=min(2, len(STATIC_CORE_LINKS)))
    internal_links_context += "\nDANH SÁCH BÀI VIẾT NỀN TẢNG (BẮT BUỘC CHÈN THÊM):\n"
    for link in selected_static_links:
        internal_links_context += f"- Nội dung/Từ khóa: '{link['desc']}' -> Link đích: {link['url']}\n"
            
    past_titles_text = "\n- ".join(filter(None, past_titles[-15:])) or "Chưa có"

    # Hình ảnh minh họa
    eng_body1 = get_english_prompt(target_keyword, "emotional memoir photo")
    img_body1_raw = fetch_stock_image_url(eng_body1, 600, 600)
    img_body1_url = upload_image_get_url(img_body1_raw, target_keyword) or img_body1_raw
    
    eng_body2 = get_english_prompt(target_keyword, "old family vintage photo")
    img_body2_raw = fetch_stock_image_url(eng_body2, 600, 600)
    img_body2_url = upload_image_get_url(img_body2_raw, target_keyword) or img_body2_raw
    
    img_product_url = ""
    img_product_name = ""
    img_product_link = ""
    if sale_info and sale_info.get("image"):
        img_product_url = sale_info["image"]
        img_product_name = sale_info["name"]
        img_product_link = sale_info["link"]

    prompt = f"""Viết bài chuẩn SEO và GEO chuyên tư vấn về viết hồi ký, chấp bút sách và lưu giữ di sản.

TỪ KHÓA CHÍNH: "{target_keyword}"
LOẠI BÀI: {article_type}
{"(Bài này phải cực kỳ dài, bao quát ý nghĩa tổng quan về việc viết hồi ký, lưu giữ di sản tinh thần.)" if is_pillar else "(Bài này phải đi vào một ngách cụ thể, giải quyết đúng 1 thắc mắc chuyên sâu.)"}

TIÊU ĐỀ H1 (SEO chuẩn, NGẮN GỌN tối đa 70 ký tự):
- Chứa từ khóa "{target_keyword}".
- Tuyệt đối KHÔNG đặt tiêu đề dài lê thê. ĐÚNG 1 THẺ <h1>

YÊU CẦU NGHIÊM NGẶT VỀ NỘI DUNG VÀ BÁO GIÁ (CHỐNG ẢO GIÁC):
- ĐỘ DÀI VÀ CHIỀU SÂU: Bài viết BẮT BUỘC PHẢI ĐẠT TỐI THIỂU 1500 TỪ. Phải phân tích thật sâu sắc, chi tiết, mở rộng các góc nhìn, lấy nhiều ví dụ thực tế cảm động về gia đình, tuyệt đối không được viết ngắn gọn, hời hợt.
- BÁO GIÁ / CHI PHÍ: TUYỆT ĐỐI KHÔNG TỰ BỊA ĐẶT HOẶC GÂY ẢO GIÁC VỀ CÁC CON SỐ GIÁ CẢ DỊCH VỤ. Chỉ được phép hướng dẫn khách hàng tìm hiểu thêm tại chuyên mục "Viết Hồi Ký" trên website hoặc liên hệ trực tiếp đội ngũ chuyên gia BE HERITAGE để được tư vấn lộ trình và chi phí cụ thể. Không tự ý báo giá bất kỳ gói nào.

CÁC TIÊU ĐỀ CŨ ĐÃ DÙNG (CẤM LẶP LẠI MÔ-TÍP VÀ GÓC NHÌN):
- {past_titles_text}

{internal_links_context}

CẤU TRÚC BÀI ĐÚNG FRAMEWORK BE HERITAGE (E-E-A-T & GEO):
<p>[Viết 50-60 chữ trả lời ngay lập tức ý nghĩa cốt lõi của "{target_keyword}" trong việc lưu giữ kỷ niệm và xây dựng di sản gia đình. Bắt đầu thẳng vào vấn đề, KHÔNG in ra các chữ như "Tóm tắt:", "Direct Answer:", hay bất kỳ tiêu đề nào ở dòng đầu này]</p>

<h2>Giá Trị Tinh Thần Của Việc Viết Ký Ức</h2>
<p>...</p>
<!-- ILLUSTRATION_1 -->

<h2>Vì Sao Việc Chấp Bút Ký Ức Này Là Vô Giá?</h2>
<p>...</p>
<ul>...</ul>

<h2>Những Câu Chuyện Truyền Cảm Hứng (Tối ưu Trải Nghiệm Người Dùng)</h2>
<p>[Tạo 1 bảng HTML <table> so sánh ví dụ: Khác biệt giữa việc truyền miệng và việc ghi chép lại thành sách, hoặc Bài học thế hệ trước vs thế hệ sau]. Bảng là yếu tố BẮT BUỘC để người đọc dễ đối chiếu.</p>

<h2>Hành Trình Ghi Nhận Kỷ Niệm Cùng BE HERITAGE</h2>
<!-- ILLUSTRATION_2 -->
<h3>Bước 1: ...</h3>

<h2>Giải Pháp Chấp Bút Từ Be Heritage</h2>
<p>[Giới thiệu ưu điểm của BE HERITAGE: {HOIKY_USPS}]</p>
<p>Tìm hiểu thêm về <strong><a href="https://hoiky.com.vn/">Dịch vụ chấp bút hồi ký</a></strong> của BE HERITAGE để lưu giữ câu chuyện đời mình cho những người thân yêu.</p>

<h2>Câu Hỏi Thường Gặp (FAQ)</h2>
<h3>1. [Câu hỏi thực tế về việc xuất bản hay bảo mật]?</h3><p>[Trả lời ngắn gọn]</p>
<h3>2. [Câu hỏi thực tế về thời gian thực hiện]?</h3><p>[Trả lời]</p>

<h2>Kết Luận & Giá Trị Lan Tỏa</h2>
<p>[Tóm tắt khuyên dùng]</p>
<hr/>
<p><em>✍️ Bài viết được tham vấn chuyên môn bởi: <strong>Chuyên gia Chấp bút - Nền tảng Viết Hồi Ký BE HERITAGE</strong>.</em></p>
"""

    if not is_pillar and pillar_url:
        prompt += f"\nLUẬT INTERNAL LINK PILLAR (BẮT BUỘC): Trong bài viết, bạn PHẢI chèn 1 thẻ <a> tự nhiên trỏ về bài Pillar như sau: <a href=\"{pillar_url}\">{pillar_kw}</a>."

    prompt += """
PHÂN TÍCH ĐỐI THỦ:
{competitor_data}

LUẬT BẮT BUỘC:
1. Bạn BẮT BUỘC chèn tự nhiên các link tĩnh (Internal Link) đã được cung cấp ở trên vào bài viết bằng thẻ HTML `a`.
2. Trả về HTML thuần túy. KHÔNG có câu trò chuyện Robot. KHÔNG markdown.
"""

    try:
        raw = chat_with_qwen(prompt)

        html_text = strip_markdown_to_html(raw)

        h1_idx = html_text.find("<h1")
        if h1_idx > 0:
            html_text = html_text[h1_idx:]

        # Thay thế Placeholders bằng hình ảnh thực (Mã HTML)
        fig_ai_1 = f'<figure class="wp-block-image size-large aligncenter"><img src="{img_body1_url}" alt="Tư vấn {target_keyword[:40]}" style="max-width:100%; border-radius: 8px;" /></figure>'
        fig_ai_2 = f'<figure class="wp-block-image size-large aligncenter"><img src="{img_body2_url}" alt="Hướng dẫn {target_keyword[:40]}" style="max-width:100%; border-radius: 8px;" /></figure>'
        fig_prod = ''
        if img_product_url:
            fig_prod = f'<figure class="wp-block-image size-large aligncenter"><a href="{img_product_link}" target="_blank"><img src="{img_product_url}" alt="{img_product_name}" style="max-width:100%; border-radius:10px; border:2px solid #287bff;" /></a><figcaption><strong>{img_product_name}</strong> – <a href="{img_product_link}" target="_blank">Tìm hiểu trên HelloConsen</a></figcaption></figure>'

        html_text = html_text.replace("<!-- ILLUSTRATION_1 -->", fig_ai_1)
        html_text = html_text.replace("<!-- ILLUSTRATION_2 -->", fig_ai_2)
        # Disabled generic product injection

        # --- Inject Schema JSON-LD (Article + FAQPage) ---
        faq_items_raw = re.findall(r'<h3>\d+\.?\s*(.+?)</h3>\s*<p>(.+?)</p>', html_text, re.DOTALL)
        faq_schema_items = ""
        for q, a in faq_items_raw[:5]:
            clean_q = re.sub('<[^>]+>', '', q).strip().replace('"', '&quot;')
            clean_a = re.sub('<[^>]+>', '', a).strip().replace('"', '&quot;')[:300]
            faq_schema_items += f'{{"@type":"Question","name":"{clean_q}","acceptedAnswer":{{"@type":"Answer","text":"{clean_a}"}}}},'
        faq_schema_items = faq_schema_items.rstrip(',')
        schema_block = f"""
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "Article",
      "headline": "{target_keyword[:110].replace(chr(34), '')}",
      "author": {{"@type": "Person", "name": "Chuyên gia Chấp bút", "worksFor": {{"@type": "Organization", "name": "BE HERITAGE"}}}},
      "publisher": {{"@type": "Organization", "name": "BE HERITAGE", "url": "https://hoiky.com.vn"}},
      "datePublished": "{datetime.now().strftime('%Y-%m-%d')}",
      "description": "Hướng dẫn chuyên sâu về {target_keyword[:80].replace(chr(34), '')}"
    }},
    {{
      "@type": "FAQPage",
      "mainEntity": [{faq_schema_items}]
    }}
  ]
}}
</script>"""
        html_text = html_text + schema_block

        return html_text
    except Exception as e:
        print(f"  [-] Lỗi tạo bài: {e}")
        return None

def track_seo_ranking(keyword):
    try:
        urls = list(search(keyword, num=30, stop=30, pause=2.0))
        for rank, url in enumerate(urls, start=1):
            if "hoiky.com.vn" in url:
                return rank
    except:
        pass
    return 100


def post_to_wordpress(title, content, featured_media_id=None):
    headers = {"Content-Type": "application/json"}
    data = {
        "title": title,
        "content": content,
        "status": "publish",
        "categories": [1],
        "meta": {"_yoast_wpseo_metadesc": f"Thông tin chuyên sâu về {title[:120]}"},
    }
    if featured_media_id:
        data["featured_media"] = featured_media_id

    print(f"🚀 Triển khai Website hoiky.com.vn: {title[:50]}...")
    try:
        response = requests.post(
            WP_API_URL,
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            headers=headers,
            json=data
        )
        if response.status_code == 201:
            post_url = response.json().get('link', '')
            print(f"  [+] Chuyển tiếp vĩnh viễn (Live): {post_url}")
            return post_url
        else:
            print(f"  [-] Lỗi WP: {response.status_code} – {response.text[:200]}")
    except Exception as e:
        print(f"  [-] Lỗi mạng kết nối tới WP Server: {e}")
    return None


def run_daily_job():
    target_keyword, pillar_kw, is_pillar, pillar_url, kw_index = discover_daily_keyword()
    if not target_keyword:
        print("  [-] Dừng chu kỳ. Đã hết danh sách các từ khóa.")
        return
    comp_data = research_competitors(target_keyword)

    products = get_woo_products()
    sale_info = auto_discount_product(products) if products else None

    html_content = generate_sales_article(target_keyword, pillar_kw, is_pillar, pillar_url, comp_data, sale_info)

    if not html_content:
        print("  [-] Dừng chu kỳ do LLM sập.")
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    title = target_keyword.capitalize()
    h1 = soup.find('h1')
    if h1:
        title = h1.get_text().strip()
        h1.decompose()
    clean_content = str(soup).strip()

    # Upload Sinh AI Featured Image
    featured_media_id = None
    eng_featured = get_english_prompt(pillar_kw, "high resolution cover graphic background")
    featured_img_ai_url = fetch_stock_image_url(eng_featured, 600, 600)
    featured_media_id = upload_image_to_wp(featured_img_ai_url, alt_text=title)

    # Đăng bài
    post_url = post_to_wordpress(title, clean_content, featured_media_id=featured_media_id)
    success = bool(post_url)

    # Cập nhật DB
    rank = track_seo_ranking(target_keyword)
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
        "keyword": target_keyword,
        "status": "Published" if success else "Failed",
        "url": post_url if isinstance(post_url, str) else "",
        "date": datetime.now().strftime("%Y-%m-%d")
    })

    if kw_index != -1 and success:
        db["keywords"][kw_index]["published_count"] = db["keywords"][kw_index].get("published_count", 0) + 1
        if is_pillar and post_url and isinstance(post_url, str):
            db["keywords"][kw_index]["pillar_url"] = post_url
            
        db["keywords"][kw_index].setdefault("history", []).append(rank)

    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    notify_desktop("Đăng bài Xong!", f"Bài mới: {title[:40]}...")
    
    # Auto Publish to Facebook if WP was successful
    if success and post_url:
        try:
            trigger_facebook_post(target_keyword, post_url)
        except Exception as fb_err:
            print(f"[-] Facebook Poster Module crashed: {fb_err}")


def run_weekly_job():
    print("\n[🕒] Đang khởi chạy Module Báo Cáo 100 Từ Khóa Qua Email...")
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

                # Tính delta
                if rank_now is not None and rank_prev is not None:
                    delta = rank_prev - rank_now  # positive = improved
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
                    bg_color = "#e8f5e9"
                    total_top10 += 1
                elif isinstance(rank_now, int) and rank_now <= 30:
                    bg_color = "#fff9c4"
                else:
                    bg_color = "#fff"

                # Đếm số bài cluster đã có
                articles_in_silo = [a for a in db.get("articles", []) if a.get("keyword", "").split()[0].lower() == k['keyword'].split()[0].lower()]
                bai_da_viet = len(articles_in_silo)

                keywords_status += (
                    f"<tr style='background-color:{bg_color}'>"
                    f"<td style='padding:8px;border:1px solid #ddd;'>{k['keyword']}</td>"
                    f"<td style='padding:8px;border:1px solid #ddd;text-align:center;'>Top {rank_display}</td>"
                    f"<td style='padding:8px;border:1px solid #ddd;text-align:center;'>{delta_str}</td>"
                    f"<td style='padding:8px;border:1px solid #ddd;text-align:center;'>{bai_da_viet} bài</td>"
                    f"</tr>"
                )
    except Exception as e:
        print(f"  [-] Lỗi truy cập Database Báo Cáo: {e}")

    html_msg = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #0d47a1;">📊 Báo Cáo SEO Tuần - hoiky.com.vn</h2>
        <p>Thưa Sếp, đây là snapshot chiến dịch từ khóa Hồi Ký tuần này:</p>

        <div style="display:flex; gap:20px; margin-bottom:20px;">
          <div style="background:#e3f2fd;padding:15px;border-radius:8px;flex:1;">
            <p style="margin:0;font-size:13px;color:#555;">Tổng Từ Khóa Đang Theo Dõi</p>
            <p style="margin:0;font-size:28px;font-weight:bold;color:#0d47a1;">{total_tracked}</p>
          </div>
          <div style="background:#e8f5e9;padding:15px;border-radius:8px;flex:1;">
            <p style="margin:0;font-size:13px;color:#555;">Đang Trên Top 10 Google</p>
            <p style="margin:0;font-size:28px;font-weight:bold;color:#2e7d32;">{total_top10}</p>
          </div>
          <div style="background:#fff9c4;padding:15px;border-radius:8px;flex:1;">
            <p style="margin:0;font-size:13px;color:#555;">Doanh Thu Tháng Này</p>
            <p style="margin:0;font-size:22px;font-weight:bold;color:#e65100;">{revenue:,.0f}đ</p>
          </div>
        </div>

        <h3>📋 Bảng Theo Dõi 100 Từ Khóa</h3>
        <table style="border-collapse:collapse;width:100%;max-width:800px;margin-bottom:30px;">
          <tr style="background-color:#0d47a1;color:white;">
            <th style="padding:10px;border:1px solid #ddd;text-align:left;">Từ Khóa</th>
            <th style="padding:10px;border:1px solid #ddd;text-align:center;">Thứ Hạng</th>
            <th style="padding:10px;border:1px solid #ddd;text-align:center;">Delta (▲▼)</th>
            <th style="padding:10px;border:1px solid #ddd;text-align:center;">Số Bài Silo</th>
          </tr>
          {keywords_status}
        </table>

        <p style="font-size:12px;color:#aaa;"><i>🟢 Xanh = Top 10 | 🟡 Vàng = Top 11-30 | Trắng = Cần đẩy thêm bài Cluster. Báo cáo tự sinh mỗi Chủ Nhật.</i></p>
    </body>
    </html>
    """

    try:
        if SENDER_EMAIL and SENDER_PASS and RECEIVER_EMAIL:
            msg = MIMEText(html_msg, "html")
            msg['Subject'] = f"📈 Báo Cáo SEO Từ Khóa HOIKY - {datetime.now().strftime('%d/%m/%Y')}"
            msg['From'] = SENDER_EMAIL
            msg['To'] = RECEIVER_EMAIL
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(SENDER_EMAIL, SENDER_PASS)
                server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
            print(f"  [+] Email báo cáo {total_tracked} từ khóa đã gửi! Top10: {total_top10}")
            notify_desktop("Báo Cáo Tuần", f"Top10: {total_top10}/{total_tracked} từ khóa. Doanh thu: {revenue:,.0f}đ")
        else:
            print("  [-] Thiếu cấu hình email trong .env")
    except Exception as e:
        print(f"  [-] Lỗi gửi email: {e}")


def run_safe(job_func):
    try:
        job_func()
    except Exception as e:
        print(f"  [X] System Alert: Job {job_func.__name__} bị lỗi: {e}")

import time
from datetime import datetime

if __name__ == "__main__":
    print("=============================================================")
    print("     HE THONG VAN HANH SEO TU DONG (ROBUST SCHEDULER)")
    print("=============================================================")
    print(f"Kich hoat he thong tu dong dang bai! (Moi { 4320 } giay 1 bai)")

    last_daily_run = 0
    last_order_check = time.time()
    last_weekly_report = None

    while True:
        now_ts = time.time()
        now_dt = datetime.now()

        # Check orders every 5 minutes (300 seconds)
        if True:
            if now_ts - last_order_check >= 300:
                run_safe(check_new_orders) if "run_safe" in globals() else check_new_orders()
                last_order_check = now_ts

        # Run daily job
        if now_ts - last_daily_run >= 4320:
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
