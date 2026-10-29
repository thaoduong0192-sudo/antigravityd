---
description: Chạy batch upload tiếp theo cho kênh YouTube hiện tại
---

# Chạy Pipeline Upload Tiếp Theo

## Bước 1: Kiểm tra trạng thái
- Đếm video còn lại trong output_factory/long_videos/ và output_factory/short_videos/
- Báo cáo: đã upload bao nhiêu, còn lại bao nhiêu

## Bước 2: Chạy Module 4
- Chạy `uv run python module_4_youtube_bot.py`
- Bot tự động upload tối đa 15 video và lên lịch

## Bước 3: Báo cáo kết quả
- Kiểm tra log output
- Báo cáo số video đã lên lịch thành công
- Nhắc user chạy lại nếu còn video
