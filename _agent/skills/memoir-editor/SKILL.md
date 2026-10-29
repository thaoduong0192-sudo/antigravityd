---
name: memoir-editor
description: Biên tập hồi ký chị Theresa (Thu Thủy) do Hạnh Nguyễn viết - track change trên file Word, đối chiếu bản gốc .pages và Google Doc chị Thủy bổ sung, tô xanh lá chi tiết tự viết thêm, cắt lặp ý, chẻ câu dài, sửa chính tả - ngữ pháp - viết hoa, nối ý, kiểm cấu trúc mở - thân - kết. Kích hoạt khi người dùng yêu cầu sửa, rà soát, merge, khôi phục hoặc lập kế hoạch biên tập bất kỳ chương nào của cuốn hồi ký.
---

# KỸ NĂNG BIÊN TẬP HỒI KÝ CHỊ THERESA

Đọc theo thứ tự, không bỏ bước. Trước khi làm, đọc [nhat_ky_loi.md](references/nhat_ky_loi.md) - 18 lỗi đã thật sự xảy ra. Mỗi quy tắc dưới đây sinh ra từ một lỗi trong đó.

## 0. Vai trò (không được nhầm)

| Vai | Là ai | Ghi chú |
|---|---|---|
| Nhân vật chính | Chị Theresa Nguyễn Thị Thu Thủy (Bác sĩ Thủy). Trong ghi chú: "CT" | Hành động nhiều hơn lời nói; khiêm nhường; y đức đến từ mất mát thật của gia đình |
| Tác giả / người kể "tôi" | Hạnh Nguyễn (Hanah), em gái út. Trong ghi chú: "H" | Giọng mộc mạc, chân thành, thương kính chị. Phải nhận ra được giọng này xuyên suốt sách |
| Biên tập viên | Hương Thảo | Gọt giũa văn phong, cấu trúc, nhịp điệu |
| Revision author trong Word | Luôn đặt tên là `Huong Thao` | Theo yêu cầu dứt khoát của tác giả: KHÔNG để từ AI vào trong đó. Toàn bộ track change biên tập viên thực hiện đều mang tên `Huong Thao` |

## 1. Mười một quy tắc bắt buộc

**R1. Không bao giờ xóa bản gốc ngoài track change.** Mọi bỏ - thêm - sửa đều là `w:del` / `w:ins`. Không viết lại cả đoạn rồi chèn như văn bản mới. Câu nào của bản gốc cũng phải còn trong file: hoặc nguyên vẹn, hoặc dưới dạng gạch track change. Kiểm bằng `silent_cuts` - kết quả mới phát sinh phải bằng 0.

**R2. Không bịa. Thứ gì không có trong nguồn thì tô xanh lá.** Nguồn gồm: bản gốc `.pages` của cụm chương đó, Google Doc chị Thủy/Hạnh bổ sung, và track change `Huong Thao`. Chỉ được làm "sinh động" bằng chính chi tiết có trong nguồn. Câu nối ý, câu tả cảnh, câu chiêm nghiệm, dữ kiện lịch sử trong chú thích mà nguồn không có => tô xanh lá (`<w:highlight w:val="green"/>`). Đừng tô bằng trí nhớ: dùng `audit_ai_insertions` để máy đo. Không thêm chi tiết giác quan (mùi, âm thanh, thời tiết, nước mắt) nếu nguồn không nói; muốn có thì đặt thành câu hỏi cho tác giả.

**R3. Giữ giọng văn hai nhân vật.** Sửa tối thiểu cần thiết. Giữ từ ngữ mộc mạc Nam Bộ của tác giả. Không biến văn hồi ký thành văn tiểu thuyết bóng bẩy ("miệng sóng gầm gào", "vết cắt sâu thẳm trong tâm can" là văn của AI, không phải của Hạnh).

**R4. Cắt lặp ý, lặp lý, lặp từ - triệt để trong phạm vi một chương.** Cùng một ý ("nhà đông con nghèo khó", "chị đẹp chị giỏi", "cánh đồng") xuất hiện nhiều lần trong chương: giữ lần đắt nhất, gạch các lần còn lại. Ngoại lệ do tác giả yêu cầu: một ý cốt lõi ĐƯỢC nhắc lại ngắn gọn ở chương khác để người đọc bỏ lỡ chương trước vẫn hiểu.

**R5. Không chạm vào track change cũ.** Không sửa đè lên chữ nằm trong `w:ins`/`w:del` của người khác. `docx_tc` tự từ chối thao tác và từ chối lưu nếu mất dù chỉ một revision cũ.

**R6. Nối ý liền mạch.** Khi đưa tư liệu bổ sung của chị Thủy vào, thêm 1 câu dẫn trước và (nếu cần) 1 câu khép sau để khớp với đoạn trước/sau. Câu nối không có trong nguồn => tô xanh (R2). Đặt tư liệu đúng vị trí thời gian của câu chuyện, không dán thành khối rời cuối chương.

**R7. Chính tả - ngữ pháp - viết hoa.** Sửa câu thiếu chủ ngữ/vị ngữ, câu què, sai dấu, dính chữ ("ởTrường"). Danh xưng thân tộc giữa câu viết thường: ba, má, chị, em, bà cố, bà nội, cô, dì, chú, bác (kể cả trong lời thoại: "Bà xuống đây đi bà"). Theo cách người duyệt đã sửa: "thiên ý" viết thường trong ngoặc kép, "thượng đế" viết thường. Viết hoa: tên riêng, địa danh, tên trường, tôn danh tôn giáo (Đức Mẹ, Quán Thế Âm Bồ Tát).

**R8. Chẻ câu dài.** Câu trên 35 chữ hoặc có từ 3 mệnh đề trở lên: chẻ thành 2-3 câu ngắn, giữ nguyên ý và chữ của tác giả, chỉ thêm/bớt từ nối. Đây là thay đổi track change bình thường, không tô xanh.

**R9. Không để ghi chú nội bộ trong thân bài.** Không chèn "[Chi tiết biên tập viên ...]", "[Đoạn tư liệu ...]" vào giữa văn bản. Câu hỏi cho tác giả để trong khối đề xuất đầu chương hoặc báo cáo. Không nhân đôi khối "Cập nhật biên tập".

**R10. Không icon/emoji** trong file, nhận xét, báo cáo.

**R11. Báo cáo bằng số đo, không bằng lời hứa.** Không nói "đã đạt 10/10", "đã rà soát kỹ" nếu chưa có output của `lint.py`, `silent_cuts`, `audit_ai_insertions`, `verify_word`.

## 2. Chỉ tiêu định lượng mỗi chương (chống sửa hời hợt)

Rút từ phần người duyệt tự sửa Chương 1-5 và số đo V7 (xem nhật ký lỗi):

- Độ dài bản cuối: **65-85% bản gốc**. Trên 90% là sửa chưa tới; trên 100% là đang thêm thắt (Chương 1 và 3 hiện đang 107% và 104%).
- Câu trên 35 chữ còn lại: **không quá 5**, mỗi câu giữ lại phải có lý do.
- Danh xưng viết hoa sai giữa câu, ghi chú nội bộ trong thân bài: **0**.
- Cụm rào đón của người kể ("Tôi không biết...", "Trong trí tưởng tượng của tôi...", "Tôi không muốn viết thay cảm xúc..."): giữ tối đa 1-2 chỗ thật cần thiết cho cả chương.
- Câu gốc bị mất ngoài track change (`silent_cuts` mới phát sinh): **0**.
- Mọi `w:ins` của AI từ 3 chữ trở lên không phải "GỐC": **100% xanh lá**.

## 3. Quy trình mỗi chương (bắt buộc đủ 8 bước)

Công cụ ở `scripts/` (Python, chạy trên Windows). Không tự viết script XML mới; nếu thiếu chức năng thì bổ sung vào `docx_tc.py` và chạy lại kiểm thử.

**Bước 0 - Kiểm tra file.** `python scripts/preflight.py "<file>"`. Có cảnh báo (file đang mở, bản mới hơn, AutoRecover mới hơn) => dừng, hỏi người dùng dùng file nào. Lưu lại bảng revision theo tác giả x chương để so sau khi sửa.

**Bước 1 - Đọc trọn chương và nguồn.** Đọc toàn văn vùng bản thảo (`Doc.manuscript_range(n)`), đoạn tương ứng trong `resources/sources/goc_*.txt` và phần liên quan trong `gdoc_bo_sung_chi_thuy.txt`. Nếu nguồn có thay đổi, chạy `scripts/build_sources.py`. Không lập kế hoạch khi chưa đọc xong.

**Bước 2 - Lập bảng tư liệu.** Ba danh sách, mỗi mục ghi số đoạn (P...):
  (a) sự kiện có nguồn (trích nguyên văn ngắn); (b) tư liệu Google Doc chưa có trong bản thảo + vị trí sẽ chèn; (c) cụm lặp ý (liệt kê tất cả lần xuất hiện, chọn lần giữ lại).

**Bước 3 - Khung mở - thân - kết, dựng từ chất liệu có sẵn.**
  - Mở: câu/đoạn gốc nào nêu vấn đề hoặc biến cố của chương (đưa lên đầu nếu đang nằm giữa).
  - Thân: chuỗi sự kiện theo thời gian, hành động của chị trước, cảm xúc của người em sau (thứ tự: cảnh - hành động của chị - phản ứng người xung quanh - chiêm nghiệm của em).
  - Kết: chọn đoạn chiêm nghiệm sẵn có của tác giả trả lời "biến cố này đã góp gì cho con người và hành trình của chị". Nếu không có, viết 1-2 câu ngắn, tô xanh, và ghi vào báo cáo để tác giả duyệt.
  Khi người dùng yêu cầu "kế hoạch trước", trình bày Bước 2-3 rồi dừng chờ duyệt.

**Bước 4 - Sửa bằng `docx_tc`.** Thứ tự: (1) cắt lặp ý; (2) chèn tư liệu bổ sung + câu nối; (3) sắp lại mở/kết nếu cần (bằng gạch ở chỗ cũ + chèn ở chỗ mới); (4) chẻ câu dài; (5) chính tả, ngữ pháp, viết hoa, từ lặp. Mỗi thao tác có `reason` ngắn.

**Bước 5 - Đo nguồn gốc.** `audit_ai_insertions` (tự tô xanh), `audit_final_text` (liệt kê câu không nguồn), `silent_cuts` (phải không tăng so với trước khi sửa).

**Bước 6 - Đo chất lượng.** `python scripts/lint.py "<file>" <n>`. Chưa đạt chỉ tiêu mục 2 => quay lại Bước 4.

**Bước 7 - Đọc lại cả chương như độc giả.** Đọc liền bản Accept All từ đầu đến cuối: đoạn nào chuyển ý gãy, mở bài có nêu vấn đề không, kết có đọng lại bài học/ý nghĩa không, giọng có còn là Hạnh không, chị có phải nhân vật trung tâm không. Sửa tiếp nếu cần.

**Bước 8 - Lưu và kiểm chứng.** `Doc.save()` (tự kiểm toàn vẹn revision, tự sao lưu nếu ghi đè) rồi `verify_word()`. Chạy lại `preflight.py` trên file mới: số revision `Huong Thao` từng chương phải y hệt Bước 0.

## 4. Báo cáo cho người duyệt (mỗi lần giao file)

1. Đường dẫn file mới và file sao lưu.
2. Bảng mỗi chương: độ dài gốc -> cuối (%), số chỗ cắt lặp ý, số câu đã chẻ, số lỗi chính tả/viết hoa đã sửa, số đoạn tư liệu Google Doc đã chèn.
3. Danh sách mọi chỗ xanh lá (số đoạn + trích ngắn) để tác giả xác nhận.
4. Câu hỏi cần hỏi chị Thủy (thay cho việc tự bịa chi tiết).
5. Kết quả kiểm chứng: Word mở được, số revision cũ giữ nguyên.
Không icon. Không tự chấm điểm.

## 5. Chỉ đạo riêng của tác giả (từ Google Doc - phải tuân thủ)

- "Thiên Ý": hiểu là chông gai, thử thách giúp chị mạnh mẽ hơn cho hành trình sau; tránh màu sắc dị đoan, mê tín.
- Chương 3: dùng đúng 4 câu thơ Hạnh tự sáng tác. Cảnh đón ở phi trường Melbourne năm 1991 có thể lược bỏ.
- Chương 4: giữ bài hát "Chị tôi" của Trần Tiến (làm cô đọng), ưu tiên hơn ẩn dụ hoa sen.
- Chương 5: dùng chi tiết thật về đêm chia tay ba má 15/11/1978 và gói hành lý do tác giả cung cấp - không thêm thắt.
- Chương 12-13: cẩn trọng từ ngữ y khoa - tâm linh (phát hành trong nước).
- Chương 15: không nhắc chữa bệnh miễn phí công khai; chỉ diễn đạt ở phương diện y khoa, xoa dịu tâm lý, hỗ trợ giải tỏa thể chất và tinh thần.
- Chương 16: không dùng "chữa lành bằng tâm linh", "hết bệnh"; nhấn mạnh giải tỏa, xoa dịu nỗi đau, thay đổi theo hướng yêu thương, từ bi, cải thiện các mối quan hệ.
- Chương 19: đính chính - chị về Phú Yên tổ chức hội thảo về năng lượng sinh học, KHÔNG có cảnh quỳ hôn đất mẹ ở Long Thạnh Mỹ (tiêu đề "TRỞ VỀ QUÊ HƯƠNG, HÔN LÊN MẸ ĐẤT" cần xem lại).

## 6. Tệp và đường dẫn

- File làm việc chính: `C:\Users\US\Downloads\Hoi ky chi Hanh\TOÀN_TẬP_HỒI_KÝ_BẢN_THẢO_GỐC_&_ĐỀ_XUẤT_BIÊN_TẬP_HIGHLIGHT_V7_CHUAN_HOA.docx` (luôn xác nhận lại bằng `preflight.py`).
- Bản gốc: 4 file `.pages` trong `C:\Users\US\Downloads\Hoi ky chi Hanh\` (Lời mở đầu-Ch5, Ch6-11, Ch12-16, Ch17-22 + Lời kết) -> cache tại `resources/sources/`.
- Google Doc bổ sung: `15M38L4HifB0DVfFE3k6wqOmHM8-lI6xMm_cQQ27Pnz8` -> `resources/sources/gdoc_bo_sung_chi_thuy.txt`.
- Tên file Windows có dấu và ký tự `&`: trong PowerShell đặt trong nháy đơn; trong Python dùng chuỗi `r'...'` và `sys.stdout.reconfigure(encoding='utf-8')`.
- Người dùng nói "sửa trực tiếp file này" thì ghi vào file đó (docx_tc tự sao lưu trước). Không nói gì thì xuất file mới có hậu tố mô tả, không ghi đè.
