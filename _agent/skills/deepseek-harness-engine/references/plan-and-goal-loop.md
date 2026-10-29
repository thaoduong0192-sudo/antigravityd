# Vòng Lặp Điều Phối Suy Luận: Plan Mode, Todo, Goal Round & Loop Guard

Tài liệu này trích xuất nguyên bản cơ chế điều phối từ 4 gói lõi của **DeepSeek Harness (`dsh`)**: `@deepseek-ai/dsh-plan-mode`, `@deepseek-ai/dsh-tool-todo`, `@deepseek-ai/dsh-goal-round-driver`, và `@deepseek-ai/dsh-repeat-tool-reminder`.

---

## 1. Chế độ Lập Kế Hoạch Chuẩn (`plan:policy`)

Khi nhận bài toán lớn hoặc khi người dùng yêu cầu lập kế hoạch trước khi thực thi:

1. **Khảo sát trước, không sửa file (Explore First):**
   - Chỉ dùng các công cụ đọc, tìm kiếm (`read_file`, tìm kiếm tĩnh) để neo kế hoạch vào mã nguồn thực tế của dự án.
   - Không sửa file, không chạy formatter làm thay đổi file đang theo dõi cho đến khi kế hoạch được chốt.
   - Ưu tiên sử dụng lại các hàm, cấu trúc và mẫu thiết kế (patterns) đã có sẵn trong dự án thay vì tự chế thêm tầng trừu tượng mới.
2. **Tự giải quyết thông tin có thể tra cứu (Resolve Discoverable Facts by Inspection):**
   - Tuyệt đối không hỏi người dùng "code nằm ở đâu" hay "hàm hiện tại chạy thế nào" nếu có thể tự đọc code để biết.
   - Chỉ dùng công cụ `ask_question` cho các lựa chọn thuộc thẩm quyền quyết định của người dùng hoặc sự mơ hồ về nghiệp vụ mà code không thể trả lời.
3. **Kế hoạch Đủ Quyết Định (Decision-Complete Plan):**
   Một bản kế hoạch đạt chuẩn phải có:
   - **Mục tiêu & Tiêu chí thành công (Goal & Success Criteria).**
   - **Nhóm thay đổi theo từng phân hệ (Subsystem Grouping).**
   - **Thay đổi về API công khai, Schema và Luồng dữ liệu (Public API, Schema & Data-Flow).**
   - **Các trường hợp biên, kịch bản lỗi, bài kiểm thử và giả định tường minh (Edge Cases, Failure Modes, Tests & Assumptions).**
   - Đủ ngắn gọn để người dùng duyệt nhanh nhưng đủ chi tiết để bất kỳ kỹ sư hay subagent nào cũng có thể code ngay mà không phải tự đoán thiết kế.

---

## 2. Kỷ Luật Quản Lý Danh Sách Việc Cần Làm (`tool-todo`)

- **Bỏ qua cho việc đơn giản 1 bước**, nhưng **bắt buộc dùng** cho mọi tác vụ nhiều bước.
- Mỗi mục (`todo`) là một câu mệnh lệnh ngắn gọn, cụ thể.
- **3 trạng thái nghiêm ngặt:**
  - `pending`: Chưa bắt đầu.
  - `in_progress`: Đang thực hiện ngay lúc này (chỉ giữ 1 mục `in_progress` nếu làm tuần tự; chỉ mở nhiều mục `in_progress` khi đang chạy song song nhiều subagent hoặc background tasks).
  - `completed`: Đã hoàn thành và đã kiểm chứng xong.
- Đánh dấu `completed` ngay khi bước đó hoàn tất; không dồn đến cuối phiên mới cập nhật một thể.

---

## 3. Động Cơ Bám Đuổi Mục Tiêu Nhiều Vòng (`goal-round-driver`)

Khi thực hiện tác vụ dài hạn (nhiều bước nối tiếp hoặc sử dụng `/goal`):

```text
<goal_round_protocol>
- Coi trạng thái hiện tại của workspace, kết quả trả về từ công cụ (tool results) và dữ liệu bền vững là nguồn sự thật duy nhất.
- Luôn kiểm tra thực tế thay vì giả định rằng những gì đã nói ở các lượt trước vẫn còn đúng.
- Tạo ra tiến triển cụ thể ở mỗi lượt và kiểm chứng kết quả ngay.
- Trước khi tuyên bố hoàn thành toàn bộ mục tiêu: phải thu thập đủ bằng chứng thực thi rằng toàn bộ yêu cầu đã đạt được 100%.
</goal_round_protocol>
```

---

## 4. Bộ Chặn Vòng Lặp Công Cụ (`repeat-tool-reminder` — Ngưỡng `[3, 5, 8]`)

Cơ chế tự giám sát chống kẹt vòng lặp vô hạn (Loop Guard):

- **Ngưỡng 1 (Lần lặp thứ 3 với cùng công cụ & tham số tương đương):**
  > *"Bạn đang lặp lại chính xác cùng một lệnh gọi công cụ với tham số y hệt. Hãy phân tích kỹ kết quả trước đó trước khi gọi lại: nếu tác vụ chưa xong, hãy thử cách tiếp cận khác hoặc tham số khác thay vì lặp lại lệnh cũ."*
- **Ngưỡng 2 (Lần lặp thứ 5 trở lên):**
  > *"Các lệnh gọi lặp lại không tạo ra tiến triển. CẤM gọi lại công cụ này với bộ tham số cũ. Hãy đọc kết quả mới nhất và chọn hành động khác, tham số khác, hoặc dừng lại báo cáo nguyên nhân gốc rễ (root cause)."*

---

## 5. Phân Bổ Đội Hình Subagent & Cô Lập Workspace (`invoke_subagent` × Claude Code Agent Teams)

Tận dụng tối đa khả năng đa tác tử (Multi-Agent) và cô lập không gian làm việc của Antigravity:

### A. 3 Mẫu Điều Phối Subagent Chuẩn:
1. **Context-Isolated Explorer (`TypeName: "research"`):**
   - **Khi nào dùng:** Khi cần khảo sát rộng (>8–10 files), tìm kiếm trên nhiều thư mục hoặc tra cứu tài liệu lớn mà nếu đọc trực tiếp sẽ làm đầy bộ nhớ ngữ cảnh chính.
   - **Lợi ích:** Subagent `research` chỉ có quyền đọc (read-only), tự tiêu thụ hàng chục nghìn token log tìm kiếm ở cửa sổ ngữ cảnh riêng và chỉ trả về bản đúc kết tinh gọn kèm đường dẫn file/số dòng cho Agent chính.
2. **Parallel Worktree Executor (`TypeName: "self"`, `Workspace: "share"` hoặc `"branch"`):**
   - **Khi nào dùng:** Khi thực hiện refactor lớn, thử nghiệm phương án kiến trúc mới hoặc giải quyết nhiều phân hệ hoàn toàn độc lập song song.
   - **Lợi ích:** Tham số `Workspace: "share"` tạo ra một không gian làm việc chia sẻ kho lưu trữ nền (tương đương **Git Worktree** trong Claude Code) mà không tốn dung lượng nhân bản ổ cứng, giúp chạy thử nghiệm an toàn không ảnh hưởng đến nhánh chính.
3. **Multi-Axis PR / Code Reviewer (Mô hình `pr-review-toolkit` của Claude Code):**
   - Trước khi bàn giao một tính năng phức tạp, có thể phóng Subagent kiểm tra độc lập trên 3 trục:
     - *Trục 1 (Preservation Audit):* Đối chiếu `git diff` với `AGENTS.md` để đảm bảo không mất bất kỳ bảng quản trị Admin hay tính năng đã duyệt nào.
     - *Trục 2 (Security Audit):* Kiểm tra ranh giới tin cậy (Trust Boundary, Zero Client Trust, SQL/Command Injection, lộ Secret) theo `vibe-code-security-protocol.md`.
     - *Trục 3 (Correctness & Defensive Check):* Kiểm tra lifecycle, xử lý lỗi và điều kiện biên theo `defensive-patterns.md`.

### B. Nguyên Tắc Giao Việc Cho Subagent:
- Giao phạm vi có biên giới rõ ràng (Bounded Domain), nêu rõ mục tiêu, danh sách file/thư mục trọng tâm và định dạng bằng chứng đầu ra cần trả về.
- Không cần gọi lệnh chờ (polling) trong vòng lặp; hệ thống Reactive Wakeup của Antigravity sẽ tự động đánh thức Agent chính ngay khi Subagent hoàn thành nhiệm vụ.
