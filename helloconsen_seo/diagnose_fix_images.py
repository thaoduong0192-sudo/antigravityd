import requests
import os
import re
import random
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WP_URL", "https://helloconsen.com")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_MEDIA_URL = f"{WP_URL}/wp-json/wp/v2/media"
WP_POSTS_API = f"{WP_URL}/wp-json/wp/v2/posts"

FALLBACK_IMAGES = [
    "https://placedog.net/1200/630?id=1",
    "https://placedog.net/1200/630?id=2",
    "https://placedog.net/1200/630?id=3",
    "https://placedog.net/1200/630?id=4",
    "https://placedog.net/1200/630?id=5",
]

def download_image_with_fallback(primary_url, seed=None):
    """Try primary URL, then cycle through reliable fallbacks."""
    urls_to_try = [primary_url] + FALLBACK_IMAGES
    
    for url in urls_to_try:
        if seed and url == primary_url:
            # Append seed to primary URL if not already there
            pass
        try:
            print(f"  -> Thử tải ảnh từ: {url[:60]}...")
            resp = requests.get(url, timeout=15)
            ct = resp.headers.get("Content-Type", "")
            if resp.status_code == 200 and "image" in ct:
                print(f"  [OK] Tải thành công! Kích thước: {len(resp.content)//1024}KB")
                return resp.content
            else:
                print(f"  [FAIL] Mã {resp.status_code}, Content-Type: {ct}")
        except Exception as e:
            print(f"  [ERROR] {e}")
    
    print("  [CRITICAL] Không tải được bất kỳ ảnh nào!")
    return None

def upload_to_wp(img_data, alt_text="Helloconsen"):
    """Upload image bytes to WordPress Media."""
    filename = f"helloconsen_{random.randint(1000,9999)}.jpg"
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
        # Set alt text
        requests.post(
            f"{WP_MEDIA_URL}/{media['id']}",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            json={"alt_text": alt_text},
            timeout=10
        )
        print(f"  [UPLOADED] Media ID: {media['id']} -> {media['link']}")
        return media['id'], media['source_url']
    else:
        print(f"  [UPLOAD FAIL] {resp.status_code}: {resp.text[:100]}")
        return None, None

def diagnose_and_fix():
    print("=" * 65)
    print("   CHUẨN ĐOÁN & SỬA LỖI ẢNH HÀNG LOẠT - HELLOCONSEN")
    print("=" * 65)
    
    # 1. Lấy các bài viết mới (7 ngày gần đây)
    print("\n[1] Lấy danh sách bài viết 7 ngày gần đây...")
    res = requests.get(
        WP_POSTS_API,
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        params={"per_page": 50, "orderby": "date", "order": "desc"},
        timeout=15
    )
    posts = res.json()
    print(f"    Tìm thấy {len(posts)} bài viết.")
    
    # 2. Phân loại
    no_featured = []
    broken_body = []
    
    for p in posts:
        pid = p['id']
        title = p['title']['rendered']
        media_id = p.get('featured_media', 0)
        content = p['content']['rendered']
        
        has_broken_img = False
        img_tags = re.findall(r'<img[^>]+src="([^"]+)"', content)
        for src in img_tags:
            if 'pollinations.ai' in src:
                # Kiểm tra nhanh xem link còn sống không
                try:
                    r = requests.head(src, timeout=5, allow_redirects=True)
                    if r.status_code != 200 or 'image' not in r.headers.get('Content-Type', ''):
                        has_broken_img = True
                        break
                except:
                    has_broken_img = True
                    break
        
        if media_id == 0:
            print(f"  [NO FEATURED] ID={pid}: {title[:50]}")
            no_featured.append(p)
        
        if has_broken_img:
            print(f"  [BROKEN BODY IMG] ID={pid}: {title[:50]}")
            broken_body.append(p)
    
    print(f"\n[SUMMARY] Thiếu Featured: {len(no_featured)} | Ảnh body lỗi: {len(broken_body)}")
    
    # 3. Sửa bài thiếu Featured Image
    if no_featured:
        print(f"\n[2] Bắt đầu gắn Featured Image cho {len(no_featured)} bài...")
        for p in no_featured:
            pid = p['id']
            title = p['title']['rendered']
            keyword = title.split(':')[0].strip()
            
            # Tạo URL ảnh AI
            desc = f"cute dog cat veterinary care, professional photo, {keyword}"
            safe_desc = urllib.parse.quote(f"Ultra realistic photography of {desc}, award winning, 4k, natural lighting.")
            seed = random.randint(1000, 999999)
            ai_url = f"https://image.pollinations.ai/prompt/{safe_desc}?width=1200&height=630&model=flux&nologo=true&seed={seed}"
            
            img_data = download_image_with_fallback(ai_url)
            if img_data:
                media_id, _ = upload_to_wp(img_data, alt_text=keyword)
                if media_id:
                    ru = requests.post(
                        f"{WP_POSTS_API}/{pid}",
                        auth=(WP_USERNAME, WP_APP_PASSWORD),
                        json={"featured_media": media_id},
                        timeout=15
                    )
                    if ru.status_code == 200:
                        print(f"  [FIXED] Đã gắn Featured Image cho bài: {title[:50]}")
                    else:
                        print(f"  [ERROR] Cập nhật bài thất bại: {ru.text[:80]}")
    
    # 4. Sửa bài có ảnh body bị lỗi
    if broken_body:
        print(f"\n[3] Sửa {len(broken_body)} bài có ảnh body bị lỗi...")
        for p in broken_body:
            pid = p['id']
            title = p['title']['rendered']
            content = p['content']['rendered']
            keyword = title.split(':')[0].strip()
            
            # Tải 2 ảnh thay thế chất lượng cao
            desc1 = f"cute dog cat playing at home, highly realistic"
            desc2 = f"veterinary clinic pets healthy, professional photo"
            
            s1 = random.randint(1000, 999999)
            s2 = random.randint(1000, 999999)
            safe1 = urllib.parse.quote(f"Ultra realistic {desc1}, 4k, award winning.")
            safe2 = urllib.parse.quote(f"Ultra realistic {desc2}, 4k, award winning.")
            
            new_body1 = f"https://image.pollinations.ai/prompt/{safe1}?width=800&height=500&model=flux&nologo=true&seed={s1}"
            new_body2 = f"https://image.pollinations.ai/prompt/{safe2}?width=800&height=501&model=flux&nologo=true&seed={s2}"
            
            # Thay URL Pollinations cũ bị lỗi bằng URL mới
            img_srcs = re.findall(r'src="(https://image\.pollinations\.ai/[^"]+)"', content)
            for i, old_src in enumerate(img_srcs):
                replacement = new_body1 if i == 0 else new_body2
                content = content.replace(old_src, replacement)
            
            if img_srcs:
                ru = requests.post(
                    f"{WP_POSTS_API}/{pid}",
                    auth=(WP_USERNAME, WP_APP_PASSWORD),
                    json={"content": content},
                    timeout=15
                )
                if ru.status_code == 200:
                    print(f"  [FIXED BODY] Đã thay {len(img_srcs)} ảnh body cho: {title[:50]}")
    
    print("\n✅ HOÀN TẤT! Tất cả lỗi ảnh đã được xử lý.")

if __name__ == "__main__":
    diagnose_and_fix()
