---
trigger: always_on
description: Giao thức Bảo mật Tuyệt đối cho mọi App/Tool Vibe Code (Cloudflare Security-Audit-Skill × Vibe-Security Guardrails)
---

# Giao Thức Bảo Mật Tuyệt Đối Cho App & Tool Vibe Code

Mọi ứng dụng, công cụ, API, bot, script và hệ thống web được xây dựng ("vibe code") hoặc chỉnh sửa trong Antigravity bắt buộc phải tuân thủ nghiêm ngặt khung bảo mật kép kết hợp giữa **`security-audit`** (Cloudflare 6-Phase Security Audit Harness) và **`vibe-security`**:

## 1. Nguyên Tắc Bất Khả Xâm Phạm: Zero Client Trust (Không Tin Tưởng Client)
- **Mọi dữ liệu từ phía Client đều bị coi là do kẻ tấn công kiểm soát:** Giá tiền (`price`/`amount`), `user_id`, quyền hạn (`role`), trạng thái gói cước (`plan`/`subscription`), số dư ví, bộ đếm giới hạn (`rate_limit`) và cờ tính năng (`feature_flag`) **BẮT BUỘC** phải được truy vấn và kiểm chứng ở phía Server (Backend/Database). Tuyệt đối không lấy giá tiền hay quyền hạn trực tiếp từ `req.body`, query params hay `localStorage` để xử lý nghiệp vụ.
- **Bảo vệ Bí mật & Biến môi trường (Secrets & Env Hygiene):**
  - Không bao giờ hardcode API Key, Secret Token, Private Key, chuỗi kết nối DB hoặc mật khẩu SMTP vào mã nguồn.
  - Tuyệt đối không gắn tiền tố lộ ra client (`NEXT_PUBLIC_`, `VITE_`, `EXPO_PUBLIC_`, `REACT_APP_`) cho các khóa đặc quyền như `service_role` (Supabase), Admin SDK, Stripe Secret Key, OpenAI/Gemini/Anthropic API Key hay Telegram Bot Token.
  - Luôn đảm bảo `.env`, `.env.*`, `*.pem`, `*.key`, `credentials.json` nằm trong `.gitignore` trước khi commit.

## 2. Chốt Chặn 8 Bề Mặt Tấn Công Phổ Biến Nhất Của App Vibe Code
Khi viết hoặc sửa bất kỳ tính năng nào liên quan đến 8 bề mặt sau, Agent phải chủ động áp dụng cơ chế phòng thủ ngay trong lúc viết code:
1. **Xác thực & Phân quyền (AuthN & AuthZ / IDOR):** Mọi API endpoint, Server Action, RPC hoặc webhook phải xác thực danh tính ở tầng đầu vào và kiểm tra quyền sở hữu tài nguyên (Ownership Check / Row-Level Security - RLS) trước khi đọc/ghi/xóa.
2. **Truy cập Cơ sở dữ liệu & Chống Injection:** Bắt buộc dùng Parameterized Queries / Prepared Statements hoặc ORM an toàn; nghiêm cấm nối chuỗi trực tiếp vào câu lệnh SQL/NoSQL/Shell (`child_process.exec`).
3. **Thanh toán & Ví điện tử (Payment & Billing Integrity):** Luôn đối chiếu chữ ký cryptographic (`webhook signature`), kiểm tra tính duy nhất của giao dịch (`idempotency` / chống cộng tiền lặp `double-credit`), và tính toán số tiền thanh toán từ bảng giá gốc trên Server.
4. **Tích hợp AI / LLM & Agent Tools:** Đặt giới hạn token/quota, bọc dữ liệu người dùng tách biệt khỏi system prompt (chống Prompt Injection), không truyền trực tiếp đầu ra của LLM vào `eval`, shell, SQL hoặc `dangerouslySetInnerHTML` khi chưa làm sạch (sanitize).
5. **Giao diện Web & Client-Side (XSS / CSRF / CORS):** Escape dữ liệu hiển thị, cấu hình CORS theo danh sách tên miền xác định (không dùng `*` kèm credentials), thiết lập cookie `HttpOnly`, `Secure`, `SameSite`.
6. **Upload File & Xử lý Đường dẫn (Path Traversal & SSRF):** Kiểm tra định dạng thực tế (magic bytes/MIME), giới hạn kích thước, đổi tên file ngẫu nhiên, chặn ký tự `..` hoặc symlink khi đọc/ghi file, và chặn IP nội bộ (`127.0.0.1`, `169.254.169.254`, mạng LAN) khi server tải URL từ người dùng.
7. **Giới hạn Tốc độ & Chống Cạn kiệt Tài nguyên (Rate Limiting & DoS):** Áp dụng rate-limit phía server cho các luồng đăng nhập, gửi OTP, tạo đơn hàng, rút tiền và gọi API AI tốn phí.
8. **Chuỗi cung ứng & Cài đặt Gói (Supply Chain):** Chỉ sử dụng thư viện chính thống, khóa phiên bản (`package-lock.json` / `requirements.txt`), không tự động thực thi mã nguồn hoặc script không rõ nguồn gốc ngoài vùng cô lập (`scratch/`).

## 3. Kích Hoạt Quy Trình Kiểm Toán Bảo Mật (`security-audit` & `vibe-security`)
- **Khi đang viết hoặc sửa tính năng nhạy cảm (Guidance Mode):** Chủ động tham chiếu sổ tay chuyên sâu trong skill [`vibe-security`](file:///d:/Antigravity/_agent/skills/vibe-security/SKILL.md) và [`security-audit`](file:///d:/Antigravity/_agent/skills/security-audit/SKILL.md) (như `WEB-PROTOCOL-AND-AUTH.md`, `AI-AND-LLM.md`, `CLIENT-SIDE.md`, `DATA-ISOLATION-AND-LIFECYCLE.md`) để rà soát ranh giới tin cậy (Trust Boundary) trước khi bàn giao.
- **Khi người dùng yêu cầu rà soát bảo mật, kiểm tra trước khi ra mắt (Pre-launch) hoặc Pen-test (Full Audit Mode):** Kích hoạt đầy đủ quy trình 6 pha của Cloudflare [`security-audit`](file:///d:/Antigravity/_agent/skills/security-audit/SKILL.md) (Reconnaissance → Coverage-led Hunting → Candidate Validation → Structured Output → Independent Verification → Target-Neutral Report) và chạy bộ kiểm định `validate-coverage-ledger.cjs` + `validate-findings.cjs`.
