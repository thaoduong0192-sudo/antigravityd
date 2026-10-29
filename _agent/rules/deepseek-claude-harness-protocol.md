---
trigger: always_on
description: Bộ khung kỷ luật suy luận sâu và thực thi tác vụ chuẩn DeepSeek Harness (dsh) & Claude Code
---

# Giao Thức Suy Luận & Thực Thi DeepSeek Harness × Claude Code

Áp dụng kỷ luật điều phối Agent từ mã nguồn **DeepSeek Harness (`dsh`)** và **Claude Code** cho mọi tác vụ kỹ thuật:

## 1. Vòng Lặp 5 Bước: Explore → Plan → Todo → Execute → Verify (Đồng bộ Karpathy Guidelines)
- **Explore First → Think Before Coding:** Tự tìm câu trả lời về mặt kỹ thuật bằng công cụ đọc file/tìm kiếm (`read_file`, `rg`) trước. Sau khi đã khảo sát thực địa, nếu yêu cầu nghiệp vụ có nhiều cách hiểu hoặc ẩn chứa đánh đổi (tradeoffs), áp dụng nguyên tắc **Think Before Coding** ([`karpathy-coding-guidelines.md`](file:///d:/Antigravity/_agent/rules/karpathy-coding-guidelines.md)) để nêu rõ giả định và hỏi người dùng (`ask_question`) thay vì đoán mò.
- **Decision-Complete Plan & Simplicity First:** Với tác vụ nhiều bước, xác định rõ mục tiêu (`[Step] → verify: [check]`), tiêu chí hoàn thành, các file/module bị ảnh hưởng và edge cases trước khi sửa code. Ưu tiên tái sử dụng hàm/mẫu có sẵn và viết lượng code tối thiểu giải quyết đúng bài toán hiện tại (chống Overengineering).
- **Todo Tracking (`pending` → `in_progress` → `completed`):** Chia tác vụ phức tạp thành danh sách bước cụ thể. Giữ đúng các bước đang làm ở trạng thái `in_progress` và đánh dấu `completed` ngay khi xác minh xong từng bước.
- **Keep Change Face Equal to Review Face (Surgical Changes):** Chỉ sửa đúng những dòng phục vụ hành vi được yêu cầu, giữ nguyên văn phong code hiện hữu (Match Existing Style) và chỉ dọn dẹp import/biến dư thừa do chính thay đổi của mình tạo ra. Khi di chuyển/tách file (migration), giữ nguyên hành vi trước rồi mới sửa logic ở bước riêng; tuyệt đối không xóa tính năng cũ hoặc dead code có sẵn ngoài phạm vi.
- **Falsifiable Verification Gate (Goal-Driven Execution):** Coi trạng thái thực tế của workspace và kết quả chạy công cụ là nguồn sự thật duy nhất (không tin vào suy đoán). Trước khi báo cáo hoàn thành, bắt buộc chạy kiểm tra thực tế hẹp nhất bao phủ phần vừa sửa (syntax/typecheck/test/run) và chỉ báo cáo những lệnh đã thực sự chạy.

## 2. Chống Lặp Lỗi Vô Hạn (Repeat-Tool Loop Guard `[3, 5, 8]`)
- **Ngưỡng cảnh báo lần 2–3:** Tuyệt đối KHÔNG gọi lại cùng một lệnh/công cụ với tham số y hệt nếu đã thất bại 2 lần liên tiếp.
- **Bắt buộc đổi chiến thuật:** Khi lệnh lỗi hoặc kết quả không đổi sau 2 lần thử, phải dừng lại đọc kỹ log lỗi, kiểm tra giả định gốc, tạo script tái hiện nhỏ trong `scratch/` hoặc đổi hướng tiếp cận.

## 3. Năm Nguyên Tắc Phòng Thủ Cốt Lõi (Defensive Patterns)
1. **Make Correctness Explicit:** Tính đúng đắn phải đến từ trạng thái và luồng gọi tường minh, không dùng `setTimeout` / `sleep` cảm tính để "đợi" bất đồng bộ.
2. **Keep One Source of Truth:** Mỗi dữ liệu/cấu hình chỉ có một nơi làm chủ (single owner); không tạo biến toàn cục ngầm hay copy trạng thái dư thừa.
3. **One Value States One Fact:** Phân biệt rõ 3 trạng thái `unknown` (chưa rõ), `empty` (rỗng) và `value` (có giá trị); không lạm dụng chuỗi `a?.b?.c ?? fallback` để che giấu lỗi hợp đồng dữ liệu.
4. **Catch, Recover, or Stop:** Bắt lỗi (`catch`) chỉ chặn lan truyền ngoại lệ chứ không tự khôi phục trạng thái hỏng. Nếu không đảm bảo được invariant an toàn để chạy tiếp, phải dừng luồng phụ thuộc và báo lỗi rõ nguyên nhân + hành động tiếp theo.
5. **Dispose to Quiescence & Scrub Secrets:** Mọi tiến trình con, kết nối hoặc tài nguyên tạm phải được dọn dẹp đến khi dừng hẳn (quiescence) và không làm lộ biến môi trường nhạy cảm (`*KEY*`, `*SECRET*`, `*TOKEN*`, `*PASSWORD*`).

## 4. Điều Tra Lỗi 4 Pha, Subagent Worktree & Bộ Nhớ Xuyên Phiên (`superpowers` × `MEMORY.md`)
- **Luật Sắt Khi Gặp Bug (No Fixes Without Root Cause First):** Cấm sửa triệu chứng mò mẫm. Phải đọc kỹ stack trace, tái hiện lỗi, truy vết ngược luồng dữ liệu (Backward Tracing) và chỉ thử 1 biến số mỗi lần. Nếu vá trượt 2 lần liên tiếp (*3-Strike Rule*), phải dừng lại xem xét kiến trúc (xem [`systematic-debugging-and-tdd.md`](file:///d:/Antigravity/_agent/skills/deepseek-harness-engine/references/systematic-debugging-and-tdd.md)).
- **Subagent Cô Lập & Worktree (`invoke_subagent`):** Giao việc quét diện rộng (>10 files) cho subagent `research` để giữ sạch ngữ cảnh chính; dùng `Workspace: "share"` (tương đương Git Worktree) khi cần chạy thử nghiệm nhánh độc lập.
- **Bộ Nhớ Dự Án (`PROJECT_MEMORY.md`):** Tham chiếu và cập nhật bản đồ kiến trúc & các bẫy kỹ thuật đã biết tại [`PROJECT_MEMORY.md`](file:///d:/Antigravity/_agent/memory/PROJECT_MEMORY.md).

> Khi thực hiện các tác vụ phức tạp (debug lỗi khó, tối ưu hiệu năng, xử lý lỗi hệ thống, dọn dẹp kiến trúc, viết test chống flaky hoặc review code sâu), hãy kích hoạt skill **`deepseek-harness-engine`** để nạp sổ tay chi tiết.
