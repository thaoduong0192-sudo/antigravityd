/**
 * Setup.gs — Chạy 1 lần duy nhất để cấu hình toàn bộ hệ thống
 *
 * HƯỚNG DẪN:
 * 1. Điền CLAUDE_API_KEY vào dòng bên dưới (lấy từ console.anthropic.com)
 * 2. Bấm Run → runFullSetup()
 * 3. Xong! Xoá file này hoặc để nguyên cũng được
 */

var SETUP_CONFIG = {
  // ✅ ĐÃ CÓ — không cần sửa
  BOT_TOKEN:         "8745219967:AAF03aey-RNaanp960sOGwdtuouKwgq5LXE",
  SPREADSHEET_ID:    "1VP6co4USMhEeIw3Jzkjig15VlXkQ2ix7IHEeltnrxjk",
  ALLOWED_CHAT_IDS:  "6357286859",
  CLAUDE_MODEL:      "claude-haiku-3-5-20241022",

  CLAUDE_API_KEY:    "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",

  WEBAPP_URL:        "https://script.google.com/macros/s/AKfycbzLJvbh2rcasiprTr1UYSGhYsKF9Gi-EV-6McU_PPwsOBwm-foxwhM-xiZgbVA3obfZkg/exec"
};

// ─────────────────────────────────────────────────────────────────────────────

/**
 * Chạy hàm này 1 lần để setup toàn bộ:
 * - Ghi Script Properties (credentials)
 * - Tạo tất cả sheets với headers
 * - Nhập dữ liệu GFCF và huyệt đạo
 */
function runFullSetup() {
  Logger.log("=== BẮT ĐẦU SETUP ===");

  step1_setScriptProperties();
  step2_createSheets();
  step3_addHeaders();
  step4_populateGFCF();
  step5_populateAcupressure();

  Logger.log("=== ✅ SETUP HOÀN TẤT ===");
  Logger.log("Bước tiếp theo:");
  Logger.log("1. Bấm Deploy → New deployment → Web app → Anyone → Deploy");
  Logger.log("2. Copy URL web app → dán vào SETUP_CONFIG.WEBAPP_URL bên trên");
  Logger.log("3. Chạy hàm updateWebappUrl()");
  Logger.log("4. Chạy hàm setupTelegramWebhook()");
}

function step1_setScriptProperties() {
  Logger.log("Bước 1: Ghi Script Properties...");
  var props = PropertiesService.getScriptProperties();
  props.setProperty("BOT_TOKEN",        SETUP_CONFIG.BOT_TOKEN);
  props.setProperty("SPREADSHEET_ID",   SETUP_CONFIG.SPREADSHEET_ID);
  props.setProperty("CLAUDE_API_KEY",   SETUP_CONFIG.CLAUDE_API_KEY);
  props.setProperty("CLAUDE_MODEL",     SETUP_CONFIG.CLAUDE_MODEL);
  props.setProperty("ALLOWED_CHAT_IDS", SETUP_CONFIG.ALLOWED_CHAT_IDS);
  if (SETUP_CONFIG.WEBAPP_URL) {
    props.setProperty("WEBAPP_URL", SETUP_CONFIG.WEBAPP_URL);
  }
  Logger.log("✓ Script Properties đã lưu");
}

function step2_createSheets() {
  Logger.log("Bước 2: Tạo các sheets...");
  var ss = SpreadsheetApp.openById(SETUP_CONFIG.SPREADSHEET_ID);
  var required = ["Knowledge_Base", "GFCF_Diet", "Acupressure_Points", "Users", "Daily_Logs", "Weekly_Scores"];

  required.forEach(function(name) {
    var existing = ss.getSheetByName(name);
    if (!existing) {
      ss.insertSheet(name);
      Logger.log("  Tạo sheet: " + name);
    } else {
      Logger.log("  Sheet đã tồn tại: " + name);
    }
  });

  // Xoá Sheet1 mặc định nếu còn
  var defaultSheet = ss.getSheetByName("Sheet1") || ss.getSheetByName("Trang tính1");
  if (defaultSheet && ss.getSheets().length > 1) {
    ss.deleteSheet(defaultSheet);
    Logger.log("  Xoá sheet mặc định");
  }
  Logger.log("✓ Tất cả sheets đã sẵn sàng");
}

function step3_addHeaders() {
  Logger.log("Bước 3: Thêm tiêu đề cột...");
  var ss = SpreadsheetApp.openById(SETUP_CONFIG.SPREADSHEET_ID);

  var headers = {
    "Knowledge_Base":    [["id","category","subcategory","title_vi","source_url","summary_vi","tags","age_range","difficulty","scraped_at"]],
    "GFCF_Diet":         [["food_name_vi","food_type","gluten_free","casein_free","category","notes_vi"]],
    "Acupressure_Points":[["point_name_vi","point_name_en","location_vi","technique_vi","benefit_vi","caution_vi"]],
    "Users":             [["telegram_chat_id","display_name","child_age_months","child_condition","onboarding_step","status_summary","current_program","program_week","last_active","total_days_logged","created_at"]],
    "Daily_Logs":        [["log_id","telegram_chat_id","log_date","parent_report","motor_task","nutrition_task","acupressure_task","kb_references","tokens_input","tokens_output","cache_hit"]],
    "Weekly_Scores":     [["score_id","telegram_chat_id","week_start","days_reported","motor_progress","language_progress","social_progress","weekly_summary","created_at"]]
  };

  Object.keys(headers).forEach(function(sheetName) {
    var sheet = ss.getSheetByName(sheetName);
    sheet.getRange(1, 1, 1, headers[sheetName][0].length).setValues(headers[sheetName]);
    sheet.getRange(1, 1, 1, headers[sheetName][0].length).setFontWeight("bold");
    sheet.setFrozenRows(1);
  });
  Logger.log("✓ Headers đã thêm xong");
}

function step4_populateGFCF() {
  Logger.log("Bước 4: Nhập dữ liệu GFCF...");
  var ss    = SpreadsheetApp.openById(SETUP_CONFIG.SPREADSHEET_ID);
  var sheet = ss.getSheetByName("GFCF_Diet");

  var data = [
    // food_name_vi, food_type, gluten_free, casein_free, category, notes_vi
    ["Gạo trắng",      "safe",  true, true, "grain",      "Thay thế hoàn hảo cho mì sợi và bánh mì"],
    ["Gạo lứt",        "safe",  true, true, "grain",      "Giàu dinh dưỡng hơn gạo trắng, tốt cho tiêu hóa"],
    ["Bún gạo",        "safe",  true, true, "grain",      "Thay thế mì sợi trong các bữa ăn"],
    ["Phở gạo",        "safe",  true, true, "grain",      "An toàn khi nước dùng không có gluten"],
    ["Khoai lang",     "safe",  true, true, "vegetable",  "Ngọt tự nhiên, giàu beta-carotene và chất xơ"],
    ["Khoai tây",      "safe",  true, true, "vegetable",  "Dễ chế biến, giàu kali"],
    ["Thịt gà tươi",   "safe",  true, true, "protein",    "Chỉ dùng thịt tươi không tẩm ướp sẵn"],
    ["Thịt heo tươi",  "safe",  true, true, "protein",    "Tránh xúc xích, thịt nguội đóng gói"],
    ["Cá hồi",         "safe",  true, true, "protein",    "Giàu Omega-3, rất tốt cho não bộ"],
    ["Cá thu",         "safe",  true, true, "protein",    "Giàu đạm và Omega-3"],
    ["Cá rô phi",      "safe",  true, true, "protein",    "Dễ mua, giá hợp lý"],
    ["Trứng gà",       "safe",  true, true, "protein",    "Nguồn đạm tốt, dễ chế biến nhiều cách"],
    ["Rau cải xanh",   "safe",  true, true, "vegetable",  "Tất cả rau xanh tươi đều an toàn"],
    ["Bí đỏ",          "safe",  true, true, "vegetable",  "Ngọt, dễ nghiền, tốt cho tiêu hóa"],
    ["Cà rốt",         "safe",  true, true, "vegetable",  "Giàu vitamin A, tốt cho mắt"],
    ["Chuối",          "safe",  true, true, "fruit",      "Dễ ăn, bổ dưỡng, ngọt tự nhiên"],
    ["Táo",            "safe",  true, true, "fruit",      "Giàu chất xơ, tốt cho tiêu hóa"],
    ["Xoài",           "safe",  true, true, "fruit",      "Giàu vitamin C và beta-carotene"],
    ["Dưa hấu",        "safe",  true, true, "fruit",      "Cung cấp nước tốt cho cơ thể"],
    ["Dầu dừa",        "safe",  true, true, "fat",        "Tốt cho não bộ, kháng khuẩn tự nhiên"],
    ["Dầu ô liu",      "safe",  true, true, "fat",        "Chất béo tốt, chống viêm"],
    ["Sữa dừa",        "safe",  true, true, "dairy_alt",  "Thay thế sữa bò, kem dừa nguyên chất"],
    ["Sữa hạnh nhân",  "safe",  true, true, "dairy_alt",  "Chọn loại không đường, không thêm phụ gia"],
    ["Sữa gạo",        "safe",  true, true, "dairy_alt",  "Nhẹ nhàng cho tiêu hóa"],
    // --- CẦN TRÁNH ---
    ["Bánh mì",        "avoid", false, true, "grain",     "Chứa gluten từ lúa mì - tránh hoàn toàn"],
    ["Mì sợi",         "avoid", false, true, "grain",     "Chứa gluten - thay bằng bún gạo"],
    ["Bánh quy",       "avoid", false, true, "grain",     "Chứa gluten và thường có đường cao"],
    ["Cháo yến mạch",  "avoid", false, true, "grain",     "Yến mạch thường nhiễm chéo gluten"],
    ["Lúa mì",         "avoid", false, true, "grain",     "Nguồn gluten chính cần loại bỏ"],
    ["Sữa bò",         "avoid", true, false, "dairy",     "Chứa casein - thay bằng sữa dừa/hạnh nhân"],
    ["Sữa dê",         "avoid", true, false, "dairy",     "Casein trong sữa dê tương tự sữa bò"],
    ["Phô mai",        "avoid", true, false, "dairy",     "Hàm lượng casein rất cao"],
    ["Bơ động vật",    "avoid", true, false, "dairy",     "Chứa casein - thay bằng dầu dừa"],
    ["Kem lạnh",       "avoid", true, false, "dairy",     "Chứa casein và đường cao"],
    ["Sữa chua thường","avoid", true, false, "dairy",     "Chứa casein - có loại sữa chua dừa thay thế"],
    ["Xúc xích",       "avoid", false, false,"processed", "Chứa cả gluten lẫn casein và phụ gia"],
    ["Nước ngọt",      "avoid", true, true,  "processed", "Đường cao, phụ gia, ảnh hưởng hành vi"],
    ["Kẹo bánh CN",    "avoid", false, false,"processed", "Đa số chứa gluten, casein, phẩm màu nhân tạo"]
  ];

  if (sheet.getLastRow() < 2) {
    sheet.getRange(2, 1, data.length, data[0].length).setValues(data);
    Logger.log("✓ Đã nhập " + data.length + " dòng dữ liệu GFCF");
  } else {
    Logger.log("⚠ GFCF_Diet đã có dữ liệu, bỏ qua");
  }
}

function step5_populateAcupressure() {
  Logger.log("Bước 5: Nhập dữ liệu huyệt đạo...");
  var ss    = SpreadsheetApp.openById(SETUP_CONFIG.SPREADSHEET_ID);
  var sheet = ss.getSheetByName("Acupressure_Points");

  var data = [
    // point_name_vi, point_name_en, location_vi, technique_vi, benefit_vi, caution_vi
    [
      "Á Môn", "Yamen (GV-15)",
      "Sau gáy, chính giữa đường chân tóc — lõm nhỏ ngay dưới xương chẩm",
      "Dùng ngón cái bấm nhẹ vào lõm đó, giữ 30 giây. Lặp 2 lần/ngày (sáng + tối).",
      "Hỗ trợ phát triển ngôn ngữ, kích thích vùng não điều khiển lời nói",
      "Tuyệt đối không bấm mạnh. Tránh khi trẻ sốt hoặc đau đầu."
    ],
    [
      "Thần Môn", "Shenmen (HT-7)",
      "Cổ tay trong (mặt bên lòng bàn tay), tại nếp gấp cổ tay, thẳng xuống từ ngón út",
      "Bấm nhẹ bằng ngón cái, giữ 30 giây. Làm cả 2 tay. 2 lần/ngày.",
      "An thần, giảm lo âu, giúp trẻ ngủ ngon, giảm meltdown",
      "Bấm nhẹ, không ấn mạnh vào dây thần kinh cổ tay"
    ],
    [
      "Nội Quan", "Neiguan (PC-6)",
      "Cổ tay trong, đặt 3 ngón tay từ nếp gấp lên → điểm cuối ngón thứ 3, giữa 2 gân",
      "Bấm nhẹ bằng ngón cái, giữ 30 giây. Làm cả 2 tay. 2 lần/ngày.",
      "Cải thiện tiêu hóa, giảm buồn nôn, an thần nhẹ",
      "Bấm nhẹ, phù hợp trẻ mọi độ tuổi"
    ],
    [
      "Bách Hội", "Baihui (GV-20)",
      "Đỉnh đầu: tìm điểm giao nhau giữa đường giữa đầu và đường nối 2 đỉnh tai",
      "Dùng ngón giữa bấm nhẹ, xoay tròn nhẹ 30 giây. 2 lần/ngày.",
      "Tăng tập trung, kích thích não bộ, cải thiện giấc ngủ",
      "Không ấn mạnh, đặc biệt với trẻ nhỏ dưới 2 tuổi"
    ],
    [
      "Hợp Cốc", "Hegu (LI-4)",
      "Mu bàn tay: vùng thịt phồng giữa gốc ngón cái và ngón trỏ — điểm cao nhất khi 2 ngón chụm",
      "Bấm nhẹ bằng ngón cái tay kia, giữ 30 giây. Làm cả 2 tay. 2 lần/ngày.",
      "Giảm căng thẳng, giảm đau đầu, cân bằng thần kinh",
      "Thường dùng được. Không dùng khi trẻ đang sốt cao."
    ],
    [
      "Lao Cung", "Laogong (PC-8)",
      "Lòng bàn tay: khi trẻ nắm tay nhẹ, điểm ngón giữa chạm vào lòng bàn tay",
      "Bấm nhẹ bằng ngón cái, giữ 30 giây. Làm cả 2 tay. 2 lần/ngày.",
      "An thần sâu, cân bằng cảm xúc, giảm kích động",
      "Bấm nhẹ tay, phù hợp trẻ mọi độ tuổi"
    ]
  ];

  if (sheet.getLastRow() < 2) {
    sheet.getRange(2, 1, data.length, data[0].length).setValues(data);
    Logger.log("✓ Đã nhập 6 huyệt đạo");
  } else {
    Logger.log("⚠ Acupressure_Points đã có dữ liệu, bỏ qua");
  }

  Logger.log("=== SETUP CƠ BẢN HOÀN TẤT ===");
}

/**
 * Chạy hàm này SAU KHI có Webapp URL từ Deploy
 */
function updateWebappUrl() {
  var url = SETUP_CONFIG.WEBAPP_URL;
  if (!url || url === "") {
    throw new Error("Điền WEBAPP_URL vào SETUP_CONFIG trước!");
  }
  PropertiesService.getScriptProperties().setProperty("WEBAPP_URL", url);
  Logger.log("✓ WEBAPP_URL đã lưu: " + url);
}

/**
 * Xoá dữ liệu user cũ để bắt đầu lại sạch
 * Chạy 1 lần sau khi migrate sang PropertiesService
 */
function resetUserData() {
  var props = PropertiesService.getScriptProperties();
  var keys  = props.getKeys();
  var count = 0;
  keys.forEach(function(k) {
    if (k.indexOf("user_") === 0 || k.indexOf("d_") === 0 || k.indexOf("q_") === 0) {
      props.deleteProperty(k);
      count++;
    }
  });
  Logger.log("✓ Đã xoá " + count + " key cũ. User sẽ bắt đầu onboarding lại từ đầu.");
}

/**
 * Xem thông tin user hiện tại (để kiểm tra)
 */
function xemUserData() {
  var props = PropertiesService.getScriptProperties();
  var keys  = props.getKeys().filter(function(k){ return k.indexOf("user_") === 0; });
  if (keys.length === 0) {
    Logger.log("Chưa có user nào.");
    return;
  }
  keys.forEach(function(k) {
    Logger.log(k + ": " + props.getProperty(k));
  });
}

/**
 * Đăng ký lại webhook (chạy khi URL thay đổi)
 */
function setupTelegramWebhook() {
  var props   = PropertiesService.getScriptProperties();
  var token   = props.getProperty("BOT_TOKEN");
  var webUrl  = props.getProperty("WEBAPP_URL");
  if (!token || !webUrl) {
    throw new Error("Thiếu BOT_TOKEN hoặc WEBAPP_URL trong Script Properties");
  }
  var url  = "https://api.telegram.org/bot" + token + "/setWebhook?url=" + webUrl;
  var resp = UrlFetchApp.fetch(url);
  Logger.log("Webhook: " + resp.getContentText());
}
