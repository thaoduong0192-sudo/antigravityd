import os
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_API_URL = "https://helloconsen.com/wp-json/wp/v2/posts"

# Từ khóa spam phổ biến hacker hay nhúng vào web
SPAM_KEYWORDS = ["casino", "betting", "gambling", "thenationonlineng", "slot", "poker", "baccarat"]
# Những domain vệ tinh của chúng ta (để ngoại trừ)
SAFE_DOMAINS = ["helloconsen.com", "ecopets.vn", "facebook.com", "zalo.me", "lazada.vn", "tiki.vn", "shopee.vn"]

def is_spam_link(tag):
    if tag.name != 'a': return False
    href = tag.get('href', '').lower()
    text = tag.get_text().lower()
    
    if any(sd in href for sd in SAFE_DOMAINS):
        return False
        
    for kw in SPAM_KEYWORDS:
        if kw in href or kw in text:
            return True
    return False

def inject_geo_schema(html_content, title):
    """Bơm Structure Data dạng MedicalOrganization (Pet Clinic) để tăng điểm E-E-A-T"""
    if "https://schema.org" in html_content and "MedicalOrganization" in html_content:
        return html_content
        
    schema = f"""
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "MedicalOrganization",
      "name": "HelloConsen Pet Shop Hữu Cơ",
      "url": "https://helloconsen.com",
      "description": "Nền tảng cung cấp giải pháp chăm sóc thú cưng hữu cơ, phân phối Beta Amin, men vi sinh cho chó mèo."
    }}
  ]
}}
</script>
"""
    return html_content + schema

def optimize_post(post):
    post_id = post['id']
    title = post['title']['rendered']
    
    # Lấy Raw html nếu được cấp quyền 'edit', thao tác trên RAW sẽ không bị WP strip tags.
    raw_content = post['content']['raw'] if 'raw' in post['content'] else post['content']['rendered']
    
    soup = BeautifulSoup(raw_content, 'html.parser')
    modified = False
    stats = {"spam_removed": 0, "h1_fixed": 0}
    
    # 1. Malware Cleanser
    for a in soup.find_all('a'):
        if is_spam_link(a):
            a.extract()  # Gỡ bỏ tận gốc node HTML chứa spam
            modified = True
            stats["spam_removed"] += 1
            
    # 2. Xóa các node ẩn (Thủ đoạn nhét text ẩn của hacker SEO mũ đen)
    for el in soup.find_all(style=re.compile(r'display:\s*none', re.I)):
        el.extract()
        modified = True
        stats["spam_removed"] += 1

    # 3. Hierarchy Fixer: Đổi H1 trong bài thành H2. Theme đã có H1 ở Title bài.
    for h1 in soup.find_all('h1'):
        h1.name = 'h2'
        modified = True
        stats["h1_fixed"] += 1

    # Force modification to inject schema because previously it skipped
    final_content = str(soup)
    new_content = inject_geo_schema(final_content, title)
    if new_content != final_content:
        modified = True
        final_content = new_content

    if not modified:
        return False, stats
    
    # Đẩy (Update) bài lên WP
    headers = {"Content-Type": "application/json"}
    data = {"content": final_content}
    
    # post['_links']['self'][0]['href'] returns the real endpoint for this entity (be it post or page)
    # But usually just API_URL + id works if we match the correct endpoint type
    # For safety, I'll pass the endpoint explicitly
    endpoint_url = post.get('_links', {}).get('self', [{}])[0].get('href', f"{WP_API_URL}/{post_id}")
    
    try:
        response = requests.post(
            endpoint_url,
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            headers=headers,
            json=data,
            timeout=20
        )
        return response.status_code == 200, stats
    except Exception as e:
        print(f"[-] Lỗi cập nhật bài {post_id}: {e}")
        return False, stats

def run_geo_optimizer():
    print("=====================================================")
    print("   HELLOCONSEN - CÔNG CỤ TỐI ƯU KỸ THUẬT & KHỬ ĐỘC")
    print("=====================================================")
    if not WP_USERNAME or not WP_APP_PASSWORD:
        print("[-] LỖI: Chưa cấu hình WP_USERNAME và WP_APP_PASSWORD trong .env")
        return
        
    endpoints = [
        "https://helloconsen.com/wp-json/wp/v2/posts",
        "https://helloconsen.com/wp-json/wp/v2/pages"
    ]
    
    total_scanned = 0
    total_optimized = 0
    total_spam_removed = 0
    
    for endpoint in endpoints:
        print(f"\n[*] BẮT ĐẦU QUÉT TẠI ENDPOINT: {endpoint}")
        page = 1
        while True:
            print(f"[*] Đang nạp dữ liệu từ CSDL (Page {page})...")
            try:
                # Dùng context=edit để trả về RAW HTML thay vì compiled wp-blocks
                res = requests.get(
                    endpoint, 
                    params={"per_page": 20, "page": page, "context": "edit"},
                    auth=(WP_USERNAME, WP_APP_PASSWORD), 
                    timeout=20
                )
                if res.status_code != 200:
                     if res.status_code == 400: # end of pages
                         print(f"[*] Đã duyệt hết nội dung tại {endpoint}.")
                         break
                     print(f"[-] Lỗi API: {res.status_code}")
                     break
                
                posts = res.json()
                if not posts:
                    print(f"[*] Đã duyệt hết nội dung tại {endpoint}.")
                    break
                    
                for post in posts:
                    total_scanned += 1
                    success, stats = optimize_post(post)
                    if success:
                        total_optimized += 1
                        total_spam_removed += stats["spam_removed"]
                        print(f"  [+] Đã Tối ưu [{post['id']}]: Xóa {stats['spam_removed']} Malware, Fix {stats['h1_fixed']} thẻ H1, Bơm Schema Thành Công.")
                    elif stats["spam_removed"] > 0 or stats["h1_fixed"] > 0:
                        print(f"  [-] Lỗi kết nối khi cập nhật bài {post['id']}")
                        
                page += 1
            except Exception as e:
                print(f"[-] Lỗi ngắt quãng tại endpoint {endpoint}: {e}")
                break

    print(f"\n=====================================================")
    print(f"✅ HOÀN TẤT CHIẾN DỊCH QUÉT TOÀN TRANG")
    print(f" -> Tổng số Bài/Page đã phân tích: {total_scanned}")
    print(f" -> Số bài được chuẩn hóa GEO Schema & H1: {total_optimized}")
    print(f" -> Tổng Backlink Casino / Mã độc ẩn đã dọn dẹp: {total_spam_removed}")
    print("=====================================================")

if __name__ == "__main__":
    run_geo_optimizer()
