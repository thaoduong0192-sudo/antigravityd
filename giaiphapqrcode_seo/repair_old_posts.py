# -*- coding: utf-8 -*-
"""
repair_old_posts.py - Sửa tự động các bài viết cũ bị lỗi:
  1. Xóa nhãn [Direct Answer - Tóm tắt trực diện 50-60 chữ]:
  2. Thay thế ảnh Pollinations.ai (gen AI) bằng ảnh stock công nghệ thực
  3. Thay ảnh pet/animal bằng ảnh công nghệ
  4. Cập nhật alt text ảnh
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import os, re, random, requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

WP_URL        = os.getenv("WP_URL", "https://giaiphapqrcode.com")
WP_USERNAME   = os.getenv("WP_USERNAME", "bluedata")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_POSTS_API  = f"{WP_URL}/wp-json/wp/v2/posts"
WP_MEDIA_API  = f"{WP_URL}/wp-json/wp/v2/media"

TECH_IMAGE_POOL = [
    "technology", "barcode", "qrcode", "software", "dashboard",
    "smartphone", "business", "office", "digital", "laptop",
    "coding", "network", "data", "analytics", "startup"
]

# Các domain/pattern ảnh cần thay thế
BAD_IMAGE_PATTERNS = [
    "pollinations.ai",
    "placedog.net",
    "loremflickr.com/800/480",  # ảnh cũ không đúng size
    "picsum.photos",
    "placeholder",
]

BAD_TEXT_PATTERNS = [
    r'<p>\s*<strong>\[Direct Answer[^<]*\]:</strong>[^<]*</p>',
    r'<p>\s*\[Direct Answer[^\]]*\][^<]*</p>',
    r'\[Direct Answer[^\]]*\]:',
    r'<strong>\[Direct Answer[^\]]*\]:</strong>',
]


def get_stock_image_url(width=1200, height=630, seed=None):
    if seed is None:
        seed = random.randint(1, 999999)
    kw = random.choice(TECH_IMAGE_POOL)
    url = f"https://loremflickr.com/{width}/{height}/{kw}?lock={seed}"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            return url
    except:
        pass
    return f"https://loremflickr.com/{width}/{height}/technology?lock={seed+1}"


def upload_image_to_wp(image_url, alt_text="Giải Pháp QR Code"):
    try:
        resp = requests.get(image_url, timeout=30)
        if resp.status_code != 200 or 'image' not in resp.headers.get('Content-Type', ''):
            print(f"  [-] Không tải được ảnh: {image_url[:60]}")
            return None
        img_data = resp.content
        filename = f"qrcode_tech_{random.randint(10000, 99999)}.jpg"
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "image/jpeg",
        }
        res = requests.post(WP_MEDIA_API, auth=(WP_USERNAME, WP_APP_PASSWORD),
                            headers=headers, data=img_data, timeout=30)
        if res.status_code == 201:
            media_id = res.json()['id']
            media_url = res.json().get('source_url', '')
            # Cập nhật alt text
            requests.post(f"{WP_MEDIA_API}/{media_id}",
                          auth=(WP_USERNAME, WP_APP_PASSWORD),
                          json={"alt_text": alt_text}, timeout=10)
            print(f"  [+] Đã upload ảnh mới: ID={media_id}")
            return media_id, media_url
    except Exception as e:
        print(f"  [-] Lỗi upload ảnh: {e}")
    return None, None


def is_bad_image_url(url):
    if not url:
        return True
    for pattern in BAD_IMAGE_PATTERNS:
        if pattern in url:
            return True
    return False


def fix_content(content, post_title):
    """Sửa nội dung bài viết: xóa Direct Answer label, thay ảnh xấu."""
    changed = False

    # 1. Xóa các nhãn [Direct Answer ...]:
    for pattern in BAD_TEXT_PATTERNS:
        new_content, n = re.subn(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
        if n > 0:
            content = new_content
            changed = True
            print(f"  [+] Đã xóa {n} nhãn 'Direct Answer' rò rỉ")

    # 2. Tìm và thay thế các ảnh xấu trong nội dung
    soup = BeautifulSoup(content, 'html.parser')
    imgs = soup.find_all('img')
    for img in imgs:
        src = img.get('src', '')
        if is_bad_image_url(src):
            seed = random.randint(1, 999999)
            new_url = get_stock_image_url(
                int(img.get('width', 800)),
                int(img.get('height', 500)),
                seed=seed
            )
            print(f"  [~] Thay ảnh xấu: {src[:50]} -> {new_url[:50]}")
            img['src'] = new_url
            img['alt'] = f"Giải pháp QR Code công nghệ - {post_title[:40]}"
            changed = True

    return str(soup) if changed else content, changed


def get_all_posts(per_page=100):
    """Lấy tất cả bài viết WordPress."""
    all_posts = []
    page = 1
    while True:
        res = requests.get(WP_POSTS_API,
                           auth=(WP_USERNAME, WP_APP_PASSWORD),
                           params={"per_page": per_page, "page": page, "status": "publish"},
                           timeout=30)
        if res.status_code != 200:
            break
        posts = res.json()
        if not posts:
            break
        all_posts.extend(posts)
        total_pages = int(res.headers.get('X-WP-TotalPages', 1))
        print(f"  -> Đã tải trang {page}/{total_pages} ({len(all_posts)} bài tổng cộng)")
        if page >= total_pages:
            break
        page += 1
    return all_posts


def repair_post(post):
    """Sửa 1 bài viết: nội dung + ảnh đại diện."""
    post_id   = post['id']
    title     = post['title']['rendered']
    content   = post['content']['rendered']
    media_id  = post.get('featured_media', 0)
    update_payload = {}

    print(f"\n[*] Kiểm tra bài #{post_id}: {title[:60]}...")

    # --- Sửa nội dung ---
    new_content, content_changed = fix_content(content, title)
    if content_changed:
        update_payload['content'] = new_content

    # --- Kiểm tra ảnh đại diện ---
    if media_id:
        media_res = requests.get(f"{WP_MEDIA_API}/{media_id}",
                                 auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=15)
        if media_res.status_code == 200:
            media_src = media_res.json().get('source_url', '')
            if is_bad_image_url(media_src):
                print(f"  [!] Ảnh đại diện bị lỗi: {media_src[:60]}")
                new_img_url = get_stock_image_url(1200, 630)
                new_id, _ = upload_image_to_wp(new_img_url, alt_text=f"QR Code - {title[:50]}")
                if new_id:
                    update_payload['featured_media'] = new_id
        else:
            # Không tìm được ảnh, tải ảnh mới
            print(f"  [!] Không tìm được ảnh đại diện (media_id={media_id}). Tải ảnh mới...")
            new_img_url = get_stock_image_url(1200, 630)
            new_id, _ = upload_image_to_wp(new_img_url, alt_text=f"QR Code - {title[:50]}")
            if new_id:
                update_payload['featured_media'] = new_id
    else:
        # Bài không có ảnh đại diện
        print(f"  [!] Bài chưa có ảnh đại diện. Tải ảnh mới...")
        new_img_url = get_stock_image_url(1200, 630)
        new_id, _ = upload_image_to_wp(new_img_url, alt_text=f"QR Code - {title[:50]}")
        if new_id:
            update_payload['featured_media'] = new_id

    # --- Gửi cập nhật lên WordPress ---
    if update_payload:
        ru = requests.post(f"{WP_POSTS_API}/{post_id}",
                           auth=(WP_USERNAME, WP_APP_PASSWORD),
                           json=update_payload, timeout=30)
        if ru.status_code == 200:
            print(f"  [✓] Đã cập nhật bài #{post_id} thành công!")
        else:
            print(f"  [-] Cập nhật thất bại: {ru.status_code} - {ru.text[:120]}")
    else:
        print(f"  [=] Bài #{post_id} không cần sửa.")


if __name__ == "__main__":
    print("=" * 60)
    print("  REPAIR TOOL - SỬA BÀI VIẾT CŨ BỊ LỖI")
    print("  Website: giaiphapqrcode.com")
    print("=" * 60)

    print("\n[*] Đang tải danh sách bài viết từ WordPress...")
    posts = get_all_posts()
    print(f"\n[*] Tổng cộng {len(posts)} bài viết cần kiểm tra.\n")

    fixed = 0
    for post in posts:
        repair_post(post)
        fixed += 1

    print(f"\n{'='*60}")
    print(f"  HOÀN TẤT! Đã kiểm tra và sửa {fixed} bài viết.")
    print(f"{'='*60}")
