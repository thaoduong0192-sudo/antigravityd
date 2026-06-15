import os
import csv
import json
import time
import requests
from dotenv import load_dotenv
import qwen_manager
from bs4 import BeautifulSoup

load_dotenv()

WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_API_URL = "https://helloconsen.com/wp-json/wp/v2/posts"
CSV_FILE = "D:\\Antigravity\\helloconsen_seo\\gsc_export\\Blog_Posts.csv"

def get_post_by_slug(slug):
    url = f"{WP_API_URL}?slug={slug}"
    response = requests.get(url, auth=(WP_USERNAME, WP_APP_PASSWORD))
    if response.status_code == 200:
        data = response.json()
        if data and len(data) > 0:
            return data[0]
    return None

def trash_post(post_id):
    url = f"{WP_API_URL}/{post_id}"
    response = requests.delete(url, auth=(WP_USERNAME, WP_APP_PASSWORD))
    return response.status_code in [200, 201]

def update_post(post_id, new_content):
    url = f"{WP_API_URL}/{post_id}"
    payload = {"content": new_content}
    response = requests.post(url, json=payload, auth=(WP_USERNAME, WP_APP_PASSWORD))
    return response.status_code in [200, 201]

def clean_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=' ', strip=True)

def main():
    print("🚀 Bắt đầu Chiến dịch Cứu hộ Bài viết Blog HelloConsen...")
    
    rows = []
    try:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if row:
                    rows.append(row[0])
    except Exception as e:
        print(f"Lỗi đọc CSV: {e}")
        return

    deleted_count = 0
    rewritten_count = 0
    not_found_count = 0

    for i, url in enumerate(rows):
        url = url.strip()
        if "?p=" in url or url.endswith(".html") or "/page/" in url:
            continue
            
        slug = url.strip("/").split("/")[-1]
        print(f"\n[{i+1}/{len(rows)}] Đang xử lý: {slug}")
        
        post = get_post_by_slug(slug)
        if not post:
            print("  [-] Không tìm thấy bài viết trên WordPress.")
            not_found_count += 1
            continue
            
        post_id = post["id"]
        title = post["title"]["rendered"]
        raw_content = post["content"]["rendered"]
        clean_text = clean_html(raw_content)
        
        judge_prompt = f"""Bạn là một chuyên gia kiểm duyệt nội dung SEO cho website HelloConsen.com (Mô hình B2B Petshop, sỉ thức ăn, nhượng quyền Trạm Dinh Dưỡng Xanh).
Nhiệm vụ của bạn là đọc tiêu đề và trích đoạn nội dung dưới đây, và quyết định xem bài viết này nên XÓA hay GIỮ LẠI.

Tiêu chí XÓA:
- Bài viết chỉ hướng đến B2C (người nuôi chó mèo lẻ tẻ) mà không có giá trị kinh doanh B2B.
- Nội dung rác AI lan man, lặp lại từ khóa.

Tiêu chí GIỮ LẠI (Để viết lại):
- Chủ đề B2B tốt (VD: sỉ phụ kiện, kinh doanh petshop, lợi nhuận, chiến lược bán hàng, nhượng quyền).
- Chủ đề về dinh dưỡng nhưng có thể lái sang việc kinh doanh (tại sao cửa hàng nên bán sản phẩm này).

Tiêu đề: {title}
Trích đoạn: {clean_text[:800]}

Chỉ được trả lời duy nhất 1 từ: XOA hoặc GIU"""

        decision = qwen_manager.chat_with_qwen(judge_prompt, max_tokens=10, temperature=0.1)
        if not decision:
            print("  [-] Lỗi gọi AI Judge.")
            continue
            
        decision = decision.strip().upper()
        
        if "XOA" in decision:
            print(f"  [Quyết định] 🗑️ XÓA: {title}")
            if trash_post(post_id):
                print("  [+] Đã chuyển vào Thùng rác.")
                deleted_count += 1
            else:
                print("  [-] Lỗi khi xóa bài.")
        elif "GIU" in decision:
            print(f"  [Quyết định] ♻️ GIỮ & VIẾT LẠI: {title}")
            
            rewrite_prompt = f"""Bạn là Chuyên gia tư vấn chiến lược kinh doanh Pet Shop, chuyên cung cấp sỉ thức ăn và nhượng quyền Trạm Dinh Dưỡng Xanh của HelloConsen.
Hãy viết lại bài viết sau đây để chuẩn SEO và mang đậm tính thực chiến B2B.
Tiêu đề: {title}

Yêu cầu:
- KHÔNG dùng cấu trúc AI rập khuôn.
- Mở bài nhắm thẳng vào nỗi đau của chủ Pet Shop (tồn kho, vốn, thiếu khách).
- Phân tích chi phí/lợi nhuận, chiến lược bán hàng.
- Độ dài khoảng 1200 - 1500 từ.
- Trả về định dạng HTML thuần (các thẻ <h2>, <h3>, <p>, <ul>). Không bọc trong code block Markdown.
- Bắt buộc có thẻ <h2> kết luận kêu gọi các chủ shop hợp tác kinh doanh sỉ với HelloConsen.com.
"""
            new_html = qwen_manager.chat_with_qwen(rewrite_prompt, max_tokens=4000, temperature=0.7)
            if new_html:
                new_html = new_html.replace("```html", "").replace("```", "").strip()
                if update_post(post_id, new_html):
                    print("  [+] Đã cập nhật (Rewrite) thành công.")
                    rewritten_count += 1
                else:
                    print("  [-] Lỗi khi cập nhật bài viết.")
            else:
                print("  [-] Lỗi AI khi viết lại.")
        else:
            print(f"  [?] AI trả lời không rõ ràng: {decision}")
            
        time.sleep(2)

    print("\n" + "="*40)
    print("BÁO CÁO KẾT QUẢ CHIẾN DỊCH HELLOCONSEN:")
    print(f"- Đã XÓA (Trash): {deleted_count} bài")
    print(f"- Đã VIẾT LẠI (Rewrite): {rewritten_count} bài")
    print(f"- Không tìm thấy URL: {not_found_count} bài")
    print("="*40)

if __name__ == "__main__":
    main()
