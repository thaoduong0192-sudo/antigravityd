---
name: autonomous-seo-geo-engine
description: >-
  Cỗ máy tăng trưởng SEO và GEO (Generative Engine Optimization) độc lập tự động.
  Quét website thực địa, tạo ma trận silo độc lập, sinh bài viết chuẩn E-E-A-T 13 thành phần (2.500-3.500 từ),
  lấy ảnh bản quyền Pexels, đăng bài tự động lên WordPress và kiểm định điểm chuẩn GEO mà không phụ thuộc Gemini API.
---

# Autonomous SEO & GEO Engine

Hệ thống tăng trưởng nội dung tự động hóa toàn diện cho các website thương hiệu độc lập (đã cấu hình sẵn cho `hoiky.com.vn` và `cryptodataprovn.com`).

## 1. NGUYÊN TẮC CỐT LÕI
1. **Phân tách thực thể 100%:** Tuyệt đối không gộp chung đề tài, persona hay silo giữa các website có phân khúc khác nhau.
2. **Không phụ thuộc API Gemini bên ngoài:** Tự động sinh nội dung E-E-A-T 2.500 – 3.500 từ chuyên sâu thông qua cấu trúc Antigravity Native Generator.
3. **Chuẩn GEO & E-E-A-T 13 thành phần:**
   - Breadcrumb & Badge chứng nhận thực tế.
   - Hộp tóm tắt nhanh AI Overview Direct Answer.
   - Bảng so sánh trực quan (Table).
   - Quy trình giải pháp 4 tầng / bước.
   - Trích dẫn chuyên gia & Lời tựa thương hiệu.
   - Schema `FAQPage` JSON-LD tự động.
   - Ảnh minh họa Pexels phân giải cao kèm Alt text & bản quyền.

---

## 2. DANH MỤC LỆNH VẬN HÀNH

### Quét thực địa & Sinh kế hoạch hành động mới:
```bash
python core/site_scanner.py
```
*Tự động quét trang chủ, meta, chuyên mục, bài viết mẫu của các website và cập nhật `config/silos_<site>.json` kèm báo cáo `reports/action_plan_<site>.md`.*

### Xuất bản bài viết theo batch:
- **Chỉ xuất bản cho hoiky.com.vn:**
  ```bash
  python run_cycle.py --site hoiky --count 1
  ```
- **Chỉ xuất bản cho cryptodataprovn.com:**
  ```bash
  python run_cycle.py --site cryptodatapro --count 1
  ```
- **Chạy song song cả 2 website:**
  ```bash
  python run_cycle.py --site all --count 1
  ```

---

## 3. CẤU TRÚC THƯ MỤC HỆ THỐNG
* `core/site_scanner.py`: Quét website thực địa và sinh Ma trận Silo + Kế hoạch hành động 30 ngày.
* `core/wp_client.py`: Giao tiếp WordPress REST API (Basic Auth Application Password), tự động bypass lỗi DNS.
* `core/pexels_media.py`: Cào ảnh bản quyền miễn phí từ Pexels theo ngữ cảnh từng ngành.
* `core/generator_hoiky.py`: Engine viết bài chuyên sâu cho Hồi ký & Di sản gia đình BE HERITAGE.
* `core/generator_crypto.py`: Engine viết bài phân tích định lượng & Sóng Elliott cho Crypto Data Pro.
* `core/auditor.py`: Bộ kiểm định chất lượng 10 tiêu chí SEO & GEO (chấm điểm /100).
* `reports/`: Lưu trữ Kế hoạch hành động và Báo cáo kiểm định sau mỗi bài đăng.
