# 11 Mẫu Thiết Kế Phòng Thủ Cốt Lõi (DeepSeek Harness Defensive Patterns)

Mỗi quy tắc dưới đây là một lớp lỗi thực tế đã được đội ngũ **DeepSeek Harness (`dsh`)** đúc kết thành luật bắt buộc khi viết và duyệt code. Đọc kỹ các mẫu liên quan trước khi viết code xử lý vòng đời (lifecycle), bất đồng bộ (concurrency), tiến trình con (subprocess) hoặc quản lý trạng thái.

---

## 1. Báo cáo độc lập các kết quả trực giao (Report Orthogonal Outcomes Independently)
- Một tiến trình có thể **vừa bị timeout VỪA trả về `exitCode === 0`** (do tiến trình đó bắt tín hiệu dừng và tự thoát êm).
- **Quy tắc:** Phải trả về từng cờ trạng thái độc lập (`timedOut`, `signal`, `exitCode`). Không bao giờ lồng nhánh kiểm tra `timedOut` vào bên trong nhánh `exitCode !== 0`, nếu không một tiến trình bị cắt ngang do hết giờ sẽ bị hiểu nhầm là chạy thành công.

## 2. Chuẩn hóa hợp đồng ở cả 2 phía của API (Honor Public Contracts on Both Sides)
- Khi một tầng bên dưới có thể trả về lỗi dưới nhiều hình thức (vừa `throw` ngoại lệ, vừa trả về sự kiện `{ kind: 'error' | 'aborted' }`), tầng API công khai phải chuẩn hóa chúng về một định dạng duy nhất đã cam kết trước khi trả cho bên gọi (consumer).
- Người gọi API phải xác định được nguồn gốc lỗi chỉ bằng cách đọc hợp đồng công khai mà không phải đoán xem lỗi đến từ mạng, từ wrapper hay từ chính bộ giải mã.

## 3. Trạng thái bất đồng bộ KHÔNG PHẢI trạng thái đồng bộ (Async State Is Not Synchronous State)
- Một cờ chung như `status === 'running'` hoặc `whenIdle()` có thể bao hàm nhiều tác vụ xếp hàng nối tiếp nhau.
- **Quy tắc:** Không bao giờ dùng một biến trạng thái dùng chung để suy diễn kết quả của riêng một thông điệp đơn lẻ. Luôn định nghĩa rõ biên độ bắt đầu – kết thúc của từng đơn vị công việc và xử lý tường minh nhánh "không có gì để đợi" (tránh treo `await` vĩnh viễn khi sự kiện chuyển trạng thái đã đi qua hoặc không bao giờ xảy ra).

## 4. Không dùng thời gian chờ để đảm bảo tính đúng đắn (Timing Does Not Carry Correctness)
- Tính đúng đắn phải đến từ thứ tự gọi tường minh (explicit call points) và máy trạng thái (state machine), **không bao giờ dựa vào việc một callback kịp chạy trong `setTimeout(..., 0)` hay `queueMicrotask`**.
- Code phụ thuộc vào `setTimeout` sẽ chạy đúng khi máy rảnh và lỗi ngầm khi tải nặng.
- **Đúng:**
  ```ts
  store.dispose()
  store = createStore(scopeKey)
  ```
- **Sai (Cấm):**
  ```ts
  queueMicrotask(() => { if (!ready) refresh() })
  setTimeout(() => setMounted(true), 0)
  ```

## 5. Tham số tùy chọn phải định nghĩa rõ cả 2 nhánh hành vi (Optional Inputs State Both Behaviors)
- Khi một hàm nhận tham số tùy chọn (`options?: ...`), hợp đồng của hàm phải quy định rõ hàm làm gì khi có mặt và khi vắng mặt tham số đó.
- **Dấu hiệu vi phạm:** Chuỗi `const value = a?.b?.c?.d ?? fallback`. Việc chồng chất `?.` che giấu câu hỏi liệu trường đó có bắt buộc phải tồn tại hay không và nuốt mất lỗi dữ liệu hỏng.

## 6. Một giá trị chỉ biểu diễn một sự thật (One Value States One Fact)
- **"Chưa truy vấn (`unknown`)"**, **"Đã truy vấn nhưng rỗng (`empty`)"**, và **"Có giá trị (`value`)"** là 3 sự thật khác nhau.
- Không bao giờ dùng một giá trị `null` hoặc `undefined` duy nhất để đại diện cho cả 3 trường hợp trên. Hãy dùng Discriminated Union tường minh:
  ```ts
  type ValueState<T> = { kind: 'unknown' } | { kind: 'empty' } | { kind: 'value'; value: T }
  ```

## 7. Từ chối biến Singleton `active`/`current` toàn cục mới (Refuse Global Active/Current Singletons)
- Không tạo biến cấp module như `let activeTabId` hay `globalThis.__cache`. Biến toàn cục làm các luồng/view độc lập ghi đè lẫn nhau và rò rỉ trạng thái giữa các lần chạy.
- Mỗi view hoặc phiên làm việc phải tự giữ tham chiếu/khóa (`sessionKey`) của riêng nó, hoặc gắn trạng thái vào một instance/service có vòng đời được quản lý rõ ràng.

## 8. Trạng thái dùng chung phải có một chủ sở hữu định danh (Shared State Has One Owner)
- Mọi trạng thái chia sẻ phải thuộc về một đối tượng dịch vụ (service/instance) có vòng đời khởi tạo và thu hồi rõ ràng. Nếu không chỉ tên được đối tượng nào làm chủ và chịu trách nhiệm dọn dẹp biến đó, phải thiết kế lại chủ sở hữu trước khi code.

## 9. Năng lực nghiệp vụ tự làm chủ chính nó (A Business Capability Owns Itself)
- Khi thêm tính năng mới, hãy đăng ký nó qua điểm mở rộng (registry, plugin, hook, event listener) tại chính module sở hữu nghiệp vụ đó.
- Tầng điều phối trung tâm (runtime, controller, manager) chỉ quản lý cấu trúc đăng ký và vòng đời, **không nhồi nhét câu lệnh `if (featureName === 'xyz')` vào bộ điều phối trung tâm**.

## 10. Dọn dẹp tài nguyên phải chờ đến khi tĩnh lặng hoàn toàn (Dispose Must Reach Quiescence)
- Gọi `kill()`, `abort()`, hoặc `close()` mà không `await` tiến trình con hoặc kết nối thực sự đóng xong là dọn dẹp chưa hoàn chỉnh.
- Hàm `dispose` / `teardown` phải chặn thông báo mới, gỡ listener, và chờ mọi tác vụ con mà nó khởi tạo kết thúc hẳn trước khi trả về.
- Trong bộ phát sự kiện (event dispatcher), phải bọc `try / catch` cho từng listener độc lập để một listener bị lỗi không làm sập chuỗi thông báo của các listener phía sau.

## 11. Lọc sạch biến môi trường nhạy cảm & Xóa symlink an toàn (Scrub Env & Unlink Link-Shaped Paths)
- Khi khởi chạy tiến trình con với đầu vào không tin cậy, phải lọc bỏ các biến môi trường chứa khóa bí mật (`*KEY*`, `*SECRET*`, `*TOKEN*`, `*PASSWORD*`) và tạo thư mục/file tạm với tên ngẫu nhiên, quyền truy cập riêng biệt.
- Trên Windows và POSIX, khi xóa đường dẫn có thể là symlink hoặc Windows junction, kiểm tra `lstatSync().isSymbolicLink()` và dùng `unlinkSync` để chỉ gỡ liên kết, tuyệt đối không dùng `rmSync` đệ quy đi xuyên qua junction làm mất dữ liệu thư mục gốc.
