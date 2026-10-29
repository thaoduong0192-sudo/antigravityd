---
description: Đóng gói YouTube Factory Kit và hướng dẫn deploy lên máy mới
---

# Nhân Bản Qua Máy Mới

## Bước 1: Đóng gói trên máy gốc
- Tạo thư mục youtube-factory-kit/
- Copy toàn bộ:
  - _agent/skills/youtube-factory/ → kit/skill/
  - _agent/rules/youtube-factory-rules.md → kit/rules/
  - _agent/rules/multi-channel-safety.md → kit/rules/
  - _agent/workflows/tao_kenh_moi.md → kit/workflows/
  - _agent/workflows/chay_pipeline.md → kit/workflows/
  - _agent/workflows/nhan_ban_may.md → kit/workflows/
  - youtube_notebooklm_elearning/*.py → kit/pipeline/
  - youtube_notebooklm_elearning/modules/ → kit/pipeline/modules/
  - youtube_notebooklm_elearning/requirements.txt → kit/
- KHÔNG copy: chrome_profile_bot/, .env, output_factory/
- Nén thành youtube-factory-kit.zip

## Bước 2: Chuyển sang máy mới
- Copy ZIP qua USB / Google Drive / GitHub private repo
- Giải nén vào thư mục làm việc

## Bước 3: Cài đặt trên máy mới
### Tự động (chạy script):
```powershell
powershell -ExecutionPolicy Bypass -File scripts/01_install_dependencies.ps1
```

### Thủ công (BẮT BUỘC — 3 bước):
1. Chạy `scripts/03_login_notebooklm.bat` → Đăng nhập Google cho NotebookLM
2. Chạy `scripts/04_login_youtube.bat` → Đăng nhập YouTube Studio
3. Vào https://myaccount.google.com → Security → App Passwords → tạo password → điền vào .env

## Bước 4: Cài Antigravity
- Cài Antigravity IDE/CLI trên máy mới
- Copy thư mục _agent/ vào project root
- Verify: skills, rules, workflows xuất hiện trong Antigravity

## Bước 5: Tạo kênh và chạy
- Gõ `/tao_kenh_moi` để tạo kênh mới
- Hoặc gõ `/chay_pipeline` nếu đã có video sẵn
