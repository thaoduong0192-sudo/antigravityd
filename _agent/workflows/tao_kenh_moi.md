---
description: Khởi tạo kênh YouTube mới hoặc thêm chủ đề mới vào kênh đã có — từ phân tích Insight đến upload video tự động
---

# Workflow: Tạo Kênh Mới / Thêm Chủ Đề Mới

Khi người dùng kích hoạt `/tao_kenh_moi`, thực hiện tuần tự:

## Bước 1: Thu Thập 4 Đầu Vào Bắt Buộc
Hỏi người dùng:
1. **Chủ đề kênh** (Channel Topic)
2. **Đối tượng kênh** (Target Audience)  
3. **Mô tả chi tiết chủ đề** (Detailed Description)
4. **Kết quả mong muốn** (Desired Outcome)

Hỏi thêm:
- Đây là **kênh mới** hay **thêm chủ đề mới** vào kênh đã có?
- Nếu kênh đã có: Kênh nào? (liệt kê từ `channels_registry.yaml`)

## Bước 2: Khởi Tạo Thư Mục
```bash
cd d:\Antigravity\youtube_notebooklm_elearning
uv run python -c "from config import get_topic_dir; get_topic_dir('[CHANNEL_INDEX]', '[CHANNEL_ID]', '[TOPIC_INDEX]', '[TOPIC_ID]')"
```

## Bước 3: [CHECKPOINT 1] Phân Tích Insight & Đề Xuất Từ Khóa
- Dùng AI phân tích chuyên sâu 4 đầu vào
- Đề xuất 10 YouTube keywords + 5 Google keywords
- **CHỜ USER DUYỆT** trước khi tiếp tục

## Bước 4: Cào 150 Nguồn YouTube
```bash
uv run python module_1_content_gen.py "[CHỦ ĐỀ]" --topic-dir output_factory/channel_XX_name/topic_XX_name
```

## Bước 5: [CHECKPOINT 2] Gửi Link NotebookLM Để Duyệt Nguồn
- Gửi link NotebookLM cho user kiểm tra chất lượng 150 nguồn
- **CHỜ USER DUYỆT** trước khi render video

## Bước 6: Render Video
```bash
uv run python module_2_3_video_factory.py --topic-dir output_factory/channel_XX_name/topic_XX_name
```

## Bước 7: Upload & Lên Lịch YouTube
```bash
uv run python module_4_youtube_bot.py --topic-dir output_factory/channel_XX_name/topic_XX_name --chrome-profile output_factory/channel_XX_name/chrome_profile --start-date YYYY-MM-DD
```

## Bước 7b: Phân Phối Tự Động Facebook Reels Distributor
```bash
python module_6_facebook_ig_poster.py --topic-dir output_factory/channel_XX_name/topic_XX_name
```
- Phân phối video 9:16 qua Facebook Reels API (`/{page_id}/video_reels`) kích hoạt thuật toán đề xuất Facebook Reels.
- Phân phối video 16:9 qua Facebook Page Videos API (`/{page_id}/videos`).
- Đính kèm bộ Reels Viral Hashtags + Link website + Hook thu hút viewer.


## Bước 8: Cập Nhật Registry
Thêm entry mới vào `channels_registry.yaml` với `current_step: 5`.

## Bước 9: Bật 24/7 Daemon
Hướng dẫn user tạo Windows Task Scheduler chạy `daemon_24_7.py` mỗi 15 phút.
