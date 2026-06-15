import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_API_URL = "https://ecopets.vn/wp-json/wp/v2/posts"

SLUG = "si-phu-kien-thu-cung-tphcm-thiet-ke-quay-thu-ngan-de-giu-chan-73-khach"
TITLE = "Sỉ Phụ Kiện Thú Cưng TPHCM: Thiết Kế Quầy Thu Ngân Để Giữ Chân 73% Khách"

HTML_CONTENT = """
<p>Trong ngành kinh doanh thú cưng đầy cạnh tranh hiện nay, việc tìm kiếm nguồn <strong>sỉ phụ kiện thú cưng TPHCM</strong> giá tốt chỉ là bước đầu. Để thực sự tạo ra lợi nhuận và xây dựng tệp khách hàng trung thành, bạn cần tối ưu hóa từng điểm chạm trong cửa hàng của mình. Đáng ngạc nhiên thay, khu vực quầy thu ngân lại chính là "vũ khí bí mật" quyết định đến trải nghiệm cuối cùng của người mua.</p>

<p>Theo các nghiên cứu về hành vi tiêu dùng, một quầy thu ngân được thiết kế khoa học và chuyên nghiệp có khả năng <strong>giữ chân tới 73% khách hàng</strong> quay trở lại. Vậy làm thế nào để biến khu vực tính tiền của pet shop trở thành cỗ máy chốt sale và tạo thiện cảm tối đa?</p>

<h2>1. Tại sao quầy thu ngân lại quyết định 73% tỷ lệ quay lại của khách hàng?</h2>
<p>Quầy thu ngân không chỉ là nơi để trao đổi tiền bạc. Đó là điểm dừng chân cuối cùng của khách hàng trước khi rời đi, là nơi lưu lại ấn tượng mạnh mẽ nhất về dịch vụ của cửa hàng.</p>
<ul>
<li><strong>Tâm lý mua hàng bốc đồng (Impulse Buying):</strong> Trong lúc chờ thanh toán, khách hàng thường có xu hướng dễ dàng chi thêm tiền cho những món đồ nhỏ, tiện ích hoặc bắt mắt.</li>
<li><strong>Trải nghiệm dịch vụ:</strong> Một quầy thu ngân lộn xộn, nhân viên chậm chạp sẽ phá hỏng toàn bộ trải nghiệm mua sắm tuyệt vời trước đó. Ngược lại, sự gọn gàng, thơm tho và quy trình nhanh chóng sẽ tạo ra sự hài lòng tuyệt đối.</li>
<li><strong>Điểm nhấn thương hiệu:</strong> Đây là nơi hoàn hảo để bạn truyền tải thông điệp kinh doanh, ví dụ như mô hình "Trạm dinh dưỡng xanh" hay các chương trình thẻ thành viên.</li>
</ul>

<h2>2. Bí quyết thiết kế quầy thu ngân "hái ra tiền" cho Pet Shop</h2>
<p>Nếu bạn đang lấy sỉ phụ kiện thú cưng TPHCM và chuẩn bị setup cửa hàng, hãy áp dụng ngay 4 nguyên tắc thiết kế quầy thu ngân dưới đây:</p>

<h3>2.1. Trưng bày sản phẩm "Cross-sell" (Bán chéo) chiến lược</h3>
<p>Khu vực quanh máy tính tiền là "mảnh đất vàng" để trưng bày các sản phẩm nhỏ gọn, giá rẻ và dễ kích thích nhu cầu tức thời.</p>
<ul>
<li><strong>Sản phẩm gợi ý:</strong> Bánh thưởng (treats), xương gặm sạch răng, cỏ mèo (catnip), đồ chơi nhỏ, hoặc các túi khăn ướt lau mắt cho chó mèo.</li>
<li><strong>Mẹo:</strong> Đừng chất đống quá nhiều. Hãy sắp xếp chúng gọn gàng vào các khay mica trong suốt hoặc kệ gỗ nhỏ ngang tầm mắt khách hàng.</li>
</ul>

<h3>2.2. Tích hợp "Trạm dinh dưỡng mini" ngay tại quầy</h3>
<p>Nếu định hướng của bạn là cung cấp các sản phẩm chăm sóc sức khỏe toàn diện, hãy biến một góc quầy thu ngân thành không gian tư vấn dinh dưỡng thu nhỏ. Đặt các mẫu thử nghiệm (sample) của dòng hạt cao cấp hoặc thực phẩm bổ sung, kèm theo một vài cuốn cẩm nang chăm sóc sức khỏe. Khách hàng sẽ cảm thấy họ nhận được giá trị chuyên gia chứ không chỉ là mua bán đơn thuần.</p>

<h3>2.3. Ánh sáng và màu sắc thân thiện</h3>
<p>Khu vực thanh toán cần có ánh sáng sáng sủa nhưng ấm áp. Tránh sử dụng đèn huỳnh quang quá chói. Sử dụng các gam màu gỗ tự nhiên hoặc màu xanh lá cây để tạo cảm giác gần gũi, sạch sẽ – điều cực kỳ quan trọng đối với một cửa hàng bán đồ cho thú cưng.</p>

<h3>2.4. Khu vực chờ thoải mái cho thú cưng</h3>
<p>Đừng quên rằng khách hàng thường bế theo "boss" khi thanh toán. Thiết kế quầy thu ngân với một mặt bàn đủ rộng, không trơn trượt để khách có thể đặt giỏ xách hoặc thú cưng lên tạm thời. Một lọ xịt khử mùi hoặc một đĩa nhỏ đựng bánh thưởng miễn phí trên bàn thu ngân sẽ ghi điểm tuyệt đối trong mắt khách hàng.</p>

<h2>3. Nguồn nhập sỉ phụ kiện thú cưng TPHCM tối ưu cho khu vực thu ngân</h2>
<p>Để chiến lược "upsell" tại quầy thành công, bạn cần chọn đúng sản phẩm. Khi tìm các tổng kho sỉ phụ kiện thú cưng TPHCM, hãy đặc biệt chú ý săn lùng các mặt hàng sau để đặt tại quầy:</p>
<ul>
<li><strong>Phụ kiện làm đẹp tiện lợi:</strong> Lược chải lông mini, kẹp nơ, dây dắt thiết kế độc lạ.</li>
<li><strong>Snack & Treat size nhỏ:</strong> Các gói bánh thưởng dùng thử, pate gói nhỏ, xúc xích cho chó mèo.</li>
<li><strong>Sản phẩm vệ sinh thiết yếu:</strong> Xịt khử mùi hôi miệng, dung dịch nhỏ tai, túi nilon nhặt phân.</li>
</ul>
<p>Những sản phẩm này có đặc điểm chung là: <strong>Giá vốn thấp - Lợi nhuận biên cao - Dễ dàng quyết định mua ngay lập tức.</strong></p>

<h2>4. Tổng kết</h2>
<p>Việc nhập sỉ phụ kiện thú cưng TPHCM với giá rẻ sẽ giúp bạn có lợi thế cạnh tranh về giá, nhưng chính cách bạn thiết kế không gian – đặc biệt là quầy thu ngân – mới là yếu tố <strong>giữ chân 73% khách hàng</strong>. Hãy biến khu vực thanh toán thành một điểm nhấn tinh tế, gọn gàng và đầy ắp những "cám dỗ" ngọt ngào để tối đa hóa doanh thu cho Pet Shop của bạn.</p>
"""

def main():
    print(f"Đang kiểm tra bài viết với slug: {SLUG}")
    search_url = f"{WP_API_URL}?slug={SLUG}&status=publish,draft,trash,private"
    auth = (WP_USERNAME, WP_APP_PASSWORD)
    
    resp = requests.get(search_url, auth=auth)
    posts = resp.json()
    
    headers = {"Content-Type": "application/json"}
    data = {
        "title": TITLE,
        "content": HTML_CONTENT,
        "slug": SLUG,
        "status": "publish",
        "categories": [1] # Adding a default category just in case
    }
    
    if posts and isinstance(posts, list) and len(posts) > 0:
        post_id = posts[0]['id']
        print(f"Đã tìm thấy bài viết ID {post_id}. Đang cập nhật nội dung...")
        update_url = f"{WP_API_URL}/{post_id}"
        r = requests.post(update_url, auth=auth, headers=headers, json=data)
        if r.status_code == 200:
            print(f"Cập nhật thành công! Link: {r.json().get('link')}")
        else:
            print(f"Lỗi cập nhật: {r.status_code} - {r.text}")
    else:
        print("Không tìm thấy bài viết, tiến hành tạo mới...")
        r = requests.post(WP_API_URL, auth=auth, headers=headers, json=data)
        if r.status_code == 201:
            print(f"Tạo mới thành công! Link: {r.json().get('link')}")
        else:
            print(f"Lỗi tạo mới: {r.status_code} - {r.text}")

if __name__ == "__main__":
    main()
