import os
import json
import time
import requests
import base64
import random
from dotenv import load_dotenv
from qwen_manager import chat_with_qwen

load_dotenv()

# WordPress Credentials
WP_USER = os.getenv("WP_USERNAME")
WP_PASS = os.getenv("WP_APP_PASSWORD")
WP_TOKEN = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

TARGET_POSTS_PER_RUN = 20

DB_PATH = "cat_campaign_db.json"
STATE_PATH = "cat_campaign_state.json"

def fetch_pexels_image(keyword="cat"):
    url = f"https://api.pexels.com/v1/search?query={keyword}&per_page=15&orientation=landscape"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            if data.get('photos'):
                photo = random.choice(data['photos'])
                return photo['src']['large'], photo['id']
    except Exception as e:
        print(f"Lỗi Pexels: {e}")
    return None, None

def upload_image_to_wp(image_url):
    try:
        r = requests.get(image_url)
        if r.status_code != 200: return None
        
        filename = f"cat-litter-seo-{int(time.time())}.jpg"
        headers = {
            "Authorization": f"Basic {WP_TOKEN}",
            "Content-Type": "image/jpeg",
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
        resp = requests.post("https://helloconsen.com/wp-json/wp/v2/media", headers=headers, data=r.content)
        if resp.status_code == 201:
            return resp.json().get('id')
    except Exception as e:
        print(f"Lỗi Upload ảnh: {e}")
    return None

def post_to_wp(title, content, media_id=None):
    headers = {"Authorization": f"Basic {WP_TOKEN}"}
    payload = {
        "title": title,
        "content": content,
        "status": "publish"
    }
    if media_id:
        payload["featured_media"] = media_id
        
    r = requests.post("https://helloconsen.com/wp-json/wp/v2/posts", json=payload, headers=headers)
    if r.status_code == 201:
        return r.json().get('link')
    print(f"Lỗi đăng bài: {r.status_code} - {r.text}")
    return None

def generate_article(keyword, title, pillar_url):
    prompt = f"""
    Viết 1 bài Blog B2C chuẩn SEO, độ dài khoảng 1200 từ, với tiêu đề: "{title}".
    Từ khóa chính cần tối ưu là: "{keyword}".
    
    YÊU CẦU BẮT BUỘC (NẾU VI PHẠM SẼ BỊ PHẠT NGHIÊM TRỌNG):
    1. TUYỆT ĐỐI SỬ DỤNG 100% TIẾNG VIỆT. KHÔNG ĐƯỢC CHÈN BẤT KỲ CÂU TIẾNG ANH HAY TIẾNG TRUNG NÀO.
    2. Giọng văn: Gần gũi, chia sẻ kinh nghiệm thực tế dành cho "sen" (người nuôi mèo), đặc biệt là dân chung cư tại TP.HCM/Hà Nội.
    3. Đánh vào tâm lý: Mùi khai khay cát ám ảnh, dọn phân vất vả, sợ vi khuẩn gây bệnh cho gia đình.
    4. Trình bày bằng HTML đầy đủ (<h2>, <h3>, <ul>, <li>, <strong>). KHÔNG bọc trong markdown ```html.
    5. KHÔNG viết phần kết luận (để tôi chèn CTA sau).
    
    BẮT ĐẦU VIẾT LUÔN NỘI DUNG HTML BÊN TRONG:
    """
    
    content = chat_with_qwen(prompt, max_tokens=6000)
    if not content: return None
    
    # Remove markdown blocks
    if content.startswith("```html"): content = content[7:]
    if content.startswith("```"): content = content[3:]
    if content.endswith("```"): content = content[:-3]
    
    cta_block = f"""
    <hr style="margin-top:40px;">
    <h3>Giải Pháp Khử Mùi Cát Mèo Sinh Học Tận Gốc - Bảo Vệ Sức Khỏe Gia Đình</h3>
    <p>Nếu bạn đang đau đầu vì <strong>khay cát bốc mùi khai nồng nặc</strong> mỗi khi mở cửa phòng, hay lo lắng vi khuẩn sinh sôi gây bệnh hô hấp cho trẻ nhỏ và chính các bé mèo, thì <strong>hạt khử mùi hóa học thông thường không thể giải quyết tận gốc</strong>.</p>
    <p>Hãy trải nghiệm sự khác biệt hoàn toàn với <a href="https://helloconsen.com/san-pham/men-khu-khuan-bioline-bs1-cho-cat-ve-sinh-meo">Men Khử Khuẩn Cát Mèo Bioline BS1</a>. Chứa hàng tỷ bào tử lợi khuẩn Bacillus subtilis, men sinh học này sẽ lập tức bẻ gãy cấu trúc Amoniac và H2S, tiêu diệt vi khuẩn gây thối từ trong trứng nước. Khay cát không chỉ hết mùi ngay lập tức mà còn sạch khuẩn đến 99%!</p>
    <p style="font-size: 18px;">👉 <strong><a href="https://helloconsen.com/san-pham/men-khu-khuan-bioline-bs1-cho-cat-ve-sinh-meo">Đặt mua ngay Men khử khuẩn Bioline BS1 (Freeship siêu tốc)</a> để trả lại bầu không khí trong lành cho căn hộ của bạn!</strong></p>
    <p><em>Xem thêm cẩm nang toàn diện về giải pháp này tại đây: <a href="{pillar_url}">Toàn tập về {keyword}</a></em></p>
    """
    
    return content.strip() + "\n" + cta_block

def main():
    if not os.path.exists(DB_PATH):
        print("Database chưa sẵn sàng!")
        return
        
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)
        
    if not os.path.exists(STATE_PATH):
        state = {"total_posted": 0, "last_index": 0}
    else:
        with open(STATE_PATH, 'r', encoding='utf-8') as f:
            state = json.load(f)
            
    print(f"🚀 Bắt đầu chiến dịch B2C Cát Mèo. Mục tiêu hôm nay: {TARGET_POSTS_PER_RUN} bài.")
    
    posts_done = 0
    start_index = state["last_index"]
    
    for i in range(start_index, len(db["clusters"])):
        if posts_done >= TARGET_POSTS_PER_RUN:
            break
            
        cluster = db["clusters"][i]
        if cluster["posted"]:
            continue
            
        kw = cluster["keyword"]
        title = cluster["title"]
        pillar = db["pillars"][kw]["url"]
        
        print(f"--- Đang xử lý bài {posts_done + 1}/{TARGET_POSTS_PER_RUN} ---")
        print(f"  [Tiêu đề] {title}")
        
        html_content = generate_article(kw, title, pillar)
        if not html_content or len(html_content) < 500:
            print("  [!] Lỗi sinh nội dung AI hoặc nội dung quá ngắn!")
            continue
            
        search_kw = "cat" if random.random() > 0.5 else "cat litter"
        img_url, img_id = fetch_pexels_image(search_kw)
        media_id = None
        if img_url:
            media_id = upload_image_to_wp(img_url)
            
        post_link = post_to_wp(title, html_content, media_id)
        if post_link:
            print(f"  [✅] Đăng thành công: {post_link}")
            cluster["posted"] = True
            posts_done += 1
            state["total_posted"] += 1
            state["last_index"] = i + 1
            
            # Cập nhật liên tục để an toàn
            with open(DB_PATH, 'w', encoding='utf-8') as f:
                json.dump(db, f, ensure_ascii=False, indent=4)
            with open(STATE_PATH, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=4)
                
            time.sleep(10)
            
    print(f"🎉 Hoàn thành hôm nay: {posts_done} bài. Tổng số đã đăng: {state['total_posted']}")

if __name__ == "__main__":
    main()
