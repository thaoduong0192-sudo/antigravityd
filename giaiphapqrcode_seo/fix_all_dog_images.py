import sys; sys.stdout.reconfigure(encoding='utf-8')
import os, re, requests, json, time
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import random

load_dotenv()

WP_URL          = "https://giaiphapqrcode.com"
WP_USERNAME     = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_POSTS_API    = f"{WP_URL}/wp-json/wp/v2/posts"
WP_MEDIA_API    = f"{WP_URL}/wp-json/wp/v2/media"
PEXELS_API_KEY  = os.getenv("PEXELS_API_KEY")

TECH_IMAGE_POOL = [
    "qr code", "barcode technology", "business dashboard", "data analytics", "smartphone technology", 
    "office technology", "digital business", "software coding", "startup office", "laptop business", 
    "chart business", "technology scan", "mobile payment", "business meeting", "digital transformation",
    "inventory management", "point of sale system", "customer loyalty program", "electronic warranty",
    "anti-counterfeit technology", "smart packaging", "business automation", "cloud computing",
    "data security", "enterprise resource planning", "customer relationship management", "digital marketing",
    "online transaction", "contactless payment", "modern office", "tech startup", "data center",
    "artificial intelligence in business", "machine learning", "internet of things", "supply chain tech",
    "logistics management", "mobile application", "web development", "b2b software", "e-commerce platform",
    "digital identity", "biometric security", "blockchain technology", "fintech", "smart city",
    "retail technology", "business intelligence", "data mining", "cloud storage", "virtualization",
    "network infrastructure", "cybersecurity", "software testing", "agile methodology", "business teamwork",
    "corporate presentation", "tech seminar", "digital workspace", "remote work tech", "virtual meeting",
    "data visualization", "predictive analytics", "smart contract", "tech innovation", "digital economy",
    "e-governance", "digital health", "smart manufacturing", "industrial automation", "robotics in business",
    "tech consulting", "IT support", "cloud computing architecture", "software engineering", "digital product design",
    "user experience design", "user interface tech", "API integration", "microservices architecture", 
    "serverless computing", "edge computing", "5g technology", "big data analytics", "quantum computing", 
    "augmented reality business", "virtual reality tech", "metaverse business", "digital twin", "smart grid", 
    "renewable energy tech", "smart agriculture", "precision farming", "agritech", "edtech", "healthtech", 
    "proptech", "insurtech", "legaltech", "wealthtech", "marketing automation"
]

def fallback_image_url():
    safe_tech_images = [
        "https://images.pexels.com/photos/1181675/pexels-photo-1181675.jpeg?auto=compress&cs=tinysrgb&w=1200&h=630&dpr=1",
        "https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=1200&h=630&dpr=1",
        "https://images.pexels.com/photos/3861969/pexels-photo-3861969.jpeg?auto=compress&cs=tinysrgb&w=1200&h=630&dpr=1",
        "https://images.pexels.com/photos/2582937/pexels-photo-2582937.jpeg?auto=compress&cs=tinysrgb&w=1200&h=630&dpr=1",
        "https://images.pexels.com/photos/1714341/pexels-photo-1714341.jpeg?auto=compress&cs=tinysrgb&w=1200&h=630&dpr=1"
    ]
    return random.choice(safe_tech_images)

def get_pexels_image_url():
    if not PEXELS_API_KEY:
        return fallback_image_url()
        
    search_query = random.choice(TECH_IMAGE_POOL)
    headers = {"Authorization": PEXELS_API_KEY}
    page = random.randint(1, 10)
    url = f"https://api.pexels.com/v1/search?query={search_query}&per_page=15&page={page}&orientation=landscape"
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                photo = random.choice(photos)
                return photo.get("src", {}).get("large2x", photo.get("src", {}).get("large"))
    except:
        pass
    return fallback_image_url()

def upload_image_to_wp(image_url, alt_text="Giải Pháp QR Code"):
    try:
        resp = requests.get(image_url, timeout=30)
        if resp.status_code != 200 or 'image' not in resp.headers.get('Content-Type', ''):
            resp = requests.get(fallback_image_url(), timeout=20)
            if resp.status_code != 200: return None
            
        img_data = resp.content
        filename = f"tech_fixed_{random.randint(1000,9999)}.jpg"
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "image/jpeg",
        }
        res = requests.post(WP_MEDIA_API, auth=(WP_USERNAME, WP_APP_PASSWORD), headers=headers, data=img_data, timeout=30)
        if res.status_code == 201:
            media_id = res.json()['id']
            requests.post(f"{WP_MEDIA_API}/{media_id}", auth=(WP_USERNAME, WP_APP_PASSWORD), json={"alt_text": alt_text}, timeout=10)
            return media_id
    except:
        pass
    return None

def is_bad_featured_image(media_id):
    if not media_id: return True
    try:
        r = requests.get(f"{WP_MEDIA_API}/{media_id}", auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=15)
        if r.status_code != 200: return True
        data = r.json()
        alt = data.get('alt_text', '').lower()
        caption = data.get('caption', {}).get('rendered', '').lower()
        title = data.get('title', {}).get('rendered', '').lower()
        
        animal_kw = ['pet', 'dog', 'cat', 'animal', 'veterinary', 'thú cưng', 'chó', 'mèo']
        for kw in animal_kw:
            if kw in alt or kw in caption or kw in title:
                return True
                
        # Check if the filename contains generic terms from pollinations or loremflickr
        source_url = data.get('source_url', '').lower()
        if 'technology' in source_url and 'giaiphapqrcode' in source_url:
            # It might be a dog from loremflickr fallback!
            pass
            
        # Download and check content type
        img_resp = requests.get(data.get('source_url', ''), timeout=10)
        if 'image' not in img_resp.headers.get('Content-Type', ''): return True
        if img_resp.content[:5].strip().startswith(b'{'): return True
    except:
        pass
    return False

def get_all_posts():
    all_posts = []
    page = 1
    while True:
        res = requests.get(WP_POSTS_API, auth=(WP_USERNAME, WP_APP_PASSWORD), params={"per_page": 50, "page": page, "status": "publish"}, timeout=30)
        if res.status_code != 200: break
        posts = res.json()
        if not posts: break
        all_posts.extend(posts)
        page += 1
    return all_posts

print("Bắt đầu quét và thay thế toàn bộ ảnh chó mèo/lỗi...")
posts = get_all_posts()
print(f"Tổng số bài viết: {len(posts)}")

fixed_count = 0

for post in posts:
    post_id = post['id']
    title = post['title']['rendered']
    content = post['content']['rendered']
    media_id = post.get('featured_media', 0)
    
    update_payload = {}
    content_changed = False
    is_suspect_post = False
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # 1. Quét nội dung bài viết
    for img in soup.find_all('img'):
        src = img.get('src', '').lower()
        bad_domains = ['loremflickr.com', 'unsplash.com', 'pollinations.ai', 'placedog.net']
        if any(domain in src for domain in bad_domains):
            new_url = get_pexels_image_url()
            print(f"  [+] Thay ảnh body lỗi trong bài {post_id}: {src} -> {new_url}")
            img['src'] = new_url
            if img.get('srcset'): del img['srcset']
            content_changed = True
            is_suspect_post = True
            
    if content_changed:
        update_payload['content'] = str(soup)
        
    # 2. Quét ảnh đại diện
    # Nếu bài viết có chứa link ảnh rác trong body, 99% ảnh đại diện cũng được tạo cùng lúc bằng fallback rác -> XÓA!
    if is_suspect_post or is_bad_featured_image(media_id):
        print(f"  [!] Đang thay thế ảnh đại diện chó/mèo/lỗi cho bài {post_id}")
        new_featured_url = get_pexels_image_url()
        new_media_id = upload_image_to_wp(new_featured_url, title)
        if new_media_id:
            update_payload['featured_media'] = new_media_id
            
    if update_payload:
        ru = requests.post(f"{WP_POSTS_API}/{post_id}", auth=(WP_USERNAME, WP_APP_PASSWORD), json=update_payload, timeout=30)
        if ru.status_code == 200:
            print(f"Đã sửa thành công bài: {title}")
            fixed_count += 1
            
print(f"HOÀN TẤT! Đã sửa xong {fixed_count} bài viết lỗi.")
