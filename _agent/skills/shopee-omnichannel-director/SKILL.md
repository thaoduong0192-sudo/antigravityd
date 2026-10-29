---
name: shopee-omnichannel-director
description: Hệ thống Quản trị & Vận hành Sàn Shopee Toàn diện (Chuẩn Giám đốc Vận hành TMĐT 30 năm kinh nghiệm). Tự động kiểm toán 360 độ gian hàng Shopee (Account Health, SLA Giao hàng nhanh FHR, Tiêu chí Shop Yêu Thích+, Công cụ Tối ưu AI), phân tích đối thủ cạnh tranh theo từng CSPU Đấu Giá Rẻ Vô Địch kết hợp Giá vốn Sapo (COGS Margin Guard >= 60%), xử lý bẫy tỷ lệ giá 5x (price_ratio = 5), gỡ khoá tồn kho Flash Sale, kích hoạt Combo/Mua Kèm Deal Sốc và điều phối Quảng cáo Shopee PAS (GMV Max / Chiến dịch Nhóm MPD / Bảo hiểm Hoàn tiền ROAS).
---

# Shopee Omnichannel Director (Giám Đốc Vận Hành Sàn Shopee Toàn Năng)

Skill này tích hợp kiến thức thực chiến từ các bộ công cụ mã nguồn mở trên GitHub (`congminh1254/shopee-sdk`, `JimCurryWang/python-shopee`, `omkarcloud/shopee-scraper`) cùng **Bộ Quy chuẩn Vận hành & Thuật toán Shopee Việt Nam mới nhất (2025–2026)** và **Hệ thống Điều phối Trực tiếp qua Chrome CDP (`banhang.shopee.vn`)**.

---

## I. TỔNG HỢP CÁC REPO GITHUB & KIẾN TRÚC KỸ THUẬT SHOPEE AUTOMATION

1. **`congminh1254/shopee-sdk` (TypeScript / Node.js) & `JimCurryWang/python-shopee` (Python)**:
   - Chuẩn hoá các phân hệ quản trị Shopee Open Platform v2: `Product`, `Order`, `Logistics`, `Marketing` (`Discount`, `Bundle Deal`, `Add-on Deal`, `Voucher`, `Flash Sale`), `ShopCategory` và `AccountHealth`.
2. **`omkarcloud/shopee-scraper` & Chrome CDP Direct Session (`chrome-omnichannel-mcp`)**:
   - Do Shopee Open API v2 giới hạn quyền can thiệp sâu vào **Đấu Giá Rẻ Vô Địch (`CSPU Realtime Bidding`)**, **Quảng cáo Nội sàn (`PAS - Product Ads Service`)**, và **Bảo hiểm Hoàn tiền ROAS (`auto_rebate`)**, phương pháp tối ưu nhất là kết nối trực tiếp vào phiên đăng nhập Kênh Người Bán (`https://banhang.shopee.vn/`) qua Chrome CDP (`port 9333`) sử dụng cookie `SPC_CDS` để gọi trực tiếp các Internal APIs của Shopee.

---

## II. 7 QUY ĐỊNH BẮT BUỘC CỦA SHOPEE ĐỐI VỚI NHÀ BÁN HÀNG (CẬP NHẬT 2025–2026)

Một Giám đốc Vận hành Shopee thực chiến luôn kiểm soát chặt 7 trụ cột luật chơi mới nhất của sàn:

1. **Cấu trúc Phí Sàn Mới (18% – 25%+ Tổng Doanh Thu)**:
   - **Phí Cố Định (Commission Fee)**: Ngành Chăm sóc thú cưng (`Chăm sóc sức khỏe` / `Vệ sinh` / `Thức ăn`) chịu phí cố định **14% – 17%** (Non-Mall).
   - **Phí Thanh Toán / Xử Lý Giao Dịch**: **5% – 6%** tính trên tổng thanh toán của khách (bao gồm cả phí ship).
   - **Phí Hạ Tầng**: **3.000đ/đơn hàng** thành công (đánh rất nặng vào các đơn hàng giá trị thấp `< 30.000đ` nếu chỉ bán 1 gói lẻ mà không có phễu upsell lên Combo/Mua kèm!).
   - **Phí Gói Dịch Vụ (`Voucher Xtra` / `Freeship Xtra`)**: **5.5% – 8%**.
   - **Quy tắc sống còn**: Biên lợi nhuận gộp trên Giá vốn Sapo (`Gross Margin = (Giá bán - Giá vốn Sapo) / Giá bán`) **BẮT BUỘC phải đạt tối thiểu `>= 60%`** (hoặc giá trị đơn hàng trung bình `AOV >= 75.000đ`) thì sau khi trừ ~22% phí sàn + 12–15% chi phí Ads (`ROAS 6.5 – 8.0`), nhà bán mới giữ được **23% – 30% lợi nhuận ròng (Net Margin)**.

2. **Chỉ số Bàn Giao Nhanh (`FHR - Fast Handover Rate`) & Phạt Sao Quả Tạ**:
   - Đơn phát sinh trước hạn cắt đơn trong ngày phải được bấm chuẩn bị hàng và bàn giao ĐVVC đúng mốc SLA.
   - Tỷ lệ giao hàng trễ (`LSR >= 10%`) hoặc tỷ lệ đơn không thành công (`NFR >= 10%`) bị phạt ngay **1 – 2 điểm Sao Quả Tạ** vào mỗi thứ Hai hàng tuần, làm tụt điểm hiển thị tự nhiên của toàn bộ gian hàng.
   - Kênh **Hoả Tốc / Siêu Tốc 4 Giờ** được tính SLA độc lập; vi phạm LSR kênh Hoả tốc `>= 10%` cũng bị phạt Sao Quả Tạ.

3. **Tiêu chí Mới Xét Duyệt `Shop Yêu Thích` & `Shop Yêu Thích+` (Từ 2025–2026)**:
   - Bỏ điều kiện cộng dồn số tuần liên tiếp, xét duyệt theo hạn mức doanh thu & số đơn thành công của từng ngành hàng.
   - **Điều kiện bắt buộc mới tại TP.HCM / Hà Nội**: Phải bật kênh vận chuyển **Hoả Tốc đạt tỷ lệ `>= 90%` sản phẩm trong shop**.
   - Tỷ lệ phản hồi Chat `>= 85%`, Điểm đánh giá Shop `>= 4.6 – 4.8`, Điểm phạt Sao Quả Tạ `= 0`.

4. **Thuật toán Tìm kiếm Mới: Từ `Keyword Matching` sang `Intent Matching + CSPU Price Score`**:
   - Shopee gom các sản phẩm cùng loại trên toàn sàn vào chung một mã **CSPU (`Standardized Product Unit`)**.
   - Trong cùng 1 CSPU, sản phẩm nào thắng giải **Đấu Giá Rẻ Vô Địch (`Realtime Bidding`)** sẽ được gắn huy hiệu **Rẻ Vô Địch**, được Shopee trợ giá Voucher nền tảng (`SHP..._MCP`, giảm thêm 10–15%) và chiếm trọn vị trí Top đầu tìm kiếm + Tab Đề Xuất.

5. **Rào cản Kỹ thuật `5x Price Ratio` (`error 1400101314`) & Trần Giảm Giá 50% (`error 1400101308`)**:
   - Trong cùng 1 link sản phẩm, **Giá phân loại cao nhất / Giá phân loại thấp nhất sau giảm giá KHÔNG ĐƯỢC vượt quá `5.0 lần`**.
   - Nếu gộp chung `Gói lẻ 5g (20.000đ)` với `Hũ lớn 500g / Combo 15 gói (180.000đ)` trong cùng 1 sản phẩm, Shopee sẽ chặn không cho phân loại gói lẻ tham gia Chương trình Khuyến mãi (`Promo = 0đ`), làm chết hoàn toàn phễu kéo traffic của sản phẩm đó.

6. **Cơ chế Bảo hiểm Hoàn tiền Quảng cáo (`ROAS Protection Rebate - auto_rebate`)**:
   - Các chiến dịch `GMV Max / ROI Two` được Shopee cấp bảo hiểm hoàn tiền quảng cáo nếu đạt đủ đơn hàng nhưng ROAS thực tế thấp hơn ROAS mục tiêu.
   - **Cấm kỵ**: Tuyệt đối không chỉnh tay `roi_two_target` lên mức ảo (`10.0 – 15.0`) hoặc bật/tắt liên tục, vì sẽ bị hệ thống đánh dấu `rebate_campaign_status: "invalid"` (`roi_two_target_changed` / `campaign_inactive`), làm mất quyền hoàn tiền bảo hiểm!

7. **Tuân thủ Pháp lý, Định danh Thuế & Giấy phép Sản phẩm**:
   - Bắt buộc đồng bộ Mã số thuế, thông tin pháp nhân/Hộ kinh doanh và tải lên Giấy công bố chất lượng / Giấy phép lưu hành đối với các sản phẩm Thực phẩm bổ sung, Chế phẩm sinh học, Thuốc thú y.

---

## III. BẢNG ĐIỀU KHIỂN INTERNAL API SHOPEE SELLER CENTER (`banhang.shopee.vn`)

Khi kết nối qua Chrome CDP (`http://127.0.0.1:9333`), sử dụng `SPC_CDS` từ cookie để thực thi trực tiếp:

### 1. Kiểm toán & Cập nhật Giá Gốc / Giá Khuyến Mãi (`5x Ratio Safe`)
- **Lấy chi tiết sản phẩm & phân loại**:
  `GET /api/v3/product/get_product_info?SPC_CDS=${cds}&SPC_CDS_VER=2&item_id=${itemId}`
- **Cập nhật giá gốc (`original_price`)**:
  `POST /api/v3/product/update_product_info?SPC_CDS=${cds}&SPC_CDS_VER=2`
  *(Lưu ý: Lọc `model_list = model_list.filter(m => m.id > 0)` và xoá các object rỗng như `complaint_policy` trước khi gửi).*
- **Cập nhật giá Khuyến mãi của Shop (`promotion_id`)**:
  `POST /api/marketing/v4/discount/update_seller_discount_items/?SPC_CDS=${cds}&SPC_CDS_VER=2`

### 2. Gỡ khoá Tồn kho Flash Sale Của Shop
- **Danh sách khung giờ Flash Sale**:
  `GET /api/marketing/v4/shop_flash_sale/get_shop_flash_sale_list/?offset=0&limit=50&type=1`
- **Tắt khung giờ Flash Sale bị kẹt tồn kho (`stock <= 2` hoặc `0 sản phẩm`)**:
  `POST /api/marketing/v4/shop_flash_sale/set_shop_flash_sale/` (`status: 2`)

### 3. Đấu Giá Rẻ Vô Địch (`CSPU Realtime Bidding`)
- **Thống kê tổng quan**:
  `POST /api/mkt/bidding/get_ongoing_statistics` (`body: "{}"`)
- **Lấy danh sách phân loại đang đấu giá & giá sàn đối thủ (`must_win_floor_price`, `default_bid_price`)**:
  `POST /api/mkt/bidding/get_item_ongoing_list` (`{ page_no: 1, page_size: 50, tab_type: 1 | 2 | 3 }`)
- **Lấy danh sách phân loại được đề cử tham gia (`matchPage`)**:
  `POST /api/mkt/bidding/get_item_match_list` (`{ page_no: 1, page_size: 50 }`)
- **Cập nhật giá đấu thầu để thắng ngay (`Winning`)**:
  `POST /api/mkt/bidding/edit_bidding_info` (`{ bid_id, bid_price: String(price * 100000), bid_stock: 0, accept_rebate: 1 }`)
- **Đề cử mới vào Đấu Giá Rẻ Vô Địch**:
  `POST /api/mkt/bidding/submit_bidding_online`

### 4. Quảng Cáo Shopee (`PAS - Product Ads Service`)
- **Kiểm tra số dư Ví Quảng cáo**:
  `POST /api/pas/v1/meta/get_ads_data/` (`{ info_type_list: ["ads_expense", "ads_credit", "campaign_day", "has_ads", "incentive", "ads_toggle"] }`)
- **Truy vấn hiệu quả toàn bộ chiến dịch**:
  `POST /api/pas/v1/homepage/query/`
- **Chỉnh sửa Ngân sách / ROAS Mục tiêu / Tạm dừng Chiến dịch**:
  `POST /api/pas/v1/product/edit/` (`type: "change_budget" | "change_roi_two_target" | "pause" | "resume"`)
- **Thêm/Gỡ sản phẩm trong Chiến dịch Nhóm tự động (`product_mpd` — Tối đa 30 SP/nhóm, truyền từng SP một)**:
  `POST /api/pas/v1/product/mpd/item/edit/` (`{ campaign_id, item_id_list: [singleItemId], type: "add" | "delete" }`)
- **Bật/Tắt sản phẩm trong Chiến dịch Tự động Chọn Sản phẩm cấp độ Shop (`product_gms`)**:
  `POST /api/pas/v1/product/gms/item/edit/` (`{ campaign_id, item_id_list: [...], type: "add" | "delete" }`)

---

## IV. QUY TRÌNH 5 BƯỚC CỦA GIÁM ĐỐC VẬN HÀNH KHI TỐI ƯU GIAN HÀNG

1. **Bước 1 — Kiểm toán Sức khoẻ Vận hành & Đòn bẩy Marketing (`Health & Promo Matrix`)**:
   - Kiểm tra Sao Quả Tạ, Tỷ lệ bàn giao nhanh (`FHR`), Tỷ lệ phản hồi Chat, Tỷ lệ bật Hoả Tốc, trạng thái `Flash Sale`, `Combo Khuyến Mãi (Bundle Deal)`, `Mua Kèm Deal Sốc (Add-on Deal)`, `Mã Giảm Giá (Voucher)`.
2. **Bước 2 — Đối chiếu Giá vốn Sapo (`COGS`) vs Giá Sàn Đối Thủ (`CSPU Floor Price`)**:
   - Phân tách rõ **Phân loại Phễu Kéo Traffic (`Gói lẻ 5g / 30g`)** và **Phân loại Chốt Lợi Nhuận (`Combo 3 / Combo 5 / Hũ 50g – 500g`)**.
   - Phát hiện xung đột giá nội bộ (Đại lý/Shop vệ tinh bán phá giá cùng mã CSPU) và tách cấu trúc quy cách để không bị kẹt rào cản `5x price_ratio`.
3. **Bước 3 — Mở khoá Tồn kho & Khôi phục 100% Khuyến mãi (`Discount Recovery`)**:
   - Xoá/tắt các Flash Sale khoá tồn kho `stock = 2`, cập nhật lại giá gốc và kích hoạt giảm giá cho toàn bộ phân loại bị `Promo = 0đ`.
4. **Bước 4 — Đánh chiếm Huy hiệu `Rẻ Vô Địch` có Chốt chặn Biên lợi nhuận (`>= 60% Gross Margin`)**:
   - Tự động đặt giá thầu bằng `must_win_floor_price` hoặc `default_bid_price` cho các phân loại gói lẻ/phễu nếu biên lãi gộp trên giá vốn Sapo `>= 60%`. Tuyệt đối chặn không cho phân loại Combo nhiều gói bị khớp nhầm vào CSPU gói lẻ.
5. **Bước 5 — Điều phối Quảng cáo PAS Bảo Toàn 100% Traffic**:
   - Dừng các chiến dịch đốt tiền (`ROAS < 2.5`), đồng thời tự động chuyển toàn bộ sản phẩm đang còn hàng từ chiến dịch tạm dừng vào **Chiến dịch Nhóm phân phối tự động (`product_mpd`)** và **Chiến dịch Tự động cấp độ Shop (`product_gms`)** để không một sản phẩm nào bị đứt nguồn traffic.
