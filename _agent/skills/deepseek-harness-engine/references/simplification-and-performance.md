# Tinh Gọn Kiến Trúc, Tối Ưu Hiệu Năng & Chuẩn Hóa Ngôn Từ

Tổng hợp từ 4 skill nâng cao của **DeepSeek Harness (`dsh`)**: `dsh-find-simplifications`, `dsh-speed-up-perf`, `dsh-trim-cot-leakage`, và `dsh-prose-standard`.

---

## PHẦN 1: Tìm & Cắt Bỏ Gánh Nặng Bảo Trì (`dsh-find-simplifications`)

Mục tiêu là tìm những thay đổi giúp **loại bỏ hoàn toàn nghĩa vụ phải bảo trì** (API thừa, trạng thái thừa, đường dẫn cấu hình không ai dùng, bản sao dữ liệu dư thừa) thay vì chỉ đổi tên hay di chuyển code.

### 5 Câu hỏi truy vết để tìm điểm tinh gọn:
1. **Tính năng được khai báo có đường dẫn tác động hoàn chỉnh không?**
   - Lần từ nơi sinh dữ liệu (producer) → các bước biến đổi → nơi tiêu thụ (consumer) → kết quả quan sát được. Một trường dữ liệu được copy qua 5 tầng nhưng cuối cùng không có nơi nào đọc hoặc bị ghi đè trước khi dùng là ứng viên cần dọn bỏ.
2. **Sự phân biệt trạng thái này có làm thay đổi hành động của bên nhận không?**
   - Nếu 4 trạng thái nội bộ khác nhau đều dẫn tới cùng một hành động duy nhất ở phía người dùng/consumer, hãy gộp chúng lại ở biên giao tiếp.
3. **Consumer có thể đọc trực tiếp từ nguồn chính thống khi cần thay vì tự lưu bản sao (cache/ledger) riêng không?**
   - Việc đọc trực tiếp hoặc dẫn xuất (derive) từ một nguồn duy nhất giúp xóa bỏ cùng lúc cả bộ nhớ đệm, sự kiện làm mới (invalidation), lỗi dữ liệu cũ (stale state) và logic khôi phục.
4. **Một hành vi tường minh nhỏ gọn hơn có thể thay thế cả một hệ thống con phức tạp không?**
   - Đánh giá chi phí bảo trì toàn bộ hệ thống cũ so với giải pháp thay thế (tính cả lớp keo nối - residual glue).
5. **Chứng minh bằng tìm kiếm thực tế (`rg`):**
   - Trước khi xóa bất kỳ hàm, biến hay cấu hình nào, bắt buộc dùng `rg` quét toàn bộ mã nguồn, cấu hình động, template và script để phân biệt rõ:
     - *Hành vi chết hoàn toàn không nơi nào chạm tới* (An toàn để xóa).
     - *Hành vi thu hẹp có đánh đổi tính năng* (Phải hỏi ý kiến người dùng trước).
     - *Điểm mở rộng có chủ đích hoặc tính năng đã duyệt trong quy tắc bảo toàn* (Tuyệt đối giữ nguyên).

---

## PHẦN 2: Tối Ưu Hóa Hiệu Năng Có Đo Đạc (`dsh-speed-up-perf`)

Biến yêu cầu chung chung *"làm cho nó chạy nhanh hơn"* thành các phép đo tái lập được trên luồng người dùng thực tế và các bản sửa nhỏ có bằng chứng trước/sau.

### 1. Lập Thẻ Đo Đạc (Measurement Card) trước khi tối ưu:
| Hạng mục | Quyết định bắt buộc |
|---|---|
| **Thao tác người dùng (User Operation)** | Hành động cụ thể và điều kiện hoàn tất quan sát được từ bên ngoài |
| **Tải công việc (Workload)** | Kích thước dữ liệu đầu vào cố định (điển hình & trường hợp nặng/tail) |
| **Đường dẫn thực thi (Entry Path)** | Chạy qua luồng thực tế của sản phẩm, không đo trên hàm giả lập rời rạc |
| **Đồng hồ đo (Clock)** | Tách bạch chi phí mạng/API bên ngoài với chi phí xử lý cục bộ (CPU/IO/DOM) |
| **Bộ nhớ (Memory)** | Bộ nhớ giữ lại sau khi xong (retained memory) và đỉnh bộ nhớ tạm thời (peak) |
| **Tiêu chí kết luận (Verdict)** | Số liệu trước/sau (tuyệt đối & tỷ lệ %) + kiểm tra đảm bảo hành vi không đổi |

### 2. Các mẫu tối ưu hiệu quả nhất:
- **Giữ cấu trúc dữ liệu gọn suốt đường ống:** Tránh tạo hàng nghìn object trung gian cho từng mảnh nhỏ (delta) khi nơi nhận chỉ cần kết quả tổng hợp cuối cùng.
- **Loại bỏ việc parse, copy, clone hoặc validate lặp lại nhiều lần** trên cùng một dữ liệu đã qua biên kiểm duyệt tin cậy.
- **Xử lý theo luồng (Streaming) & giới hạn bộ đệm trung gian** thay vì nạp toàn bộ lịch sử/tập dữ liệu lớn vào RAM cùng lúc.
- **Trì hoãn công việc của các thành phần đang ẩn (Defer inactive/collapsed views)** và thu hẹp phạm vi đăng ký sự kiện (narrow subscriptions) để 1 thay đổi nhỏ không kích hoạt vẽ lại toàn bộ danh sách.
- **Thay đổi từng nhân tố một (One causal factor at a time):** Đo lại sau mỗi thay đổi; nếu một tối ưu làm phức tạp hóa code nhưng không cải thiện đáng kể thời gian tổng thể (end-to-end), hãy loại bỏ nó.

---

## PHẦN 3: Chuẩn Hóa Tài Liệu & Chống Rò Rỉ Luồng Suy Nghĩ (`dsh-prose-standard` & `dsh-trim-cot-leakage`)

Khi viết comment, docstring (JSDoc/Python docstring) hoặc tài liệu kỹ thuật:

### Bài kiểm tra duy nhất (The One Test):
> **"Một người đọc mã nguồn tại trạng thái hiện tại (HEAD), không hề biết lịch sử trò chuyện hay bản nháp lúc sửa code, có thể hiểu và kiểm chứng mọi thông tin trong comment này không?"**

### Những gì CẤM viết vào comment mã nguồn (Chain-of-Thought Leakage):
1. **Trích dẫn phiên làm việc tạm thời:** Không viết kiểu `theo quyết định số 3`, `như đã bàn ở bước trước`, `sửa theo yêu cầu review`.
2. **Kể chuyện lịch sử thay đổi trên comment mô tả trạng thái hiện tại:** Không viết kiểu `"Hàm này trước đây dùng X nhưng giờ đổi sang Y"`. Hãy mô tả thẳng hành vi hiện tại ở thì hiện tại; nếu muốn cảnh báo lỗi hồi quy, hãy viết dưới dạng câu điều kiện hiện tại: *"Nếu không có bước kiểm tra X, hiện tượng Y sẽ xảy ra khi..."*.
3. **Biện hộ với người chấm:** Không viết `"Ép kiểu chỗ này hoàn toàn an toàn vì..."`. Hãy nêu thẳng bất biến (invariant) đảm bảo điều đó.
4. **Thuật lại từng dòng code (Code Restatement):** Xóa các comment kiểu `"Đầu tiên khởi tạo mảng, sau đó lặp qua từng phần tử"`. Chỉ giữ lại comment giải thích **hợp đồng không hiển nhiên (non-obvious contracts), điều kiện biên, thứ tự tránh xung đột (race ordering), quyền sở hữu tài nguyên và lý do kiến trúc**.
