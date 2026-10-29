# Antigravity Pro Brain Pack (Full Rules, 15 Skills, Lifecycle Hooks & Memory)

Bộ não cấu hình toàn diện của **Antigravity**, đóng gói trọn bộ **100% các Skill cũ và mới**, **13 Rules**, **Lifecycle Hooks tất định (`hooks.json`)**, **7 Workflows**, và **Bộ nhớ kiến trúc xuyên phiên (`PROJECT_MEMORY.md`)**.

---

## 1. Danh Mục Đầy Đủ Có Trong Gói Này

### A. 15 Skills Chuyên Sâu (`_agent/skills/`)
1. **`deepseek-harness-engine`**: Hệ thống suy luận sâu từ DeepSeek Harness (`dsh`) × Claude Code (*Plan-Todo-Goal Loop, 11 Defensive Patterns, Error Handling, Flaky Test Reliability, Code Review, Speed-Up Perf, Systematic Debugging 4 Pha & TDD, Subagent Worktree*).
2. **`karpathy-guidelines`**: 4 nguyên tắc vàng của Andrej Karpathy (*Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution*).
3. **`security-audit`**: Khung kiểm toán bảo mật 6 pha của Cloudflare kèm công cụ kiểm định `.cjs`.
4. **`vibe-security`**: Chống lỗ hổng bảo mật cho ứng dụng Vibe Code (*Zero Client Trust, RLS, Auth, Payment, Secrets*).
5. **`frontend-design`**: Hệ thống thiết kế UI/UX AI-Native toàn diện (*50+ styles, 97 palettes, UX Psychology, Animation, Motion Graphics, UI/UX Pro Max*).
6. **`mobile-design`**: Tư duy thiết kế & tối ưu hiệu năng ứng dụng iOS / Android (React Native, Flutter).
7. **`tailwind-patterns`**: Kiến trúc Design Token & chuẩn Tailwind CSS v4.
8. **`web-design-guidelines`**: Kiểm toán giao diện web chuẩn Accessibility & UX.
9. **`reverse-engineer-anything`**: Dịch ngược đa nền tảng (Native, Electron/JS, Android APK, Apple, Firmware) kết hợp MCP `rea`.
10. **`shopee-omnichannel-director`**: Quản trị & vận hành sàn Shopee 360 độ kết hợp Giá vốn Sapo (`COGS Margin Guard >= 60%`).
11. **`autonomous-seo-geo-engine`**: Cỗ máy tăng trưởng SEO & GEO độc lập chuẩn E-E-A-T 13 thành phần (2.500–3.500 từ).
12. **`youtube-factory`**: Tự động hóa kênh YouTube end-to-end (NotebookLM, Remotion, Upload YouTube Studio, Email Lead).
13. **`nlm-skill`**: Chuyên gia điều khiển NotebookLM CLI (`nlm`) toàn diện.
14. **`memoir-editor`**: Biên tập hồi ký chuyên sâu (Track Changes Word, đối chiếu bản gốc `.pages` & Google Docs).
15. **`chuyen-gia-sang-tao-tro-choi-bat-am`**: Thiết kế trò chơi giáo dục sớm 15 phút bật âm vô thức cho bé Bư & xuất tin nhắn Zalo theo khung giờ.

### B. 13 Rules Bảo Toàn & Kỹ Thuật (`AGENTS.md` + `_agent/rules/`)
- **Bảo toàn & Kỷ luật lõi (`Always On`):** `AGENTS.md`, `global-preservation-rules.md`, `deepseek-claude-harness-protocol.md`, `karpathy-coding-guidelines.md`, `vibe-code-security-protocol.md`, `multi-channel-safety.md`.
- **Quy chuẩn Dự án Chuyên biệt:** `crypto-analyzer-standards.md`, `crypto-data-pro-shorts-standards.md`, `beheritage-website-rules.md`, `memoir-editorial-standards.md`, `ebook-quality-standards.md`, `brand-storytelling-standards.md`, `video-production-standards.md`, `youtube-factory-rules.md`.

### C. Chốt Chặn Tất Định Lifecycle Hooks (`_agent/hooks.json` & `_agent/hooks/`)
- **`pre-tool-guard.cjs` (`PreToolUse`):** Chặn lệnh xóa dữ liệu nguy hiểm (`git reset --hard`, `git clean -fd`) và bảo vệ file `.env` / khóa bí mật.
- **`post-edit-verify.cjs` (`PostToolUse`):** Kiểm tra tính hợp lệ của file cấu hình `.json` ngay sau khi sửa.
- **`session-start-memory.cjs` (`SessionStart`):** Nạp bản đồ kiến trúc từ `_agent/memory/PROJECT_MEMORY.md` khi bắt đầu phiên mới.

---

## 2. Cách Cài Đặt Sang Máy Khác (Chỉ 1 Lệnh Duy Nhất)

Trên máy mới (đã cài Antigravity và Git):

```powershell
# Bước 1: Clone kho lưu trữ về máy mới
git clone <URL_GITHUB_REPO_CUA_BAN> d:\Antigravity
cd d:\Antigravity

# Bước 2: Chạy script tự động đồng bộ toàn bộ 15 Skills vào cả Workspace và Global (~/.gemini)
powershell -ExecutionPolicy Bypass -File .\_agent\install-antigravity-brain.ps1
```

Ngay sau khi chạy lệnh trên, Antigravity ở máy mới sẽ có **100% sức mạnh, kỹ năng, quy tắc bảo toàn, bộ nhớ và chốt chặn bảo mật** giống hệt máy gốc của bạn.
