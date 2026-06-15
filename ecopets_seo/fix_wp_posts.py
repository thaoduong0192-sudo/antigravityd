import requests
import re
import unicodedata

WP_USERNAME = "aivietbai"
WP_APP_PASSWORD = "kNZG 0aEW 1iy0 tTcT Degh pTR4"
WP_API_URL = "https://ecopets.vn/wp-json/wp/v2/posts"

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii').lower()
    slug = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    words = slug.split('-')
    if len(words) > 7:
        slug = '-'.join(words[:7])
    return slug

def process_posts():
    page = 1
    processed_count = 0
    updated_count = 0
    drafted_count = 0

    schema_block = """
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Ecopets",
  "image": "https://ecopets.vn/wp-content/uploads/2026/05/logo-ecopets.jpg",
  "url": "https://ecopets.vn",
  "telephone": "19001000",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Việt Nam",
    "addressLocality": "Hồ Chí Minh",
    "addressRegion": "Hồ Chí Minh",
    "postalCode": "700000",
    "addressCountry": "VN"
  }
}
</script>"""

    while True:
        print(f"\nĐang tải trang {page}...")
        try:
            resp = requests.get(WP_API_URL, params={"per_page": 20, "page": page, "status": "publish"}, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=30)
            
            if resp.status_code == 400: # Beyond last page
                break
            if resp.status_code != 200:
                print(f"Lỗi truy cập WP API: {resp.status_code} - {resp.text}")
                break

            posts = resp.json()
            if not posts:
                break

            for post in posts:
                processed_count += 1
                post_id = post['id']
                old_slug = post['slug']
                title = post['title']['raw'] if 'raw' in post['title'] else post['title']['rendered']
                content = post['content']['raw'] if 'raw' in post['content'] else post['content']['rendered']
                
                # Sửa HTML tags trong title (wp đôi khi trả về rendered có chứa thẻ)
                title = re.sub(r'<[^>]+>', '', title)

                # 1. Rà soát bài rỗng hoặc lỗi nặng
                if len(content) < 100 or "pollinations.ai" in content or "Lỗi Qwen" in content:
                    print(f"[-] BÀI LỖI: {title[:40]} -> Đang chuyển về Draft")
                    update_resp = requests.post(f"{WP_API_URL}/{post_id}", json={"status": "draft"}, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=15)
                    if update_resp.status_code == 200:
                        drafted_count += 1
                    continue

                needs_update = False
                update_data = {}

                # 2. Fix Slug
                words = old_slug.split('-')
                if len(words) > 9 or len(old_slug) > 80:
                    new_slug = slugify(title)
                    if new_slug != old_slug and new_slug:
                        update_data['slug'] = new_slug
                        needs_update = True
                        print(f"  [Slug] Rút gọn: {old_slug[:20]}... -> {new_slug}")

                # 3. Add LocalBusiness Schema
                if '"@type": "LocalBusiness"' not in content:
                    new_content = content + schema_block
                    update_data['content'] = new_content
                    needs_update = True
                    print(f"  [SEO] Nhúng GEO Schema cho bài {post_id}")

                if needs_update:
                    update_resp = requests.post(f"{WP_API_URL}/{post_id}", json=update_data, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=30)
                    if update_resp.status_code == 200:
                        updated_count += 1
                        print(f"  [+] Đã cập nhật thành công Post ID {post_id}")
                    else:
                        print(f"  [x] Cập nhật lỗi Post ID {post_id}: {update_resp.text[:100]}")

            page += 1
        except Exception as e:
            print(f"Lỗi ngoại lệ: {e}")
            break

    print("\n" + "=" * 40)
    print("QUÉT HOÀN TẤT!")
    print(f"Tổng số bài đã kiểm tra: {processed_count}")
    print(f"Số bài đã cập nhật Slug/GEO: {updated_count}")
    print(f"Số bài đã chuyển về Draft (Lỗi): {drafted_count}")

if __name__ == "__main__":
    process_posts()
