---
description: Xem trạng thái tất cả kênh YouTube và chủ đề đang chạy trong hệ thống
---

# Workflow: Xem Trạng Thái Kênh

Khi người dùng gõ `/xem_kenh`:

## Bước 1: Đọc Registry
Đọc file `d:\Antigravity\youtube_notebooklm_elearning\channels_registry.yaml`

## Bước 2: Quét Thư Mục Thực Tế
Với mỗi kênh/chủ đề trong registry, đếm số file `.mp4` trong:
- `topic_dir/long_videos/` (Long videos đã render)
- `topic_dir/short_videos/` (Short videos đã render)
- `topic_dir/uploaded/` (Videos đã upload)

## Bước 3: Hiển Thị Bảng Trạng Thái
Trình bày dưới dạng bảng markdown:

| Kênh | Chủ Đề | Bước Hiện Tại | Long | Short | Uploaded | NotebookLM |
|------|--------|---------------|------|-------|----------|------------|

## Bước 4: Đề Xuất Hành Động
Dựa trên trạng thái, đề xuất hành động tiếp theo cho từng kênh/chủ đề.
