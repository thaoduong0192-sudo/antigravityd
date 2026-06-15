/**
 * Database.gs — Lưu Users vào PropertiesService (nhanh, không lỗi quyền)
 *               Lưu Daily_Logs vào Google Sheets (append-only, để xem lịch sử)
 */

// Column index cho sheet Daily_Logs
var CL = { id:0, chatid:1, ngay:2, baocao:3, vandog:4, dinhduong:5, bamhuyet:6, kb:7, tin:8, tout:9, cache:10 };
// Column index cho sheet Knowledge_Base
var CK = { id:0, cat:1, sub:2, title:3, url:4, tomtat:5 };

function _getSheet(ten) {
  var id = PropertiesService.getScriptProperties().getProperty("SPREADSHEET_ID");
  return SpreadsheetApp.openById(id).getSheetByName(ten);
}

function _getNow() {
  return Utilities.formatDate(new Date(), "Asia/Ho_Chi_Minh", "yyyy-MM-dd'T'HH:mm:ss");
}

function formatTuoi(thang) {
  if (!thang || thang <= 0) return "Chưa rõ";
  var nam     = Math.floor(thang / 12);
  var thangDu = thang % 12;
  if (nam === 0) return thangDu + " tháng";
  if (thangDu === 0) return nam + " tuổi";
  return nam + " tuổi " + thangDu + " tháng";
}

// ─── Users: lưu trong PropertiesService ───────────────────────────────────────
// Key: "user_{chatId}", Value: JSON string

function timUser(chatId) {
  try {
    var raw = PropertiesService.getScriptProperties().getProperty("user_" + chatId);
    if (!raw) return null;
    var u = JSON.parse(raw);
    // Đảm bảo các trường số đúng kiểu
    u.buoc       = Number(u.buoc)       || 0;
    u.tuoi_thang = Number(u.tuoi_thang) || 0;
    u.so_ngay    = Number(u.so_ngay)    || 0;
    return u;
  } catch(e) {
    return null;
  }
}

function taoUser(chatId, ten) {
  var user = {
    chatId:       String(chatId),
    ten:          ten || "",
    tuoi_thang:   0,
    tinh_trang:   "",
    buoc:         0,
    tom_tat:      "",
    chuong_trinh: "",
    tuan:         0,
    so_ngay:      0,
    tao_luc:      _getNow()
  };
  PropertiesService.getScriptProperties().setProperty("user_" + chatId, JSON.stringify(user));
}

function capNhatUser(chatId, data) {
  var u = timUser(chatId);
  if (!u) { taoUser(chatId, data.ten || ""); u = timUser(chatId); }
  if (!u) return;

  // Merge các trường được cập nhật
  if (data.ten           !== undefined) u.ten          = data.ten;
  if (data.tuoi_thang    !== undefined) u.tuoi_thang   = data.tuoi_thang;
  if (data.tinh_trang    !== undefined) u.tinh_trang   = data.tinh_trang;
  if (data.buoc          !== undefined) u.buoc         = data.buoc;
  if (data.tom_tat       !== undefined) u.tom_tat      = data.tom_tat;
  if (data.chuong_trinh  !== undefined) u.chuong_trinh = data.chuong_trinh;
  if (data.tuan_chuong_trinh !== undefined) u.tuan     = data.tuan_chuong_trinh;

  PropertiesService.getScriptProperties().setProperty("user_" + chatId, JSON.stringify(u));
}

function datBuoc(chatId, buoc) {
  var u = timUser(chatId);
  if (!u) return;
  u.buoc = Number(buoc);
  PropertiesService.getScriptProperties().setProperty("user_" + chatId, JSON.stringify(u));
}

function tangNgay(chatId) {
  var u = timUser(chatId);
  if (!u) return;
  u.so_ngay = (Number(u.so_ngay) || 0) + 1;
  PropertiesService.getScriptProperties().setProperty("user_" + chatId, JSON.stringify(u));
}

function capNhatTomTat(chatId, tomtat) {
  var u = timUser(chatId);
  if (!u) return;
  u.tom_tat = tomtat;
  PropertiesService.getScriptProperties().setProperty("user_" + chatId, JSON.stringify(u));
}

// ─── Daily Logs ───────────────────────────────────────────────────────────────

function luuNhatKy(data) {
  var sheet  = _getSheet("Daily_Logs");
  var ds     = Utilities.formatDate(new Date(), "Asia/Ho_Chi_Minh", "yyyyMMdd");
  var ngay   = Utilities.formatDate(new Date(), "Asia/Ho_Chi_Minh", "yyyy-MM-dd");
  var plan   = data.kehoach || {};
  sheet.appendRow([
    data.chatId + "_" + ds,
    String(data.chatId),
    ngay,
    (data.baocao || "").slice(0, 200),
    JSON.stringify(plan.motor_task        || {}),
    JSON.stringify(plan.nutrition_task    || {}),
    JSON.stringify(plan.acupressure_task  || {}),
    (data.kb_ids || []).join(","),
    data.tin   || 0,
    data.tout  || 0,
    data.cache ? "TRUE" : "FALSE"
  ]);
}

function layNhatKyGanDay(chatId, soNgay) {
  var sheet = _getSheet("Daily_Logs");
  var rows  = sheet.getDataRange().getValues();
  return rows
    .filter(function(r){ return String(r[CL.chatid]) === String(chatId); })
    .slice(-soNgay)
    .map(function(r){ return { ngay: r[CL.ngay], baocao: r[CL.baocao] }; });
}

// ─── Knowledge Base ───────────────────────────────────────────────────────────

function layKB(tinhTrang, limit) {
  try {
    var sheet   = _getSheet("Knowledge_Base");
    var rows    = sheet.getDataRange().getValues();
    var results = [];
    for (var i = 1; i < rows.length; i++) {  // bỏ header row
      var r = rows[i];
      if (r[CK.cat] === tinhTrang && r[CK.tomtat]) {
        results.push({ id: r[CK.id], title_vi: r[CK.title], summary_vi: r[CK.tomtat] });
        if (results.length >= limit) break;
      }
    }
    return results;
  } catch(e) {
    return [];  // KB chưa có dữ liệu → dùng kiến thức chung của Claude
  }
}

// ─── Weekly Scores ────────────────────────────────────────────────────────────

function luuDiemTuan(chatId, weekNum, soNgay, tomtat) {
  var sheet = _getSheet("Weekly_Scores");
  sheet.appendRow([
    chatId + "_W" + weekNum, String(chatId),
    Utilities.formatDate(new Date(), "Asia/Ho_Chi_Minh", "yyyy-MM-dd"),
    soNgay, "unknown", "unknown", "unknown", tomtat, _getNow()
  ]);
}
