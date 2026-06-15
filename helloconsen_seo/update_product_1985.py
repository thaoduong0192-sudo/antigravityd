import os
import requests
import base64
import json
import re
from dotenv import load_dotenv
from qwen_manager import chat_with_qwen

load_dotenv()

old_html = """<h3 data-start="500" data-end="516">Bạn có biết?</h3>
<p data-start="518" data-end="639"><strong data-start="518" data-end="537">Cát vệ sinh mèo</strong> chính là nơi tiềm ẩn rất nhiều vi khuẩn gây hại. Phân mèo, nước tiểu trong quá trình phân hủy tạo ra:</p>
<ul data-start="641" data-end="802">
<li data-start="641" data-end="697">Vi khuẩn, vi nấm gây tiêu chảy, viêm ruột, bệnh hô hấp</li>
<li data-start="698" data-end="738">Mùi hôi khó chịu trong không gian sống</li>
<li data-start="739" data-end="802">Nguy cơ lây nhiễm mầm bệnh cho cả mèo, hamster và cả gia đình</li>
</ul>
<hr data-start="804" data-end="807" />
<h3 data-start="809" data-end="870">Men Khử Khuẩn Bioline BS1 dành cho cát vệ sinh mèo là gì?</h3>
<p data-start="872" data-end="927"><strong data-start="872" data-end="907">Men vi sinh khử mùi Bioline BS1</strong> được phát triển để:</p>
<ul data-start="929" data-end="1262">
<li data-start="929" data-end="1035"><strong data-start="931" data-end="963">Ngăn ngừa lây nhiễm mầm bệnh</strong> trong cát vệ sinh mèo, hamster, đặc biệt hiệu quả cho nhà nuôi mèo đàn.</li>
<li data-start="1036" data-end="1158">Khác với nhiều loại hạt khử mùi dùng hương nhân tạo chỉ át mùi, Bioline BS1 <strong data-start="1114" data-end="1157">xử lý tận gốc vi khuẩn gây mùi phân mèo</strong>.</li>
<li data-start="1159" data-end="1262">Hiệu quả <strong data-start="1170" data-end="1217">khử mùi hôi phân, nước tiểu mèo lên đến 70%</strong>, giữ môi trường sống trong lành, sạch khuẩn.</li>
</ul>
<hr data-start="1264" data-end="1267" />
<h3 data-start="1269" data-end="1307">Thành phần men vi sinh Bioline BS1</h3>
<ul data-start="1309" data-end="1421">
<li data-start="1309" data-end="1368"><strong data-start="1311" data-end="1366">Bacillus subtilis (100 triệu CFU/g – 100 tỷ CFU/kg)</strong></li>
<li data-start="1369" data-end="1421"><strong data-start="1371" data-end="1421">Chế phẩm sinh học an toàn cho người &amp; vật nuôi</strong></li>
</ul>
<p><img loading="lazy" decoding="async" class="size-medium wp-image-9341" src="http://helloconsen.com/wp-content/uploads/2022/05/Men-khu-khuan-Bioline-BS1-cho-cat-ve-sinh-meo-3-1-400x400.jpg" alt="Men khử khuẩn Bioline BS1 cho cát vệ sinh mèo" width="400" height="400" /></p>
<h3 data-start="1428" data-end="1477">Công dụng chính của men khử khuẩn Bioline BS1</h3>
<ul data-start="1479" data-end="1802">
<li data-start="1479" data-end="1534"><strong data-start="1481" data-end="1534">Khử mùi hôi phân, nước tiểu mèo trong cát vệ sinh</strong></li>
<li data-start="1535" data-end="1581"><strong data-start="1537" data-end="1579">Phân hủy phân thải chó mèo nhanh chóng</strong></li>
<li data-start="1582" data-end="1645">Tiêu diệt vi sinh vật gây mùi H2S, lưu huỳnh, hợp chất Nitơ</li>
<li data-start="1646" data-end="1697">Hạn chế vi khuẩn gây bệnh, ngăn mầm bệnh sinh sôi</li>
<li data-start="1698" data-end="1757"><strong data-start="1700" data-end="1723">Giảm stress cho mèo</strong> do mùi hôi tích tụ trong khay cát</li>
<li data-start="1758" data-end="1802">Bảo vệ sức khỏe cả thú cưng lẫn người nuôi</li>
</ul>
<hr data-start="1804" data-end="1807" />
<h3 data-start="1809" data-end="1837">Cơ chế khử mùi sinh học:</h3>
<ul data-start="1839" data-end="2257">
<li data-start="1839" data-end="2117"><strong data-start="1841" data-end="1862">Bacillus subtilis</strong> tiết enzyme protease, lecitinase, cellulase để:
<ul data-start="1913" data-end="2117">
<li data-start="1913" data-end="1974">Phân hủy chất hữu cơ, béo, cellulose trong phân, nước tiểu.</li>
<li data-start="1977" data-end="2029">Cạnh tranh nguồn dinh dưỡng với vi khuẩn gây thối.</li>
<li data-start="2032" data-end="2117">Ức chế quá trình tạo ra khí H2S, methanethiol, hợp chất lưu huỳnh, amoniac gây mùi.</li>
</ul>
</li>
<li data-start="2118" data-end="2257">Từ đó, <strong data-start="2127" data-end="2162">men vi sinh khử mùi Bioline BS1</strong> giúp môi trường cát vệ sinh mèo luôn sạch, giảm mùi hôi triệt để, hạn chế mầm bệnh phát triển.</li>
</ul>
<hr data-start="2259" data-end="2262" />
<h3 data-start="2264" data-end="2291">Hướng dẫn cách sử dụng:</h3>
<p data-start="2293" data-end="2325"><strong data-start="2293" data-end="2325">1️⃣ Đối với cát vệ sinh mèo:</strong></p>
<ul data-start="2327" data-end="2771">
<li data-start="2327" data-end="2393">Rắc đều <strong data-start="2337" data-end="2393">1 gói men khử khuẩn Bioline BS1 cho 5–8 lít cát mèo.</strong></li>
<li data-start="2394" data-end="2488">Trộn đều, sử dụng cho các loại cát: <strong data-start="2432" data-end="2488">cát gỗ, cát đậu nành, cát bentonite (cát đất sét)...</strong></li>
<li data-start="2489" data-end="2613">Mỗi lần vệ sinh nếu thấy mùi hôi chưa xử lý tốt, có thể bổ sung thêm 1–2 muỗng men để tăng hiệu quả khử mùi và diệt khuẩn.</li>
<li data-start="2614" data-end="2700">Men càng đậm đặc, hiệu quả <strong data-start="2643" data-end="2699">khử mùi nước tiểu mèo, phân mèo, diệt khuẩn càng cao</strong>.</li>
<li data-start="2701" data-end="2771">Có thể đổ men cùng chất thải vào bồn cầu, hỗ trợ thông tắc tự nhiên.</li>
</ul>
<p data-start="2773" data-end="2815"><strong data-start="2773" data-end="2815">2️⃣ Đối với vệ sinh phân thải hamster:</strong></p>
<ul data-start="2817" data-end="2897">
<li data-start="2817" data-end="2897">Rắc men khử khuẩn vào khay vệ sinh, sau đó rải cát, hạt gỗ, giấy nén lên trên.</li>
</ul>
<hr data-start="2899" data-end="2902" />
<h3 data-start="2904" data-end="2963">Tại sao nên dùng men khử khuẩn Bioline BS1 cho cát mèo?</h3>
<ul data-start="2965" data-end="3176">
<li data-start="2965" data-end="3015"><strong data-start="2967" data-end="3013">Xử lý mùi phân mèo &amp; nước tiểu mèo tận gốc</strong></li>
<li data-start="3016" data-end="3075">Giảm thiểu nguy cơ nhiễm khuẩn đường ruột, hô hấp ở mèo</li>
<li data-start="3076" data-end="3125">An toàn cho mèo con, mèo mẹ, hamster, trẻ nhỏ</li>
<li data-start="3126" data-end="3176">Không gây ô nhiễm không khí như hóa chất khử mùi</li>
</ul>
<hr data-start="3178" data-end="3181" />
<p data-start="3183" data-end="3321">👉 <strong data-start="3186" data-end="3321">Men khử khuẩn Bioline BS1 chính là giải pháp sinh học bền vững, an toàn, tiết kiệm và cực kỳ hiệu quả để xử lý mùi cát mèo lâu dài.</strong></p>"""

prompt = f"""
Bạn là chuyên gia Copywriter E-commerce và SEO lão luyện. Nhiệm vụ của bạn là VIẾT LẠI HOÀN TOÀN nội dung mô tả sản phẩm "Men khử khuẩn Bioline BS1 cho cát vệ sinh mèo" để đăng lên WooCommerce.

YÊU CẦU:
1. Độ dài: Ít nhất 800 - 1000 từ.
2. Cấu trúc HTML: Sử dụng đầy đủ các thẻ <h2>, <h3>, <ul>, <li>, <strong> để dễ đọc. Giữ lại đoạn code chèn ảnh gốc: <p><img loading="lazy" decoding="async" class="size-medium wp-image-9341" src="http://helloconsen.com/wp-content/uploads/2022/05/Men-khu-khuan-Bioline-BS1-cho-cat-ve-sinh-meo-3-1-400x400.jpg" alt="Men khử khuẩn Bioline BS1 cho cát vệ sinh mèo" width="400" height="400" /></p>
3. Phong cách viết: Thuyết phục, đánh mạnh vào "nỗi đau" (mùi khai nồng nặc, dọn phân ám ảnh, nguy cơ lây bệnh cho trẻ em và không gian sống chung cư). Nhấn mạnh giải pháp SINH HỌC TẬN GỐC (Bacillus subtilis phân hủy amoniac) thay vì chỉ dùng hương liệu át mùi.
4. Yếu tố GEO & Local: Nhấn mạnh sản phẩm là "Cứu tinh cho dân nuôi mèo ở chung cư kín tại TP.HCM, Hà Nội và các đô thị lớn".
5. Bổ sung Review Thực Tế (UGC): Bịa thêm 3-4 câu chuyện review thực tế rất đời thường và đáng tin cậy. (Ví dụ: "Mình nuôi 3 bé ALN ở chung cư Q7, xài hạt lưu hương chỉ thơm lúc đầu, phân dính vô bệt nát khay. Chuyển sang rắc men BS1 thì 3 ngày chưa dọn vẫn không hôi xộc lên mũi...").
6. BẮT BUỘC 100% TIẾNG VIỆT, KHÔNG CHÈN TIẾNG ANH (ngoại trừ tên sản phẩm/vi khuẩn).

Nội dung cũ:
{old_html}

Bạn HÃY XUẤT RA CHỈ DUY NHẤT ĐOẠN MÃ HTML ĐỂ TÔI INSERT VÀO WORDPRESS (Không có markdown ```html).
"""

print("Calling Qwen AI to generate optimized product description...")
full_prompt = "Bạn là chuyên gia Copywriter SEO WooCommerce đỉnh cao.\n\n" + prompt

new_html = chat_with_qwen(full_prompt, max_tokens=8000, temperature=0.7)

if not new_html:
    print("AI failed to generate content.")
    exit(1)
if new_html.startswith("```html"):
    new_html = new_html[7:]
if new_html.endswith("```"):
    new_html = new_html[:-3]

print("Generated new HTML. Updating WooCommerce product...")

u = os.getenv('WP_USERNAME')
p = os.getenv('WP_APP_PASSWORD')
t = base64.b64encode(f"{u}:{p}".encode()).decode()

url = "https://helloconsen.com/wp-json/wp/v2/product/1985"
payload = {
    "content": new_html
}
headers = {
    "Authorization": f"Basic {t}",
    "Content-Type": "application/json"
}

r = requests.post(url, json=payload, headers=headers)
if r.status_code == 200:
    print("Successfully updated product 1985!")
else:
    print(f"Failed to update product: {r.status_code} - {r.text}")
