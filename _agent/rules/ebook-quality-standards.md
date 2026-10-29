---
trigger: model_decision
description: Tiêu chuẩn chất lượng xuất bản Ebook (PDF/Markdown) - Chống lỗi font, dính code, định dạng thương mại chuẩn
---

# Tiêu Chuẩn Xuất Bản Ebook Chuẩn Thương Mại (Ebook Quality Standards)

## 1. QUY TẮC BẮT BUỘC VỀ FONT TIẾNG VIỆT (ZERO FONT ERRORS)
- **TUYỆT ĐỐI KHÔNG**: Tải các font web rút gọn (subset) hoặc font không rõ nguồn gốc từ GitHub raw dễ gây lỗi vỡ font tiếng Việt có dấu.
- **LUÔN LUÔN**: Sử dụng trực tiếp bộ font hệ thống Windows chuẩn (`C:\Windows\Fonts\arial.ttf`, `arialbd.ttf`, `ariali.ttf`, `arialbi.ttf` hoặc `C:\Windows\Fonts\times.ttf`, `timesbd.ttf`, `timesi.ttf`, `timesbi.ttf`) để đảm bảo 100% hiển thị đầy đủ dấu tiếng Việt Unicode không bị lỗi ô vuông, đè chữ hay mất dấu.
- **Đăng ký Font Family đầy đủ**: Luôn gọi `registerFontFamily` với đủ 4 biến thể (normal, bold, italic, boldItalic) trong ReportLab.

## 2. QUY TẮC LÀM SẠCH NỘI DUNG (ZERO CODE / MARKDOWN LEAKS)
- **Xử lý triệt để ký tự Markdown**: Toàn bộ nội dung đưa vào PDF PHẢI được parse sạch sẽ:
  - Loại bỏ hoàn toàn dấu backtick (```), thăng (`#`), sao (`*`), gạch nối thô (`---`), dấu lớn (`>`).
  - Chuyển đổi cú pháp in đậm/in nghiêng sang thẻ XML hợp lệ của ReportLab (`<b>`, `<i>`).
  - Escape các ký tự đặc biệt HTML/XML (`&` thành `&amp;`, `<` thành `&lt;`, `>` thành `&gt;`).
- **Không để dính cú pháp kỹ thuật**: Người đọc Ebook là khách hàng/doanh chủ, văn phong phải mượt mà, định dạng đoạn văn rõ ràng, không được để lọt code snippet kỹ thuật, câu lệnh terminal thô hoặc cú pháp lập trình vào nội dung giáo trình/cẩm nang.

## 3. TIÊU CHUẨN ĐỊNH DẠNG EBOOK THƯƠNG MẠI THỰC THỤ (COMMERCIAL GRADE LAYOUT)
- **Trang bìa (Cover Page)**: Đầy đủ Tên tác phẩm, Phụ đề, Đơn vị phát hành, Website chính thức, Phiên bản, khung bản quyền chuyên nghiệp.
- **Trang Mục lục (Table of Contents)**: Trình bày rõ ràng cấu trúc các chương và bài học.
- **Header & Footer tự động (Numbered Canvas)**:
  - Header: Hiển thị tên Cẩm nang / Kênh.
  - Footer: Hiển thị Bản quyền thương hiệu & Số trang dạng `Trang X / Y` (đếm tổng số trang tự động).
- **Hộp điểm nhấn (Callout Box / Key Takeaways)**: Các bài học quan trọng, nguyên tắc founder hoặc lời khuyên chuyên gia phải được đóng khung có màu nền (`#F7FAFC`), viền bo góc hoặc kẻ dọc (`#2B6CB0`) sang trọng.
- **Bảng biểu & Danh sách (Clean Tables & Bullets)**: Bảng biểu so sánh có màu xen kẽ (zebra styling), danh sách gạch đầu dòng căn lề chuẩn (leftIndent, leading hợp lý).
