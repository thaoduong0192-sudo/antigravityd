# YouTube Studio DOM Selectors (Tested August 2026)

Dưới đây là danh sách toàn bộ DOM selector an toàn dùng để tương tác với YouTube Studio.

## Các Element Chính
- `input[type='file']` — Input file để upload video
- `#title-textarea` nằm trong `ytcp-social-suggestions-textbox` — Nhập tiêu đề video
- `#description-textarea` — Nhập mô tả video
- `VIDEO_MADE_FOR_KIDS_NOT_MFK` — Radio button chọn nội dung không dành cho trẻ em
- `#next-button` — Nút chuyển bước tiếp theo
- `#second-container` — Phần Lên lịch (Schedule) (click để mở)
- `ytcp-video-visibility-select[second-container-style]` — Kiểm tra nếu phần Schedule đang mở (thuộc tính `second-container-style` phải bằng 'selected')
- `#second-container-expand-button` — Nút mở rộng nếu chưa được tự động mở
- `ytcp-datetime-picker tp-yt-paper-input:first` — Input nhập ngày tháng
- `#visibility-title` — Điểm click an toàn để ẩn dropdown ngày tháng (KHÔNG DÙNG phím Escape!)
- `#done-button` — Nút Lưu / Lên lịch (Văn bản sẽ chuyển thành 'Lên lịch' khi chọn schedule)
- `#google-feedback` — Overlay chặn sự kiện click (PHẢI xóa trước khi click nút done)
- `tp-yt-iron-overlay-backdrop` — Lớp nền mờ chặn tương tác (PHẢI xóa)
- Popup 'Đã hiểu' / 'Got it' — Popup xác nhận bắt buộc click sau khi lên lịch thành công
- `ytcp-video-share-dialog` — Hộp thoại share hiện ra sau khi xử lý thành công
- `ytcp-button#close-button` — Nút đóng hộp thoại share

## CẢNH BÁO QUAN TRỌNG (CRITICAL WARNINGS)
- **KHÔNG BAO GIỜ** dùng `force=True` trên `#done-button` (YouTube sử dụng event listeners nội bộ, force sẽ không kích hoạt đúng).
- **KHÔNG BAO GIỜ** dùng phím `Escape` để đóng dropdown (nó sẽ đóng toàn bộ dialog upload!).
- **LUÔN LUÔN** xóa các overlay bằng `page.evaluate()` trước khi click done.
- **LUÔN LUÔN** chờ trạng thái auto-save hoàn tất trước khi click done.
- **LUÔN LUÔN** click xác nhận popup 'Đã hiểu' sau khi hoàn tất click lên lịch.
