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
WP_API_URL = "https://ecopets.vn/wp-json/wp/v2/posts"
CSV_FILE = r"D:\Antigravity\ecopets_seo\gsc_export_1306\Bảng.csv"

def get_post_by_slug(slug):
    url = f"{WP_API_URL}?slug={slug}"
    try:
        response = requests.get(url, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]
    except Exception as e:
        print(f"  [-] Lỗi kết nối khi get_post: {e}")
    return None

def trash_post(post_id):
    url = f"{WP_API_URL}/{post_id}"
    try:
        response = requests.delete(url, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=30)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"  [-] Lỗi kết nối khi trash_post: {e}")
        return False

def update_post(post_id, new_content):
    url = f"{WP_API_URL}/{post_id}"
    payload = {"content": new_content}
    try:
        response = requests.post(url, json=payload, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=45)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"  [-] Lỗi kết nối khi update_post: {e}")
        return False

def clean_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=' ', strip=True)

def main():
    print("🚀 Bắt đầu Chiến dịch Cứu hộ 231 bài viết...")
    
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
    
    START_INDEX = 784

    for i, url in enumerate(rows):
        if i < START_INDEX:
            continue
            
        url = url.strip()
        # Bỏ qua các URL không phải là bài viết
        if "?p=" in url or url.endswith(".html") or "/page/" in url:
            continue
        if "/tag/" in url or "/product-tag/" in url or "/category/" in url or "/feed" in url:
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
        
        # 1. Đánh giá (Judge)
        judge_prompt = f"""Bạn là một chuyên gia kiểm duyệt nội dung SEO cho website Ecopets.vn.
Nhiệm vụ của bạn là đọc tiêu đề và trích đoạn nội dung dưới đây, và quyết định xem bài viết này nên XÓA hay GIỮ LẠI.

Tiêu chí XÓA:
- Bài viết quá ngắn, cấu trúc rập khuôn kiểu AI rẻ tiền.
- Tiêu đề nhồi nhét từ khóa vô nghĩa, lủng củng.
- Nội dung lan man, lặp lại các bài khác (vd: chó biếng ăn, chó rụng lông viết chung chung).

Tiêu chí GIỮ LẠI (Để viết lại):
- Chủ đề hay, từ khóa ngách tiềm năng (VD: review sản phẩm, sỉ phụ kiện, kinh nghiệm mở pet shop, trị bệnh chuyên sâu).

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
            
            rewrite_prompt = f"""Bạn là Bác sĩ thú y kiêm Chủ chuỗi Pet Shop Ecopets.
Hãy viết lại bài viết sau đây để chuẩn SEO và mang đậm kinh nghiệm thực tế (EEAT).
Tiêu đề: {title}

Yêu cầu:
- KHÔNG dùng cấu trúc AI rập khuôn (như: "chào mừng bạn đến với", "tóm lại", "hi vọng bài viết", "như chúng ta đã biết").
- Mở bài trực tiếp vào vấn đề.
- Chèn các câu chuyện thực tế tư vấn khách hàng, số liệu, mẹo hay của Ecopets.
- Độ dài khoảng 1000 - 1500 từ.
- Trả về định dạng HTML thuần (các thẻ <h2>, <h3>, <p>, <ul>). Không bọc trong code block Markdown.
- Bắt buộc có thẻ <h2> kết luận kêu gọi mua hàng tại Ecopets.vn.
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
            
        time.sleep(2)  # Tránh Rate Limit

    print("\n" + "="*40)
    print("BÁO CÁO KẾT QUẢ CHIẾN DỊCH:")
    print(f"- Đã XÓA (Trash): {deleted_count} bài")
    print(f"- Đã VIẾT LẠI (Rewrite): {rewritten_count} bài")
    print(f"- Không tìm thấy URL: {not_found_count} bài")
    print("="*40)

if __name__ == "__main__":
    main()
