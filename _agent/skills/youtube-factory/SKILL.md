---
name: youtube-factory
description: >-
  Hệ thống tự động hóa kênh YouTube end-to-end: cào nguồn YouTube, tạo giáo trình qua NotebookLM,
  render video, upload + lên lịch YouTube Studio, gửi email tự động.
  Kích hoạt khi user muốn tạo kênh YouTube tự động, nhân bản kênh, hoặc deploy pipeline lên máy mới.
---

# YouTube Factory Kit

Hệ thống tự động hóa hoàn toàn việc vận hành kênh YouTube từ A-Z.

## Pipeline 5 Module

| Module | Chức năng | Công cụ |
|--------|-----------|--------|
| Module 1 | Cào 150 nguồn YouTube + tạo giáo trình 20 bài + PDF Ebook | yt-dlp, NotebookLM CLI, Gemini API |
| Module 2-3 | Render 20 Long + 100 Short video | NotebookLM Video Studio |
| Module 4 | Upload + lên lịch tự động lên YouTube Studio | Playwright |
| Module 5 | Gửi email Ebook tự động cho leads | Gmail SMTP |

## Cách sử dụng

### Tạo kênh mới trên máy hiện tại
User gõ `/tao_kenh_moi` → Agent hỏi thông tin → chạy pipeline tự động.

### Nhân bản qua máy mới
User gõ `/nhan_ban_may` → Agent đóng gói + hướng dẫn setup máy mới.

### Chạy batch upload tiếp theo
User gõ `/chay_pipeline` → Agent chạy Module 4 upload 15 video tiếp theo.

## Tài liệu tham khảo & Quy trình Thực thi (`references/` & `workflows/`)
- [Setup Guide](./references/setup_guide.md) — Hướng dẫn cài đặt máy mới
- [YouTube Studio DOM](./references/youtube_studio_dom.md) — DOM selectors đã test
- [Troubleshooting](./references/troubleshooting.md) — Xử lý lỗi thường gặp
- [Anti-Spam Guide](./references/anti_spam_guide.md) — Quy tắc chống spam YouTube
- [Workflow: Tạo kênh mới (`/tao_kenh_moi`)](../../workflows/tao_kenh_moi.md) — Quy trình 9 bước khởi tạo kênh & chủ đề mới
- [Workflow: Tạo giáo trình (`/tao_giao_trinh`)](../../workflows/tao_giao_trinh.md) — Quy trình sinh giáo trình 20 bài & PDF Ebook
- [Workflow: Chạy pipeline (`/chay_pipeline`)](../../workflows/chay_pipeline.md) — Chạy batch upload 15 video tiếp theo
- [Workflow: Nhân bản máy (`/nhan_ban_may`)](../../workflows/nhan_ban_may.md) — Đóng gói & triển khai sang máy mới
- [Workflow: Xem kênh (`/xem_kenh`)](../../workflows/xem_kenh.md) — Kiểm tra trạng thái danh sách kênh trong registry

## Cấu trúc thư mục
```
youtube-factory-kit/
├── scripts/          # Setup scripts
├── templates/        # Config templates
├── references/       # Tài liệu kỹ thuật
└── pipeline/         # Source code pipeline (copy từ youtube_notebooklm_elearning)
```
