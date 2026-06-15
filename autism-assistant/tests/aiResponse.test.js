"use strict";
/**
 * TDD: Validate footer enforcement + prompt building + Claude response parsing
 */

require("./__mocks__/sheetsMock");
const { mockClaudeResponse, mockValidPlan } = require("./__mocks__/urlFetchMock");

const LEGAL_FOOTER = "Lưu ý: Ứng dụng chỉ cung cấp thông tin tham khảo nhắc việc sinh hoạt, không thay thế chẩn đoán y khoa.";
const ACUPRESSURE_POINTS = ["Á Môn", "Thần Môn", "Nội Quan", "Bách Hội", "Hợp Cốc", "Lao Cung"];

// ─── Shared functions (mirrors gas/Utils.gs + gas/AIAgent.gs) ────────────────
function appendFooter(text) {
  return text + "\n\n---\n" + LEGAL_FOOTER;
}

function buildSystemPrompt() {
  return `Bạn là trợ lý giáo dục hỗ trợ phụ huynh can thiệp cho trẻ rối loạn phát triển tại nhà.

## GFCF - Thực phẩm AN TOÀN
Gạo, gạo lứt, bún gạo, khoai lang, khoai tây, thịt gà tươi, thịt heo tươi, cá, trứng, rau xanh tươi, dầu dừa, sữa dừa.

## GFCF - Thực phẩm CẦN TRÁNH
Lúa mì, bánh mì, mì sợi; sữa bò, phô mai, bơ, kem, sữa chua thường.

## Bấm huyệt (30 giây × 2 lần/ngày)
1. Á Môn (GV-15): sau gáy → ngôn ngữ
2. Thần Môn (HT-7): cổ tay trong → an thần
3. Nội Quan (PC-6): cổ tay trong → tiêu hóa
4. Bách Hội (GV-20): đỉnh đầu → tập trung
5. Hợp Cốc (LI-4): mu bàn tay → giảm căng thẳng
6. Lao Cung (PC-8): lòng bàn tay → an thần`;
}

function buildUserPrompt(user, reportText, kbSnippets) {
  const years = Math.floor(user.child_age_months / 12);
  const months = user.child_age_months % 12;
  const conditionLabels = {
    autism: "Tự kỷ (ASD)",
    adhd: "Tăng động giảm chú ý (ADHD)",
    speech: "Chậm nói / ngôn ngữ",
    social: "Kỹ năng xã hội",
    mixed: "Nhiều vấn đề kết hợp"
  };
  const ageStr = months > 0 ? `${years} tuổi ${months} tháng` : `${years} tuổi`;

  const kbSection = kbSnippets.length
    ? kbSnippets.map(kb => `[${kb.id}] ${kb.title_vi}: ${kb.summary_vi}`).join("\n")
    : "Chưa có tài liệu liên quan.";

  return `## Thông tin trẻ
- Tuổi: ${ageStr}
- Tình trạng: ${conditionLabels[user.child_condition] || user.child_condition}
- Tóm tắt tiến độ: ${user.status_summary || "Chưa có dữ liệu"}

## Báo cáo hôm nay
${reportText}

## Tài liệu tham khảo
${kbSection}`;
}

function extractPlanFromResponse(apiResponse) {
  const toolUse = apiResponse.content && apiResponse.content.find(c => c.type === "tool_use");
  if (!toolUse || toolUse.name !== "generate_daily_plan") {
    throw new Error("No generate_daily_plan tool_use in response");
  }
  return toolUse.input;
}

function formatDailyPlanMessage(plan) {
  return `Gợi ý hoạt động ngày mai cho bé:

🏃 VẬN ĐỘNG — ${plan.motor_task.title} (${plan.motor_task.duration_minutes} phút)
${plan.motor_task.description}

🥗 DINH DƯỠNG GFCF — ${plan.nutrition_task.title}
${plan.nutrition_task.description}

💆 BẤM HUYỆT — ${plan.acupressure_task.point_name}
${plan.acupressure_task.rationale}
${plan.acupressure_task.technique_reminder}

💪 ${plan.encouragement}`;
}

// ─── Tests ───────────────────────────────────────────────────────────────────
describe("Footer Enforcement", () => {

  test("appendFooter adds legal disclaimer", () => {
    const result = appendFooter("Nội dung bình thường.");
    expect(result).toContain(LEGAL_FOOTER);
  });

  test("footer is after the main content", () => {
    const result = appendFooter("Nội dung.");
    const footerIndex = result.indexOf(LEGAL_FOOTER);
    const contentIndex = result.indexOf("Nội dung.");
    expect(footerIndex).toBeGreaterThan(contentIndex);
  });

  test("footer appears exactly once", () => {
    const result = appendFooter("abc");
    const count = (result.match(new RegExp(LEGAL_FOOTER.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "g")) || []).length;
    expect(count).toBe(1);
  });

  test("formatted daily plan contains footer when sent through appendFooter", () => {
    const message = appendFooter(formatDailyPlanMessage(mockValidPlan));
    expect(message).toContain("chẩn đoán y khoa");
  });

  test("appendFooter does not strip Vietnamese characters", () => {
    const text = "Hôm nay bé quấy, không chịu ăn.";
    const result = appendFooter(text);
    expect(result).toContain(text);
  });
});

describe("System Prompt Content", () => {

  test("system prompt contains all 6 acupressure point names", () => {
    const prompt = buildSystemPrompt();
    ACUPRESSURE_POINTS.forEach(point => {
      expect(prompt).toContain(point);
    });
  });

  test("system prompt contains GFCF safe foods section", () => {
    const prompt = buildSystemPrompt();
    expect(prompt).toContain("GFCF");
    expect(prompt).toContain("Gạo");
  });

  test("system prompt contains GFCF avoid foods section", () => {
    const prompt = buildSystemPrompt();
    expect(prompt).toContain("TRÁNH");
    expect(prompt).toContain("sữa bò");
  });
});

describe("User Prompt Building", () => {
  const mockUser = {
    child_age_months: 36,
    child_condition: "autism",
    status_summary: "Bé tiến bộ về giao tiếp mắt."
  };

  test("user prompt contains child age in years", () => {
    const prompt = buildUserPrompt(mockUser, "Hôm nay bé quấy", []);
    expect(prompt).toContain("3 tuổi");
  });

  test("user prompt contains condition in Vietnamese", () => {
    const prompt = buildUserPrompt(mockUser, "test", []);
    expect(prompt).toContain("Tự kỷ");
  });

  test("user prompt contains parent report text", () => {
    const report = "Hôm nay bé không chịu ăn và nằm lăn ra sàn.";
    const prompt = buildUserPrompt(mockUser, report, []);
    expect(prompt).toContain(report);
  });

  test("user prompt contains status summary", () => {
    const prompt = buildUserPrompt(mockUser, "test", []);
    expect(prompt).toContain("tiến bộ về giao tiếp mắt");
  });

  test("user prompt includes KB snippets when provided", () => {
    const kb = [{ id: "KB-001", title_vi: "Từng bước nhỏ", summary_vi: "Chương trình can thiệp." }];
    const prompt = buildUserPrompt(mockUser, "test", kb);
    expect(prompt).toContain("KB-001");
    expect(prompt).toContain("Từng bước nhỏ");
  });

  test("age with months formatted correctly (36 months = 3 tuổi)", () => {
    const user = { ...mockUser, child_age_months: 36 };
    const prompt = buildUserPrompt(user, "test", []);
    expect(prompt).toContain("3 tuổi");
    expect(prompt).not.toContain("3 tuổi 0 tháng");
  });

  test("age with months formatted correctly (43 months = 3 tuổi 7 tháng)", () => {
    const user = { ...mockUser, child_age_months: 43 };
    const prompt = buildUserPrompt(user, "test", []);
    expect(prompt).toContain("3 tuổi 7 tháng");
  });
});

describe("Claude Response Parsing", () => {

  test("extracts plan from valid tool_use response", () => {
    const result = extractPlanFromResponse(mockClaudeResponse);
    expect(result).toEqual(mockValidPlan);
  });

  test("throws if no tool_use in response", () => {
    const badResponse = { content: [{ type: "text", text: "Hello" }] };
    expect(() => extractPlanFromResponse(badResponse)).toThrow("No generate_daily_plan tool_use");
  });

  test("throws if tool name is wrong", () => {
    const badResponse = { content: [{ type: "tool_use", name: "other_tool", input: {} }] };
    expect(() => extractPlanFromResponse(badResponse)).toThrow("No generate_daily_plan tool_use");
  });

  test("cache_hit detected from response usage", () => {
    const cacheHit = mockClaudeResponse.usage.cache_read_input_tokens > 0;
    expect(cacheHit).toBe(true);
  });

  test("tokens extracted from response", () => {
    const { input_tokens, output_tokens } = mockClaudeResponse.usage;
    expect(input_tokens).toBe(790);
    expect(output_tokens).toBe(350);
  });
});

module.exports = { appendFooter, buildSystemPrompt, buildUserPrompt, extractPlanFromResponse, formatDailyPlanMessage };
