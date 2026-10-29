---
description: Tự động hóa quy trình cào 150 nguồn YouTube, tạo NotebookLM, sinh 20 chủ đề con bài học và render 20 video học thuật (Tiếng Việt).
---

# Workflow: Tạo Khóa Học 20 Video Chuyên Sâu với NotebookLM

Khi người dùng kích hoạt lệnh này với một chủ đề (ví dụ: `/tao_giao_trinh [chủ đề]`), hãy thực hiện chính xác tuần tự các bước sau. **Không được bỏ qua bất kỳ bước nào.**

## Bước 1: Cào 150 Nguồn YouTube Uy Tín
- Chạy lệnh sau để trích xuất 150 video YouTube uy tín và lưu vào file `urls.txt`:
  ```bash
  cd d:\Antigravity\youtube_notebooklm_elearning
  python -c "from modules.youtube_scraper import YouTubeScraper; import sys; scraper = YouTubeScraper(max_results=150); videos = scraper.scrape_and_process(sys.argv[1]); open('urls.txt', 'w', encoding='utf-8').write('\n'.join([v['url'] for v in videos]))" "[CHỦ ĐỀ CỦA NGƯỜI DÙNG]"
  ```
- Nếu lệnh chạy thất bại, hãy báo lỗi cho người dùng. Nếu thành công, chuyển sang bước 2.

## Bước 2: Chạy Python Tổng Chỉ Huy 20 Video
- Gọi script tổng chỉ huy để thực hiện chuỗi quy trình tạo Sổ, nạp dữ liệu và bóc tách thành 20 chủ đề con:
  ```bash
  python course_generator.py "[CHỦ ĐỀ CỦA NGƯỜI DÙNG]"
  ```
- Lệnh này sẽ chạy mất khoảng 10-15 phút do phải giao tiếp nhiều lần với AI và tạo 20 ghi chú (Note) cùng 20 tác vụ render video (Studio).

## Bước 3: Trả Kết Quả Về Cho Người Dùng
- Kịch bản sẽ in ra Link NotebookLM. Bạn hãy copy link này và báo cho người dùng biết quá trình phân rã 20 video đã kích hoạt thành công.
- Dặn dò người dùng: "Khóa học 20 bài đã được lên dàn ý và lưu thành 20 Ghi chú. Hệ thống đang tiến hành render 20 Video bài giảng ngầm trên server, mỗi video tương ứng với 1 chủ đề con. Bạn có thể mở link để xem kết quả!"
