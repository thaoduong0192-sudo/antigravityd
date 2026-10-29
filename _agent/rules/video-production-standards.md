---
trigger: model_decision
description: Tiêu chuẩn sản xuất Video Shorts chuyển động Remotion, âm thanh Neural 1.2x và đồ họa thương mại cho toàn bộ dự án
---

# Tiêu Chuẩn Sản Xuất Video Shorts Chuyển Động (Video Production Standards)

## 1. TIÊU CHUẨN ÂM THANH & GIỌNG ĐỌC AI (AUDIO / TTS)
- **Engine Bắt Buộc**: Sử dụng 100% Microsoft Neural Voice (`vi-VN-NamMinhNeural` cho giọng nam doanh nhân quyền lực / `vi-VN-HoaiMyNeural` cho giọng nữ sắc bén).
- **Tốc Độ Đọc (Speed / Rate)**: LUÔN cài đặt `rate='+20%'` (Tốc độ 1.2x). Tiết tấu dứt khoát, nhanh, cuốn hút, tối ưu tỷ lệ giữ chân người xem (Retention Rate) trên YouTube Shorts / TikTok / Reels.
- **Xử Lý Kỹ Thuật Windows**: Khởi tạo bằng `aiohttp.connector.DefaultResolver = aiohttp.resolver.ThreadedResolver` để tránh lỗi DNS trên Windows.
- **Biên Soạn Lời Thoại**: Viết câu có ngắt nghỉ rõ ràng bằng dấu phẩy, dấu chấm, phiên âm số và thuật ngữ (`năm bước`, `chống giả`, `con-ten chấm bờ-lu chấm a-i chấm vi-en`) để không bị nuốt chữ.

## 2. TIÊU CHUẨN HÌNH ẢNH & TYPOGRAPHY (VISUAL & FONTS)
- **Độ Phân Giải Chuẩn**: Khổ dọc 9:16 (`1080 x 1920`), 30 fps, H.264 CRF 18 xuất xưởng sắc nét.
- **Font Chữ Hệ Thống**: 100% dùng font Windows gốc (`C:\Windows\Fonts\arialbd.ttf`, `arial.ttf`, `timesbd.ttf`) để không bao giờ bị lỗi font tiếng Việt.
- **Quy Tắc Phụ Đề**: **KHÔNG sinh phụ đề đè (No Subtitle Burning)** lên video để tránh rủi ro vỡ font và không che khuất các thẻ đồ họa chuyển động.
- **Bảng Màu Thương Hiệu**: Nền Dark Navy (`#0F172A`), Header/Footer Slate (`#1E293B`), Điểm nhấn Vàng Cam Amber (`#F59E0B`), Neon Blue (`#3B82F6`), Success Green (`#22C55E`), Alert Red (`#DC2626`).

## 3. TIÊU CHUẨN HIỆU ỨNG CHUYỂN ĐỘNG REMOTION (MOTION GRAPHICS & PHYSICS)
- **Thanh Tiến Trình Động (Dynamic Progress Bar)**: Đặt ở đỉnh video, lấp đầy mượt mà từ 0% đến 100% theo thời gian thực kèm điểm sáng dẫn đường.
- **Hạt Bụi Sáng Lơ Lửng (Floating Particles)**: 50 - 60 hạt sáng chuyển động trôi nhẹ nhàng với độ mờ và bán kính thay đổi theo hàm `sin(t)`.
- **Vật Lý Bật Nảy Đàn Hồi (Spring & Ease-Out-Back Physics)**:
  - Các Warning Badge và Tiêu đề Hook trượt từ 2 bên hoặc nảy lò xo vào tâm khung hình.
  - Các Thẻ Bước 1 đến Bước 5 xuất hiện tuần tự (Staggered Card Reveals) theo đúng nhịp nói của giọng đọc.
- **Phân Cảnh Kêu Gọi Hành Động (CTA Scene - 10-15s Cuối)**:
  - Các dòng tính năng/lợi ích trượt vào lần lượt với dấu tick xanh lá.
  - Nút CTA chuyển động nhịp thở (`1.0 + 0.03 * sin(t * 6)` - Breathing Pulse Effect).
  - Viền Neon phát sáng làm nổi bật thông tin dịch vụ và website: **`https://content.blue.ai.vn/`**.
