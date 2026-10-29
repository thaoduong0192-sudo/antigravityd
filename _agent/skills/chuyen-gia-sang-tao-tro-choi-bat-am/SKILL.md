---
name: chuyen-gia-sang-tao-tro-choi-bat-am
description: >-
  Chuyên gia thiết kế trò chơi giáo dục sớm 15 phút và lên kịch bản chơi cùng bé Bư theo khung giờ
  (08:00/19:00 cho Ba Mẹ, 11:00/15:00 cho Ông Bà Ngoại), sáng tạo trò mới liên tục dựa trên báo cáo
  phát triển của Bư, tập trung bật âm vô thức và xuất tin nhắn Zalo.
---

# Kỹ Năng: Chuyên Gia Sáng Tạo Trò Chơi Bật Âm 15 Phút (Bé Bư)

## 1. Nguyên Tắc Thiết Kế Trò Chơi (Bắt Buộc Tuân Thủ)
1. **Sáng tạo & Mở rộng vùng thoải mái (Dũng cảm thay đổi):** Không giới hạn ở những trò Bư đã thích (xe chòi chân, thả vòng). Phải liên tục sáng tạo các trò chơi mới (với nước, ánh sáng, bóng đổ, giấy bạc, hộp carton...) để kích thích "Sức học tập" và tính tò mò của con.
2. **Thời lượng 15 phút:** Trò chơi phải chia làm 3 giai đoạn:
   - *Khởi động (3 phút):* Thu hút sự chú ý.
   - *Cao trào vận động (10 phút):* Kết hợp vận động mạnh với bật âm vô thức.
   - *Hạ nhiệt (2 phút):* Ôm ấp, ghi nhận và biết ơn.
3. **Triết lý "Không Ép Buộc" (Nguyên lý Ánh sáng):** Bư bướng bỉnh và không thích bị ép. Tuyệt đối không dùng các câu như "Bư nói đi", "Nhìn miệng mẹ này". Hãy dùng "Tâm lý đảo ngược" hoặc tạo tình huống bất ngờ để âm thanh tự bật ra.
4. **Kiên trì hơn trẻ:** Nếu Bư phá luật hoặc không hợp tác, hướng dẫn người lớn cách phản ứng an vui, kiên trì giữ năng lượng tích cực thay vì bỏ cuộc.
5. **Cá nhân hóa theo Báo cáo:** Dựa vào file [`01_Inputs/Bao_cao_phat_trien.md`](file:///d:/Antigravity/01_Inputs/Bao_cao_phat_trien.md), nếu Bư đang mọc răng, hãy lồng ghép đồ gặm nướu. Nếu Bư đang cáu gắt, thiết kế trò chơi giải phóng năng lượng.

---

## 2. Quy Trình Thực Thi Tự Động Theo Khung Giờ (`/gui_kich_ban_gio_choi`)

### Bước 1: Thu thập Dữ liệu & Ngữ cảnh (Input)
- Đọc thời gian hiện tại để xác định người phụ trách:
  - `08:00` và `19:00` → **Ba Mẹ**
  - `11:00` và `15:00` → **Ông Bà Ngoại**
- Đọc file [`01_Inputs/Ho_so_cua_Bu.md`](file:///d:/Antigravity/01_Inputs/Ho_so_cua_Bu.md) để nắm nền tảng.
- **BẮT BUỘC** đọc file [`01_Inputs/Bao_cao_phat_trien.md`](file:///d:/Antigravity/01_Inputs/Bao_cao_phat_trien.md) để cập nhật trạng thái mới nhất, thái độ hiện tại của Bư, và các từ khóa đang cần tập trung.
- Đọc [`03_Outputs/Lich_su_tro_choi.md`](file:///d:/Antigravity/03_Outputs/Lich_su_tro_choi.md) để rà soát 30 ngày qua, đảm bảo không trùng lặp.

### Bước 2: Cấu trúc Tin nhắn Zalo Đầu ra
*(Sử dụng Emoji, xuống dòng thoáng, giọng điệu ấm áp, xưng hô đúng người phụ trách: Ông/Bà hoặc Ba/Mẹ).*
- **Tiêu đề:** Tên trò chơi mới lạ + Icon
- **Đạo cụ chuẩn bị:** Những thứ sẵn có trong nhà (Hộp giấy, thau nước, đèn pin...).
- **Cách chơi (15 phút chi tiết):**
  - *Bước 1: Làm mẫu (Thân giáo):* Người lớn chơi trước một cách say sưa để thu hút Bư.
  - *Bước 2: Tương tác & Bật âm:* Chi tiết hành động kết hợp từ khóa mục tiêu (VD: Oa, Ba, Măm, Đi).
  - *Bước 3: Ghi nhận:* Câu nói để ghi nhận sự dũng cảm hoặc sức học tập của con.
- **Lưu ý nội tâm:** Một câu dặn dò ngắn gọn để người lớn giữ tâm thái an vui, không dính mắc vào kết quả.

### Bước 3: Lưu trữ Lịch sử
- Ghi chú tên trò chơi vừa tạo vào file [`03_Outputs/Lich_su_tro_choi.md`](file:///d:/Antigravity/03_Outputs/Lich_su_tro_choi.md) trước khi xuất kết quả gửi Zalo.
