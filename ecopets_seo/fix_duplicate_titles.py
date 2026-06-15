import os
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
WP_USERNAME = "aivietbai"
WP_APP_PASSWORD = "kNZG 0aEW 1iy0 tTcT Degh pTR4"
WP_API_URL = "https://ecopets.vn/wp-json/wp/v2/posts"





from qwen_manager import chat_with_qwen

def generate_new_title(content):
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text(separator=' ').strip()
    # Lấy 800 ký tự đầu tiên để AI hiểu nội dung
    sample_text = text[:800]
    
    prompt = f"""Đọc đoạn nội dung bài viết dưới đây và đặt 1 tiêu đề H1 thật sáng tạo, hấp dẫn, ngắn gọn (tối đa 70 ký tự) để làm tiêu đề bài viết.
Chỉ trả về DUY NHẤT nội dung tiêu đề, không có dấu ngoặc kép, không có từ ngữ thừa.

Nội dung:
{sample_text}"""

    try:
        resp = qwen_client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.8
        )
        return resp.choices[0].message.content.strip().replace('"', '').replace('**', '')
    except Exception as e:
        print(f"Lỗi AI: {e}")
        return None

def fix_duplicate_titles():
    print("Đang lấy danh sách bài viết...")
    resp = requests.get(WP_API_URL, params={"per_page": 30, "status": "publish"}, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=15)
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
            print(f"\nPhát hiện {len(grouped_posts)} bài viết bị TRÙNG tiêu đề: '{title}'")
            # Sửa tất cả các bài bị trùng (có thể giữ nguyên bài đầu tiên, nhưng ở đây sửa hết bằng AI cho chắc chắn khác nhau)
            for i, post in enumerate(grouped_posts):
                if i == 0:
                    print(f"  - Bỏ qua bài gốc (ID {post['id']}) giữ nguyên tiêu đề.")
                    continue
                
                print(f"  - Đang tạo tiêu đề mới cho bài ID {post['id']}...")
                content = post['content']['raw'] if 'raw' in post['content'] else post['content']['rendered']
                new_title = generate_new_title(content)
                
                if new_title and new_title.lower() != title.lower():
                    print(f"    -> Tiêu đề mới: {new_title}")
                    # Cập nhật lên WP
                    update_resp = requests.post(
                        f"{WP_API_URL}/{post['id']}", 
                        json={"title": new_title}, 
                        auth=(WP_USERNAME, WP_APP_PASSWORD), 
                        timeout=15
                    )
                    if update_resp.status_code == 200:
                        print("    [+] Cập nhật thành công!")
                    else:
                        print("    [x] Lỗi cập nhật:", update_resp.text)
                else:
                    print("    [-] AI không tạo được tiêu đề mới khác biệt.")

if __name__ == "__main__":
    if qwen_client:
        fix_duplicate_titles()
    else:
        print("Không thể kết nối AI")
