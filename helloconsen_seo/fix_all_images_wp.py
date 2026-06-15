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

# Các bộ từ khoá ảnh thú cưng phong phú để mỗi bài có ảnh khác nhau
PLACEDOG_IDS = list(range(1, 50))
_placedog_idx = 0

def get_placedog_url(width=1200, height=630):
    """Lấy ảnh PlaceDog tuần hoàn để mỗi bài có ảnh chó khác nhau."""
    global _placedog_idx
    idx = PLACEDOG_IDS[_placedog_idx % len(PLACEDOG_IDS)]
    _placedog_idx += 1
    return f"https://placedog.net/{width}/{height}?id={idx}"

def download_image(url, timeout=20):
    """Tải ảnh, trả về bytes hoặc None."""
    try:
        r = requests.get(url, timeout=timeout)
        ct = r.headers.get("Content-Type", "")
        if r.status_code == 200 and "image" in ct and len(r.content) > 5000:
            return r.content
    except Exception as e:
        print(f"    [ERR] {e}")
    return None

def upload_to_wp(img_data, alt_text="helloconsen", width=1200, height=630):
    """Upload bytes lên WP Media, trả về (media_id, source_url)."""
    filename = f"helloconsen_{random.randint(10000,99999)}.jpg"
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
        mid = media['id']
        src = media.get('source_url', '')
        # Set alt + dimensions
        requests.post(
            f"{WP_MEDIA_URL}/{mid}",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            json={"alt_text": alt_text},
            timeout=10
        )
        print(f"    [UPLOADED] Media ID={mid} ({len(img_data)//1024}KB)")
        return mid, src
    else:
        print(f"    [UPLOAD FAIL] {resp.status_code}: {resp.text[:80]}")
        return None, None

def get_or_create_image(desc_prompt, width=1200, height=630, alt_text="helloconsen"):
    """Tải ảnh từ AI (FLUX) -> fallback PlaceDog -> upload WP."""
    seed = random.randint(1000, 999999)
    safe = urllib.parse.quote(
        f"Ultra realistic photography of {desc_prompt}, award winning photo, 4k, natural lighting, real animal, no text."
    )
    ai_url = f"https://image.pollinations.ai/prompt/{safe}?width={width}&height={height}&model=flux&nologo=true&seed={seed}"
    
    # Thử AI
    img_data = download_image(ai_url, timeout=25)
    if not img_data:
        print(f"    [FALLBACK] AI lỗi, dùng PlaceDog...")
        fallback_url = get_placedog_url(width, height)
        img_data = download_image(fallback_url, timeout=15)
    
    if img_data:
        return upload_to_wp(img_data, alt_text=alt_text, width=width, height=height)
    return None, None

def fix_all_broken():
    print("=" * 65)
    print("    SỬA TOÀN BỘ LỖI ẢNH - UPLOAD TRỰC TIẾP VÀO WP MEDIA")
    print("=" * 65)
    
    # Lấy 100 bài gần nhất
    print("\n[1] Lấy danh sách bài viết...")
    res = requests.get(
        WP_POSTS_API,
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        params={"per_page": 100, "orderby": "date", "order": "desc"},
        timeout=20
    )
    posts = res.json()
    print(f"    Tìm thấy {len(posts)} bài.")
    
    fixed_featured = 0
    fixed_body = 0
    
    for i, p in enumerate(posts):
        pid = p['id']
        title = p['title']['rendered']
        keyword = re.sub(r'<[^>]+>', '', title).split(':')[0].strip()
        content = p['content']['rendered']
        media_id = p.get('featured_media', 0)
        update_payload = {}
        
        print(f"\n[{i+1}/{len(posts)}] {title[:55]}...")
        
        # --- Sửa Featured Image ---
        needs_featured = (media_id == 0)
        if not needs_featured:
            # Kiểm tra xem media còn sống không
            mr = requests.get(f"{WP_MEDIA_URL}/{media_id}", auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=10)
            if mr.status_code != 200:
                print(f"    [DEAD MEDIA] ID={media_id} không còn tồn tại")
                needs_featured = True
        
        if needs_featured:
            print(f"    -> Đang tạo Featured Image...")
            mid, src = get_or_create_image(
                f"cute dog cat pet care veterinary, {keyword}",
                width=1200, height=630,
                alt_text=keyword
            )
            if mid:
                update_payload["featured_media"] = mid
                fixed_featured += 1
        
        # --- Sửa ảnh Body (thay URL ngoài bằng WP-hosted) ---
        img_srcs_in_body = re.findall(
            r'<img[^>]+src="(https://(?:image\.pollinations\.ai|loremflickr\.com)[^"]+)"',
            content
        )
        
        if img_srcs_in_body:
            print(f"    -> Tìm {len(img_srcs_in_body)} ảnh body cần sửa...")
            new_content = content
            for j, old_src in enumerate(img_srcs_in_body):
                desc = "cute dog cat playing healthy" if j == 0 else "pet veterinary clinic care natural"
                w, h = (800, 500) if j == 0 else (800, 501)
                _, new_src = get_or_create_image(desc, width=w, height=h, alt_text=f"{keyword} chó mèo")
                if new_src:
                    new_content = new_content.replace(old_src, new_src)
                    print(f"    -> Đã thay ảnh {j+1}: {new_src[:60]}...")
            
            if new_content != content:
                update_payload["content"] = new_content
                fixed_body += 1
        
        # --- Gửi cập nhật lên WP ---
        if update_payload:
            ru = requests.post(
                f"{WP_POSTS_API}/{pid}",
                auth=(WP_USERNAME, WP_APP_PASSWORD),
                json=update_payload,
                timeout=20
            )
            if ru.status_code == 200:
                print(f"    [✅ OK] Đã cập nhật bài viết ID={pid}")
            else:
                print(f"    [FAIL] {ru.status_code}: {ru.text[:80]}")
        else:
            print(f"    [SKIP] Bài này không cần sửa.")
    
    print(f"\n{'='*65}")
    print(f"✅ HOÀN TẤT! Featured sửa: {fixed_featured} | Body sửa: {fixed_body}")
    print(f"{'='*65}")

if __name__ == "__main__":
    fix_all_broken()
