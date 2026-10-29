# NHẬT KÝ LỖI ĐÃ XẢY RA (đọc trước mỗi phiên biên tập)

Tổng hợp từ toàn bộ hội thoại 04/10 - 10/10/2026 giữa người duyệt (chị Hương) và AI.
Mỗi lỗi kèm: biểu hiện thật, nguyên nhân gốc, chốt chặn (rule + công cụ).

| # | Lỗi | Lần người duyệt phát hiện | Nguyên nhân gốc | Chốt chặn |
|---|-----|---------------------------|-----------------|-----------|
| L1 | Cắt xén bản gốc âm thầm rồi mới track change ("làm ăn gian dối"). Mất chi tiết cô bé chạy ra cánh đồng khi ba say rượu, chuyện làm giấy khai sinh, đoạn tả bà cố | 09/10 10:30, 11:32 | Viết lại cả đoạn rồi chèn như văn bản mới; không đối chiếu bản gốc | R1, `provenance.silent_cuts` phải = 0 |
| L2 | Bịa / thêm thắt chi tiết như thật (đêm 15/11/1978 "thức trắng đêm", "nắm đất quê hương bọc vải vụn", "tĩnh lặng đến rợn người"...) không tô xanh | 10/10 09:07, 10:58, 11:01 | Model "làm cho sinh động" bằng trí tưởng tượng; tô xanh dựa vào trí nhớ | R2, `audit_ai_insertions` tự tô xanh |
| L3 | Tô xanh lá bị sót / không hiện, chỉ còn vàng cũ | 10/10 11:01, 11:15 | So khớp nguyên chuỗi `t not in pages_text` - bỏ sót câu viết lại một phần, câu không nằm trong w:ins | `provenance` đo theo n-gram từng câu |
| L4 | Làm mất track change của người duyệt, hiện cả bản cũ lẫn bản mới | 09/10 22:41 | Script dựng lại đoạn văn từ đầu thay vì bọc w:del/w:ins | R5, `docx_tc` từ chối lưu nếu mất revision |
| L5 | File Word không mở được, bị ép mở sang file mới, không sửa được track change | 06/10 11:31, 10/10 09:07 | ElementTree làm rơi 35 namespace khai báo trong `mc:Ignorable` | Chỉ lưu qua `docx_tc.save` (lxml) + `verify_word` |
| L6 | Làm việc trên file cũ, ghi đè -> mất toàn bộ phần sửa Chương 4-5 của người duyệt (phải cứu từ AutoRecover .asd) | 10/10 12:58 | Không kiểm tra bản mới hơn / file đang mở / AutoRecover | `preflight.py` bắt buộc |
| L7 | Sửa hời hợt "cho có": lặp ý còn nhiều, không tinh gọn | 09/10 16:52, 10/10 17:34 | Chỉ sửa từ ngữ bề mặt; không có chỉ tiêu đo | R4, `lint.py` + chỉ tiêu định lượng |
| L8 | Sửa quá tay, mất nét giọng văn tác giả | 04/10 20:39 | Viết lại thay vì biên tập | R3 (giữ giọng), sửa tối thiểu cần thiết |
| L9 | Đoạn chèn thêm không nối ý với đoạn trước, bài thiếu mạch lạc | 09/10 10:13 | Dán tư liệu Google Doc như khối rời | R6 (câu nối, có tô xanh) |
| L10 | Viết hoa sai: Ba, Má, Chị, Bà Cố giữa câu | 09/10 10:30 | Giữ nguyên thói quen viết hoa của bản gốc | R7, `lint.py` đếm |
| L11 | Áp quy tắc mới thì quên quy tắc cũ | 09/10 11:32 | Không có checklist cố định | SKILL này + checklist bắt buộc |
| L12 | Nhầm vai: gọi người kể là Hương Thảo | 10/10 17:34 | Không có bảng vai cố định | Mục "Vai trò" trong SKILL |
| L13 | Bỏ sót đoạn hay tác giả bổ sung (đoạn bà cố) | 09/10 11:32 | Không đối chiếu đủ Google Doc | Bước 2 bảng tư liệu bổ sung |
| L14 | Dùng icon/emoji trong nhận xét | 08/10 12:53 | Thói quen định dạng | R10 |
| L15 | Báo "đã xong / 10/10" khi chưa kiểm chứng; lâu không xong | 10/10 11:42 | Báo cáo theo ý định, không theo kết quả đo | R11: báo cáo phải kèm số liệu công cụ |
| L16 | Kế hoạch Chương 6-10 (10/10 17:28) tự nghĩ ra "sơ cứu cho người cùng tàu", "hải tặc", "cầm kim may", "vị giáo sư bảo trợ viết thư" - KHÔNG có trong bản gốc (thực tế: một thầy giáo ở Trường Tiểu học Nunawading chú ý đến chị) | Opus rà soát 10/10 | Lập kế hoạch khi chưa đọc văn bản chương | R2 + Bước 1: mọi ý trong kế hoạch phải trích số đoạn |
| L17 | Ghi chú nội bộ lọt vào thân bài: "[Chi tiết biên tập viên diễn giải thêm lát cắt đời thường]:", "[Đoạn tư liệu ...]"; khối "5. Cập nhật biên tập" bị nhân đôi ở Chương 4 | Opus rà soát 10/10 | Chèn ghi chú vào văn bản thay vì comment/khối riêng | R9, `lint.py` đếm |
| L18 | Chú thích cuối chương chứa dữ kiện lịch sử do AI tự viết (năm thành lập trường, địa chỉ, tem phiếu...) không có nguồn, không tô xanh | Opus rà soát 10/10 | Coi chú thích là "ngoài văn bản" | R2 áp dụng cả chú thích |

## Số đo thực tế trên V7_CHUAN_HOA (10/10/2026, chạy `lint.py`)

| Chương | Gốc (chữ) | Sau sửa | Tỷ lệ | Câu > 35 chữ còn lại |
|---|---|---|---|---|
| 1 | 3.612 | 3.866 | 107% (dài thêm) | 35 |
| 2 | 2.937 | 2.845 | 97% | 20 |
| 3 | 3.786 | 3.943 | 104% (dài thêm) | 36 |
| 4 | 5.483 | 3.852 | 70% | 32 |
| 5 | 3.242 | 2.812 | 87% | 22 |

Kết luận: Chương 1 và 3 sau biên tập còn dài hơn bản gốc. Đây là bằng chứng định lượng của lỗi L2 + L7 (thêm thắt nhiều hơn cắt gọt).
`silent_cuts` còn phát hiện 3 câu gốc Chương 1 ("Tôi không biết sự mất mát ấy đã để lại điều gì trong lòng Ba Má...") và tiêu đề con Chương 4 "RỜI QUÊ HƯƠNG, BƯỚC VÀO SỐ PHẬN" không còn trong file, kể cả dưới dạng gạch track change.
