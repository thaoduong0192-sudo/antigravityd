# Rà Soát Mã Nguồn & Kiểm Định Trước Bàn Giao (Code Review & Pre-Push Verification)

Tổng hợp từ hai skill kiểm định chất lượng của **DeepSeek Harness (`dsh`)**: `dsh-code-review` và `dsh-pre-push-checks`.

---

## PHẦN 1: Quy Trình Rà Soát Mã Nguồn Sâu (`dsh-code-review`)

> **Nguyên tắc vàng:** Ưu tiên tính đúng đắn (correctness), quản lý vòng đời (lifecycle), bảo mật (security) và hành vi bắt buộc bị hỏng hơn là bắt lỗi trình bày lặt vặt. Một bản review ngắn chỉ ra đúng 1 lỗi nghiêm trọng có bằng chứng giá trị hơn một danh sách dài các góp ý vụn vặt.

### Các hạng mục kiểm tra thủ công bắt buộc (Manual Review Checklist):

1. **Đọc yêu cầu & Hợp đồng gốc trước khi đọc bản sửa (Read Requirements Before Judging Diff):**
   - Mở các file quy tắc (`AGENTS.md`, `rules/`) và các file định nghĩa gốc mà bản sửa chạm tới trước khi đánh giá code mới. Đánh giá code chỉ dựa vào trí nhớ sẽ bỏ lọt vi phạm.
2. **Hợp đồng giao tiếp 2 đầu (Intent & Interface Contracts):**
   - Lần theo cả phía gọi (caller/producer) và phía nhận (callee/consumer) của mọi hàm/API vừa sửa. Kiểm tra đầy đủ nhánh lỗi, hủy tác vụ (cancellation), quyền sở hữu dữ liệu và dọn dẹp tài nguyên.
3. **Phạm vi, Sự cần thiết & Tránh tổng quát hóa thừa (Scope, Ownership & Necessity):**
   - Với mỗi trường dữ liệu mới, biến cờ mới, adapter mới hoặc nhánh tương thích mới: đặt câu hỏi **"Hành vi thực tế nào bắt buộc phải có nó?"**
   - Phân biệt giữa việc *xóa bỏ hoàn toàn một khái niệm thừa* với việc *chỉ di chuyển chỗ khai báo của nó*. Di chuyển một khái niệm không cần thiết sang chỗ khác không phải là làm gọn code.
4. **Không mở rộng API công khai chỉ cho 1 nơi gọi nội bộ:**
   - Nếu một hàm công khai mới trên dịch vụ chung chỉ được gọi bởi đúng 1 consumer nội bộ, hãy thu hẹp nó về phạm vi riêng tư hoặc truyền qua closure lúc khởi tạo.
5. **Thứ tự ưu tiên cấu hình (Configuration Precedence):**
   - Khi truyền tham số cấu hình hoặc biến môi trường qua nhiều tầng, kiểm tra xem giá trị truyền đi có bị tầng khác ghi đè (shadowed) trước khi được sử dụng hay không.
6. **Kiểm tra giới hạn trên kết quả cuối cùng (Bounds Cover the Final Operation):**
   - Khi giới hạn kích thước dữ liệu/file/chuỗi, hãy kiểm tra ở nơi xuất ra kết quả hoàn chỉnh cuối cùng (bao gồm cả phần bọc metadata và ký tự đa byte UTF-8).
7. **Sức mạnh thực chất của bài kiểm thử & Đối chứng âm (Test Strength & Negative Controls):**
   - Bài test phải kiểm tra trạng thái/kết quả đầu ra thực tế chứ không chỉ lặp lại công thức cài đặt bên trong.
   - **Negative Control:** Đảm bảo rằng khi cố tình truyền một dữ liệu sai/vi phạm quy tắc mới sửa, hệ thống thực sự bắt được và từ chối đúng như thiết kế.

---

## PHẦN 2: Cổng Kiểm Định Trước Khi Bàn Giao / Commit (`dsh-pre-push-checks`)

Mục tiêu: Chọn **bộ kiểm chứng nhỏ nhất nhưng sát thực tế nhất** có khả năng phát hiện lỗi hồi quy của phần vừa sửa mà không chạy tràn lan vô ích.

### 1. Xác định phạm vi thay đổi thực tế
- Kiểm tra danh sách các file đã sửa, thêm mới hoặc xóa (`git status --short --branch`, `git diff`).
- Đối chiếu với các quy tắc bảo toàn dự án (đảm bảo không vô tình sửa hoặc làm mất các tính năng ngoài phạm vi yêu cầu).

### 2. Chọn bằng chứng kiểm thử tương ứng với bề mặt thay đổi (Match Evidence to the Surface)
- **Thay đổi logic hàm / module / script:** Chạy trực tiếp bài test hoặc script kiểm thử tập trung vào đúng module đó (và các module lân cận nếu thay đổi hợp đồng dùng chung).
- **Thay đổi kiểu dữ liệu (TypeScript / Python types / Schema):** Chạy công cụ kiểm tra kiểu (`typecheck` / `tsc --noEmit` / syntax check) trên toàn bộ nhánh bị ảnh hưởng.
- **Thay đổi cấu hình đóng gói, entry point hoặc build:** Chạy lệnh `build` và chạy thử bản build (smoke test) để chắc chắn đầu ra hoạt động.
- **Thay đổi giao diện người dùng (UI / Web / Ebook / Video):** Kiểm tra trực quan đầu ra thực tế (DOM, ảnh chụp, file xuất bản) để xác nhận không vỡ bố cục, không lỗi font và không mất tính năng quản trị.

### 3. Xử lý khi kiểm định thất bại
- Nếu bất kỳ phép kiểm tra liên quan nào báo lỗi: **Dừng lại và sửa triệt để nguyên nhân gốc** trước khi báo cáo hoàn thành cho người dùng.
- Nếu lỗi do môi trường cục bộ (ví dụ thiếu thông tin xác thực của dịch vụ bên ngoài): phải nêu rõ lệnh nào đã chạy, phần nào đã kiểm chứng thành công, và phần nào cần môi trường thực tế xác nhận. Tuyệt đối không báo cáo một phép kiểm tra đang lỗi hoặc bị bỏ qua là "đã pass".
