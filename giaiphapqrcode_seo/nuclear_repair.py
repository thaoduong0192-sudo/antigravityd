# -*- coding: utf-8 -*-
"""
nuclear_repair.py - Sửa TRIỆT ĐỂ theo cơ chế kiểm tra filename:
  - Ảnh có filename giaiphapqrcode_*.jpg / repaired_image_*.jpg = Pollinations cũ → THAY
  - Ảnh body có src loremflickr / picsum mà bị broken → THAY
  - Ảnh body có alt chứa "chăm sóc thú cưng" / "chó mèo" → THAY
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
# Bộ ID ảnh Picsum đã xác nhận là tech/office (không animal)
# Source: https://picsum.photos — editorial curated
# ============================================================
PICSUM_TECH_IDS = [
    # Công nghệ, máy tính, code
    3, 4, 10, 11, 20, 48, 49, 50, 96, 180,
    188, 193, 239, 240, 274, 275, 287, 299,
    # Văn phòng, kinh doanh, họp
    316, 317, 325, 326, 366, 373, 375, 393,
    # Trừu tượng, dữ liệu, ánh sáng đô thị
    401, 450, 452, 453, 454, 474, 488, 500,
    501, 502, 503, 504, 542, 543, 580, 583,
]

# Filename patterns của ảnh Pollinations cũ (cần thay)
OLD_FILENAME_PATTERNS = [
    "giaiphapqrcode_",
    "repaired_image_",
    "healed_image_",
]

# Filename của ảnh đã được chúng ta thay (giữ lại)
GOOD_FILENAME_PATTERNS = [
    "qr_tech_",
    "qr_code_",
]

ANIMAL_ALT_KEYWORDS = [
    'thú cưng', 'chó', 'mèo', 'chăm sóc thú', 'hướng dẫn chăm sóc',
    'veterinary', 'placedog', 'real animal', 'pet', 'dog', 'cat',
]

# URLs loremflickr cũ (body image cần thay)
BAD_BODY_SRC_PATTERNS = [
    "pollinations.ai",
    "placedog.net",
    "loremflickr.com",  # tất cả loremflickr đều không đáng tin
]


def get_picsum_url(width=1200, height=630, slot=0):
    """Lấy ảnh Picsum theo ID xác nhận tech/office."""
    pid = PICSUM_TECH_IDS[slot % len(PICSUM_TECH_IDS)]
    url = f"https://picsum.photos/id/{pid}/{width}/{height}"
    try:
        r = requests.get(url, timeout=25, allow_redirects=True)
        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            return r.url
    except:
        pass
    # Fallback seed-based
    seed = random.randint(100, 999)
    return f"https://picsum.photos/seed/tech{seed}/{width}/{height}"


def upload_image_to_wp(image_url, alt_text="Giải Pháp QR Code"):
    """Tải ảnh từ URL và upload lên WordPress Media Library."""
    try:
        resp = requests.get(image_url, timeout=40, allow_redirects=True)
        ct = resp.headers.get('Content-Type', '')
        if resp.status_code != 200 or 'image' not in ct:
            print(f"  [-] Lỗi tải ảnh ({resp.status_code}), thử fallback...")
            fallback = f"https://picsum.photos/seed/qrcode{random.randint(1,999)}/1200/630"
            resp = requests.get(fallback, timeout=30, allow_redirects=True)
            if resp.status_code != 200:
                return None, None
        img_data = resp.content
        filename = f"qr_tech_{random.randint(100000, 999999)}.jpg"
        headers  = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "image/jpeg",
        }
        res = requests.post(WP_MEDIA_API, auth=(WP_USERNAME, WP_APP_PASSWORD),
                            headers=headers, data=img_data, timeout=40)
        if res.status_code == 201:
            media_id = res.json()['id']
            requests.post(f"{WP_MEDIA_API}/{media_id}",
                          auth=(WP_USERNAME, WP_APP_PASSWORD),
                          json={"alt_text": alt_text, "caption": "", "description": ""},
                          timeout=10)
            print(f"  [+] Upload OK → media_id={media_id}")
            return media_id, res.json().get('source_url', '')
        else:
            print(f"  [-] Upload thất bại: {res.status_code}")
    except Exception as e:
        print(f"  [-] Lỗi: {e}")
    return None, None


def should_replace_featured(media_id):
    """
    Quyết định có nên thay ảnh đại diện không dựa trên:
    1. Filename có chứa pattern cũ (Pollinations)
    2. Alt text chứa từ animal
    3. File thực tế bị lỗi (JSON thay vì ảnh)
    """
    if not media_id:
        return True, "Không có ảnh đại diện"
    try:
        r = requests.get(f"{WP_MEDIA_API}/{media_id}",
                         auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=15)
        if r.status_code != 200:
            return True, "Media không tồn tại"

        data     = r.json()
        src      = data.get('source_url', '')
        alt      = data.get('alt_text', '').lower()
        caption  = str(data.get('caption', {}).get('rendered', '')).lower()
        filename = src.split('/')[-1].lower()

        # Kiểm tra filename → ảnh Pollinations cũ
        for pat in OLD_FILENAME_PATTERNS:
            if pat in filename:
                return True, f"Filename cũ (Pollinations): {filename}"

        # Kiểm tra alt/caption → từ animal
        combined = alt + " " + caption
        for kw in ANIMAL_ALT_KEYWORDS:
            if kw in combined:
                return True, f"Alt text animal: '{alt[:50]}'"

        # Kiểm tra file thực tế
        try:
            ir = requests.get(src, timeout=20)
            ct = ir.headers.get('Content-Type', '')
            if 'image' not in ct:
                return True, f"Content-type sai: {ct}"
            if ir.content[:5].strip().startswith(b'{'):
                return True, "File là JSON (Pollinations lỗi)"
            if ir.status_code != 200:
                return True, f"HTTP {ir.status_code}"
        except Exception as e:
            return True, f"Không kiểm tra được: {e}"

        return False, "OK"
    except Exception as e:
        return True, f"Lỗi API: {e}"


def fix_post_content(content, post_title, slot=0):
    """Sửa nội dung bài: thay ảnh body bị lỗi hoặc từ loremflickr."""
    changed = False
    soup = BeautifulSoup(content, 'html.parser')

    # 1. Xóa figcaption chứa JSON Pollinations
    for el in soup.find_all(True):
        inner = str(el)
        if '{"prompt":' in inner or '"model":"sana"' in inner or '"model":"flux"' in inner:
            if el.name in ['figcaption', 'span', 'div', 'p'] and len(inner) > 60:
                el.decompose()
                changed = True
                print(f"  [+] Xóa {el.name} chứa JSON")

    # 2. Thay thế ảnh body có src xấu hoặc alt animal
    imgs = soup.find_all('img')
    for i, img in enumerate(imgs):
        src = img.get('src', '')
        alt = img.get('alt', '').lower()

        needs_replace = False
        reason = ""

        # Src từ domain xấu (loremflickr, pollinations, placedog)
        for bad in BAD_BODY_SRC_PATTERNS:
            if bad in src:
                needs_replace = True
                reason = f"src={src[:50]}"
                break

        # Alt text chứa animal
        if not needs_replace:
            for kw in ANIMAL_ALT_KEYWORDS:
                if kw in alt:
                    needs_replace = True
                    reason = f"alt='{alt[:45]}'"
                    break

        # Kiểm tra ảnh có load được không
        if not needs_replace and src.startswith('http'):
            try:
                check = requests.head(src, timeout=8, allow_redirects=True)
                if check.status_code not in [200, 301, 302]:
                    needs_replace = True
                    reason = f"HTTP {check.status_code}"
            except:
                needs_replace = True
                reason = "Không kết nối được"

        if needs_replace:
            w = min(int(img.get('width', 800) or 800), 1200)
            h = min(int(img.get('height', 500) or 500), 800)
            new_url = get_picsum_url(w, h, slot=slot + i)
            print(f"  [~] Thay ảnh body ({reason}) → Picsum ID slot {(slot+i) % len(PICSUM_TECH_IDS)}")
            img['src'] = new_url
            img['alt'] = f"Phần mềm QR Code - {post_title[:40]}"
            if img.get('srcset'):
                del img['srcset']
            changed = True

    # 3. Xóa Direct Answer label
    for tag in soup.find_all(['p', 'div']):
        ih = str(tag)
        if '[Direct Answer' in ih:
            cleaned = re.sub(r'\[Direct Answer[^\]]*\]:', '', ih)
            cleaned = re.sub(r'<strong[^>]*>\[Direct Answer[^\]]*\].*?</strong>', '', cleaned)
            if cleaned != ih:
                tag.replace_with(BeautifulSoup(cleaned, 'html.parser'))
                changed = True
                print("  [+] Xóa nhãn Direct Answer")

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
    payload  = {}

    print(f"\n[*] #{post_id}: {title[:60]}...")

    # --- Sửa nội dung bài ---
    new_content, changed = fix_post_content(content, title, slot=slot_offset)
    if changed:
        payload['content'] = new_content

    # --- Kiểm tra ảnh đại diện ---
    replace_feat, reason = should_replace_featured(media_id)
    if replace_feat:
        print(f"  [!] Thay ảnh đại diện ({reason})")
        new_url = get_picsum_url(1200, 630, slot=slot_offset + 10)
        new_id, _ = upload_image_to_wp(new_url,
                                        alt_text=f"Phần mềm QR Code - {title[:50]}")
        if new_id:
            payload['featured_media'] = new_id

    # --- Push ---
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
        print(f"  [=] #{post_id} sạch.")
    return False


if __name__ == "__main__":
    print("=" * 65)
    print("  NUCLEAR REPAIR — KIỂM TRA FILENAME + HTTP + ALT TEXT")
    print("  Website: giaiphapqrcode.com")
    print("=" * 65)

    posts = get_all_posts()
    print(f"\n[*] {len(posts)} bài cần kiểm tra.\n")

    fixed = 0
    for i, p in enumerate(posts):
        if repair_post(p, slot_offset=i * 2):
            fixed += 1

    print(f"\n{'='*65}")
    print(f"  HOÀN TẤT! Đã sửa {fixed}/{len(posts)} bài.")
    print(f"{'='*65}")
