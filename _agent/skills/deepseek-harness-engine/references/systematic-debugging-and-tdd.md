# Điều Tra Lỗi Có Hệ Thống & Phát Triển Hướng Kiểm Thử (Systematic Debugging & TDD)

Tài liệu này tích hợp phương pháp luận **Systematic Debugging 4 Pha** và **Red-Green-Refactor TDD** từ hệ sinh thái **Claude Code (`obra/superpowers` & `feature-dev`)** đồng bộ với kỷ luật của **DeepSeek Harness (`dsh`)**.

---

## PHẦN 1: Luật Sắt Khi Gặp Bug (The Iron Law of Debugging)

> **LUẬT SẮT:** **KHÔNG ĐỀ XUẤT BẤT KỲ BẢN VÁ NÀO KHI CHƯA TÌM RA NGUYÊN NHÂN GỐC RỄ (NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST).**
> Sửa triệu chứng (symptom fixing) hoặc sửa mò (shotgun debugging) là lãng phí thời gian và tạo ra lỗi chồng lỗi.

Khi gặp bất kỳ lỗi kỹ thuật, test fail, hành vi sai lệch hoặc sự cố hiệu năng nào, BẮT BUỘC đi qua đúng **4 Pha tuần tự**:

### Pha 1: Điều Tra Nguyên Nhân Gốc Rễ (Root Cause Investigation)
Trước khi chạm vào một dòng code để sửa:
1. **Đọc kỹ toàn bộ thông báo lỗi & Stack Trace:**
   - Không lướt qua. Ghi nhận chính xác mã lỗi, số dòng, tên file và chuỗi gọi hàm (call stack).
2. **Tái hiện lỗi nhất quán (Reproduce Consistently):**
   - Tìm lệnh hoặc kịch bản nhỏ nhất làm lỗi xuất hiện chắc chắn. Nếu chưa tái hiện được, phải thu thập thêm dữ liệu, không đoán mò.
3. **Kiểm tra các thay đổi gần nhất (`git diff` / `git status`):**
   - Cái gì vừa thay đổi về code, cấu hình, biến môi trường hoặc phiên bản thư viện?
4. **Truy vết ngược luồng dữ liệu (Backward Data-Flow Tracing):**
   - Khi một giá trị sai (`null`, `undefined`, chuỗi rỗng, sai kiểu) gây nổ ở hàm B, **đừng chỉ đặt `if (!val) return` ở hàm B** (đó là che giấu lỗi). Hãy lần ngược lên hàm A, hàm khởi tạo, API response hoặc DB query để tìm chính xác nơi đầu tiên sinh ra giá trị sai đó.
5. **Trong hệ thống nhiều tầng (Client → API → Server → DB / Subprocess):**
   - Nếu không nhìn rõ dữ liệu gãy ở tầng nào, hãy chèn log chẩn đoán tạm thời ở từng ranh giới để xác định đúng tầng bị hỏng trước khi sửa.

### Pha 2: Phân Tích Mẫu Đối Chiếu (Pattern Analysis)
1. **Tìm đoạn code tương tự đang chạy tốt trong cùng codebase:**
   - Dùng `rg` tìm một endpoint, component hoặc module tương đương trong dự án đang hoạt động ổn định.
2. **Đặt lên bàn cân đối chiếu:**
   - Liệt kê mọi điểm khác biệt giữa chỗ chạy đúng và chỗ bị lỗi (thứ tự khởi tạo, quyền hạn, kiểu dữ liệu, cấu hình header, xử lý bất đồng bộ).

### Pha 3: Kiểm Chứng Giả Thuyết Đơn Biến (Hypothesis & Single-Variable Testing)
1. **Phát biểu giả thuyết tường minh:**
   - *"Tôi nghĩ X là nguyên nhân gốc của lỗi Y bởi vì bằng chứng Z tại file A dòng B."*
2. **Thử nghiệm với thay đổi nhỏ nhất (1 biến số duy nhất):**
   - Tuyệt đối không sửa 4 chỗ cùng lúc rồi chạy lại xem có ăn may hết lỗi hay không.
   - Nếu giả thuyết sai: hoàn tác (revert) thử nghiệm đó ngay và quay lại Pha 1 với dữ liệu mới thu được.

### Pha 4: Khắc Phục Triệt Để & Quy Tắc "Quá Tam Baận" (3-Strike Architecture Escalation)
1. **Viết bài kiểm thử tái hiện lỗi trước khi sửa (Failing Test / Reproducer Script):**
   - Tạo một test nhỏ (hoặc script trong `scratch/`) chứng minh lỗi thực sự xảy ra (Red).
2. **Sửa tại nguyên nhân gốc rễ (Fix at the Source):**
   - Sửa đúng nơi phát sinh dữ liệu/trạng thái sai và xác nhận test chuyển sang Pass (Green).
3. **Chốt chặn "Quá Tam Ba Bận" (The 3-Strike Rule):**
   - Nếu đã thử **2 bản sửa liên tiếp** ở các vị trí khác nhau mà lỗi vẫn còn hoặc nảy sinh lỗi mới ở chỗ khác → **DỪNG NGAY LẬP TỨC.**
   - Đây là dấu hiệu kiến trúc hiện tại đang có mâu thuẫn căn bản. Không đắp thêm bản vá thứ 3; hãy báo cáo lại cho người dùng nguyên nhân cấu trúc và đề xuất phương án thiết kế lại.

---

## PHẦN 2: Kỷ Luật Kiểm Thử Thực Chiến (Pragmatic TDD: Red → Green → Refactor)

Khi viết hàm xử lý logic nghiệp vụ mới, tính toán tài chính/định lượng, phân quyền hoặc parser:
1. **RED (Chứng minh bài test có tác dụng):**
   - Viết bài kiểm thử mô tả hành vi mong muốn (bao gồm cả trường hợp chuẩn và trường hợp đối chứng âm / đầu vào sai).
   - Chạy kiểm thử để xác nhận nó thực sự bắt được lỗi khi chưa có code mới.
2. **GREEN (Code tối giản để vượt qua kiểm thử):**
   - Viết lượng code tối thiểu, rõ ràng nhất để vượt qua bài kiểm thử (kết hợp nguyên tắc *Simplicity First* của Karpathy).
3. **REFACTOR (Làm sạch trong vùng an toàn):**
   - Dọn dẹp trùng lặp, đặt tên rõ nghĩa trong khi giữ nguyên 100% bài kiểm thử ở trạng thái Xanh.
