/**
 * AIAgent.gs — Claude API với Prompt Caching + Structured Output
 */

var TOOL_CLAUDE = {
  name: "tao_ke_hoach_ngay",
  description: "Tạo 3 hoạt động cho ngày mai cho trẻ rối loạn phát triển",
  input_schema: {
    type: "object",
    properties: {
      motor_task: {
        type: "object",
        properties: {
          title:            { type: "string", description: "Tên bài tập ngắn gọn (dưới 8 từ)" },
          description:      { type: "string", description: "Hướng dẫn chi tiết 2-3 câu bằng tiếng Việt" },
          duration_minutes: { type: "integer", minimum: 5, maximum: 30 },
          kb_reference:     { type: "string" }
        },
        required: ["title","description","duration_minutes","kb_reference"]
      },
      nutrition_task: {
        type: "object",
        properties: {
          title:           { type: "string", description: "Tên gợi ý dinh dưỡng ngắn" },
          description:     { type: "string", description: "Hướng dẫn cụ thể 2-3 câu bằng tiếng Việt" },
          gfcf_compliant:  { type: "boolean" },
          foods_mentioned: { type: "array", items: { type: "string" } }
        },
        required: ["title","description","gfcf_compliant","foods_mentioned"]
      },
      acupressure_task: {
        type: "object",
        properties: {
          point_name: {
            type: "string",
            enum: ["Á Môn","Thần Môn","Nội Quan","Bách Hội","Hợp Cốc","Lao Cung"]
          },
          rationale:          { type: "string", description: "Tại sao chọn huyệt này (1-2 câu)" },
          technique_reminder: { type: "string", description: "Cách bấm ngắn gọn" }
        },
        required: ["point_name","rationale","technique_reminder"]
      },
      encouragement: { type: "string", description: "Câu động viên ngắn cho ba mẹ (dưới 20 từ)" }
    },
    required: ["motor_task","nutrition_task","acupressure_task","encouragement"]
  }
};

function _systemPrompt() {
  return "Bạn là trợ lý giáo dục hỗ trợ phụ huynh can thiệp sớm cho trẻ rối loạn phát triển tại nhà ở Việt Nam.\n" +
  "Nhiệm vụ: dựa vào báo cáo hôm nay của phụ huynh, đề xuất 3 hoạt động cụ thể cho ngày mai.\n" +
  "Trả lời bằng TIẾNG VIỆT CÓ DẤU, ngôn ngữ thân thiện, dễ hiểu.\n\n" +

  "THỰC PHẨM AN TOÀN (GFCF - không chứa Gluten và Casein):\n" +
  "Gạo trắng, gạo lứt, bún gạo, phở gạo, khoai lang, khoai tây;\n" +
  "Thịt gà tươi, thịt heo tươi, cá (hồi, thu, rô phi), trứng gà;\n" +
  "Rau xanh tươi, cà rốt, bí đỏ; Chuối, táo, xoài, dưa hấu;\n" +
  "Dầu dừa, dầu ô liu; Sữa dừa, sữa hạnh nhân không đường.\n\n" +

  "THỰC PHẨM CẦN TRÁNH:\n" +
  "Gluten: lúa mì, bánh mì, mì sợi, bánh quy, cháo yến mạch.\n" +
  "Casein: sữa bò, phô mai, bơ động vật, kem lạnh, sữa chua thường.\n" +
  "Chế biến sẵn: xúc xích, nước ngọt, kẹo bánh công nghiệp.\n\n" +

  "HUYỆT ĐẠO BẤM HUYỆT (30 giây × 2 lần/ngày, bấm nhẹ):\n" +
  "1. Á Môn (GV-15): Sau gáy, giữa chân tóc → hỗ trợ ngôn ngữ\n" +
  "2. Thần Môn (HT-7): Cổ tay trong, phía ngón út → an thần, ngủ ngon\n" +
  "3. Nội Quan (PC-6): Cổ tay trong, trên Thần Môn 3 ngón → tiêu hóa, an thần\n" +
  "4. Bách Hội (GV-20): Đỉnh đầu → tăng tập trung, kích thích não\n" +
  "5. Hợp Cốc (LI-4): Mu bàn tay, vùng giữa ngón cái-trỏ → giảm căng thẳng\n" +
  "6. Lao Cung (PC-8): Lòng bàn tay, điểm ngón giữa chạm khi nắm nhẹ → an thần\n\n" +

  "QUY TẮC BẮT BUỘC:\n" +
  "- Đề xuất ĐÚNG 3 hoạt động: 1 vận động, 1 dinh dưỡng GFCF, 1 bấm huyệt\n" +
  "- Phù hợp độ tuổi và tình trạng được cung cấp\n" +
  "- Ngôn ngữ đơn giản, ba mẹ không chuyên tự làm được tại nhà\n" +
  "- KHÔNG đề xuất thuốc, KHÔNG chẩn đoán bệnh\n" +
  "- Tên huyệt PHẢI là một trong 6 huyệt đã liệt kê";
}

function _userPrompt(user, baocao, kb) {
  var nhan = { autism:"Tự kỷ (ASD)", adhd:"Tăng động (ADHD)", speech:"Chậm nói", social:"Kỹ năng xã hội", mixed:"Nhiều vấn đề" };
  var kbText = kb && kb.length
    ? kb.map(function(k){ return "[" + k.id + "] " + k.title_vi + ": " + k.summary_vi; }).join("\n")
    : "Không có tài liệu tham khảo — dùng kiến thức chung.";

  return "THÔNG TIN TRẺ:\n" +
    "- Tuổi: " + formatTuoi(user.tuoi_thang) + "\n" +
    "- Tình trạng: " + (nhan[user.tinh_trang] || "Chưa rõ") + "\n" +
    "- Tiến độ gần nhất: " + (user.tom_tat || "Chưa có dữ liệu") + "\n\n" +
    "BÁO CÁO HÔM NAY CỦA PHỤ HUYNH:\n" + (baocao || "").slice(0, 200) + "\n\n" +
    "TÀI LIỆU THAM KHẢO:\n" + kbText + "\n\n" +
    "Hãy tạo kế hoạch 3 hoạt động phù hợp cho bé ngày mai.";
}

function goiClaude(user, baocao, kb) {
  var props  = PropertiesService.getScriptProperties();
  var apiKey = props.getProperty("CLAUDE_API_KEY");
  var model  = props.getProperty("CLAUDE_MODEL") || "claude-haiku-3-5-20241022";

  if (!apiKey) throw new Error("Chưa có CLAUDE_API_KEY trong Script Properties");

  var payload = {
    model:      model,
    max_tokens: 1024,
    system: [{
      type: "text",
      text: _systemPrompt(),
      cache_control: { type: "ephemeral" }
    }],
    tools:       [TOOL_CLAUDE],
    tool_choice: { type: "tool", name: "tao_ke_hoach_ngay" },
    messages:    [{ role: "user", content: _userPrompt(user, baocao, kb) }]
  };

  var resp = UrlFetchApp.fetch("https://api.anthropic.com/v1/messages", {
    method:  "post",
    headers: {
      "Content-Type":      "application/json",
      "x-api-key":         apiKey,
      "anthropic-version": "2023-06-01",
      "anthropic-beta":    "prompt-caching-2024-07-31"
    },
    payload:            JSON.stringify(payload),
    muteHttpExceptions: true
  });

  var status = resp.getResponseCode();
  var body   = JSON.parse(resp.getContentText());

  if (status !== 200) {
    throw new Error("Claude API lỗi " + status + ": " + (body.error ? body.error.message : "Unknown"));
  }

  var toolResult = null;
  var content = body.content || [];
  for (var i = 0; i < content.length; i++) {
    if (content[i].type === "tool_use" && content[i].name === "tao_ke_hoach_ngay") {
      toolResult = content[i].input;
      break;
    }
  }
  if (!toolResult) throw new Error("Claude không trả về kết quả hợp lệ");

  var usage = body.usage || {};
  return {
    plan:         toolResult,
    tokensInput:  usage.input_tokens  || 0,
    tokensOutput: usage.output_tokens || 0,
    cacheHit:     (usage.cache_read_input_tokens || 0) > 0
  };
}

function tomTatTuan(chatId) {
  var user   = timUser(chatId);
  var nhatky = layNhatKyGanDay(chatId, 7);
  if (!user || nhatky.length === 0) return;

  var props  = PropertiesService.getScriptProperties();
  var apiKey = props.getProperty("CLAUDE_API_KEY");
  var model  = props.getProperty("CLAUDE_MODEL") || "claude-haiku-3-5-20241022";

  var baocao = nhatky.map(function(l){ return l.ngay + ": " + l.baocao; }).join("\n");

  var resp = UrlFetchApp.fetch("https://api.anthropic.com/v1/messages", {
    method:  "post",
    headers: {
      "Content-Type":      "application/json",
      "x-api-key":         apiKey,
      "anthropic-version": "2023-06-01"
    },
    payload: JSON.stringify({
      model: model, max_tokens: 150,
      messages: [{ role: "user", content:
        "Tóm tắt tiến độ của bé trong tuần qua thành 1 câu ngắn (tối đa 30 từ) bằng tiếng Việt:\n\n" + baocao
      }]
    }),
    muteHttpExceptions: true
  });

  var body = JSON.parse(resp.getContentText());
  if (resp.getResponseCode() === 200 && body.content && body.content[0]) {
    var tomtat  = body.content[0].text.trim();
    var weekNum = Math.ceil((new Date() - new Date(user.tao_luc || "2026-01-01")) / (7*24*3600*1000));
    capNhatTomTat(chatId, tomtat);
    luuDiemTuan(chatId, weekNum, nhatky.length, tomtat);
  }
}
