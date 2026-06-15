import os
import requests
import json
import urllib.parse
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WP_URL", "https://helloconsen.com")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

WP_POSTS_API = f"{WP_URL}/wp-json/wp/v2/posts"
WP_MEDIA_API = f"{WP_URL}/wp-json/wp/v2/media"

def upload_image_to_wp_flux(english_prompt, width=1200, height=630):
    import random
    seed = random.randint(1000, 999999)
    safe_desc = urllib.parse.quote(f"Ultra realistic professional photography of {english_prompt}, award winning photo, 4k, natural lighting, real animal, no deformities, no text.")
    flux_url = f"https://image.pollinations.ai/prompt/{safe_desc}?width={width}&height={height}&model=flux&nologo=true&seed={seed}"
    
    print(f"  -> Downloading from FLUX: {flux_url[:60]}...")
    try:
        resp = requests.get(flux_url, timeout=30)
        if resp.status_code != 200 or 'image' not in resp.headers.get('Content-Type', ''):
            print("  [-] Lỗi tải ảnh từ Flux! Kích hoạt LỐP DỰ PHÒNG PLACEDOG...")
            fallback = f"https://placedog.net/1200/630?random={random.randint(1,9999)}"
            resp = requests.get(fallback, timeout=20)
            if resp.status_code != 200: return None
            
        img_data = resp.content
        filename = f"repaired_image_{random.randint(1000,9999)}.jpg"
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "image/jpeg",
        }
        res = requests.post(WP_MEDIA_API, auth=(WP_USERNAME, WP_APP_PASSWORD), headers=headers, data=img_data, timeout=30)
        if res.status_code == 201:
            media_id = res.json()['id']
            print(f"  [+] Đã tải lên WP Media ID: {media_id}")
            return media_id
    except Exception as e:
        print(f"  [-] Lỗi: {e}")
    return None

def fix_recent_posts():
    print("[*] Đang tìm các bài viết bị lỗi ảnh...")
    try:
        res = requests.get(WP_POSTS_API, auth=(WP_USERNAME, WP_APP_PASSWORD), params={"per_page": 20}, timeout=15)
        posts = res.json()
        
        for post in posts:
            post_id = post['id']
            title = post['title']['rendered']
            media_id = post.get('featured_media', 0)
            
            # Check if media is broken or from the broken batch
            # We assume anything posted in the last 24-48 hours might have used loremflickr and failed
            post_date = datetime.strptime(post['date'], "%Y-%m-%dT%H:%M:%S")
            time_diff = datetime.now() - post_date
            
            if time_diff.days <= 2:
                print(f"\n[*] Đang sửa ảnh cho bài: {title[:50]}...")
                
                new_media_id = upload_image_to_wp_flux("cute dog and cat in veterinary clinic or home", 1200, 630)
                if new_media_id:
                    # Cập nhật Featured Image
                    update_payload = {"featured_media": new_media_id}
                    
                    # Chúng ta cũng sửa luôn ảnh minh họa trong body nếu bị lỗi (tìm loremflickr)
                    content = post['content']['rendered']
                    if 'loremflickr.com' in content:
                        print("  -> Phát hiện link loremflickr rác trong bài, tiến hành thay thế...")
                        # Thay the các img_body = FLUX URLs! Để đơn giản thay bằng link cứng
                        import re
                        safe_body = urllib.parse.quote("cute dog playing or eating, highly realistic")
                        new_body_url1 = f"https://image.pollinations.ai/prompt/{safe_body}?width=800&height=500&model=flux&nologo=true&seed=121"
                        safe_body2 = urllib.parse.quote("cute cat resting, highly realistic")
                        new_body_url2 = f"https://image.pollinations.ai/prompt/{safe_body2}?width=800&height=501&model=flux&nologo=true&seed=122"
                        
                        urls_to_replace = re.findall(r'src="(https://loremflickr.com/[^"]+)"', content)
                        for i, old_url in enumerate(urls_to_replace):
                            replacement = new_body_url1 if i % 2 == 0 else new_body_url2
                            content = content.replace(old_url, replacement)
                            
                        update_payload["content"] = content
                    
                    # Gọi API update post
                    ru = requests.post(f"{WP_POSTS_API}/{post_id}", auth=(WP_USERNAME, WP_APP_PASSWORD), json=update_payload, timeout=20)
                    if ru.status_code == 200:
                        print("  [+] Sửa thành công!")
                    else:
                        print("  [-] Sửa thất bại:", ru.text[:100])
                
    except Exception as e:
        print(f"[-] Lỗi trong quá trình quét: {e}")

if __name__ == "__main__":
    fix_recent_posts()
