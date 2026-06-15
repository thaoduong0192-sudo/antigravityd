# -*- coding: utf-8 -*-
"""
repair_final_images.py - Thay TOÀN BỘ ảnh thú cưng/animal bằng ảnh công nghệ
từ Unsplash Source API (đảm bảo chỉ trả về ảnh QR, dashboard, kinh doanh).
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

# ============================================================
# Pool keyword công nghệ xoay vòng cho Unsplash Source API
# ============================================================
TECH_KEYWORDS_UNSPLASH = [
    "qr-code",
    "barcode,technology",
    "business,dashboard",
    "data,analytics",
    "smartphone,technology",
    "office,technology",
    "digital,business",
    "software,coding",
    "startup,office",
    "laptop,business",
    "chart,business",
    "technology,scan",
    "mobile,payment",
    "business,meeting",
    "digital,transformation",
]

# Từ khóa phát hiện ảnh animal
ANIMAL_KEYWORDS = [
    'pet', 'dog', 'cat', 'animal', 'raccoon', 'veterinary', 'puppy', 'kitten',
    'thú cưng', 'chó', 'mèo', 'chăm sóc', 'ultra realistic', 'real animal',
    'cute', 'fluffy', 'paw', 'fur',
]

BAD_SRC_PATTERNS = ["pollinations.ai", "placedog.net"]
JSON_MARKERS = ['{"prompt":', '"model":"sana"', '"model":"flux"', '"originalPrompt"', 'nologo=true']


def get_unsplash_url(width=1200, height=630, slot=0):
    """Lấy URL ảnh Unsplash theo keyword công nghệ, xác nhận là ảnh hợp lệ."""
    kw = TECH_KEYWORDS_UNSPLASH[slot % len(TECH_KEYWORDS_UNSPLASH)]
    sig = random.randint(1, 9999)
    url = f"https://source.unsplash.com/{width}x{height}/?{kw}&sig={sig}"
    # Unsplash source sẽ redirect đến ảnh thực — HEAD request để lấy URL cuối
    try:
        r = requests.get(url, timeout=30, allow_redirects=True)
        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            print(f"  -> Unsplash [{kw}]: {r.url[:70]}")
            return r.url  # URL sau redirect (ảnh thực sự)
    except Exception as e:
        print(f"  [-] Unsplash lỗi: {e}")

    # Fallback: thử keyword khác
    fallback_kw = TECH_KEYWORDS_UNSPLASH[(slot + 3) % len(TECH_KEYWORDS_UNSPLASH)]
    fallback_sig = random.randint(1, 9999)
    return f"https://source.unsplash.com/{width}x{height}/?{fallback_kw}&sig={fallback_sig}"


def upload_image_to_wp(image_url, alt_text="Giải Pháp QR Code", width=1200, height=630):
    """Tải ảnh về rồi upload lên WordPress Media Library."""
    try:
        headers_dl = {'User-Agent': 'Mozilla/5.0 (compatible; GiaiphapQRCode/1.0)'}
        resp = requests.get(image_url, timeout=40, headers=headers_dl, allow_redirects=True)
        ct = resp.headers.get('Content-Type', '')
        if resp.status_code != 200 or 'image' not in ct:
            print(f"  [-] Không tải được ảnh (status={resp.status_code}, ct={ct})")
            return None, None
        img_data = resp.content
        filename = f"qr_tech_{random.randint(100000, 999999)}.jpg"
        headers_up = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "image/jpeg",
        }
        res = requests.post(WP_MEDIA_API,
                            auth=(WP_USERNAME, WP_APP_PASSWORD),
                            headers=headers_up, data=img_data, timeout=40)
        if res.status_code == 201:
            media_id  = res.json()['id']
            media_url = res.json().get('source_url', '')
            # Cập nhật alt text và xóa caption
            requests.post(f"{WP_MEDIA_API}/{media_id}",
                          auth=(WP_USERNAME, WP_APP_PASSWORD),
                          json={"alt_text": alt_text, "caption": "", "description": ""},
                          timeout=10)
            print(f"  [+] Upload OK: media_id={media_id}")
            return media_id, media_url
        else:
            print(f"  [-] Upload thất bại: {res.status_code}")
    except Exception as e:
        print(f"  [-] Lỗi upload: {e}")
    return None, None


def is_animal_media(media_id):
    """Kiểm tra xem media có phải ảnh animal không."""
    if not media_id:
        return True
    try:
        r = requests.get(f"{WP_MEDIA_API}/{media_id}",
                         auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=15)
        if r.status_code != 200:
            return True
        data    = r.json()
        src     = data.get('source_url', '')
        alt     = data.get('alt_text', '').lower()
        caption = str(data.get('caption', {}).get('rendered', '')).lower()
        title_m = data.get('title', {}).get('rendered', '').lower()
        combined = alt + " " + caption + " " + title_m

        for kw in ANIMAL_KEYWORDS:
            if kw in combined:
                print(f"  [!] Ảnh animal (alt='{alt[:60]}')")
                return True
        for bad in BAD_SRC_PATTERNS:
            if bad in src:
                return True
        # Kiểm tra nội dung thực tế
        try:
            ir = requests.get(src, timeout=20)
            if 'image' not in ir.headers.get('Content-Type', ''):
                return True
            if ir.content[:10].strip().startswith(b'{'):
                print(f"  [!] File ảnh là JSON (Pollinations lỗi)")
                return True
        except:
            pass
        return False
    except:
        return False


def fix_post_content(content, post_title, slot=0):
    """Sửa nội dung bài: thay ảnh xấu, xóa JSON caption, xóa Direct Answer."""
    changed = False
    soup = BeautifulSoup(content, 'html.parser')

    # 1. Xóa figcaption/node chứa JSON Pollinations
    for el in soup.find_all(True):
        inner_str = str(el)
        if any(m in inner_str for m in ['{"prompt":', '"model":"sana"', '"model":"flux"']):
            if el.name in ['figcaption', 'span', 'caption', 'div', 'p'] and len(inner_str) > 50:
                print(f"  [+] Xóa {el.name} chứa JSON Pollinations")
                el.decompose()
                changed = True

    # 2. Thay ảnh có alt text animal hoặc src xấu
    for i, img in enumerate(soup.find_all('img')):
        src = img.get('src', '')
        alt = img.get('alt', '').lower()
        needs_replace = any(bad in src for bad in BAD_SRC_PATTERNS)
        if not needs_replace:
            needs_replace = any(kw in alt for kw in ANIMAL_KEYWORDS)

        if needs_replace:
            w   = min(int(img.get('width', 800)), 1200)
            h   = min(int(img.get('height', 500)), 800)
            new_url = get_unsplash_url(w, h, slot=slot + i)
            print(f"  [~] Thay ảnh: '{alt[:45]}' → Unsplash tech")
            img['src'] = new_url
            img['alt'] = f"Giải pháp QR Code - {post_title[:40]}"
            if img.get('srcset'):
                del img['srcset']
            changed = True

    # 3. Xóa nhãn Direct Answer rò rỉ
    for tag in soup.find_all(['p', 'div']):
        inner_html = str(tag)
        if '[Direct Answer' in inner_html:
            cleaned = re.sub(r'\[Direct Answer[^\]]*\]:', '', inner_html)
            cleaned = re.sub(r'<strong[^>]*>\[Direct Answer[^\]]*\].*?</strong>', '', cleaned)
            if cleaned != inner_html:
                tag.replace_with(BeautifulSoup(cleaned, 'html.parser'))
                changed = True
                print(f"  [+] Xóa nhãn Direct Answer")

    return str(soup), changed


def get_all_posts():
    all_posts, page = [], 1
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
        print(f"  -> Trang {page}/{total_pages} — {len(all_posts)} bài")
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

    new_content, content_changed = fix_post_content(content, title, slot=slot_offset)
    if content_changed:
        update_payload['content'] = new_content

    if is_animal_media(media_id):
        print(f"  [!] Ảnh đại diện animal → thay bằng Unsplash công nghệ")
        new_url = get_unsplash_url(1200, 630, slot=slot_offset + 7)
        new_id, _ = upload_image_to_wp(new_url,
                                        alt_text=f"Giải pháp QR Code - {title[:50]}",
                                        width=1200, height=630)
        if new_id:
            update_payload['featured_media'] = new_id

    if update_payload:
        ru = requests.post(f"{WP_POSTS_API}/{post_id}",
                           auth=(WP_USERNAME, WP_APP_PASSWORD),
                           json=update_payload, timeout=30)
        if ru.status_code == 200:
            print(f"  [✓] Đã sửa bài #{post_id}")
            return True
        else:
            print(f"  [-] Thất bại: {ru.status_code}")
    else:
        print(f"  [=] Bài #{post_id} sạch.")
    return False


if __name__ == "__main__":
    print("=" * 65)
    print("  REPAIR FINAL — THAY ẢNH THÚ CƯNG → UNSPLASH TECH")
    print("  Website: giaiphapqrcode.com")
    print("=" * 65)

    posts = get_all_posts()
    print(f"\n[*] Tổng {len(posts)} bài cần kiểm tra.\n")

    fixed = 0
    for i, post in enumerate(posts):
        if repair_post(post, slot_offset=i * 3):
            fixed += 1

    print(f"\n{'='*65}")
    print(f"  HOÀN TẤT! Đã sửa {fixed}/{len(posts)} bài viết.")
    print(f"{'='*65}")
