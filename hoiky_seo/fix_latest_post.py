import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import json
import urllib.parse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import random

load_dotenv()
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_API_URL = "https://hoiky.com.vn/wp-json/wp/v2/posts"
WP_MEDIA_URL = "https://hoiky.com.vn/wp-json/wp/v2/media"
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def fetch_stock_image_url(english_keywords):
    if not PEXELS_API_KEY: return None
    safe_query = urllib.parse.quote(english_keywords)
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/v1/search?query={safe_query}&per_page=15&page={random.randint(1, 3)}"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            photos = res.json().get("photos", [])
            if photos: return random.choice(photos)["src"]["large"]
    except: pass
    return None

def upload_image_get_url(image_url, alt_text="Hoiky"):
    if not image_url: return None
    try:
        img_data = requests.get(image_url, timeout=20).content
        filename = f"hoiky_content_{random.randint(1000,9999)}.jpg"
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "image/jpeg",
        }
        resp = requests.post(WP_MEDIA_URL, auth=(WP_USERNAME, WP_APP_PASSWORD), headers=headers, data=img_data, timeout=30)
        if resp.status_code == 201:
            media = resp.json()
            requests.post(f"{WP_MEDIA_URL}/{media['id']}", auth=(WP_USERNAME, WP_APP_PASSWORD), json={"alt_text": alt_text}, timeout=10)
            return media['source_url']
    except: pass
    return None

def fix_latest_post():
    print("Đang lấy post mới nhất...")
    resp = requests.get(WP_API_URL, params={"per_page": 1, "status": "publish"})
    if resp.status_code == 200:
        posts = resp.json()
        if not posts: return
        post = posts[0]
        content = post['content']['rendered']
        title = post['title']['rendered']
        post_id = post['id']
        
        print(f"Sửa post ID {post_id}: {title}")
        
        # 1. Fix [Direct Answer...]
        if "[Direct Answer" in content:
            import re
            content = re.sub(r'\[Direct Answer[^\]]*\]:', 'Tóm tắt:', content)
            print("Đã xóa text Direct Answer")
            
        # 2. Fix images
        soup = BeautifulSoup(content, 'html.parser')
        changed_img = False
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if 'unsplash' in src or 'loremflickr' in src:
                print(f"Thay thế ảnh lỗi: {src}")
                alt = img.get('alt', 'Hồi ký')
                eng_kw = "vintage family" if "hướng dẫn" in alt.lower() else "emotional memory"
                new_raw = fetch_stock_image_url(eng_kw)
                new_url = upload_image_get_url(new_raw, alt)
                if new_url:
                    img['src'] = new_url
                    changed_img = True
                    print(f"-> Thay bằng: {new_url}")
                    
        new_content = str(soup)
        
        # Update post
        res = requests.post(
            f"{WP_API_URL}/{post_id}",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            json={"content": new_content}
        )
        if res.status_code == 200:
            print("Cập nhật bài viết thành công!")
        else:
            print(f"Lỗi cập nhật: {res.text}")

if __name__ == '__main__':
    fix_latest_post()
