# -*- coding: utf-8 -*-
"""
repair_old_posts_v2.py - Sửa triệt để bài viết cũ bị lỗi:
  1. Xóa figcaption/caption chứa JSON Pollinations.ai
  2. Thay thế ảnh Pollinations.ai còn sót (trong bất kỳ thuộc tính nào)
  3. Xóa nhãn [Direct Answer ...]
  4. Kiểm tra ảnh đại diện bị lỗi (tải về kiểm tra content-type)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import os, re, random, requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

WP_URL          = os.getenv("WP_URL", "https://giaiphapqrcode.com")
WP_USERNAME     = os.getenv("WP_USERNAME", "bluedata")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_POSTS_API    = f"{WP_URL}/wp-json/wp/v2/posts"
WP_MEDIA_API    = f"{WP_URL}/wp-json/wp/v2/media"

TECH_IMAGE_POOL = [
    "technology", "barcode", "qrcode", "software", "dashboard",
    "smartphone", "business", "office", "digital", "laptop",
    "coding", "network", "data", "analytics", "startup"
]

# Pattern kiểm tra ảnh/content cần xóa hoặc thay
BAD_IMG_DOMAINS = ["pollinations.ai", "placedog.net", "loremflickr.com"]
BAD_TEXT_PATTERNS = [
    r'<p[^>]*>\s*<strong[^>]*>\[Direct Answer[^\]]*\].*?</strong>.*?</p>',
    r'<p[^>]*>\s*\[Direct Answer[^\]]*\].*?</p>',
    r'\[Direct Answer[^\]]*\]:',
]


def get_stock_url(width=1200, height=630, slot=0):
    seed = random.randint(1, 999999)
    kw = TECH_IMAGE_POOL[slot % len(TECH_IMAGE_POOL)]
    return f"https://loremflickr.com/{width}/{height}/{kw}?lock={seed}"


def upload_image_to_wp(image_url, alt_text="Giải Pháp QR Code"):
    try:
        resp = requests.get(image_url, timeout=30)
        ct = resp.headers.get('Content-Type', '')
        if resp.status_code != 200 or 'image' not in ct:
            # Fallback
            seed = random.randint(1, 999999)
            fallback = f"https://loremflickr.com/1200/630/technology?lock={seed}"
            resp = requests.get(fallback, timeout=20)
            if resp.status_code != 200:
                return None, None
        img_data = resp.content
        filename = f"qr_tech_{random.randint(10000, 99999)}.jpg"
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "image/jpeg",
        }
        res = requests.post(WP_MEDIA_API, auth=(WP_USERNAME, WP_APP_PASSWORD),
                            headers=headers, data=img_data, timeout=30)
        if res.status_code == 201:
            media_id = res.json()['id']
            media_url = res.json().get('source_url', '')
            requests.post(f"{WP_MEDIA_API}/{media_id}",
                          auth=(WP_USERNAME, WP_APP_PASSWORD),
                          json={"alt_text": alt_text}, timeout=10)
            print(f"  [+] Upload ảnh mới: ID={media_id}")
            return media_id, media_url
    except Exception as e:
        print(f"  [-] Lỗi upload: {e}")
    return None, None


def is_bad_featured_image(media_id):
    """Tải ảnh đại diện về và kiểm tra: nếu là JSON hoặc animal thì trả True."""
    if not media_id:
        return True
    try:
        r = requests.get(f"{WP_MEDIA_API}/{media_id}",
                         auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=15)
        if r.status_code != 200:
            return True
        data = r.json()
        src = data.get('source_url', '')
        alt = data.get('alt_text', '').lower()
        caption = data.get('caption', {}).get('rendered', '').lower()
        
        # Kiểm tra alt/caption có chứa nội dung thú cưng / animal
        animal_kw = ['pet', 'dog', 'cat', 'animal', 'raccoon', 'veterinary',
                     'thú cưng', 'chó', 'mèo', 'chăm sóc', 'ultra realistic']
        for kw in animal_kw:
            if kw in alt or kw in caption:
                print(f"  [!] Ảnh có alt/caption animal: '{alt[:50]}'")
                return True
        
        # Tải ảnh về kiểm tra nội dung thực tế
        img_resp = requests.get(src, timeout=20)
        ct = img_resp.headers.get('Content-Type', '')
        # Nếu content-type không phải image → lỗi
        if 'image' not in ct:
            print(f"  [!] Ảnh trả về content-type sai: {ct}")
            return True
        # Nếu content bắt đầu bằng { thì là JSON bị lưu nhầm thành ảnh
        if img_resp.content[:5].strip().startswith(b'{'):
            print(f"  [!] Ảnh thực ra là JSON (Pollinations lỗi)")
            return True
        return False
    except Exception as e:
        print(f"  [?] Không kiểm tra được ảnh {media_id}: {e}")
        return False


def fix_content(content, post_title, slot=0):
    """Sửa nội dung bài viết."""
    changed = False
    soup = BeautifulSoup(content, 'html.parser')

    # --- 1. Xóa <figcaption> chứa JSON Pollinations ---
    for caption in soup.find_all(['figcaption', 'div', 'span']):
        text = caption.get_text(strip=True)
        if text.startswith('{"prompt":') or '"model":"sana"' in text or 'pollinations.ai' in text.lower():
            print(f"  [+] Xóa figcaption/div chứa JSON Pollinations")
            caption.decompose()
            changed = True

    # --- 2. Thay ảnh có src/data-src từ Pollinations ---
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if any(bad in src for bad in BAD_IMG_DOMAINS):
            slot += 1
            new_url = get_stock_url(
                width=int(img.get('width', 800)),
                height=int(img.get('height', 500)),
                slot=slot
            )
            print(f"  [~] Thay ảnh: {src[:55]}...")
            img['src'] = new_url
            img['alt'] = f"Giải pháp QR Code - {post_title[:40]}"
            if img.get('srcset'):
                del img['srcset']
            changed = True

    # --- 3. Xóa nhãn Direct Answer rò rỉ ---
    for tag in soup.find_all(['p', 'div']):
        txt = tag.get_text()
        if '[Direct Answer' in txt or 'Direct Answer' in txt:
            # Xóa thẻ <strong> chứa nhãn nếu có
            for strong in tag.find_all('strong'):
                if 'Direct Answer' in strong.get_text():
                    strong_text = strong.get_text()
                    strong.replace_with('')
            # Xóa ngoặc vuông còn lại
            inner_html = str(tag)
            cleaned = re.sub(r'\[Direct Answer[^\]]*\]:', '', inner_html)
            cleaned = re.sub(r'\[Direct Answer[^\]]*\]', '', cleaned)
            if cleaned != inner_html:
                new_tag = BeautifulSoup(cleaned, 'html.parser')
                tag.replace_with(new_tag)
                changed = True
                print(f"  [+] Xóa nhãn Direct Answer")

    return str(soup), changed


def get_all_posts():
    all_posts = []
    page = 1
    while True:
        res = requests.get(WP_POSTS_API,
                           auth=(WP_USERNAME, WP_APP_PASSWORD),
                           params={"per_page": 100, "page": page, "status": "publish"},
                           timeout=30)
        if res.status_code != 200:
            break
        posts = res.json()
        if not posts:
            break
        all_posts.extend(posts)
        total_pages = int(res.headers.get('X-WP-TotalPages', 1))
        print(f"  -> Trang {page}/{total_pages} - tổng {len(all_posts)} bài")
        if page >= total_pages:
            break
        page += 1
    return all_posts


def repair_post(post, slot_offset=0):
    post_id = post['id']
    title   = post['title']['rendered']
    content = post['content']['rendered']
    media_id = post.get('featured_media', 0)
    update_payload = {}

    print(f"\n[*] Kiểm tra #{post_id}: {title[:65]}...")

    # --- Sửa nội dung ---
    new_content, content_changed = fix_content(content, title, slot=slot_offset)
    if content_changed:
        update_payload['content'] = new_content

    # --- Kiểm tra ảnh đại diện ---
    if is_bad_featured_image(media_id):
        print(f"  [!] Ảnh đại diện bị lỗi → tải ảnh mới từ stock công nghệ")
        new_url = get_stock_url(1200, 630, slot=slot_offset + 3)
        new_id, _ = upload_image_to_wp(new_url, alt_text=f"QR Code Technology - {title[:50]}")
        if new_id:
            update_payload['featured_media'] = new_id

    # --- Gửi cập nhật ---
    if update_payload:
        ru = requests.post(f"{WP_POSTS_API}/{post_id}",
                           auth=(WP_USERNAME, WP_APP_PASSWORD),
                           json=update_payload, timeout=30)
        if ru.status_code == 200:
            print(f"  [✓] Đã sửa bài #{post_id}")
            return True
        else:
            print(f"  [-] Thất bại: {ru.status_code} {ru.text[:100]}")
    else:
        print(f"  [=] Bài #{post_id} sạch, không cần sửa.")
    return False


if __name__ == "__main__":
    print("=" * 65)
    print("  REPAIR v2 - SỬA TRIỆT ĐỂ JSON CAPTION + ẢNH LỖI")
    print("  Website: giaiphapqrcode.com")
    print("=" * 65)

    print("\n[*] Đang tải danh sách bài viết...")
    posts = get_all_posts()
    print(f"\n[*] Tổng {len(posts)} bài cần kiểm tra.\n")

    fixed = 0
    for i, post in enumerate(posts):
        if repair_post(post, slot_offset=i * 3):
            fixed += 1

    print(f"\n{'='*65}")
    print(f"  HOÀN TẤT! Đã sửa {fixed}/{len(posts)} bài viết.")
    print(f"{'='*65}")
