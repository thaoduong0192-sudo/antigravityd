"use strict";
/**
 * TDD: Validate Claude JSON output schema
 * Tests run BEFORE GAS implementation — they will fail (red) until gas/AIAgent.gs logic
 * is extracted into a shared validator.
 */

require("./__mocks__/sheetsMock");
require("./__mocks__/urlFetchMock");

const VALID_POINTS = ["Á Môn", "Thần Môn", "Nội Quan", "Bách Hội", "Hợp Cốc", "Lao Cung"];

// ─── Schema validator (mirrors logic in gas/AIAgent.gs) ──────────────────────
function validatePlanSchema(plan) {
  if (!plan || typeof plan !== "object") throw new Error("plan must be an object");

  // motor_task
  if (!plan.motor_task) throw new Error("motor_task required");
  const m = plan.motor_task;
  if (!m.title || typeof m.title !== "string") throw new Error("motor_task.title required");
  if (!m.description) throw new Error("motor_task.description required");
  if (typeof m.duration_minutes !== "number") throw new Error("motor_task.duration_minutes must be number");
  if (m.duration_minutes < 5 || m.duration_minutes > 30) throw new Error("duration_minutes out of range [5,30]");
  if (typeof m.kb_reference !== "string") throw new Error("motor_task.kb_reference must be string");

  // nutrition_task
  if (!plan.nutrition_task) throw new Error("nutrition_task required");
  const n = plan.nutrition_task;
  if (!n.title) throw new Error("nutrition_task.title required");
  if (!n.description) throw new Error("nutrition_task.description required");
  if (typeof n.gfcf_compliant !== "boolean") throw new Error("nutrition_task.gfcf_compliant must be boolean");
  if (!Array.isArray(n.foods_mentioned)) throw new Error("nutrition_task.foods_mentioned must be array");

  // acupressure_task
  if (!plan.acupressure_task) throw new Error("acupressure_task required");
  const a = plan.acupressure_task;
  if (!VALID_POINTS.includes(a.point_name)) throw new Error(`invalid point_name: "${a.point_name}". Must be one of: ${VALID_POINTS.join(", ")}`);
  if (!a.rationale) throw new Error("acupressure_task.rationale required");
  if (!a.technique_reminder) throw new Error("acupressure_task.technique_reminder required");

  // encouragement
  if (!plan.encouragement || typeof plan.encouragement !== "string") throw new Error("encouragement required");

  return true;
}

// ─── Base valid plan for reuse ────────────────────────────────────────────────
const validBase = {
  motor_task: {
    title: "Bài tập cân bằng trên gối",
    description: "Cho bé ngồi trên gối bơm hơi và giữ thăng bằng 30 giây.",
    duration_minutes: 10,
    kb_reference: "KB-007"
  },
  nutrition_task: {
    title: "Cơm gạo lứt với rau luộc",
    description: "Thay mì sợi bằng cơm gạo lứt hôm nay.",
    gfcf_compliant: true,
    foods_mentioned: ["gạo lứt", "rau xanh"]
  },
  acupressure_task: {
    point_name: "Thần Môn",
    rationale: "Bé quấy và khó ngủ.",
    technique_reminder: "Bấm nhẹ 30 giây × 2 lần/ngày."
  },
  encouragement: "Ba mẹ đang làm rất tốt!"
};

// ─── Tests ───────────────────────────────────────────────────────────────────
describe("Claude JSON Output Schema Validation", () => {

  test("valid plan passes schema", () => {
    expect(() => validatePlanSchema(validBase)).not.toThrow();
    expect(validatePlanSchema(validBase)).toBe(true);
  });

  test("missing motor_task throws", () => {
    const plan = { nutrition_task: validBase.nutrition_task, acupressure_task: validBase.acupressure_task, encouragement: "ok" };
    expect(() => validatePlanSchema(plan)).toThrow("motor_task required");
  });

  test("missing nutrition_task throws", () => {
    const plan = { motor_task: validBase.motor_task, acupressure_task: validBase.acupressure_task, encouragement: "ok" };
    expect(() => validatePlanSchema(plan)).toThrow("nutrition_task required");
  });

  test("missing acupressure_task throws", () => {
    const plan = { motor_task: validBase.motor_task, nutrition_task: validBase.nutrition_task, encouragement: "ok" };
    expect(() => validatePlanSchema(plan)).toThrow("acupressure_task required");
  });

  test("invalid acupressure point_name throws", () => {
    const plan = { ...validBase, acupressure_task: { ...validBase.acupressure_task, point_name: "Huyệt lạ" } };
    expect(() => validatePlanSchema(plan)).toThrow("invalid point_name");
  });

  test("all 6 valid acupressure point names pass", () => {
    VALID_POINTS.forEach(pointName => {
      const plan = { ...validBase, acupressure_task: { ...validBase.acupressure_task, point_name: pointName } };
      expect(() => validatePlanSchema(plan)).not.toThrow();
    });
  });

  test("duration_minutes below 5 throws", () => {
    const plan = { ...validBase, motor_task: { ...validBase.motor_task, duration_minutes: 2 } };
    expect(() => validatePlanSchema(plan)).toThrow("duration_minutes out of range");
  });

  test("duration_minutes above 30 throws", () => {
    const plan = { ...validBase, motor_task: { ...validBase.motor_task, duration_minutes: 45 } };
    expect(() => validatePlanSchema(plan)).toThrow("duration_minutes out of range");
  });

  test("duration_minutes at boundary 5 passes", () => {
    const plan = { ...validBase, motor_task: { ...validBase.motor_task, duration_minutes: 5 } };
    expect(() => validatePlanSchema(plan)).not.toThrow();
  });

  test("duration_minutes at boundary 30 passes", () => {
    const plan = { ...validBase, motor_task: { ...validBase.motor_task, duration_minutes: 30 } };
    expect(() => validatePlanSchema(plan)).not.toThrow();
  });

  test("non-boolean gfcf_compliant throws", () => {
    const plan = { ...validBase, nutrition_task: { ...validBase.nutrition_task, gfcf_compliant: "yes" } };
    expect(() => validatePlanSchema(plan)).toThrow("gfcf_compliant must be boolean");
  });

  test("non-array foods_mentioned throws", () => {
    const plan = { ...validBase, nutrition_task: { ...validBase.nutrition_task, foods_mentioned: "gạo lứt" } };
    expect(() => validatePlanSchema(plan)).toThrow("foods_mentioned must be array");
  });

  test("missing encouragement throws", () => {
    const { encouragement, ...plan } = validBase;
    expect(() => validatePlanSchema(plan)).toThrow("encouragement required");
  });

  test("null plan throws", () => {
    expect(() => validatePlanSchema(null)).toThrow("plan must be an object");
  });
});

module.exports = { validatePlanSchema };
