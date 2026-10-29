# Hướng dẫn Cài đặt YouTube Factory trên Máy Mới

## Yêu cầu cơ bản (Prerequisites)
- **Hệ điều hành**: Windows 10/11
- **Google Chrome**: Cài đặt đường dẫn mặc định
- **Python**: Phiên bản 3.10 trở lên
- **UV**: Python package manager
- **Antigravity**: Đã được cài đặt và thiết lập workspace

## Cài đặt Python Packages
Chạy danh sách các package sau thông qua UV hoặc pip:
- `google-generativeai`
- `youtube-transcript-api`
- `yt-dlp`
- `requests`
- `pydantic`
- `rich`
- `playwright`
- `python-dotenv`
- `reportlab`
- `pywin32`
- `cryptography`
- `fastapi`
- `uvicorn`
- `notebooklm-cli`

## Cài đặt Playwright
Playwright cần chromium browser để chạy, hãy chạy lệnh:
`playwright install chromium`

## Đăng nhập thủ công bắt buộc (3 bước)
1. **NotebookLM CLI**: Chạy `nlm login` để xác thực với Google.
2. **YouTube Studio**: Chạy script `Login_YouTube_Bot.bat` để tạo profile Chrome mới và đăng nhập YouTube bằng tài khoản upload. Đóng trình duyệt sau khi đăng nhập xong.
3. **Gmail SMTP**: Tạo App Password cho tài khoản Gmail muốn dùng ở Module 5 (Auto Mailer). Điền vào file `.env`.

## Cấu hình Kênh
1. Copy file `channel_config.yaml` từ thư mục templates.
2. Chỉnh sửa thông tin tên kênh, nội dung, lịch đăng bài, v.v.

## Chuẩn bị Nguồn Tài liệu
Chuẩn bị sẵn các từ khóa (queries) hoặc file PDF, Docs để dùng cho Module 1 (Tạo content).

## Xác minh cài đặt
Kiểm tra từng module hoạt động độc lập bằng các command sau:
- Module 1: `uv run python module_1_content_gen.py`
- Playwright: `uv run playwright install`
- Env variables: `type .env`
