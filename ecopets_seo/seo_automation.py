import os
import csv
import json
import time
import requests
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup
from googlesearch import search
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Cấu hình API key miễn phí từ Google Studio
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Cấu hình WordPress
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_API_URL = "https://ecopets.vn/wp-json/wp/v2/posts"
WP_MEDIA_URL = "https://ecopets.vn/wp-json/wp/v2/media"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Lợi thế độc quyền (USP) đính kèm bài viết
ECOPETS_USPS = """
Ecopets - Thương hiệu "Boss Đẹp - Việt Nam Xanh" tiên phong với sản phẩm hữu cơ sản xuất tại Việt Nam.
- Bọt vệ sinh tai thuần chay: làm sạch dịu nhẹ không kích ứng, giảm gãi ngứa tai tận gốc.
- Canxi hữu cơ an toàn: ngăn ngừa sỏi thận ở chó mèo và cực kỳ an toàn cho thai kỳ.
- Beta Amin: phục hồi sức khỏe tuyệt đối, tăng cường đề kháng tự nhiên.
"""

def extract_text_from_url(url):
    print(f"  [+] Đang nghiên cứu bài viết từ: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all(['p', 'h2', 'h3'])
        text = " ".join([p.get_text().strip() for p in paragraphs])
        return text[:1500] 
    except Exception:
        return ""

def research_competitors(keyword):
    print(f"[*] Đang lùng sục Google lấy ý tưởng từ đối thủ cho từ: '{keyword}'...")
    competitor_contents = []
    try:
        urls = list(search(keyword, num=3, stop=3, pause=2.0))
        for url in urls:
            if "ecopets.vn" not in url:
                content = extract_text_from_url(url)
                if content:
                    competitor_contents.append(f"Đối thủ ({url}):\n{content}")
    except Exception as e:
        print(f"[-] Lỗi Google Search: {e}")
    return "\n---\n".join(competitor_contents)

def get_internal_links():
    try:
        res = requests.get(f"{WP_API_URL}?per_page=5&status=publish", auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=10)
        if res.status_code == 200:
            posts = res.json()
            links = []
            for p in posts:
                links.append(f"- {p.get('title',{}).get('rendered','')}: {p.get('link','')}")
            return "\n".join(links)
    except:
        pass
    return ""

def generate_seo_article(keyword, location, competitor_data, internal_links):
    print(f"[*] Đang yêu cầu AI múa bút (Sử dụng Google Gemini 100% Miễn phí)...")
    
    geo_text = f" tại khu vực {location}" if location.lower() != "toàn quốc" else " (Hàng nội địa Việt Nam - Ship Toàn quốc)"
    
    prompt = f"""
    Bạn là một chuyên gia Content Writer về thú y tài ba. Nhiệm vụ: Viết bài chuẩn SEO đạt Top 1 Google cho từ khóa: "{keyword}"{geo_text}. 
    
    Hãy tham khảo ý chính của đối thủ để đảm bảo bài viết mình hay hơn:
    {competitor_data}
    
    YÊU CẦU ĐẶC BIỆT:
    1. Đừng copy nguyên văn. Viết bằng giọng văn đồng cảm, am hiểu chuyên môn, độ dài tầm 800 - 1000 từ.
    2. Chốt sale thật nghệ thuật ở giữa và cuối bài bằng cách lồng ghép các USP hữu cơ, an toàn tuyệt đối của hãng: 
       {ECOPETS_USPS}
    3. LIÊN KẾT NỘI BỘ (Internal Links): Hãy khéo léo chèn các link bài viết sau vào đoạn văn phù hợp bằng thẻ <a>:
       {internal_links}
    4. Định dạng kết quả rốt ráo LÀ DẠNG HTML (sử dụng <h1> làm tiêu đề gốc, các <h2>, <h3> chứa LSI keyword, <ul> cho danh sách, đoạn văn <p> ngắn gọn dễ nhìn). 
    5. KHÔNG phản hồi thêm lời chào hay bọc trong thẻ ```html. Chỉ trả về chuỗi HTML thô (Raw HTML).
    """

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        text = response.text
        text = text.replace("```html", "").replace("```", "").strip()
        return text
    except Exception as e:
        print(f"[-] Lỗi Gemini API: {e}")
        return None

def generate_free_image(keyword):
    print(f"[*] Đang tìm ảnh minh họa thực tế cho: {keyword}...")
    query_term = "pet"
    if "chó" in keyword.lower() or "cún" in keyword.lower(): query_term = "dog"
    elif "mèo" in keyword.lower() or "cat" in keyword.lower(): query_term = "cat"
    else: query_term = "veterinary"
        
    url = f"https://apis.scrimba.com/unsplash/photos/random?orientation=landscape&query={query_term}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            img_url = data['urls']['regular']
            img_data = requests.get(img_url, timeout=15).content
            filename = f"image_{int(time.time())}_{random.randint(100,999)}.jpg"
            with open(filename, "wb") as f:
                f.write(img_data)
            return filename
    except Exception as e:
        print(f"[-] Lỗi Unsplash: {e}")
        
    try:
        backup_url = f"https://loremflickr.com/1200/800/{query_term}?lock={random.randint(1,10000)}"
        img_data = requests.get(backup_url, timeout=15).content
        filename = f"image_{int(time.time())}_{random.randint(100,999)}.jpg"
        with open(filename, "wb") as f:
            f.write(img_data)
        return filename
    except:
        return None

def upload_image_to_wordpress(filepath):
    print(f"[*] Đang tải Media Image lên trang web...")
    try:
        with open(filepath, 'rb') as file:
            headers = {
                'Content-Disposition': f'attachment; filename="{os.path.basename(filepath)}"',
                'Content-Type': 'image/jpeg'
            }
            response = requests.post(WP_MEDIA_URL, 
                                     headers=headers, 
                                     auth=(WP_USERNAME, WP_APP_PASSWORD), 
                                     data=file)
            
            if response.status_code == 201:
                res = response.json()
                image_url = res.get('source_url')
                media_id = res.get('id')
                print(f"  [+] Xong! Đã mượn link ảnh: {image_url}")
                return media_id, image_url
            else:
                 print("[-] Tải ảnh thất bại")
                 return None, None
    except Exception as e:
        print(f"[-] Lỗi upload ảnh: {e}")
        return None, None

def post_to_wordpress(title, content, featured_media_id=None):
    print(f"[*] Đang đẩy thành phẩm lên bản nháp WordPress: {title}...")
    headers = {"Content-Type": "application/json"}
    
    data = {
        "title": title, 
        "content": content, 
        "status": "publish",
        "categories": [65] 
    }
    if featured_media_id:
        data["featured_media"] = featured_media_id
    
    try:
        response = requests.post(
            WP_API_URL, 
            auth=(WP_USERNAME, WP_APP_PASSWORD), 
            headers=headers, 
            json=data
        )
        if response.status_code == 201:
            print(f"  [+] Đăng bài THÀNH CÔNG! Link trải nghiệm thử: {response.json().get('link')}")
            return True
        else:
            print(f"  [-] Lỗi: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[-] Lỗi đẩy bài WP: {e}")
        return False

def save_to_dashboard_db(title, keyword, status="Published"):
    """Lưu trữ lịch sử đăng bài vào CSDL để Dashboard hiển thị"""
    db_path = "database.json"
    print("[*] Đang cập nhật trạng thái vào Dashboard database.json...")
    try:
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
        else:
            db = {"keywords": [], "articles": []}

        # Tạo record mới cho bài viết
        new_article = {
            "title": title,
            "keyword": keyword,
            "status": status,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        db["articles"].append(new_article)

        # Cập nhật xem keyword đã tồn tại trong mảng ranking chưa
        kw_exists = any(k["keyword"].lower() == keyword.lower() for k in db["keywords"])
        if not kw_exists:
            db["keywords"].append({
                "keyword": keyword,
                "history": [100] # Thiết lập xếp hạng ban đầu là 100
            })

        # Ghi đè lại file
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"[-] Lỗi cập nhật database: {e}")

def main():
    if not GEMINI_API_KEY or not WP_USERNAME or not WP_APP_PASSWORD:
         print("[-] LỖI CHƯA NHẬP KEY: Vui lòng xem hướng dẫn file README và lấy Key miễn phí nhét vào file .env")
         return

    print("=== TOOL ĐĂNG BÀI SEO ECOPETS & THÔNG BÁO TỚI DASHBOARD ===")
    
    with open('keywords.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            keyword = row.get('Keyword', '').strip()
            location = row.get('Location', 'Toàn quốc').strip()
            
            if not keyword:
                continue
                
            print(f"\n---> >>> KHỞI ĐỘNG CỖ MÁY VỚI: {keyword}")
            competitor_data = research_competitors(keyword)
            time.sleep(2)
            
            internal_links = get_internal_links()
            html_content = generate_seo_article(keyword, location, competitor_data, internal_links)
            
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                title = f"{keyword.capitalize()} {location}"
                
                h1_tag = soup.find('h1')
                if h1_tag:
                    title = h1_tag.get_text()
                    h1_tag.decompose()
                    html_content = str(soup)
                    
                img_path1 = generate_free_image(f"featured {keyword}")
                img_path2 = generate_free_image(f"content 1 {keyword}")
                img_path3 = generate_free_image(f"content 2 {keyword}")
                
                featured_id = None
                img_url2, img_url3 = "", ""
                
                if img_path1:
                    media_id, url = upload_image_to_wordpress(img_path1)
                    if media_id: featured_id = media_id
                    os.remove(img_path1)
                
                if img_path2:
                    _, url2 = upload_image_to_wordpress(img_path2)
                    if url2: img_url2 = url2
                    os.remove(img_path2)
                    
                if img_path3:
                    _, url3 = upload_image_to_wordpress(img_path3)
                    if url3: img_url3 = url3
                    os.remove(img_path3)
                    
                paragraphs = soup.find_all('p')
                if len(paragraphs) >= 2:
                    mid_index = len(paragraphs) // 2
                    if img_url2:
                        html_img2 = f'<figure class="wp-block-image size-large"><img src="{img_url2}" alt="{keyword}" style="max-width: 100%; border-radius: 8px;" /></figure>'
                        paragraphs[mid_index].insert_after(BeautifulSoup(html_img2, 'html.parser'))
                    if img_url3:
                        html_img3 = f'<figure class="wp-block-image size-large"><img src="{img_url3}" alt="{keyword}" style="max-width: 100%; border-radius: 8px;" /></figure>'
                        paragraphs[-1].insert_after(BeautifulSoup(html_img3, 'html.parser'))
                else:
                    html_prefix = ""
                    if img_url2: html_prefix += f'<figure class="wp-block-image size-large"><img src="{img_url2}" alt="{keyword}" style="max-width: 100%; border-radius: 8px;" /></figure>\n'
                    if img_url3: html_prefix += f'<figure class="wp-block-image size-large"><img src="{img_url3}" alt="{keyword}" style="max-width: 100%; border-radius: 8px;" /></figure>\n'
                    soup = BeautifulSoup(html_prefix + str(soup), 'html.parser')
                    
                html_content = str(soup)
                
                # Đăng bài và kết nối với Dashboard
                success = post_to_wordpress(title=title, content=html_content, featured_media_id=featured_id)
                if success:
                    save_to_dashboard_db(title, keyword, "Published")

if __name__ == "__main__":
    main()
