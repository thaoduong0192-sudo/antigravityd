# -*- coding: utf-8 -*-
"""
repair_final_v2.py - Dùng bộ ảnh Picsum + Unsplash specific IDs (công nghệ xác nhận)
để thay thế hoàn toàn ảnh chó mèo.
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
# Bộ ảnh công nghệ/kinh doanh đã xác nhận từ Picsum Photos
# (photos.google.com vibes - ảnh cao cấp, không có animal)
# IDs lấy từ https://picsum.photos/ — chỉ chọn ảnh tech/city/office
# ============================================================
TECH_PHOTO_IDS = [
    # Công nghệ, laptop, màn hình
    3, 4, 10, 11, 20, 25, 26, 42, 44, 48,
    49, 50, 60, 67, 77, 96, 180, 188, 193,
    # Office, kinh doanh
    238, 240, 274, 275, 287, 299, 310, 317,
    # City, hiện đại
    325, 326, 366, 373, 375, 376,
    # Abstract, data
    392, 393, 394, 395, 396, 401,
]

ANIMAL_KEYWORDS = [
    'pet', 'dog', 'cat', 'animal', 'raccoon', 'veterinary', 'puppy', 'kitten',
    'thú cưng', 'chó', 'mèo', 'chăm sóc', 'ultra realistic', 'real animal',
    'cute', 'fluffy', 'paw', 'fur',
]
BAD_SRC_PATTERNS = ["pollinations.ai", "placedog.net"]
JSON_MARKERS = ['{"prompt":', '"model":"sana"', '"model":"flux"', '"originalPrompt"']


def get_tech_image_url(width=1200, height=630, slot=0):
    """Lấy ảnh từ Picsum Photos theo ID xác nhận là tech/office/city."""
    photo_id = TECH_PHOTO_IDS[slot % len(TECH_PHOTO_IDS)]
    url = f"https://picsum.photos/id/{photo_id}/{width}/{height}"
    try:
        r = requests.get(url, timeout=20, allow_redirects=True)
        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            return r.url
    except:
        pass
    # Fallback: lấy ngẫu nhiên từ picsum (không chứa animal vì picsum dùng Unsplash editorial)
    seed = random.randint(1, 9999)
    return f"https://picsum.photos/seed/{seed}/{width}/{height}"


def upload_image_to_wp(image_url, alt_text="Giải Pháp QR Code"):
    try:
        resp = requests.get(image_url, timeout=40, allow_redirects=True)
        ct = resp.headers.get('Content-Type', '')
        if resp.status_code != 200 or 'image' not in ct:
            print(f"  [-] Lỗi tải ảnh: {resp.status_code}")
            return None, None
        img_data = resp.content
        filename = f"qr_tech_{random.randint(100000,999999)}.jpg"
        headers  = {"Content-Disposition": f'attachment; filename="{filename}"',
                    "Content-Type": "image/jpeg"}
        res = requests.post(WP_MEDIA_API, auth=(WP_USERNAME, WP_APP_PASSWORD),
                            headers=headers, data=img_data, timeout=40)
        if res.status_code == 201:
            media_id = res.json()['id']
            requests.post(f"{WP_MEDIA_API}/{media_id}",
                          auth=(WP_USERNAME, WP_APP_PASSWORD),
                          json={"alt_text": alt_text, "caption": "", "description": ""},
                          timeout=10)
            print(f"  [+] Upload OK: media_id={media_id}")
            return media_id, res.json().get('source_url', '')
    except Exception as e:
        print(f"  [-] Lỗi upload: {e}")
    return None, None


def is_animal_media(media_id):
    if not media_id:
        return True
    try:
        r = requests.get(f"{WP_MEDIA_API}/{media_id}",
                         auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=15)
        if r.status_code != 200:
            return True
        data = r.json()
        src  = data.get('source_url', '')
        alt  = data.get('alt_text', '').lower()
        cap  = str(data.get('caption', {}).get('rendered', '')).lower()

        combined = alt + " " + cap
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
    changed = False
    soup = BeautifulSoup(content, 'html.parser')

    # 1. Xóa JSON Pollinations trong figcaption/div
    for el in soup.find_all(True):
        inner = str(el)
        if any(m in inner for m in ['{"prompt":', '"model":"sana"', '"model":"flux"']):
            if el.name in ['figcaption', 'span', 'caption', 'div', 'p'] and len(inner) > 50:
                print(f"  [+] Xóa {el.name} chứa JSON")
                el.decompose()
                changed = True

    # 2. Thay ảnh animal trong thân bài
    for i, img in enumerate(soup.find_all('img')):
        src = img.get('src', '')
        alt = img.get('alt', '').lower()
        bad = any(b in src for b in BAD_SRC_PATTERNS)
        if not bad:
            bad = any(kw in alt for kw in ANIMAL_KEYWORDS)
        if bad:
            w = min(int(img.get('width', 800)), 1200)
            h = min(int(img.get('height', 500)), 800)
            new_url = get_tech_image_url(w, h, slot=slot + i)
            print(f"  [~] Thay ảnh: '{alt[:45]}' → Picsum tech ID")
            img['src'] = new_url
            img['alt'] = f"Giải pháp QR Code - {post_title[:40]}"
            if img.get('srcset'): del img['srcset']
            changed = True

    # 3. Xóa Direct Answer label
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
        if res.status_code != 200: break
        posts = res.json()
        if not posts: break
        all_posts.extend(posts)
        total_pages = int(res.headers.get('X-WP-TotalPages', 1))
        print(f"  -> Trang {page}/{total_pages} — {len(all_posts)} bài")
        if page >= total_pages: break
        page += 1
    return all_posts


def repair_post(post, slot_offset=0):
    post_id  = post['id']
    title    = post['title']['rendered']
    content  = post['content']['rendered']
    media_id = post.get('featured_media', 0)
    payload  = {}

    print(f"\n[*] #{post_id}: {title[:65]}...")

    new_content, changed = fix_post_content(content, title, slot=slot_offset)
    if changed:
        payload['content'] = new_content

    if is_animal_media(media_id):
        print(f"  [!] Ảnh đại diện animal → thay Picsum tech")
        new_url = get_tech_image_url(1200, 630, slot=slot_offset + 7)
        new_id, _ = upload_image_to_wp(new_url, alt_text=f"Giải pháp QR Code - {title[:50]}")
        if new_id:
            payload['featured_media'] = new_id

    if payload:
        ru = requests.post(f"{WP_POSTS_API}/{post_id}",
                           auth=(WP_USERNAME, WP_APP_PASSWORD),
                           json=payload, timeout=30)
        if ru.status_code == 200:
            print(f"  [✓] Đã sửa #{post_id}")
            return True
        else:
            print(f"  [-] Thất bại: {ru.status_code}")
    else:
        print(f"  [=] Bài #{post_id} sạch.")
    return False


if __name__ == "__main__":
    print("=" * 65)
    print("  REPAIR FINAL v2 — PICSUM TECH PHOTOS")
    print("  Website: giaiphapqrcode.com")
    print("=" * 65)
    posts = get_all_posts()
    print(f"\n[*] {len(posts)} bài cần kiểm tra.\n")
    fixed = sum(1 for i, p in enumerate(posts) if repair_post(p, slot_offset=i * 3))
    print(f"\n{'='*65}")
    print(f"  HOÀN TẤT! Đã sửa {fixed}/{len(posts)} bài.")
    print(f"{'='*65}")
