import os
import requests
import re
from dotenv import load_dotenv
from qwen_manager import chat_with_qwen

load_dotenv()

WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_API_URL = "https://ecopets.vn/wp-json/wp/v2/posts"

SLUG = "si-phu-kien-thu-cung-tphcm-mo-hinh-nhuong-quyen-dai-ly-it-von-thu-hoi-trong-45-ngay"
TITLE = "Sỉ Phụ Kiện Thú Cưng TPHCM: Mô Hình Nhượng Quyền Đại Lý Ít Vốn Ecopets"
KEYWORD = "Sỉ phụ kiện thú cưng TPHCM"

def strip_markdown_to_html(text: str) -> str:
    text = re.sub(r'```[\w]*\n?', '', text)
    text = text.replace('```', '')
    text = re.sub(r'^#{4}\s+(.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^#{3}\s+(.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^#{2}\s+(.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^#{1}\s+(.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'\*{3}(.+?)\*{3}', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'_{3}(.+?)_{3}', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*{2}(.+?)\*{2}', r'<strong>\1</strong>', text)
    text = re.sub(r'_{2}(.+?)_{2}', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'^[-\*]\s+(.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'((?:<li>.*</li>\n?)+)', r'<ul>\n\1</ul>\n', text)
    text = re.sub(r'^\d+\.\s+(.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'^(---+|\*\*\*+)$', '<hr/>', text, flags=re.MULTILINE)
    text = re.sub(r'^>\s+(.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
    lines = text.split('\n')
    wrapped = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('<'):
            wrapped.append(f'<p>{stripped}</p>')
        else:
            wrapped.append(line)
    return '\n'.join(wrapped).strip()

def rewrite_post():
    print(f"Đang yêu cầu Qwen viết lại bài cho URL: {SLUG}...")
    
    prompt = f"""Bạn là Giám đốc kinh doanh của thương hiệu Ecopets. Viết một bài chuẩn SEO cho từ khóa "{KEYWORD}".
Bài viết nhằm mục đích tìm kiếm đối tác sỉ, đại lý phân phối và nhượng quyền các sản phẩm chăm sóc thú cưng hữu cơ tại TPHCM và toàn quốc.

YÊU CẦU QUAN TRỌNG NHẤT ĐỂ TRÁNH BỊ XÓA BÀI (KHÔNG GÂY ẢO GIÁC - NO HALLUCINATION):
- Tuyệt đối KHÔNG ĐƯỢC cam kết những con số phi thực tế mang tính lừa đảo như "Chắc chắn thu hồi vốn trong 45 ngày", "Cam kết lợi nhuận 100%". 
- Không tự bịa ra những bảng giá nhượng quyền hay con số lợi nhuận không có thật.
- Chỉ được dùng từ ngữ định tính, thực tế: "Mô hình rủi ro thấp", "Hỗ trợ đại lý bán chéo (cross-sale)", "Sản phẩm thiết yếu vòng đời ngắn giúp quay vòng vốn nhanh".
- Không đề cập đến con số "45 ngày" một cách hứa hẹn.

CẤU TRÚC BÀI VIẾT (BẮT BUỘC):
<h1>Sỉ Phụ Kiện Thú Cưng TPHCM: Mô Hình Nhượng Quyền & Đại Lý Ít Vốn Ecopets</h1>
<p>[Mở đầu: Đánh vào nhu cầu thị trường thú cưng đang bùng nổ, sự chuyển dịch sang các sản phẩm an toàn/hữu cơ]</p>
<h2>Thị Trường Thú Cưng Tại TPHCM Đang Khát Sản Phẩm Hữu Cơ</h2>
<p>[Phân tích thị trường, tại sao các shop thú cưng cần nhập thêm dòng sản phẩm an toàn sinh học]</p>
<h2>Tại Sao Nên Trở Thành Đại Lý Của Ecopets?</h2>
<p>[Nhấn mạnh: Vốn nhập hàng linh hoạt, sản phẩm chất lượng ngách, hỗ trợ marketing từ tổng công ty]</p> 
<h2>Các Dòng Sản Phẩm Ecopets Đang Tìm Đại Lý Phân Phối</h2>
<ul>
  <li><strong>Bọt vệ sinh tai thuần chay:</strong> làm sạch dịu nhẹ không kích ứng.</li>
  <li><strong>Canxi hữu cơ an toàn:</strong> ngăn ngừa sỏi thận ở chó mèo và cực an toàn cho thai kỳ.</li>
  <li><strong>Beta Amin:</strong> phục hồi sức khỏe tuyệt đỉnh cho thú cưng ốm yếu.</li>
</ul>
<h2>Chính Sách Nhượng Quyền Và Chiết Khấu Hấp Dẫn</h2>
<p>[Lưu ý: Viết chung chung là chính sách chiết khấu sâu theo từng bậc đại lý, vốn khởi điểm thấp giúp đại lý nhỏ lẻ dễ dàng tham gia, thu hồi vốn nhanh nhờ tính thiết yếu của sản phẩm]</p>
<h2>Kết Luận</h2>
<p>[Kêu gọi hành động: Liên hệ ngay Ecopets để nhận bảng báo giá sỉ]</p>

LUẬT BẮT BUỘC:
1. Độ dài tối thiểu 1500 chữ. Phân tích sâu, văn phong thuyết phục của một chuyên gia kinh doanh (B2B).
2. Trả về HTML thuần túy. KHÔNG có câu trò chuyện Robot. KHÔNG dùng cú pháp markdown (**bold**, ##heading, -bullet, ```html).
3. Bắt đầu ngay từ thẻ <h1>.
"""
    raw = chat_with_qwen(prompt, max_tokens=8000)
    html_text = strip_markdown_to_html(raw)
    
    h1_idx = html_text.find("<h1")
    if h1_idx > 0:
        html_text = html_text[h1_idx:]
    
    headers = {"Content-Type": "application/json"}
    data = {
        "title": TITLE,
        "content": html_text,
        "slug": SLUG,
        "status": "publish",
        "categories": [1], 
    }
    
    print("Đang đẩy lên WordPress Ecopets.vn...")
    response = requests.post(
        WP_API_URL,
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        headers=headers,
        json=data
    )
    if response.status_code == 201:
        print(f"[+] Thành công khôi phục bài viết! Link: {response.json().get('link')}")
    else:
        print(f"[-] Lỗi đẩy bài: {response.status_code} - {response.text}")

if __name__ == "__main__":
    rewrite_post()
