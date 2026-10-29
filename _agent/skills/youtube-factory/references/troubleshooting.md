# Hướng dẫn Xử lý Lỗi (Troubleshooting)

Dưới đây là các lỗi thường gặp trong quá trình vận hành YouTube Factory Kit và cách xử lý.

### 1. Video bị lưu dạng 'Bản nháp' thay vì 'Đã lên lịch'
**Nguyên nhân:** YouTube chưa kịp auto-save hoặc script click nút done quá nhanh.
**Xử lý:** Tăng thời gian chờ (wait_for_timeout) hoặc kiểm tra trạng thái auto-save bằng selector `.ytcp-video-metadata-editor-saved`.

### 2. Overlay chặn thao tác click
**Nguyên nhân:** Lỗi `element intercepted` do giao diện phản hồi Google đè lên.
**Xử lý:** Dùng Playwright `page.evaluate()` để xóa các thẻ có id `#google-feedback` và tag `tp-yt-iron-overlay-backdrop` trước khi click nút lưu.

### 3. Phím Escape đóng toàn bộ dialog upload
**Nguyên nhân:** Bấm Escape để tắt hộp chọn ngày tháng.
**Xử lý:** KHÔNG dùng Escape. Thay vào đó, dùng `page.locator('#visibility-title').click()` để đưa focus ra ngoài an toàn.

### 4. `force=True` không có tác dụng
**Nguyên nhân:** Nút Lưu/Lên lịch của YouTube dùng Javascript event gắn trực tiếp vào MouseEvent thay vì trạng thái HTML.
**Xử lý:** Xóa overlay thủ công và để Playwright click tự nhiên (không dùng `force`).

### 5. Lỗi Format Input Ngày tháng
**Nguyên nhân:** Nhập sai format so với locale của account.
**Xử lý:** Với tài khoản US/English, input luôn phải là `MM/DD/YYYY` (ví dụ `08/15/2026`). Với tài khoản Tiếng Việt, có thể là `DD/MM/YYYY`. Mặc định dùng `MM/DD/YYYY`.

### 6. Dropdown Chọn Giờ phức tạp
**Nguyên nhân:** Cấu trúc DOM của input thời gian lồng ghép nhiều Shadow DOM.
**Xử lý:** Dùng phím tắt: Click vào input giờ, gõ số (vd: `10`), thêm `AM` hoặc `PM`, sau đó click ra ngoài `#visibility-title`.

### 7. NotebookLM CLI hết hạn đăng nhập
**Nguyên nhân:** Token cookie hết hạn (thường sau 14 ngày).
**Xử lý:** Chạy lại script `scripts/03_login_notebooklm.bat` để làm mới token.

### 8. Lỗi khóa Chrome Profile (Profile lock errors)
**Nguyên nhân:** Mở nhiều instance Playwright trên cùng 1 profile hoặc chưa đóng trình duyệt thủ công trước đó.
**Xử lý:** Mở Task Manager, End Task tất cả các tiến trình `chrome.exe` rồi chạy lại bot.

### 9. YouTube nhận diện Spam
**Nguyên nhân:** Upload liên tục, hành vi giống bot, IP bị blacklist.
**Xử lý:** Xem [Anti-Spam Guide](./anti_spam_guide.md). Tăng độ trễ, giới hạn dưới 15 video mỗi đợt.
