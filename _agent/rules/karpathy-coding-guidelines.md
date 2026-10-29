---
trigger: always_on
description: 4 Nguyên tắc Cốt lõi của Andrej Karpathy cho Coding Agent (Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution) đã đồng bộ tương thích với hệ Rule Antigravity
---

# Quy Chuẩn Hành Vi Coding Agent Theo Andrej Karpathy (`CLAUDE.md` Baseline Hygiene)

Áp dụng 4 nguyên tắc nền tảng từ kho mã nguồn **[multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)** (kết hợp đồng bộ với [`deepseek-claude-harness-protocol.md`](file:///d:/Antigravity/_agent/rules/deepseek-claude-harness-protocol.md), [`vibe-code-security-protocol.md`](file:///d:/Antigravity/_agent/rules/vibe-code-security-protocol.md) và [`AGENTS.md`](file:///d:/Antigravity/AGENTS.md)):

> **Nguyên tắc Đánh đổi (Tradeoff):** Ưu tiên sự cẩn trọng và độ chính xác hơn tốc độ mù quáng. Với các tác vụ nhỏ hiển nhiên (sửa typo, sửa 1 dòng rõ ràng), thực thi nhanh gọn không máy móc.

## 1. Think Before Coding — Suy Nghĩ & Phơi Bày Giả Định Trước Khi Code
- **Không đoán mò, không giấu sự mơ hồ:** Sau khi đã tự đọc mã nguồn (`Explore First`), nếu yêu cầu nghiệp vụ còn điểm chưa rõ hoặc có nhiều cách hiểu khác nhau, hãy trình bày rõ các phương án kèm đánh đổi (tradeoffs) và hỏi lại người dùng — tuyệt đối không âm thầm chọn đại một hướng.
- **Chủ động phản biện kỹ thuật (Push back when warranted):** Nếu phát hiện cách giải quyết đơn giản hơn, ít rủi ro hơn so với yêu cầu phức tạp ban đầu, hãy đề xuất rõ ràng trước khi làm.

## 2. Simplicity First — Tối Giản Trước Tiên (Chống Overengineering)
- **Viết lượng code tối thiểu giải quyết đúng bài toán được giao (Nothing speculative):**
  - Không tự đẻ thêm tính năng, bộ lọc, thông báo, hay cấu hình ngoài yêu cầu.
  - Không tạo lớp trừu tượng (`Strategy`, `Factory`, `BaseClass`, `Wrapper`) cho đoạn code chỉ dùng 1 lần.
  - Nếu một tính năng mới viết mất 200 dòng trong khi 50 dòng rõ ràng là đủ, hãy viết gọn lại thành 50 dòng.
- **Chốt chặn tương thích bắt buộc:**
  - **Tương thích Bảo toàn Dự án (`AGENTS.md` & `global-preservation-rules.md`):** Quy tắc tối giản CHỈ áp dụng cho phần code mới đang viết; tuyệt đối KHÔNG dùng làm cớ để rút gọn, xóa bớt hoặc viết lại các tính năng, bảng quản trị Admin, báo cáo AI 5 chương, biểu đồ kỹ thuật hay hệ thống E-Learning đã được duyệt.
  - **Tương thích Bảo mật (`vibe-code-security-protocol.md`):** Chỉ lược bỏ xử lý lỗi dư thừa ở hàm nội bộ; tại ranh giới giao tiếp Client/Server/DB (Trust Boundary), BẮT BUỘC giữ đầy đủ kiểm tra xác thực/phân quyền (AuthN/AuthZ), Zero Client Trust và Parameterized Queries.

## 3. Surgical Changes — Phẫu Thuật Chính Xác & Giữ Chặt Biên Giới Diff
- **Chỉ chạm vào đúng chỗ phải sửa:**
  - Không tự ý "cải tiến" code lân cận, không sửa/xóa comment cũ, không đổi định dạng (formatting/quote style) của toàn file.
  - Không refactor những phần đang chạy tốt và không liên quan đến yêu cầu.
  - **Match Existing Style:** Giữ nguyên văn phong code hiện tại của file đang sửa (kiểu nháy đơn/kép, thụt lề, quy ước đặt tên, cấu trúc xử lý lỗi) ngay cả khi bạn quen viết kiểu khác.
- **Chỉ dọn rác do chính mình tạo ra (Clean up only your own mess):**
  - Nếu thay đổi của bạn làm một `import`, biến hoặc hàm trở nên dư thừa (orphan), hãy dọn sạch nó.
  - Nếu thấy dead code có sẵn từ trước nhưng không liên quan đến yêu cầu: chỉ nêu thông báo cho người dùng, **tuyệt đối không tự ý xóa**.
- **Tiêu chuẩn kiểm tra:** Mọi dòng thay đổi trong `diff` phải truy nguyên trực tiếp về đúng yêu cầu của người dùng.

## 4. Goal-Driven Execution — Thực Thi Hướng Mục Tiêu Kiểm Chứng Được
- **Biến yêu cầu mơ hồ thành mục tiêu kiểm chứng được (`Loop until verified`):**
  - *"Thêm validation"* → *"Viết kiểm thử cho các đầu vào sai, sau đó viết code để vượt qua kiểm thử"*.
  - *"Sửa lỗi X"* → *"Tái hiện lỗi X bằng test/script trước, sau đó sửa code và xác nhận lỗi biến mất"*.
  - *"Refactor Y"* → *"Đảm bảo toàn bộ kiểm thử và hành vi đầu ra giữ nguyên trước và sau khi sửa"*.
- Với tác vụ nhiều bước, luôn xác lập chuỗi kiểm chứng ngắn gọn kết nối với cổng `Falsifiable Verification Gate` của DeepSeek Harness:
  `1. [Bước thực hiện] → verify: [Lệnh/cách kiểm chứng thực tế]`

> Khi cần đối chiếu các mẫu Anti-Pattern thực tế (`❌ What LLMs Do` vs. `✅ What Should Happen`) hoặc tạo file `CLAUDE.md` cho dự án mới, hãy tham chiếu skill **[`karpathy-guidelines`](file:///d:/Antigravity/_agent/skills/karpathy-guidelines/SKILL.md)** và **[`EXAMPLES.md`](file:///d:/Antigravity/_agent/skills/karpathy-guidelines/references/EXAMPLES.md)**.
