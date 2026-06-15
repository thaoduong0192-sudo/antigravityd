import requests
import os
import re
from dotenv import load_dotenv
from stock_photos import download_stock_photo
from bs4 import BeautifulSoup

load_dotenv()
WP_URL = os.getenv("WP_URL", "https://helloconsen.com")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_MEDIA_URL = f"{WP_URL}/wp-json/wp/v2/media"
WP_POSTS_API = f"{WP_URL}/wp-json/wp/v2/posts"

def upload_image_bytes_to_wp(img_data: bytes, alt_text: str = "Helloconsen") -> tuple:
    import random
    filename = f"helloconsen_stock_{random.randint(10000, 99999)}.jpg"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "image/jpeg",
    }
    resp = requests.post(WP_MEDIA_URL, auth=(WP_USERNAME, WP_APP_PASSWORD), headers=headers, data=img_data, timeout=30)
    if resp.status_code == 201:
        media = resp.json()
        mid = media['id']
        requests.post(f"{WP_MEDIA_URL}/{mid}", auth=(WP_USERNAME, WP_APP_PASSWORD), json={"alt_text": alt_text}, timeout=10)
        return mid, media.get('source_url', '')
    return None, None

def run():
    print("="*60)
    print("  🚀 BẮT ĐẦU THAY THẾ ẢNH CŨ BẰNG STOCK UNSPLASH")
    print("="*60)
    
    posts = []
    for page in [1, 2]:
        print(f"-> Đang tải bài viết trang {page}...")
        res = requests.get(WP_POSTS_API, auth=(WP_USERNAME, WP_APP_PASSWORD), params={"per_page": 100, "page": page, "orderby": "date", "order": "desc"})
        if res.status_code == 200:
            posts.extend(res.json())
        else:
            print("Lỗi tải bài viết:", res.status_code)
            break
            
    posts = posts[:150]
    print(f"Tổng cộng xử lý {len(posts)} bài viết gần nhất.")

    # Các từ khoá mặc định để đa dạng hình
    for i, p in enumerate(posts):
        pid = p['id']
        title = p['title']['rendered']
        # Tách keyword từ tiêu đề (ví dụ: "Phòng khám thú y gần đây: ...")
        keyword = re.sub(r'<[^>]+>', '', title).split(':')[0].strip()
        content = p['content']['rendered']
        update_payload = {}
        
        print(f"\n[{i+1}/{len(posts)}] {title[:50]}...")
        
        # 1. Update Featured Image
        print("  -> Thay thế Featured Image...")
        img_featured_data = download_stock_photo(keyword, width=1200, height=630)
        if img_featured_data:
            mid, _ = upload_image_bytes_to_wp(img_featured_data, alt_text=title)
            if mid:
                update_payload['featured_media'] = mid

        # 2. Update Body Images
        soup = BeautifulSoup(content, 'html.parser')
        changed = False
        body_img_idx = 0
        for img in soup.find_all('img'):
            if img.get('width') == '800': # Hình body do tool gen trước đó có width=800
                print(f"  -> Thay thế ảnh Body {body_img_idx+1}...")
                w, h = (800, 500) if body_img_idx == 0 else (800, 501)
                img_data = download_stock_photo(keyword, width=w, height=h)
                if img_data:
                    mid, new_src = upload_image_bytes_to_wp(img_data, alt_text=f"{keyword} chăm sóc chó mèo")
                    if new_src:
                        img['src'] = new_src
                        changed = True
                body_img_idx += 1
                
        if changed:
            update_payload['content'] = str(soup)
            
        if update_payload:
            ru = requests.post(f"{WP_POSTS_API}/{pid}", auth=(WP_USERNAME, WP_APP_PASSWORD), json=update_payload, timeout=20)
            if ru.status_code == 200:
                print("  ✅ Đã cập nhật thành công!")
            else:
                print(f"  ❌ Lỗi cập nhật: {ru.status_code}")

if __name__ == "__main__":
    run()
