# Ecopets.vn - Cỗ Máy SEO & Chốt Sale Tự Động Toàn Diện

Hệ thống này không chỉ đơn thuần là phân tích từ khóa, mà là một **"Cỗ máy Bán Hàng 24/7"**. Nó sẽ tự nghĩ từ khóa ngách mỗi ngày, tự viết bài xoáy vào tâm lý chốt sale khách hàng, tự đăng bài, và tự báo cáo **Doanh Thu WooCommerce** mỗi cuối tuần! 

---

## BƯỚC 1: LẮP RÁP PHỤ TÙNG (Chỉ Làm 1 Lần Cả Đời)

👉 Mở thư mục này, nhấp đúp chuột vào file **`cai_dat.bat`** (Hình bánh răng). Để chữ màu trắng chạy nhấp nháy vài phút, đến khi báo "HOAN TAT" thì tắt đi.

---

## BƯỚC 2: KHAI BÁO THÔNG TIN CHUẨN XÁC (Chỉ Làm 1 Lần Cả Đời)

1. Rename (Đổi tên) file **`.env.example`** thành **`.env`**.
2. Mở file `.env` bằng Notepad và hoàn thành 4 mảnh ghép này:
   - **Não bộ AI (Miễn phí 100%)**: `GEMINI_API_KEY` (Lấy dễ dàng tại link: aistudio.google.com/app/apikey).
   - **Quyền Đăng Bài WP**: `WP_USERNAME` và `WP_APP_PASSWORD` (Lấy trong phần Hồ Sơ (Profile) quản trị viên của Ecopets).
   - **Quyền Đọc Doanh Thu WooCommerce**: Để bảng Dashboard biết tháng này bạn kiếm được bao nhiêu tiền, bạn vào Admin WordPress > **WooCommerce** > **Cài đặt** > tab **Nâng cao** > **REST API** > Bấm **Thêm Khóa (Add Key)**. Chọn quyền "Read/Write". Copy đoạn `Consumer Key` dán vào chỗ `WC_CONSUMER_KEY` và `Consumer Secret` dán vào chỗ `WC_CONSUMER_SECRET` trong Notepad.
   - **Báo cáo cuối tuần**: Nhập thông tin Gmail của bạn vào các dòng EMAIL nếu muốn nhận email Chủ Nhật.

---

## BƯỚC 3: KÍCH HOẠT HỆ THỐNG VÀ... ĐI CHƠI!

Bây giờ bạn KHÔNG CẦN đụng tay vào bất kỳ file Excel nào nữa. Toàn bộ quy trình là "Suy nghĩ tự do" và Tự Động!
1. **Nhấp đúp chuột** vào file **`chay_he_thong_tu_dong.bat`**.
2. Một bảng điều khiển đen hiện lên báo "HỆ THỐNG ĐÃ KÍCH HOẠT". Bạn chỉ việc **thu nhỏ** cửa sổ đó xuống dưới thanh trạng thái Taskbar (Bấm nút dấu trừ - ở góc phải). Cứ để máy tính mở và mặc kệ nó chạy ngầm.
3. **Lịch trình cày cuốc của Bot**:
   - **Mỗi Sáng**: Tự phân tích Google Trends tìm 1 từ khóa ngách hái ra tiền -> Tự viết bài chốt sale siêu lôi cuốn -> Tự vẽ ảnh -> Đăng bài lên Dashboard.
   - **Mỗi Chủ Nhật**: Tự động mò vào WooCommerce đọc Tổng Doanh Thu -> Check bài nào đang lên Top -> Ghi vào Data -> Gửi báo cáo Email & Thông báo nổi trên màn hình cho bạn.
4. Muốn xem thành quả? Bất cứ lúc nào hãy click mở file **`dashboard.html`** để ngắm xem Doanh thu và Biểu đồ SEO đang đi lên như thế nào nhé!
