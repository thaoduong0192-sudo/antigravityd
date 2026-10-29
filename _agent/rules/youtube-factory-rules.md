---
trigger: model_decision
description: Quy tắc vận hành YouTube Factory pipeline
---

# Quy tắc YouTube Factory

## Giới hạn an toàn YouTube
- Tối đa 15 video upload mỗi lần chạy bot
- Chờ ít nhất 4-6 giờ giữa các lần chạy trên cùng 1 kênh
- Mỗi IP chỉ chạy tối đa 3 kênh YouTube
- Mỗi kênh = 1 Chrome profile riêng biệt, KHÔNG BAO GIỜ chia sẻ

## Quy tắc NotebookLM
- Mỗi kênh tạo 1 notebook riêng trên NotebookLM
- Không chạy quá 5 video render song song
- Kiểm tra `nlm login` status trước khi chạy pipeline

## Quy tắc YouTube Studio Automation
- KHÔNG dùng `force=True` khi click nút Lên lịch
- KHÔNG dùng phím `Escape` trong dialog upload
- LUÔN xóa overlay `#google-feedback` trước khi click
- LUÔN chờ auto-save xong trước khi submit
- LUÔN bấm nút 'Đã hiểu' sau khi lên lịch

## Quy tắc Đầu vào & Điểm Duyệt (User Approval Checkpoints)
- **Đầu vào bắt buộc 4 tham số**:
  1. `Chủ đề kênh` (Channel Topic)
  2. `Đối tượng kênh` (Target Audience)
  3. `Mô tả chi tiết chủ đề` (Detailed Niche Description)
  4. `Kết quả mong muốn` (Desired Outcome/Goal)
- **Điểm Duyệt 1 (Approval Checkpoint 1)**: Sau khi phân tích Insight chuyên sâu, hệ thống PHẢI đề xuất danh sách Từ khóa Tìm kiếm (YouTube + Google) và CHỜ USER DUYỆT trước khi bắt đầu cào nguồn!
- **Điểm Duyệt 2 (Approval Checkpoint 2)**: Sau khi cào 150 nguồn và tạo NotebookLM, hệ thống PHẢI gửi Link NotebookLM cho USER KIỂM TRA NGUỒN UY TÍN và CHỜ USER DUYỆT mới được bắt đầu render Ebook và Video (Long + Short)!

## Quy tắc Facebook Fanpage & Instagram Reels Automation
- Tối đa 15-20 video lên lịch cho mỗi đợt chạy bot (tương đương 5-7 ngày) để tránh spam
- Lên lịch rải đều 3 khung giờ/ngày: 08:00 (Short), 12:00 (Short), 19:00 (Long Lesson)
- Tự động đăng chéo sang Instagram Reels bằng `crosspost_to_instagram: true`
- Tự động để lại Auto-Comment từ chính Fanpage/Instagram để CTA / bổ sung thông tin
- Khi gặp Meta API Rate Limit, LUÔN tạm dừng (cooldown) ít nhất 60 phút

## Quy tắc đa máy
- Mỗi máy mới PHẢI login thủ công: NotebookLM + YouTube + Gmail
- KHÔNG copy chrome_profile giữa các máy
- Mỗi máy chạy tối đa 3 kênh tuần tự
- Dùng VPN/Proxy khác nhau cho mỗi cụm 3 kênh

## Quy tắc Sản Xuất Video Shorts (Remotion Motion Graphics & Neural Voice)
- **Âm thanh**: 100% dùng Microsoft Neural Voice (`vi-VN-NamMinhNeural` / `vi-VN-HoaiMyNeural`) với tốc độ tăng x1.2 (`rate='+20%'`) để dứt khoát, lôi cuốn, không rớt chữ.
- **Hình ảnh & Font**: Dùng 100% font hệ thống Windows (`C:\Windows\Fonts\arialbd.ttf` / `arial.ttf`). **KHÔNG sinh phụ đề đè** để tránh lỗi font.
- **Chuyển động Remotion**: Đầy đủ thanh tiến trình động (Progress Bar), hạt sáng lơ lửng, hiệu ứng nảy đàn hồi (Spring / Ease-Out-Back), thẻ bài xuất hiện tuần tự theo giọng đọc.
- **Kêu gọi hành động (10-15s Cuối)**: Nút CTA chuyển động nhịp thở (Breathing Pulse) và viền Neon làm nổi bật đường dẫn dịch vụ: `https://content.blue.ai.vn/`.

## Quy tắc Xuất Bản Ebook Chuẩn Thương Mại
- Dày từ 60+ đến 120+ trang với đầy đủ 120 bài học, bảng phân tích, tình huống thực tế và kịch bản video.
- Sử dụng font Windows Arial/Times không vỡ chữ tiếng Việt, đánh số trang động `Trang X / Y` (NumberedCanvas) và tuyệt đối không dính mã code kỹ thuật.
