"use strict";
/**
 * TDD: Validate Google Sheets row mapping logic
 */

const { mockSpreadsheet, MockSheet } = require("./__mocks__/sheetsMock");
require("./__mocks__/urlFetchMock");

// ─── Column indices (0-based) matching Database.gs schema ───────────────────
const COL = {
  USERS: {
    telegram_chat_id: 0, display_name: 1, child_age_months: 2,
    child_condition: 3, onboarding_step: 4, status_summary: 5,
    current_program: 6, program_week: 7, last_active: 8,
    total_days_logged: 9, created_at: 10
  },
  DAILY_LOGS: {
    log_id: 0, telegram_chat_id: 1, log_date: 2, parent_report: 3,
    motor_task: 4, nutrition_task: 5, acupressure_task: 6,
    kb_references: 7, tokens_input: 8, tokens_output: 9, cache_hit: 10
  }
};

// ─── Inline Database logic (mirrors gas/Database.gs) ─────────────────────────
// This is the testable subset — production code in Database.gs reuses same logic

const SHEET_NAMES = {
  USERS: "Users",
  DAILY_LOGS: "Daily_Logs",
  KNOWLEDGE_BASE: "Knowledge_Base"
};

function getSheet(name) {
  return mockSpreadsheet.getSheetByName(name);
}

function getUser(chatId) {
  const sheet = getSheet(SHEET_NAMES.USERS);
  const rows = sheet.getDataRange().getValues();
  // Skip header row (index 0 when data includes header, or check first row content)
  for (let i = 0; i < rows.length; i++) {
    if (String(rows[i][COL.USERS.telegram_chat_id]) === String(chatId)) {
      const r = rows[i];
      return {
        telegram_chat_id: r[0], display_name: r[1],
        child_age_months: r[2], child_condition: r[3],
        onboarding_step: Number(r[4] || 0),
        status_summary: r[5], current_program: r[6],
        program_week: r[7], last_active: r[8],
        total_days_logged: Number(r[9] || 0),
        created_at: r[10], _rowIndex: i
      };
    }
  }
  return null;
}

function upsertUser(chatId, data) {
  const sheet = getSheet(SHEET_NAMES.USERS);
  const existing = getUser(chatId);
  const now = new Date().toISOString();

  if (existing) {
    // Update existing row
    Object.assign(existing, data);
    sheet.data[existing._rowIndex] = [
      existing.telegram_chat_id, existing.display_name,
      existing.child_age_months, existing.child_condition,
      existing.onboarding_step, existing.status_summary,
      existing.current_program, existing.program_week,
      now, existing.total_days_logged, existing.created_at
    ];
  } else {
    // Insert new row
    sheet.appendRow([
      chatId,
      data.display_name || "",
      data.child_age_months || 0,
      data.child_condition || "",
      data.onboarding_step || 0,
      data.status_summary || "",
      data.current_program || "",
      data.program_week || 0,
      now,
      data.total_days_logged || 0,
      data.created_at || now
    ]);
  }
}

function updateUserStatus(chatId, summaryText) {
  const sheet = getSheet(SHEET_NAMES.USERS);
  const user = getUser(chatId);
  if (!user) return false;
  sheet.data[user._rowIndex][COL.USERS.status_summary] = summaryText;
  return true;
}

function incrementDaysLogged(chatId) {
  const sheet = getSheet(SHEET_NAMES.USERS);
  const user = getUser(chatId);
  if (!user) return false;
  sheet.data[user._rowIndex][COL.USERS.total_days_logged] =
    (Number(sheet.data[user._rowIndex][COL.USERS.total_days_logged]) || 0) + 1;
  return true;
}

function generateLogId(chatId, dateStr) {
  // dateStr format: yyyyMMdd
  return `${chatId}_${dateStr}`;
}

function appendDailyLog(logData) {
  const sheet = getSheet(SHEET_NAMES.DAILY_LOGS);
  const dateStr = logData.dateStr || new Date().toISOString().slice(0, 10).replace(/-/g, "");
  const logId = generateLogId(logData.chatId, dateStr);
  sheet.appendRow([
    logId,
    logData.chatId,
    logData.date || dateStr,
    (logData.reportText || "").slice(0, 200),
    JSON.stringify(logData.plan?.motor_task || {}),
    JSON.stringify(logData.plan?.nutrition_task || {}),
    JSON.stringify(logData.plan?.acupressure_task || {}),
    logData.kbReferences || "",
    logData.tokensInput || 0,
    logData.tokensOutput || 0,
    logData.cacheHit ? "TRUE" : "FALSE"
  ]);
  return logId;
}

function getKBByCondition(condition, limit) {
  const sheet = getSheet(SHEET_NAMES.KNOWLEDGE_BASE);
  const rows = sheet.getDataRange().getValues();
  return rows
    .filter(r => r[1] === condition && r[5])  // category matches AND has summary
    .slice(0, limit)
    .map(r => ({
      id: r[0], category: r[1], subcategory: r[2],
      title_vi: r[3], source_url: r[4], summary_vi: r[5]
    }));
}

// ─── Tests ───────────────────────────────────────────────────────────────────
describe("Database Row Mapping", () => {

  beforeEach(() => {
    // Reset sheets before each test
    const usersSheet = getSheet(SHEET_NAMES.USERS);
    usersSheet.data = [];
    usersSheet.appendedRows = [];
    const logsSheet = getSheet(SHEET_NAMES.DAILY_LOGS);
    logsSheet.data = [];
    logsSheet.appendedRows = [];
  });

  // ── getUser ──────────────────────────────────────────────────────────────
  test("getUser returns null for unknown chatId", () => {
    expect(getUser("unknown_999")).toBeNull();
  });

  test("getUser finds existing user by chatId", () => {
    const sheet = getSheet(SHEET_NAMES.USERS);
    sheet.data = [["111", "Nguyễn A", 36, "autism", 3, "", "tubucnho_tap4", 1, "", 5, "2026-01-01"]];
    const user = getUser("111");
    expect(user).not.toBeNull();
    expect(user.display_name).toBe("Nguyễn A");
    expect(user.child_age_months).toBe(36);
  });

  test("getUser returns correct onboarding_step as number", () => {
    const sheet = getSheet(SHEET_NAMES.USERS);
    sheet.data = [["111", "Test", 24, "speech", "2", "", "", 0, "", 0, ""]];
    const user = getUser("111");
    expect(user.onboarding_step).toBe(2);
    expect(typeof user.onboarding_step).toBe("number");
  });

  // ── upsertUser ────────────────────────────────────────────────────────────
  test("upsertUser creates new row for new user", () => {
    const sheet = getSheet(SHEET_NAMES.USERS);
    upsertUser("new_user_123", { display_name: "Trần B", child_age_months: 48, onboarding_step: 0 });
    expect(sheet.data).toHaveLength(1);
    expect(sheet.data[0][COL.USERS.telegram_chat_id]).toBe("new_user_123");
    expect(sheet.data[0][COL.USERS.display_name]).toBe("Trần B");
  });

  test("upsertUser updates existing user without creating duplicate", () => {
    const sheet = getSheet(SHEET_NAMES.USERS);
    sheet.data = [["333", "Lê C", 30, "adhd", 1, "", "", 0, "", 2, "2026-01-01"]];
    upsertUser("333", { onboarding_step: 2, child_condition: "adhd" });
    expect(sheet.data).toHaveLength(1);  // no duplicate
  });

  // ── updateUserStatus ──────────────────────────────────────────────────────
  test("updateUserStatus overwrites only status_summary (col index 5)", () => {
    const sheet = getSheet(SHEET_NAMES.USERS);
    sheet.data = [["444", "User D", 36, "autism", 3, "old summary", "tubucnho_tap4", 1, "", 10, "2026-01-01"]];
    updateUserStatus("444", "new weekly summary");
    expect(sheet.data[0][COL.USERS.status_summary]).toBe("new weekly summary");   // col F
    expect(sheet.data[0][COL.USERS.current_program]).toBe("tubucnho_tap4");       // col G unchanged
    expect(sheet.data[0][COL.USERS.total_days_logged]).toBe(10);                  // col J unchanged
  });

  test("updateUserStatus returns false for unknown user", () => {
    const result = updateUserStatus("nonexistent", "summary");
    expect(result).toBe(false);
  });

  // ── incrementDaysLogged ───────────────────────────────────────────────────
  test("incrementDaysLogged increases total_days_logged by 1", () => {
    const sheet = getSheet(SHEET_NAMES.USERS);
    sheet.data = [["555", "User E", 48, "autism", 3, "", "", 0, "", 7, "2026-01-01"]];
    incrementDaysLogged("555");
    expect(sheet.data[0][COL.USERS.total_days_logged]).toBe(8);
  });

  // ── appendDailyLog ────────────────────────────────────────────────────────
  test("appendDailyLog creates row with correct log_id format", () => {
    const logId = appendDailyLog({
      chatId: "777",
      dateStr: "20260419",
      date: "2026-04-19",
      reportText: "Hôm nay bé quấy",
      plan: { motor_task: {}, nutrition_task: {}, acupressure_task: {} },
      tokensInput: 790, tokensOutput: 350, cacheHit: true
    });
    expect(logId).toBe("777_20260419");
  });

  test("appendDailyLog truncates report to 200 chars", () => {
    const longReport = "a".repeat(300);
    const sheet = getSheet(SHEET_NAMES.DAILY_LOGS);
    appendDailyLog({ chatId: "888", dateStr: "20260419", reportText: longReport, plan: {} });
    const appendedReport = sheet.data[0][COL.DAILY_LOGS.parent_report];
    expect(appendedReport.length).toBeLessThanOrEqual(200);
  });

  test("appendDailyLog records cache_hit as TRUE string", () => {
    const sheet = getSheet(SHEET_NAMES.DAILY_LOGS);
    appendDailyLog({ chatId: "999", dateStr: "20260419", reportText: "test", plan: {}, cacheHit: true });
    expect(sheet.data[0][COL.DAILY_LOGS.cache_hit]).toBe("TRUE");
  });

  test("appendDailyLog records cache miss as FALSE string", () => {
    const sheet = getSheet(SHEET_NAMES.DAILY_LOGS);
    appendDailyLog({ chatId: "101", dateStr: "20260419", reportText: "test", plan: {}, cacheHit: false });
    expect(sheet.data[0][COL.DAILY_LOGS.cache_hit]).toBe("FALSE");
  });

  // ── getKBByCondition ──────────────────────────────────────────────────────
  test("getKBByCondition filters by category", () => {
    const sheet = getSheet(SHEET_NAMES.KNOWLEDGE_BASE);
    sheet.data = [
      ["KB-001", "autism",  "", "Tài liệu autism",  "http://a", "Tóm tắt A", "autism", "2-8", "medium", ""],
      ["KB-002", "adhd",    "", "Tài liệu ADHD",    "http://b", "Tóm tắt B", "adhd",   "4-10","medium", ""],
      ["KB-003", "autism",  "", "Tài liệu autism 2","http://c", "Tóm tắt C", "autism", "2-8", "easy",   ""]
    ];
    const results = getKBByCondition("autism", 3);
    expect(results).toHaveLength(2);
    results.forEach(r => expect(r.category).toBe("autism"));
  });

  test("getKBByCondition respects limit parameter", () => {
    const sheet = getSheet(SHEET_NAMES.KNOWLEDGE_BASE);
    sheet.data = [
      ["KB-001", "autism", "", "Doc 1", "http://a", "Summary 1", "autism", "", "", ""],
      ["KB-002", "autism", "", "Doc 2", "http://b", "Summary 2", "autism", "", "", ""],
      ["KB-003", "autism", "", "Doc 3", "http://c", "Summary 3", "autism", "", "", ""]
    ];
    const results = getKBByCondition("autism", 2);
    expect(results).toHaveLength(2);
  });

  test("getKBByCondition excludes rows with empty summary_vi", () => {
    const sheet = getSheet(SHEET_NAMES.KNOWLEDGE_BASE);
    sheet.data = [
      ["KB-001", "autism", "", "Doc with summary", "http://a", "Summary exists", "", "", "", ""],
      ["KB-002", "autism", "", "Doc no summary",   "http://b", "",               "", "", "", ""]
    ];
    const results = getKBByCondition("autism", 10);
    expect(results).toHaveLength(1);
    expect(results[0].id).toBe("KB-001");
  });

  // ── generateLogId ─────────────────────────────────────────────────────────
  test("generateLogId format is chatId_yyyyMMdd", () => {
    expect(generateLogId("12345", "20260419")).toBe("12345_20260419");
  });
});

module.exports = { getUser, upsertUser, updateUserStatus, incrementDaysLogged, appendDailyLog, getKBByCondition };
