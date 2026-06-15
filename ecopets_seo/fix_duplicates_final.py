import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
from stock_photos import download_stock_photo
from fully_auto_system import upload_image_bytes_to_wp

load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
WP_USERNAME = "aivietbai"
WP_APP_PASSWORD = "kNZG 0aEW 1iy0 tTcT Degh pTR4"
WP_API_URL = "https://ecopets.vn/wp-json/wp/v2/posts"





from qwen_manager import chat_with_qwen

def generate_new_title(content, old_title):
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text(separator=' ').strip()
    sample_text = text[:1000]
    
    prompt = f"""Đọc đoạn nội dung bài viết dưới đây và đặt 1 tiêu đề H1 thật sáng tạo, hấp dẫn, ngắn gọn (tối đa 70 ký tự).
Tuyệt đối KHÔNG ĐƯỢC GIỐNG tiêu đề cũ này: "{old_title}".
Chỉ trả về DUY NHẤT nội dung tiêu đề mới, không có dấu ngoặc kép.

Nội dung:
{sample_text}"""

    try:
        resp = qwen_client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.9
        )
        return resp.choices[0].message.content.strip().replace('"', '').replace('**', '')
    except Exception as e:
        print(f"Lỗi AI: {e}")
        return None

def fix_duplicates_final():
    print("Đang lấy danh sách 20 bài viết mới nhất...")
    resp = requests.get(WP_API_URL, params={"per_page": 20, "status": "publish"}, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=15)
    if resp.status_code != 200:
        print("Lỗi API WP")
        return

    posts = resp.json()
    title_groups = {}
    
    for post in posts:
        title = post['title']['rendered']
        title_groups.setdefault(title, []).append(post)

    for title, grouped_posts in title_groups.items():
        if len(grouped_posts) > 1:
            print(f"\nPhát hiện {len(grouped_posts)} bài viết bị TRÙNG: '{title}'")
            # Bỏ qua bài đầu tiên, sửa các bài còn lại
            for i in range(1, len(grouped_posts)):
                post = grouped_posts[i]
                print(f"  - Đang xử lý bài ID {post['id']}...")
                
                content = post['content']['raw'] if 'raw' in post['content'] else post['content']['rendered']
                
                # 1. Tạo tiêu đề mới
                new_title = generate_new_title(content, title)
                if not new_title or new_title.lower() == title.lower():
                    print("    [-] AI không tạo được tiêu đề mới. Sinh lại lần 2...")
                    new_title = generate_new_title(content, title)
                
                update_data = {}
                if new_title and new_title.lower() != title.lower():
                    update_data["title"] = new_title
                    print(f"    -> Tiêu đề mới: {new_title}")
                
                # 2. Thay hình ảnh mới (chống trùng lặp 100%)
                print("    -> Đang lấy ảnh mới từ Pexels...")
                kw_search = "nguồn sỉ thức ăn thú cưng" # Fallback chung, hệ thống tự điều hướng sang cat/dog eating
                new_img_bytes = download_stock_photo(kw_search, width=1200, height=630)
                if new_img_bytes:
                    media_id, _ = upload_image_bytes_to_wp(new_img_bytes, alt_text=new_title or title)
                    if media_id:
                        update_data["featured_media"] = media_id
                        print(f"    -> Đã đổi ảnh mới (Media ID: {media_id})")
                
                if update_data:
                    update_resp = requests.post(
                        f"{WP_API_URL}/{post['id']}", 
                        json=update_data, 
                        auth=(WP_USERNAME, WP_APP_PASSWORD), 
                        timeout=30
                    )
                    if update_resp.status_code == 200:
                        print("    [+] Đã cập nhật thành công CẢ TIÊU ĐỀ VÀ HÌNH ẢNH!")
                    else:
                        print("    [x] Lỗi cập nhật:", update_resp.text)

if __name__ == "__main__":
    if qwen_client:
        fix_duplicates_final()
    else:
        print("Không thể kết nối AI")
