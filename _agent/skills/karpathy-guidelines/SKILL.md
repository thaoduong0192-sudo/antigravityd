---
name: karpathy-guidelines
description: >-
  Bộ 4 nguyên tắc hành vi cốt lõi của Andrej Karpathy (multica-ai/andrej-karpathy-skills - 225K+ GitHub Stars)
  giúp triệt tiêu các lỗi kinh điển của Coding Agent: Think Before Coding (Không đoán mò, phơi bày giả định & đánh đổi),
  Simplicity First (Tối giản trước tiên, chống Overengineering), Surgical Changes (Phẫu thuật chính xác, giữ chặt biên giới diff),
  và Goal-Driven Execution (Thực thi hướng mục tiêu kiểm chứng được). Kích hoạt khi viết code mới, sửa lỗi, refactor
  hoặc thiết kế CLAUDE.md / AGENTS.md cho dự án.
license: MIT
---

# Karpathy Coding Guidelines (`multica-ai/andrej-karpathy-skills` × Antigravity Edition)

Bộ quy tắc hành vi nhằm giảm thiểu các sai lầm phổ biến nhất của LLM Coding Agent, được đúc kết từ các quan sát thực chiến của **Andrej Karpathy** ([bài gốc trên X](https://x.com/karpathy/status/2015883857489522876)) và kho mã nguồn trending GitHub **[multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)**.

> **Đánh đổi (Tradeoff):** Bộ nguyên tắc này ưu tiên **sự cẩn trọng hơn tốc độ thuần túy**. Với các tác vụ cực kỳ đơn giản (sửa lỗi chính tả, sửa 1 dòng hiển nhiên), hãy linh hoạt xử lý ngay mà không làm chậm quy trình.

---

## 4 Nguyên Tắc Cốt Lõi (The Four Core Principles)

### 1. Think Before Coding — Suy Nghĩ Trước Khi Viết Code
**Đừng đoán mò. Đừng giấu sự bối rối. Hãy phơi bày các đánh đổi (Surface tradeoffs).**

Trước khi bắt tay vào cài đặt (implement):
- **Nêu rõ các giả định (State assumptions explicitly):** Nếu sau khi đọc mã nguồn mà yêu cầu nghiệp vụ vẫn còn điểm chưa chắc chắn, hãy hỏi lại thay vì tự ý đoán.
- **Trình bày các cách hiểu khác nhau (Present multiple interpretations):** Khi một yêu cầu có nhiều hướng hiểu (ví dụ: "làm tìm kiếm nhanh hơn" là tối ưu DB latency, tăng throughput hay làm mượt UX?), hãy liệt kê ngắn gọn kèm ước lượng đánh đổi — tuyệt đối không âm thầm chọn đại một hướng.
- **Phản biện kỹ thuật khi cần (Push back when warranted):** Nếu có cách tiếp cận đơn giản hơn, an toàn hơn so với yêu cầu ban đầu, hãy chủ động đề xuất.
- **Dừng lại khi mơ hồ (Stop when confused):** Chỉ rõ điểm đang mâu thuẫn hoặc thiếu thông tin và hỏi người dùng trước khi code.

### 2. Simplicity First — Tối Giản Trước Tiên
**Viết lượng code tối thiểu giải quyết đúng bài toán hiện tại. Không viết code suy diễn tương lai (Nothing speculative).**

Chống lại xu hướng "overengineering" của LLM:
- **Không thêm tính năng ngoài yêu cầu:** Không tự đẻ thêm bộ lọc, thông báo, cache hay cấu hình khi chưa được yêu cầu.
- **Không tạo lớp trừu tượng (abstraction/strategy/factory) cho đoạn code chỉ dùng 1 lần.**
- **Không thêm "độ linh hoạt" hoặc "khả năng cấu hình hóa" thừa thãi.**
- **Không viết xử lý lỗi cho các kịch bản bất khả thi về mặt logic nội bộ.**
- **Nếu viết 200 dòng cho việc chỉ cần 50 dòng, hãy viết lại (đối với code mới).**

> **Bài kiểm tra chuẩn:** *"Một kỹ sư Senior nhìn vào có bảo đoạn code này đang làm phức tạp hóa vấn đề không?"* Nếu có, hãy rút gọn ngay.

### 3. Surgical Changes — Phẫu Thuật Chính Xác
**Chỉ chạm vào đúng chỗ bắt buộc phải sửa. Chỉ dọn dẹp phần rác do chính mình tạo ra.**

Khi chỉnh sửa mã nguồn hiện có:
- **Không tự ý "cải tiến" code lân cận, comment hay định dạng (formatting).**
- **Không refactor những phần đang chạy ổn định và không liên quan.**
- **Tuân thủ tuyệt đối văn phong code hiện hữu (Match existing style):** Giữ nguyên kiểu dấu nháy (`'` hay `"`), quy ước đặt tên, thụt lề, cách viết hàm của file đó — ngay cả khi bạn thích viết kiểu khác.
- **Nếu phát hiện code thừa (dead code) có sẵn từ trước:** Chỉ nêu nhận xét báo cho người dùng, **tuyệt đối không tự ý xóa**.

Khi thay đổi của BẠN tạo ra phần tử mồ côi (orphans):
- **Xóa bỏ các `import`, biến, hoặc hàm phụ trợ mà CHÍNH THAY ĐỔI CỦA BẠN làm cho không còn dùng nữa.**
- **Không xóa dead code tồn tại từ trước trừ khi người dùng yêu cầu rõ.**

> **Bài kiểm tra chuẩn:** Mọi dòng thay đổi trong `git diff` phải truy nguyên trực tiếp về đúng yêu cầu của người dùng.

### 4. Goal-Driven Execution — Thực Thi Hướng Mục Tiêu Kiểm Chứng Được
**Định nghĩa tiêu chí thành công tường minh. Lặp cho đến khi kiểm chứng xong (Loop until verified).**

Chuyển hóa các yêu cầu mệnh lệnh mơ hồ thành mục tiêu có thể kiểm chứng:
- *"Thêm kiểm tra đầu vào (validation)"* → *"Viết test cho các đầu vào không hợp lệ, sau đó viết code để test pass"*.
- *"Sửa lỗi X"* → *"Viết test tái hiện chính xác lỗi X (chứng minh test fail), sau đó sửa code để test pass"*.
- *"Refactor module Y"* → *"Đảm bảo toàn bộ test pass trước và sau khi refactor, hành vi đầu ra giữ nguyên 100%"*.

Đối với tác vụ nhiều bước, luôn phát biểu kế hoạch kiểm chứng ngắn gọn:
```text
1. [Bước 1] → verify: [Cách kiểm chứng cụ thể]
2. [Bước 2] → verify: [Cách kiểm chứng cụ thể]
3. [Bước 3] → verify: [Cách kiểm chứng cụ thể]
```

---

## Ma Trận Tương Thích Với Hệ Sinh Thái Rule Của Antigravity (Compatibility Matrix)

Skill này được tích hợp đồng bộ 100% với các Rule hiện hành trong `d:\Antigravity\_agent\rules\`, tuân thủ thứ tự ưu tiên sau để tránh mọi xung đột:

| Rule Kết Hợp | Điểm Giao Thoa | Quy Tắc Tương Thích Bắt Buộc |
| :--- | :--- | :--- |
| **[AGENTS.md](file:///d:/Antigravity/AGENTS.md)** & **[global-preservation-rules.md](file:///d:/Antigravity/_agent/rules/global-preservation-rules.md)** | *Simplicity First* vs. *Bảo toàn tính năng đã duyệt* | Quy tắc *"rút gọn 200 dòng xuống 50 dòng"* **chỉ áp dụng cho code mới đang viết trong phiên hiện tại**. Tuyệt đối KHÔNG dùng *Simplicity First* để thu nhỏ, cắt bớt hoặc viết lại các tính năng, giao diện Admin, báo cáo AI 5 chương, biểu đồ hay E-Learning đã được duyệt. |
| **[deepseek-claude-harness-protocol.md](file:///d:/Antigravity/_agent/rules/deepseek-claude-harness-protocol.md)** | *Think Before Coding* vs. *Explore First* | **Explore First trước, Ask sau:** Bắt buộc dùng `read_file` / `rg` tự khảo sát mã nguồn để giải đáp các thắc mắc kỹ thuật trước. Chỉ áp dụng *Think Before Coding* để hỏi người dùng về sự mơ hồ nghiệp vụ, đa cách hiểu hoặc đánh đổi thiết kế không có sẵn trong code. |
| **[deepseek-claude-harness-protocol.md](file:///d:/Antigravity/_agent/rules/deepseek-claude-harness-protocol.md)** | *Goal-Driven Execution* × *Falsifiable Verification Gate* | Mỗi bước `[Step] → verify: [check]` của Karpathy chính là đầu vào cho vòng lặp `Explore → Plan → Todo → Execute → Verify` và cổng kiểm định thực tế của DeepSeek Harness. |
| **[vibe-code-security-protocol.md](file:///d:/Antigravity/_agent/rules/vibe-code-security-protocol.md)** | *Simplicity First* vs. *Zero Client Trust* | Quy tắc *"không bắt lỗi kịch bản bất khả thi"* chỉ áp dụng cho hàm nội bộ đã có kiểu/trạng thái đảm bảo. Tại **Trust Boundary** (API, Webhook, Form, DB, Auth, Payment), bắt buộc giữ đủ kiểm tra xác thực, phân quyền, kiểm chứng giá/quyền ở Server và Parameterized Queries. |

---

## Tài Liệu Tham Chiếu Trong Skill (`references/`)

- **[EXAMPLES.md](./references/EXAMPLES.md):** Bộ ví dụ thực tế đối chiếu trực tiếp `❌ What LLMs Do` và `✅ What Should Happen` cho cả 4 nguyên tắc (Hidden Assumptions, Multiple Interpretations, Over-abstraction, Speculative Features, Drive-by Refactoring, Style Drift, Vague vs. Verifiable, Test-First Verification).
- **[CLAUDE.md](./references/CLAUDE.md):** Bản gốc tiếng Anh nguyên bản từ kho `multica-ai/andrej-karpathy-skills` để nhúng nhanh vào các dự án mới khi cần.
