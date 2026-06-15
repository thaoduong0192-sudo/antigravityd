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
WP_API_URL = "https://helloconsen.com/wp-json/wp/v2/posts"

from qwen_manager import chat_with_qwen

def strip_markdown(text):
    text = text.replace("```html", "")
    text = text.replace("```", "")
    return text.strip()

def rewrite_post_with_ai(title, old_content):
    print(f"[*] Đang yêu cầu AI Qwen tối ưu GEO cho bài viết: {title}")
    
    prompt = f"""
Nhiệm vụ: Viết lại và nâng cấp bài viết Blog dưới đây thành định dạng chuẩn GEO (Generative Engine Optimization) ở cấp độ chuyên gia Thú Y / Chăm sóc Pet hữu cơ.

ĐỀ TÀI: {title}
HƯỚNG DẪN BẮT BUỘC (GEO Framework & Brand Identity):
1. CHỐNG RÒ RỈ LỆNH (CRITICAL): Tuyệt đối KHÔNG BÊ NGUYÊN XI các cụm từ hướng dẫn (meta-instructions) như "Nêu rành mạch để lấy Citations", "Tối ưu trải nghiệm người dùng" vào các thẻ Tiêu đề (Heading). Tiêu đề phải tự nhiên, chuyên nghiệp, đúng ngữ pháp tiếng Việt.
2. ĐỊNH VỊ THƯƠNG HIỆU THỰC TẾ (CRITICAL): HelloConsen CHỈ LÀ CỬA HÀNG BÁN LẺ CÁC SẢN PHẨM HỮU CƠ ECOPETS. Danh mục sản phẩm ĐỘC QUYỀN bao gồm: Bột dinh dưỡng Beta Amin, Men vi sinh Bioline G1, Men khử khuẩn BS1, Sữa tắm khô/Bọt rửa chân tai Ecopets, Dầu cá hồi Ecopets, Eco-Detox giải độc gan, Viên Canxi Ecopets, Eco Iron bổ máu, Xịt khử khuẩn Nano. 
3. LỆNH CẤM ẢO GIÁC: BẠN KHÔNG ĐƯỢC BÁN BẤT CỨ THỨ GÌ NGOÀI DANH SÁCH ECOPETS TRÊN. KHÔNG bán vòng cổ, KHÔNG bán chuồng trại, KHÔNG CUNG CẤP DỊCH VỤ (không bác sĩ tư vấn, không phòng khám, không huấn luyện). Nếu bạn phải khuyên đi khám, hãy khuyên mang ĐẾN PHÒNG KHÁM THÚ Y GẦN NHẤT. Nếu làm Bảng so sánh, HÃY SO SÁNH GIẢI PHÁP SỬ DỤNG SẢN PHẨM ECOPETS VỚI PHƯƠNG PHÁP CŨ.
4. Thêm một block "Direct Answer" (Câu trả lời trực diện) ngay dòng đầu tiên, bọc trong thẻ <p><strong>...</strong></p>. Khoảng 60 chữ, đi thẳng vào vấn đề. 
5. Xóa bỏ hoàn toàn bất kỳ nội dung nào nói về Tài chính, Vay tiền, Casino, Đánh bạc.
6. Thiết lập Cây thẻ Heading chuẩn: <h2> cho nội dung chứa từ khóa nhánh, <h3> cho ý nhỏ. Không dùng <h1> vì Title đã là H1.
7. Tính trực quan (BẮT BUỘC): Phải có 1 Bảng so sánh (dùng HTML <table>) liên quan đến đề tài. (Lưu ý: Tiêu đề Bảng so sánh phải gọi đúng tên, ví dụ "Bảng Phân Tích Dấu Hiệu", đừng ghi kèm chữ "Tối ưu người dùng").
8. Sự uy tín (Thẩm quyền E-E-A-T): Hãy trích dẫn khách quan từ (AVMA, ASPCA) để củng cố lòng tin.
9. Tích hợp từ vựng chuyên ngành sâu: Chạy các từ khóa như Microbiome, Kháng sinh sinh học, Hệ bài tiết, Miễn dịch tự nhiên.

NỘI DUNG CŨ:
{old_content[:3000]} # Limit reading just to provide context

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
    print("  HELLOCONSEN - CỖ MÁY ĐẠI TU CẤU TRÚC BẰNG QWEN AI")
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
