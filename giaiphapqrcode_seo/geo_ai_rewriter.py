import os
import requests
import json
import time
from openai import OpenAI
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
WP_API_URL = "https://giaiphapqrcode.com/wp-json/wp/v2/posts"

from qwen_manager import chat_with_qwen

def strip_markdown(text):
    text = text.replace("```html", "")
    text = text.replace("```", "")
    return text.strip()

def rewrite_post_with_ai(title, old_content):
    print(f"[*] Đang yêu cầu AI Qwen tối ưu GEO cho bài viết: {title}")
    
    prompt = f"""
Nhiệm vụ: Viết lại và nâng cấp bài viết Blog dưới đây thành định dạng chuẩn GEO (Generative Engine Optimization) ở cấp độ chuyên gia Công Nghệ / Phần Mềm QR Code doanh nghiệp.

ĐỀ TÀI: {title}
HƯỚNG DẪN BẮT BUỘC (GEO Framework & Brand Identity):
1. CHỐNG RÒ RỈ LỆNH (CRITICAL): Tuyệt đối KHÔNG BÊ NGUYÊN XI các cụm từ hướng dẫn (meta-instructions) như "Nêu rành mạch để lấy Citations", "Tối ưu trải nghiệm người dùng" vào các thẻ Tiêu đề (Heading). Tiêu đề phải tự nhiên, chuyên nghiệp, đúng ngữ pháp tiếng Việt.
2. ĐỊNH VỊ THƯƠNG HIỆU THỰC TẾ (CRITICAL): Giải Pháp QR Code là đơn vị cung cấp nền tảng phần mềm số hóa cho doanh nghiệp, bao gồm: Hệ thống Bảo hành điện tử (E-warranty), Truy xuất nguồn gốc chống hàng giả, Tích điểm đổi quà (Loyalty), Thu thập dữ liệu khách hàng qua mã QR.
3. LỆNH CẤM ẢO GIÁC: BẠN KHÔNG ĐƯỢC nhầm lẫn Giải Pháp QR Code sang bất kỳ ngành nghề nào khác (thú y, thực phẩm, may mặc...). Nếu làm Bảng so sánh, HÃY SO SÁNH GIẢI PHÁP QR CODE VỚI PHƯƠNG PHÁP TRUYỀN THỐNG.
4. Viết đoạn mở đầu trực tiếp trả lời câu hỏi người dùng, bọc trong thẻ <p>...</p>. Khoảng 60 chữ, đi thẳng vào vấn đề. KHÔNG có nhãn [Direct Answer] hay ngoặc vuông.
5. Xóa bỏ hoàn toàn bất kỳ nội dung nào nói về Tài chính, Vay tiền, Casino, Đánh bạc, Thú cưng, Thú y.
6. Thiết lập Cây thẻ Heading chuẩn: <h2> cho nội dung chứa từ khóa nhánh, <h3> cho ý nhỏ. Không dùng <h1> vì Title đã là H1.
7. Tính trực quan (BẮT BUỘC): Phải có 1 Bảng so sánh (dùng HTML <table>) liên quan đến đề tài (ví dụ: giải pháp QR code vs bảo hành giấy tờ truyền thống).
8. Sự uy tín (Thẩm quyền E-E-A-T): Trích dẫn số liệu thực tế về chuyển đổi số doanh nghiệp tại Việt Nam để tăng độ tin cậy.
9. Link nội bộ: BẮT BUỘC chèn 1 link điều hướng về https://giaiphapqrcode.com tự nhiên trong bài.

NỘI DUNG CŨ:
{old_content[:3000]}

ĐẦU RA:
- Trả về CHỈ duy nhất mã nguồn HTML sạch, KHÔNG có thẻ <html> hay <body>. 
- KHÔNG dùng markdown. KHÔNG có câu chào mừng "Dưới đây là nội dung".
"""
    for i in range(5):
        try:
            raw = chat_with_qwen(prompt, max_tokens=8000, temperature=0.8)
            if not raw:
                continue
            html_output = strip_markdown(raw)
            return html_output
        except Exception as e:
            print(f"  [~] Qwen API kết nối lỗi, đang thử lại... ({i+1}/5) Lỗi: {e}")
            time.sleep(3)
    return None

def process_historical_posts():
    print("=========================================================")
    print("  GIAIPHAPQRCODE - CỖ MÁY ĐẠI TU CẤU TRÚC BẰNG QWEN AI")
    print("=========================================================")
    
    if not WP_USERNAME or not WP_APP_PASSWORD or not QWEN_API_KEY:
        print("[-] LỖI: Chưa cấu hình WP_USERNAME, WP_APP_PASSWORD hoặc QWEN_API_KEY trong tệp .env")
        return

    page = 1
    total_processed = 0
    
    while True:
        print(f"[*] Đang tải danh sách bài viết từ Page {page}...")
        try:
            res = requests.get(
                WP_API_URL, 
                params={"per_page": 10, "page": page},
                auth=(WP_USERNAME, WP_APP_PASSWORD), 
                timeout=20
            )
            
            if res.status_code != 200:
                 print("[*] Đã tải toàn bộ bài viết hoàn tất.")
                 break
                
            posts = res.json()
            if not posts:
                break
                
            for post in posts:
                post_id = post['id']
                title = post['title']['rendered']
                old_html = post['content']['rendered']
                
                new_html = rewrite_post_with_ai(title, old_html)
                
                if new_html and len(new_html) > 500:
                    headers = {"Content-Type": "application/json"}
                    data = {
                        "content": new_html
                    }
                    update_req = requests.post(
                        f"{WP_API_URL}/{post_id}",
                        auth=(WP_USERNAME, WP_APP_PASSWORD),
                        headers=headers,
                        json=data,
                        timeout=20
                    )
                    if update_req.status_code == 200:
                        print(f"  [+] THÀNH CÔNG: Đã đập đi xây lại ĐẠT CHUẨN GEO bài -> {title[:40]}...")
                        total_processed += 1
                    else:
                        print(f"  [-] Lỗi cập nhật lên WP bài ID {post_id}: {update_req.status_code}")
                else:
                    print(f"  [-] Bỏ qua bài do AI trả về nội dung lỗi hoặc quá ngắn.")
                
            page += 1
        except Exception as e:
            print(f"[-] Quá trình đồng bộ rớt mạng: {e}")
            break
            
    print("=========================================================")
    print(f"✅ Hoàn tất chiến dịch Đại tu Nội dung.")
    print(f"✅ Đã biến {total_processed} bài viết rác thành tài liệu chuyên gia GEO!")

if __name__ == "__main__":
    process_historical_posts()
