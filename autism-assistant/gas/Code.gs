/**
 * Code.gs — Telegram webhook router
 *
 * Kiến trúc async để tránh timeout:
 * 1. doPost() nhận tin → xử lý onboarding ngay → trả 200
 * 2. Báo cáo ngày: lưu queue → trigger processOneItem sau 10s
 */

function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);
    var msg  = body.message;
    if (!msg || !msg.text) return ok();

    var msgId  = String(msg.message_id);
    var chatId = String(msg.chat.id);
    var text   = msg.text.trim();
    var name   = (msg.from && msg.from.first_name) ? msg.from.first_name : "";

    var props = PropertiesService.getScriptProperties();

    // Chống duplicate
    var dedupKey = "d_" + chatId + "_" + msgId;
    if (props.getProperty(dedupKey)) return ok();
    props.setProperty(dedupKey, "1");

    // Dọn dedup key cũ
    try {
      var allKeys = props.getKeys().filter(function(k){ return k.indexOf("d_") === 0; });
      if (allKeys.length > 60) allKeys.slice(0, 20).forEach(function(k){ props.deleteProperty(k); });
    } catch(e2){}

    // Whitelist
    var allowed = (props.getProperty("ALLOWED_CHAT_IDS") || "").split(",").map(function(s){ return s.trim(); });
    if (allowed.indexOf(chatId) === -1) {
      guiTinThuong(chatId, "Bot này đang dùng nội bộ, chưa mở đăng ký.");
      return ok();
    }

    // Lệnh nhanh
    if (text === "/start")  { batDau(chatId, name); return ok(); }
    if (text === "/help")   { guiHuongDan(chatId);  return ok(); }
    if (text === "/status") { xemTrangThai(chatId);  return ok(); }
    if (text.toLowerCase().indexOf("/setup") === 0) { caiDatNhanh(chatId, text); return ok(); }

    // Kiểm tra onboarding
    var user = timUser(chatId);
    if (!user || Number(user.buoc) < 3) {
      xuLyOnboarding(chatId, text, user, name);
      return ok();
    }

    // Báo cáo ngày → async queue
    guiTinThuong(chatId, "⏳ Đang phân tích, chờ khoảng 15 giây...");
    var queueKey = "q_" + chatId + "_" + msgId;
    props.setProperty(queueKey, JSON.stringify({ chatId: chatId, text: text, ts: Date.now() }));
    ScriptApp.newTrigger("processOneItem").timeBased().after(10 * 1000).create();

  } catch(err) {
    console.error("doPost lỗi: " + err.message + "\n" + err.stack);
  }
  return ok();
}

/**
 * Được gọi bởi time trigger — xử lý 1 item trong queue
 */
function processOneItem() {
  var props = PropertiesService.getScriptProperties();
  var keys  = props.getKeys().filter(function(k){ return k.indexOf("q_") === 0; });

  if (keys.length === 0) { xoaTriggerCu(); return; }

  var key  = keys[0];
  var data = null;
  try { data = JSON.parse(props.getProperty(key)); } catch(e) {}
  props.deleteProperty(key);
  xoaTriggerCu();

  if (!data) return;
  try {
    var user = timUser(data.chatId);
    if (!user) return;
    xuLyBaoCao(data.chatId, data.text, user);
  } catch(err) {
    console.error("processOneItem lỗi: " + err.message);
    guiTinCoFooter(data.chatId, "Xin lỗi, hệ thống gặp sự cố. Ba/mẹ gửi lại báo cáo sau vài phút nhé!");
  }
}

function xoaTriggerCu() {
  ScriptApp.getProjectTriggers().forEach(function(t) {
    if (t.getHandlerFunction() === "processOneItem") ScriptApp.deleteTrigger(t);
  });
}

// ─── Xử lý báo cáo ───────────────────────────────────────────────────────────

function xuLyBaoCao(chatId, text, user) {
  var kb     = layKB(user.tinh_trang, 3);
  var ketQua = goiClaude(user, text, kb);

  luuNhatKy({
    chatId: chatId, baocao: text, kehoach: ketQua.plan,
    kb_ids: kb.map(function(k){ return k.id; }),
    tin: ketQua.tokensInput, tout: ketQua.tokensOutput, cache: ketQua.cacheHit
  });

  tangNgay(chatId);

  if (new Date().getDay() === 0) {
    try { tomTatTuan(chatId); } catch(e){ console.error("Tóm tắt tuần: " + e.message); }
  }

  guiGoiY(chatId, ketQua.plan);
}

// ─── Lệnh /status ────────────────────────────────────────────────────────────

function xemTrangThai(chatId) {
  var user = timUser(chatId);
  if (!user || user.buoc < 3) {
    guiTinThuong(chatId, "Chưa có thông tin. Gõ /start để bắt đầu.");
    return;
  }
  var nhan = { autism:"Tự kỷ (ASD)", adhd:"Tăng động (ADHD)", speech:"Chậm nói", social:"Kỹ năng xã hội", mixed:"Nhiều vấn đề" };
  guiTinThuong(chatId,
    "📋 *THÔNG TIN HIỆN TẠI:*\n" +
    "• Tuổi bé: " + formatTuoi(user.tuoi_thang) + "\n" +
    "• Tình trạng: " + (nhan[user.tinh_trang] || user.tinh_trang) + "\n" +
    "• Số ngày đã ghi: " + user.so_ngay + " ngày\n" +
    "• Tiến độ: " + (user.tom_tat || "Chưa có dữ liệu")
  );
}

function guiHuongDan(chatId) {
  guiTinThuong(chatId,
    "📖 HƯỚNG DẪN SỬ DỤNG:\n\n" +
    "Mỗi ngày nhắn tin mô tả tình trạng của bé, ví dụ:\n" +
    "\"Hôm nay bé quấy, không chịu ăn, chạy vòng vòng cả buổi\"\n\n" +
    "Bot sẽ gợi ý 3 hoạt động cho ngày mai.\n\n" +
    "Lệnh:\n" +
    "/start — Bắt đầu hoặc cài lại\n" +
    "/status — Xem thông tin bé\n" +
    "/help — Hướng dẫn"
  );
}

// ─── Helper ───────────────────────────────────────────────────────────────────

function ok() {
  return ContentService
    .createTextOutput(JSON.stringify({status:"ok"}))
    .setMimeType(ContentService.MimeType.JSON);
}

function doGet(e) {
  var action = e && e.parameter && e.parameter.action;

  // Xoá dữ liệu user cũ
  if (action === "reset") {
    var props = PropertiesService.getScriptProperties();
    var keys  = props.getKeys();
    var count = 0;
    keys.forEach(function(k) {
      if (k.indexOf("user_") === 0 || k.indexOf("d_") === 0 || k.indexOf("q_") === 0) {
        props.deleteProperty(k);
        count++;
      }
    });
    return ContentService.createTextOutput("Reset xong, da xoa " + count + " key cu.");
  }

  // Đăng ký webhook
  if (action === "webhook") {
    var token  = PropertiesService.getScriptProperties().getProperty("BOT_TOKEN");
    var webUrl = PropertiesService.getScriptProperties().getProperty("WEBAPP_URL");
    var resp   = UrlFetchApp.fetch("https://api.telegram.org/bot" + token + "/setWebhook?url=" + webUrl, { muteHttpExceptions: true });
    return ContentService.createTextOutput("Webhook: " + resp.getContentText());
  }

  // Kiểm tra cấu hình
  if (action === "debug") {
    var p = PropertiesService.getScriptProperties();
    var info = {
      BOT_TOKEN:        p.getProperty("BOT_TOKEN")        ? "CO" : "THIEU",
      CLAUDE_API_KEY:   p.getProperty("CLAUDE_API_KEY")   ? "CO" : "THIEU",
      SPREADSHEET_ID:   p.getProperty("SPREADSHEET_ID")   ? "CO" : "THIEU",
      ALLOWED_CHAT_IDS: p.getProperty("ALLOWED_CHAT_IDS") || "THIEU",
      WEBAPP_URL:       p.getProperty("WEBAPP_URL")        ? "CO" : "THIEU",
      user_keys:        p.getKeys().filter(function(k){ return k.indexOf("user_") === 0; }).length
    };
    return ContentService.createTextOutput(JSON.stringify(info, null, 2));
  }

  // Gửi tin nhắn test trực tiếp đến chatId
  if (action === "sendtest") {
    var token2  = PropertiesService.getScriptProperties().getProperty("BOT_TOKEN");
    var chatId2 = PropertiesService.getScriptProperties().getProperty("ALLOWED_CHAT_IDS").split(",")[0].trim();
    var resp2   = UrlFetchApp.fetch("https://api.telegram.org/bot" + token2 + "/sendMessage", {
      method: "post", contentType: "application/json",
      payload: JSON.stringify({ chat_id: chatId2, text: "✅ Bot đang hoạt động bình thường!" }),
      muteHttpExceptions: true
    });
    return ContentService.createTextOutput(resp2.getResponseCode() + ": " + resp2.getContentText());
  }

  return ContentService.createTextOutput("Autism Assistant Bot is running.");
}
