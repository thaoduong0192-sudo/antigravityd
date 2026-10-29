---
name: deepseek-harness-engine
description: >-
  Hệ thống kỹ năng suy luận sâu, lập kế hoạch (Plan-Todo-Goal Loop), phòng thủ mã nguồn
  (Defensive Patterns), xử lý lỗi (Error Handling), tối ưu hiệu năng (Speed-Up Perf),
  tinh gọn kiến trúc (Find Simplifications) và kiểm định chất lượng (Code Review & Pre-Push Checks)
  trích xuất nguyên bản từ mã nguồn DeepSeek Harness (dsh) và Claude Code. Kích hoạt khi giải quyết
  bài toán phức tạp, refactor lớn, debug lỗi khó, tối ưu tốc độ hoặc kiểm định chất lượng dự án.
---

# DeepSeek Harness Engine (`dsh` × Claude Code Reasoning Suite)

Skill này cung cấp toàn bộ quy trình điều phối suy luận sâu và bộ tiêu chuẩn kỹ thuật thực chiến từ kho mã nguồn **[deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)**.

## Khi nào cần đọc từng sổ tay chuyên sâu (`references/`)?

Để tiết kiệm ngữ cảnh (Progressive Disclosure), hãy đọc đúng file tài liệu tham chiếu tương ứng với nhiệm vụ đang làm:

1. **[plan-and-goal-loop.md](./references/plan-and-goal-loop.md)**
   - Đọc khi cần lập kế hoạch kiến trúc phức tạp (`plan-mode`), chia nhỏ tác vụ nhiều vòng (`goal-round-driver`), quản lý danh sách việc cần làm (`tool-todo`), phân bổ `subagent`, hoặc xử lý tình huống bị kẹt lệnh (`repeat-tool-reminder`).
2. **[defensive-patterns.md](./references/defensive-patterns.md)**
   - Đọc trước khi viết hoặc sửa code liên quan đến bất đồng bộ (async/concurrency), quản lý trạng thái (state ownership), subprocess, vòng đời tài nguyên (lifecycle/teardown), hoặc thiết kế API/module boundary.
3. **[error-handling-and-reliability.md](./references/error-handling-and-reliability.md)**
   - Đọc khi thiết kế cơ chế bắt lỗi, retry, background tasks (`dsh-error-handling`) hoặc khi viết/sửa các bài test dễ bị lỗi chập chờn do xung đột tài nguyên, cổng mạng, thời gian, đa tiến trình trên Windows/POSIX (`dsh-ci-test-reliability`).
4. **[code-review-and-verification.md](./references/code-review-and-verification.md)**
   - Đọc khi thực hiện rà soát mã nguồn (`dsh-code-review`) hoặc chọn bộ lệnh kiểm증 nhỏ nhất nhưng chặt chẽ nhất trước khi bàn giao/commit (`dsh-pre-push-checks`).
5. **[simplification-and-performance.md](./references/simplification-and-performance.md)**
   - Đọc khi cần tìm và cắt bỏ code thừa/phức tạp hóa (`dsh-find-simplifications`), đo đạc và tối ưu hóa tốc độ/bộ nhớ (`dsh-speed-up-perf`), hoặc dọn dẹp comment/tài liệu bị rò rỉ luồng suy nghĩ (`dsh-trim-cot-leakage` & `dsh-prose-standard`).
6. **[systematic-debugging-and-tdd.md](./references/systematic-debugging-and-tdd.md)**
   - Đọc ngay khi gặp bug phức tạp, lỗi chưa rõ nguyên nhân hoặc test fail để áp dụng **Phác đồ Điều tra Nguyên nhân Gốc 4 Pha (`obra/superpowers`)**, truy vết ngược luồng dữ liệu, quy tắc dừng sau 2 lần vá trượt (*3-Strike Rule*) và quy trình **TDD (Red-Green-Refactor)**.

---

## Quy Trình Vận Hành Tóm Tắt (Core Workflow)

### Bước 1: Định vị & Khảo sát (Ground in Reality)
- Dùng công cụ tìm kiếm (`rg`, `read_file`) kiểm tra toàn bộ chuỗi Producer → Consumer của đoạn code sắp sửa.
- Không đoán mò cấu trúc dữ liệu hoặc dựa vào trí nhớ từ các lượt hội thoại cũ.

### Bước 2: Thiết lập Kế hoạch Quyết định Hoàn chỉnh (Decision-Complete Plan)
- Nêu rõ:
  1. **Mục tiêu & Tiêu chí nghiệm thu (Goal & Acceptance Criteria)**
  2. **Phân nhóm thay đổi theo phân hệ (Subsystem Changes)**
  3. **Hợp đồng dữ liệu, API & Xử lý lỗi (Contracts & Failure Modes)**
  4. **Kịch bản kiểm chứng thực tế & Đối chứng âm (Verification & Negative Control)**

### Bước 3: Thực thi Phẫu thuật & Phòng thủ (Surgical & Defensive Execution)
- Áp dụng **5 thói quen phòng thủ** từ [defensive-patterns.md](./references/defensive-patterns.md):
  - *Make correctness explicit* (ràng buộc đúng đắn bằng cấu trúc/state, không dùng timer cảm tính).
  - *Keep one source of truth* (một nguồn dữ liệu duy nhất, một chủ sở hữu).
  - *Extend through registered seams* (mở rộng qua điểm ghép nối thay vì nhồi `if/else` vào hàm trung tâm).
  - *Keep change face equal to review face* (chỉ sửa đúng phạm vi yêu cầu).
  - *Require falsifiable evidence* (mọi khẳng định hoàn thành hay tối ưu đều phải đo đếm/kiểm chứng được).

### Bước 4: Kiểm định Đầu ra (Pre-Completion Verification Gate)
- Chạy bài kiểm tra hẹp nhất có khả năng bắt lỗi hồi quy (regression) của phần vừa sửa + kiểm tra đối chứng âm (negative control: đảm bảo trường hợp sai bị từ chối đúng như thiết kế).
- Báo cáo chính xác các lệnh đã chạy và kết quả thực tế.
