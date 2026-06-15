import requests
resp = requests.get('https://ecopets.vn/wp-json/wp/v2/posts?per_page=5')
posts = resp.json()
print("KẾT QUẢ 5 BÀI VIẾT MỚI NHẤT TRÊN ECOPETS.VN:\n")
for p in posts:
    print(f"Tiêu đề: {p['title']['rendered'][:60]}...")
    print(f"Đường dẫn (Slug): {p['slug']}")
    print(f"Mã Local SEO nhúng trong bài: {'CÓ' if 'LocalBusiness' in p['content']['rendered'] else 'KHÔNG'}")
    print("-" * 30)
