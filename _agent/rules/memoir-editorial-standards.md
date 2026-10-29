---
trigger: model_decision
description: Áp dụng khi biên tập, rà soát, merge hoặc lập kế hoạch sửa cuốn hồi ký chị Theresa (Thu Thủy) do Hạnh Nguyễn viết - mọi file "TOÀN_TẬP_HỒI_KÝ...", "Hoi ky chi Hanh", "Master Manuscript".
---

# TIÊU CHUẨN BIÊN TẬP HỒI KÝ CHỊ THERESA (bắt buộc)

Trước khi làm bất cứ việc gì với bản thảo này, đọc và làm theo skill `memoir-editor`
(`d:\Antigravity\_agent\skills\memoir-editor\SKILL.md`) và nhật ký lỗi
(`d:\Antigravity\_agent\skills\memoir-editor\references\nhat_ky_loi.md`).

Tóm tắt các điều không được vi phạm:

1. Vai trò: nhân vật chính là chị Theresa (Thu Thủy); tác giả - người kể "tôi" là Hạnh Nguyễn (em gái); biên tập viên là Hương Thảo. Toàn bộ revision/track change trong Word luôn đặt tên tác giả là `Huong Thao`, tuyệt đối không để từ AI vào trong đó. Không xóa hay làm mất các revision cũ đã có trong file.
2. Không xóa bản gốc ngoài track change. Mọi câu của bản gốc phải còn trong file (nguyên hoặc dạng gạch).
3. Không bịa. Mọi chữ không có trong bản gốc `.pages`, Google Doc bổ sung hoặc bản sửa của người duyệt phải tô xanh lá - đo bằng `provenance.py`, không tô theo trí nhớ. Áp dụng cả câu nối, tả cảnh, chiêm nghiệm, chú thích lịch sử, và cả kế hoạch biên tập.
4. Không sửa đè, không làm mất track change cũ. Chỉ ghi file qua `docx_tc.py` (lxml, giữ namespace, tự kiểm toàn vẹn) và kiểm bằng `verify_word`.
5. Chạy `preflight.py` trước khi sửa để không làm việc trên file cũ.
6. Biên tập phải đạt chỉ tiêu định lượng (độ dài 65-85% gốc, câu > 35 chữ không quá 5/chương, 0 lỗi viết hoa danh xưng, 0 ghi chú nội bộ trong thân bài) - đo bằng `lint.py`.
7. Cắt lặp ý trong chương; chẻ câu dài; sửa chính tả - ngữ pháp - viết hoa; nối ý liền mạch khi chèn tư liệu; mỗi chương có mở (nêu vấn đề) - thân (diễn biến, hành động của chị) - kết (biến cố đã góp gì cho cuộc đời chị), dựng từ chất liệu sẵn có.
8. Giữ giọng mộc mạc của Hạnh; không biến hồi ký thành văn tiểu thuyết.
9. Không icon/emoji. Báo cáo bằng số đo của công cụ, không tự chấm điểm.
10. TUYỆT ĐỐI KHÔNG TỰ Ý CHẾ THÊM VĂN / VIẾT LẠI CÂU CHỮ ĐÃ CHỐT: Khi xuất bản hoàn chỉnh hoặc duyệt đề xuất từ Chương 1 đến Chương 5, CHỈ duyệt (chấp nhận/accept) toàn bộ Track Changes đã có từ file gốc chuẩn hóa đã chốt (`TOÀN_TẬP_HỒI_KÝ_BẢN_THẢO_GỐC_&_ĐỀ_XUẤT_BIÊN_TẬP_HIGHLIGHT_V7_CHUAN_HOA.docx`). Giữ nguyên vẹn từng câu chữ của tác giả Hạnh Nguyễn đã được thống nhất; giữ lại đúng nguyên văn 3 đoạn tác giả yêu cầu (tô vàng). Chỉ chèn thêm đúng những chi tiết tư liệu thực tế của chị Thủy và tác giả cung cấp (tô xanh lá). Nghiêm cấm việc tự ý viết lại, tự chế thêm từ ngữ, hoặc sửa đổi lời văn gốc làm sai lệch bản thảo đã chốt.

