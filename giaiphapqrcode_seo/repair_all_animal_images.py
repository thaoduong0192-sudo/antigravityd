# -*- coding: utf-8 -*-
"""
repair_all_animal_images.py - Quét TOÀN BỘ bài viết, thay thế ảnh chó/mèo/thú cưng
bằng ảnh stock công nghệ QR Code.
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

# Từ khóa phát hiện nội dung thú cưng/animal trong alt text
ANIMAL_KEYWORDS = [
    'pet', 'dog', 'cat', 'animal', 'raccoon', 'veterinary', 'puppy', 'kitten',
    'thú cưng', 'chó', 'mèo', 'chăm sóc', 'ultra realistic', 'real animal',
    'cute', 'fluffy', 'paw', 'fur', 'placedog', 'loremflickr/800/480'
]

# Phát hiện ảnh Pollinations còn sót trong img src
BAD_SRC_PATTERNS = [
    "pollinations.ai",
    "placedog.net",
]

# Phát hiện JSON Pollinations nằm trong text/caption
JSON_MARKERS = [
    '{"prompt":', '"model":"sana"', '"model":"flux"', '"originalPrompt"',
    'pollinations.ai', 'nologo=true', 'completionImageTokens'
]


def get_tech_stock_url(width=1200, height=630, slot=0):
    seed = random.randint(1, 999999)
    kw = TECH_IMAGE_POOL[slot % len(TECH_IMAGE_POOL)]
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
        ct = resp.headers.get('Content-Type', '')
        if resp.status_code != 200 or 'image' not in ct:
            return None, None
        img_data = resp.content
        filename = f"qr_tech_{random.randint(100000, 999999)}.jpg"
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "image/jpeg",
        }
        res = requests.post(WP_MEDIA_API, auth=(WP_USERNAME, WP_APP_PASSWORD),
                            headers=headers, data=img_data, timeout=30)
        if res.status_code == 201:
            media_id  = res.json()['id']
            media_url = res.json().get('source_url', '')
            requests.post(f"{WP_MEDIA_API}/{media_id}",
                          auth=(WP_USERNAME, WP_APP_PASSWORD),
                          json={"alt_text": alt_text, "caption": ""}, timeout=10)
            print(f"  [+] Upload ảnh mới: ID={media_id} ({kw if 'kw' in dir() else ''})")
            return media_id, media_url
    except Exception as e:
        print(f"  [-] Lỗi upload: {e}")
    return None, None


def is_animal_media(media_id):
    """Kiểm tra xem ảnh WordPress có phải ảnh thú cưng/animal không."""
    if not media_id:
        return True
    try:
        r = requests.get(f"{WP_MEDIA_API}/{media_id}",
                         auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=15)
        if r.status_code != 200:
            return True
        data  = r.json()
        src   = data.get('source_url', '')
        alt   = data.get('alt_text', '').lower()
        caption = str(data.get('caption', {}).get('rendered', '')).lower()
        title = data.get('title', {}).get('rendered', '').lower()

        # Kiểm tra alt text / caption / title
        for kw in ANIMAL_KEYWORDS:
            if kw in alt or kw in caption or kw in title:
                print(f"  [!] Phát hiện ảnh animal (alt='{alt[:60]}')")
                return True

        # Kiểm tra nếu src là pollinations hay placedog
        for bad in BAD_SRC_PATTERNS:
            if bad in src:
                print(f"  [!] Phát hiện ảnh từ domain xấu: {src[:60]}")
                return True

        # Tải ảnh về kiểm tra nội dung thực tế (JSON?)
        try:
            img_resp = requests.get(src, timeout=20)
            ct = img_resp.headers.get('Content-Type', '')
            if 'image' not in ct:
                print(f"  [!] Content-type không phải ảnh: {ct}")
                return True
            # Nếu 5 byte đầu là JSON → Pollinations trả về JSON nhầm
            if img_resp.content[:10].strip().startswith(b'{'):
                print(f"  [!] File ảnh thực ra là JSON (Pollinations lỗi)")
                return True
        except:
            pass

        return False
    except Exception as e:
        print(f"  [?] Không kiểm tra được media {media_id}: {e}")
        return False


def fix_post_content(content, post_title, slot=0):
    """Sửa nội dung bài viết: xóa JSON caption, thay ảnh xấu, xóa Direct Answer."""
    changed = False
    soup = BeautifulSoup(content, 'html.parser')

    # 1. Xóa bất kỳ node nào chứa JSON Pollinations
    for el in soup.find_all(True):
        text = el.get_text(separator=' ', strip=True)
        for marker in JSON_MARKERS:
            if marker in text and len(text) > 100:  # JSON thường dài
                # Chỉ xóa nếu đây là leaf-ish node (figcaption, span, div nhỏ)
                if el.name in ['figcaption', 'span', 'caption', 'div', 'p']:
                    inner = str(el)
                    if '{"prompt":' in inner or '"model":"sana"' in inner:
                        print(f"  [+] Xóa {el.name} chứa JSON Pollinations")
                        el.decompose()
                        changed = True
                        break
                break

    # 2. Thay thế ảnh trong src có domain xấu hoặc loremflickr cũ
    for i, img in enumerate(soup.find_all('img')):
        src = img.get('src', '')
        alt = img.get('alt', '').lower()
        needs_replace = False

        # Ảnh từ Pollinations/placedog
        for bad in BAD_SRC_PATTERNS:
            if bad in src:
                needs_replace = True
                break

        # Ảnh có alt text thú cưng
        if not needs_replace:
            for kw in ANIMAL_KEYWORDS:
                if kw in alt:
                    needs_replace = True
                    break

        if needs_replace:
            w = int(img.get('width', 800))
            h = int(img.get('height', 500))
            new_url = get_tech_stock_url(w, h, slot=slot + i)
            print(f"  [~] Thay ảnh trong bài: alt='{alt[:50]}' → {new_url[:55]}")
            img['src'] = new_url
            img['alt'] = f"Giải pháp QR Code - {post_title[:40]}"
            if img.get('srcset'):
                del img['srcset']
            changed = True

    # 3. Xóa nhãn Direct Answer rò rỉ
    for tag in soup.find_all(['p', 'div']):
        inner_html = str(tag)
        if '[Direct Answer' in inner_html or 'Direct Answer' in inner_html:
            cleaned = re.sub(r'\[Direct Answer[^\]]*\]:', '', inner_html)
            cleaned = re.sub(r'<strong[^>]*>\[Direct Answer[^\]]*\].*?</strong>', '', cleaned)
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
        print(f"  -> Trang {page}/{total_pages} — tổng {len(all_posts)} bài")
        if page >= total_pages:
            break
        page += 1
    return all_posts


def repair_post(post, slot_offset=0):
    post_id  = post['id']
    title    = post['title']['rendered']
    content  = post['content']['rendered']
    media_id = post.get('featured_media', 0)
    update_payload = {}

    print(f"\n[*] #{post_id}: {title[:65]}...")

    # --- Sửa nội dung bài ---
    new_content, content_changed = fix_post_content(content, title, slot=slot_offset)
    if content_changed:
        update_payload['content'] = new_content

    # --- Kiểm tra + thay ảnh đại diện ---
    if is_animal_media(media_id):
        print(f"  [!] Ảnh đại diện là animal/lỗi → thay ảnh công nghệ QR mới")
        new_url = get_tech_stock_url(1200, 630, slot=slot_offset + 7)
        new_id, _ = upload_image_to_wp(new_url, alt_text=f"Giải pháp QR Code - {title[:50]}")
        if new_id:
            update_payload['featured_media'] = new_id

    # --- Push lên WordPress ---
    if update_payload:
        ru = requests.post(f"{WP_POSTS_API}/{post_id}",
                           auth=(WP_USERNAME, WP_APP_PASSWORD),
                           json=update_payload, timeout=30)
        if ru.status_code == 200:
            print(f"  [✓] Đã sửa bài #{post_id}")
            return True
        else:
            print(f"  [-] Thất bại: {ru.status_code} — {ru.text[:100]}")
    else:
        print(f"  [=] Bài #{post_id} sạch.")
    return False


if __name__ == "__main__":
    print("=" * 65)
    print("  REPAIR v3 — DỌN SẠCH ẢNH CHÓ MÈO TOÀN BỘ WEBSITE")
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
