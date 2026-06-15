/**
 * TelegramAPI.gs — Gửi tin nhắn Telegram
 * parse_mode: Markdown để in đậm *text*
 * Tự động fallback sang plain text nếu Markdown lỗi
 */

var FOOTER_PHAPLÝ = "\n\n─────────────────\n⚠️ Lưu ý: Thông tin chỉ mang tính tham khảo, không thay thế chẩn đoán y khoa.";

function _guiAPI(chatId, text) {
  var token = PropertiesService.getScriptProperties().getProperty("BOT_TOKEN");
  if (!token) { console.error("_guiAPI: Thiếu BOT_TOKEN"); return; }

  // Gửi với Markdown
  var resp = UrlFetchApp.fetch("https://api.telegram.org/bot" + token + "/sendMessage", {
    method:             "post",
    contentType:        "application/json",
    payload:            JSON.stringify({ chat_id: String(chatId), text: text, parse_mode: "Markdown" }),
    muteHttpExceptions: true
  });

  var code = resp.getResponseCode();
  if (code === 200) return; // thành công

  // Nếu lỗi Markdown → gửi lại plain text
  console.error("Telegram lỗi " + code + ": " + resp.getContentText().slice(0, 200));
  var plain = text.replace(/\*/g, "").replace(/_/g, "").replace(/`/g, "");
  UrlFetchApp.fetch("https://api.telegram.org/bot" + token + "/sendMessage", {
    method:             "post",
    contentType:        "application/json",
    payload:            JSON.stringify({ chat_id: String(chatId), text: plain }),
    muteHttpExceptions: true
  });
}

/** Gửi tin nhắn thường (onboarding, hỏi đáp) — không có footer */
function guiTinThuong(chatId, text) {
  _guiAPI(chatId, text);
}

/** Gửi tin nhắn có footer pháp lý — dùng cho gợi ý y tế */
function guiTinCoFooter(chatId, text) {
  _guiAPI(chatId, text + FOOTER_PHAPLÝ);
}

/** Gửi gợi ý 3 nhiệm vụ — có footer tự động */
function guiGoiY(chatId, plan) {
  var m = plan.motor_task;
  var n = plan.nutrition_task;
  var a = plan.acupressure_task;

  var text =
    "🌟 *GỢI Ý HOẠT ĐỘNG NGÀY MAI CHO BÉ:*\n\n" +

    "🏃 *1. VẬN ĐỘNG — " + m.title + "*\n" +
    "⏱ Thời gian: " + m.duration_minutes + " phút\n" +
    m.description + "\n\n" +

    "🥗 *2. DINH DƯỠNG GFCF — " + n.title + "*\n" +
    n.description + "\n\n" +

    "💆 *3. BẤM HUYỆT — Huyệt " + a.point_name + "*\n" +
    a.rationale + "\n" +
    "Cách làm: " + a.technique_reminder + "\n\n" +

    "💪 " + plan.encouragement;

  guiTinCoFooter(chatId, text);
}
