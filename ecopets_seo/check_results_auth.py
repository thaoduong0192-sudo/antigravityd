import requests

WP_USERNAME = "aivietbai"
WP_APP_PASSWORD = "kNZG 0aEW 1iy0 tTcT Degh pTR4"
WP_API_URL = "https://ecopets.vn/wp-json/wp/v2/posts"

# Gọi API với xác thực để bypass LiteSpeed Cache
resp = requests.get(WP_API_URL, params={"per_page": 5, "status": "publish"}, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=15)
posts = resp.json()

print("KẾT QUẢ THỰC TẾ 5 BÀI VIẾT (ĐÃ XUẤT BẢN) SAU KHI DỌN DẸP:\n")
for p in posts:
    title = p['title']['rendered']
    slug = p['slug']
    content = p['content']['rendered']
    
    # Check schema
    has_schema = 'LocalBusiness' in content or 'LocalBusiness' in p.get('content', {}).get('raw', '')
    
    print(f"Tiêu đề: {title[:60]}...")
    print(f"Đường dẫn (Slug): {slug}")
    print(f"Mã Local SEO nhúng trong bài: {'CÓ' if has_schema else 'KHÔNG'}")
    print("-" * 40)
