---
description: Quy trình tự động phân tích bối cảnh, sáng tạo trò chơi 15 phút và gửi Zalo theo đúng khung giờ.
---

# Workflow: Gửi Kịch Bản Chơi Cùng Bư Theo Giờ

## Bước 1: Thu thập Dữ liệu & Ngữ cảnh (Input)
- Đọc thời gian hiện tại để xác định người phụ trách:
  + 08:00 và 19:00 -> Ba Mẹ
  + 11:00 và 15:00 -> Ông Bà Ngoại
- Đọc file `01_Inputs/Ho_so_cua_Bu.md` để nắm nền tảng.
- **BẮT BUỘC** đọc file `01_Inputs/Bao_cao_phat_trien.md` để cập nhật trạng thái mới nhất, thái độ hiện tại của Bư, và các từ khóa đang cần tập trung.
- Đọc `03_Outputs/Lich_su_tro_choi.md` để rà soát 30 ngày qua.

## Bước 2: Sáng tạo Trò chơi (Process)
- Gọi Skill `chuyen-gia-sang-tao-tro-choi-bat-am` để thiết kế MỘT kịch bản trò chơi duy nhất cho khung giờ hiện tại.
- Yêu cầu: Trò chơi kéo dài 15 phút, phải là trò chơi MỚI, không trùng lặp lịch sử, mang tính sáng tạo cao để khơi gợi sự tò mò (Sức học tập) và sự dũng cảm thay đổi của Bư.

## Bước 3: Đóng gói & Lưu trữ (Output)
- Định dạng kết quả theo chuẩn tin nhắn Zalo thân thiện, gọi tên chính xác người phụ trách (Ba Mẹ hoặc Ông Bà).
- Ghi chú tên trò chơi vừa tạo vào file `03_Outputs/Lich_su_tro_choi.md`.
- Trả kết quả cuối cùng ra để hệ thống bắn vào Zalo.
