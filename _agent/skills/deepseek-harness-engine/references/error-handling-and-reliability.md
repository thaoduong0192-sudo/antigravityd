# Xử Lý Lỗi Hệ Thống & Độ Tin Cậy Kiểm Thử (Error Handling & Test Reliability)

Tổng hợp từ hai skill cốt lõi của **DeepSeek Harness (`dsh`)**: `dsh-error-handling` và `dsh-ci-test-reliability`.

---

## PHẦN 1: Nguyên Tắc Xử Lý Lỗi (`dsh-error-handling`)

> **Nền tảng lý thuyết:** Bertrand Meyer (*Design by Contract & Invariants*), Herb Sutter (*Exception Safety Guarantees*), Joe Armstrong (*Erlang Isolation & Supervision*).

### 1. Phân loại lỗi có cấu trúc (Typed, Structured Failures)
- **Lỗi dự kiến (Expected failures):** Phải có kiểu dữ liệu tường minh, mã định danh ổn định (`code` / discriminant) và thông tin chi tiết phục vụ xử lý. Luôn giữ lại nguyên nhân gốc (`cause`) và tách biệt mã định danh máy đọc với chuỗi văn bản hiển thị cho người dùng.
- **Cấm phân nhánh xử lý lỗi bằng cách cắt chuỗi `error.message` (Never route handling by parsing messages).**
- **Lỗi bất ngờ (Unexpected defects / Assertions):** Không bao giờ được biến lỗi bất ngờ thành kết quả "thành công giả" (silent success).

### 2. Bắt lỗi, Khôi phục, hoặc Dừng hẳn (Catch, Recover, or Stop)
- Với mỗi điểm có thể lỗi, phải xác định rõ:
  1. **Ai là chủ sở hữu xử lý và báo cáo lỗi?**
  2. **Biên độ cô lập lỗi (Containment boundary) ở đâu?**
  3. **Cam kết trạng thái sau lỗi (State guarantees):** Trạng thái vẫn toàn vẹn (valid invariants), chưa thay đổi (absent), thay đổi một phần (partial), đã lưu (committed), hay không xác định (unknown)?
- **Quy tắc sống còn:** Lệnh `catch` chỉ chặn ngoại lệ văng tiếp chứ **không tự động hoàn tác các biến đã bị sửa dở dang**. Chỉ có chủ sở hữu trạng thái đó mới đủ thẩm quyền xác nhận trạng thái đã an toàn để chạy tiếp. Nếu không đảm bảo được tiền điều kiện (preconditions) cho bước sau: **phải dừng công việc phụ thuộc, hủy bỏ trạng thái hỏng, hoặc báo lỗi lên cấp cao hơn. Chỉ ghi `console.log` / `logger.warn` rồi chạy tiếp KHÔNG PHẢI là khôi phục lỗi.**
- **Retry có ngân sách (Budgeted Retries):** Chỉ retry khi thao tác đó an toàn để lặp lại (idempotent), hỗ trợ hủy (`AbortSignal`), và có giới hạn số lần/thời gian rõ ràng.

### 3. Báo cáo lỗi rõ ràng, có hướng xử lý (Actionable, Visible Reports)
- Mọi thông báo lỗi cuối cùng tới người dùng phải có đủ 3 ý:
  1. **Tóm tắt dễ hiểu chuyện gì đã xảy ra.**
  2. **Thao tác/thành phần nào bị ảnh hưởng.**
  3. **Bước tiếp theo an toàn mà người dùng nên làm.**
- Không phơi bày thông tin nhạy cảm nội bộ (token, đường dẫn hệ thống ngầm) ra giao diện người dùng.
- Không bao giờ tuyên bố "đã lưu thành công", "đã rollback an toàn" hay "có thể thử lại an toàn" nếu code chưa thực sự kiểm chứng điều đó.

---

## PHẦN 2: Thiết Kế Kiểm Thử Chống Chập Chờn (`dsh-ci-test-reliability`)

### 1. Cấp phát tài nguyên nguyên tử (Allocate Resources Atomically)
- **Cổng mạng (Ports):** Luôn bind vào loopback với cổng `0` (`listen(0)`) và đọc cổng thực tế được hệ điều hành cấp sau khi server đã báo `listening`. Tuyệt đối không quét tìm cổng trống rồi mới bind sau (dễ bị tiến trình khác cướp cổng).
- **Thư mục tạm:** Tạo thư mục tạm riêng biệt cho từng bài test bằng `mkdtemp`; không dùng chung đường dẫn cố định dễ đoán.
- **Database / Socket / Session:** Cấp namespace riêng biệt cho mỗi test.

### 2. Cô lập trạng thái toàn cục của tiến trình (Contain Process-Global State)
- Coi `process.env`, `cwd`, fake timers, locale/timezone, module mocks, `globalThis`, và `fetch` interceptor là tài nguyên độc quyền:
  - Ghi nhận chính xác trạng thái ban đầu (có tồn tại hay không).
  - Bọc trong khối `try / finally` ở phạm vi nhỏ nhất để khôi phục nguyên trạng ngay lập tức.

### 3. Tôn trọng đặc thù hệ điều hành Windows vs. POSIX
- **Windows khớp tên biến môi trường không phân biệt hoa thường:** `http_proxy` và `HTTP_PROXY` là cùng một khóa trên Windows.
- **Windows giải phóng file handle bất đồng bộ:** Đổi tên hoặc xóa file ngay sau khi đóng tiến trình trên Windows có thể cần cơ chế retry có giới hạn ngắn do hệ điều hành nhả khóa trễ.
- **Độ phân giải thời gian file (`mtime`):** NTFS dùng đơn vị 100-nanosecond tick, không giả định số thập phân mili-giây giữ nguyên tuyệt đối khi ghi đè.

### 4. Đồng bộ hóa dựa trên trạng thái, không dùng `sleep` cố định (Synchronize on State)
- Một lệnh `sleep(500)` cố định không chứng minh được rằng quá trình khởi tạo hay dọn dẹp đã xong.
- Hãy chờ sự kiện sẵn sàng tường minh (readiness event, handshake, state transition, promise hoàn tất). Chỉ dùng timeout làm giới hạn chặn trên (ceiling), không bao giờ dùng timeout làm điều kiện đúng đắn.

### 5. Từ chối các cách "vá tạm" che giấu lỗi Flaky (Reject Flake-Masking Fixes)
Tuyệt đối không coi các cách sau là đã sửa xong lỗi test:
- Tăng bừa timeout mà không chỉ ra được đang chờ trạng thái nào.
- Thêm vòng lặp retry bọc ngoài một bài test đơn vị (unit test) đáng lẽ phải tất định (deterministic).
- Nuốt lỗi (`catch {}`) hoặc làm yếu câu lệnh `assert` / `expect`.
- Chèn `sleep` trước khi assert hoặc cleanup.
