/**
 * Onboarding.gs — Kịch bản hỏi thông tin user mới
 * Bước: 0=mới, 1=hỏi tuổi, 2=hỏi tình trạng, 3=hoàn tất
 */

var LUA_CHON_TINH_TRANG = {
  "1":"autism","2":"adhd","3":"speech","4":"social","5":"mixed",
  "autism":"autism","adhd":"adhd","speech":"speech","social":"social","mixed":"mixed"
};

var NHAN_TINH_TRANG = {
  autism:"Tự kỷ (ASD)", adhd:"Tăng động (ADHD)",
  speech:"Chậm nói / ngôn ngữ", social:"Kỹ năng xã hội", mixed:"Nhiều vấn đề"
};

function batDau(chatId, ten) {
  try {
    // Tạo user mới nếu chưa có
    var u = timUser(chatId);
    if (!u) taoUser(chatId, ten || "");
    datBuoc(chatId, 1);

    var tenHienThi = ten ? " " + ten : "";
    guiTinThuong(chatId,
      "Xin chào" + tenHienThi + "! 👋\n\n" +
      "Tôi là Trợ lý Giáo dục Tự kỷ tại Nhà.\n\n" +
      "Mỗi ngày ba/mẹ nhắn mô tả tình trạng bé, tôi sẽ gợi ý:\n" +
      "• 1 bài vận động\n" +
      "• 1 gợi ý dinh dưỡng GFCF\n" +
      "• 1 hướng dẫn bấm huyệt\n\n" +
      "Bé hiện bao nhiêu tuổi?\n\n" +
      "Ví dụ: gõ 3 nếu bé 3 tuổi, gõ 4.5 nếu bé 4 tuổi rưỡi"
    );
  } catch(e) {
    console.error("batDau lỗi: " + e.message + "\n" + e.stack);
    guiTinThuong(chatId, "Xin lỗi, có lỗi xảy ra. Ba/mẹ thử gõ /start lại nhé!");
  }
}

function xuLyOnboarding(chatId, text, user, ten) {
  var buoc = (user && user.buoc !== undefined) ? Number(user.buoc) : 0;

  if (text.toLowerCase().indexOf("/setup") === 0) {
    caiDatNhanh(chatId, text);
    return;
  }

  if (buoc <= 0) {
    batDau(chatId, ten || "");
  } else if (buoc === 1) {
    buoc1NhanTuoi(chatId, text);
  } else if (buoc === 2) {
    buoc2NhanTinhTrang(chatId, text);
  } else {
    guiTinThuong(chatId, "Gõ /start để bắt đầu lại nhé!");
  }
}

function buoc1NhanTuoi(chatId, text) {
  try {
    var thang = parseTuoi(text);

    if (thang === null) {
      guiTinThuong(chatId,
        "Ba/mẹ nhập số tuổi của bé giúp tôi nhé!\n\n" +
        "Ví dụ:\n" +
        "• Gõ 3 nếu bé 3 tuổi\n" +
        "• Gõ 4.5 nếu bé 4 tuổi rưỡi\n" +
        "• Gõ 30 nếu bé 30 tháng"
      );
      return;
    }

    capNhatUser(chatId, { tuoi_thang: thang });
    datBuoc(chatId, 2);

    var hienThi = formatTuoi(thang);
    guiTinThuong(chatId,
      "Bé " + hienThi + " 👶\n\n" +
      "Ba/mẹ muốn hỗ trợ bé về vấn đề gì?\n\n" +
      "1 — Tự kỷ (ASD)\n" +
      "2 — Tăng động giảm chú ý (ADHD)\n" +
      "3 — Chậm nói / ngôn ngữ\n" +
      "4 — Kỹ năng xã hội\n" +
      "5 — Nhiều vấn đề kết hợp\n\n" +
      "Gõ số 1, 2, 3, 4 hoặc 5"
    );
  } catch(e) {
    console.error("buoc1NhanTuoi lỗi: " + e.message + "\n" + e.stack);
    guiTinThuong(chatId, "Có lỗi xảy ra, ba/mẹ thử nhập lại số tuổi nhé!");
  }
}

function buoc2NhanTinhTrang(chatId, text) {
  try {
    var key = LUA_CHON_TINH_TRANG[text.trim()];

    if (!key) {
      guiTinThuong(chatId,
        "Ba/mẹ gõ số từ 1 đến 5 giúp tôi nhé:\n\n" +
        "1 — Tự kỷ (ASD)\n" +
        "2 — Tăng động (ADHD)\n" +
        "3 — Chậm nói\n" +
        "4 — Kỹ năng xã hội\n" +
        "5 — Nhiều vấn đề"
      );
      return;
    }

    capNhatUser(chatId, {
      tinh_trang:        key,
      buoc:              3,
      chuong_trinh:      key === "autism" ? "tubucnho_tap1" : "",
      tuan_chuong_trinh: 1
    });

    guiTinThuong(chatId,
      "✅ Đã lưu thông tin!\n\n" +
      "Tình trạng: " + NHAN_TINH_TRANG[key] + "\n\n" +
      "Từ bây giờ, mỗi ngày ba/mẹ nhắn mô tả tình trạng bé hôm nay.\n\n" +
      "Ví dụ:\n" +
      "\"Hôm nay bé quấy cả buổi sáng, không chịu ăn, cứ chạy vòng vòng và la hét\"\n\n" +
      "Tôi sẽ phân tích và gợi ý 3 hoạt động phù hợp 🌟\n\n" +
      "Ba/mẹ thử nhắn mô tả tình trạng bé hôm nay đi!"
    );
  } catch(e) {
    console.error("buoc2NhanTinhTrang lỗi: " + e.message + "\n" + e.stack);
    guiTinThuong(chatId, "Có lỗi xảy ra, ba/mẹ thử gõ lại số 1-5 nhé!");
  }
}

function parseTuoi(text) {
  if (!text) return null;
  var s = text.toString().trim();

  s = s.replace(/tháng\s*tuổi/gi, "")
       .replace(/tuổi\s*rưỡi/gi, ".5")
       .replace(/tuổi/gi, "")
       .replace(/tháng/gi, "")
       .replace(/tuoi/gi, "")
       .replace(/thang/gi, "")
       .replace(/rưỡi/gi, ".5")
       .replace(/ruoi/gi, ".5")
       .replace(/,/g, ".")
       .trim();

  var num = parseFloat(s);
  if (isNaN(num) || num <= 0) return null;

  var thang = num <= 12 ? Math.round(num * 12) : Math.round(num);
  if (thang < 6 || thang > 216) return null;
  return thang;
}

function caiDatNhanh(chatId, text) {
  try {
    var phan   = text.replace(/^\/setup\s*/i, "").trim().split(/\s+/);
    var tuoi   = parseTuoi(phan[0]);
    var keyRaw = (phan[1] || "").toLowerCase().trim();
    var key    = LUA_CHON_TINH_TRANG[keyRaw];

    if (!tuoi || !key) {
      guiTinThuong(chatId,
        "Cách dùng: /setup [tuổi] [tình_trạng]\n\n" +
        "Ví dụ:\n" +
        "/setup 4 autism\n" +
        "/setup 30 speech\n\n" +
        "Tình trạng: autism, adhd, speech, social, mixed"
      );
      return;
    }

    capNhatUser(chatId, {
      tuoi_thang:        tuoi,
      tinh_trang:        key,
      buoc:              3,
      chuong_trinh:      key === "autism" ? "tubucnho_tap1" : "",
      tuan_chuong_trinh: 1
    });

    guiTinThuong(chatId,
      "✅ Đã cài đặt:\n" +
      "• Tuổi: " + formatTuoi(tuoi) + "\n" +
      "• Tình trạng: " + NHAN_TINH_TRANG[key] + "\n\n" +
      "Sẵn sàng! Hãy nhắn mô tả tình trạng bé hôm nay."
    );
  } catch(e) {
    console.error("caiDatNhanh lỗi: " + e.message);
    guiTinThuong(chatId, "Có lỗi, ba/mẹ thử lại nhé!");
  }
}
