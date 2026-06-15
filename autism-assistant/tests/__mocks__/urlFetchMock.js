/**
 * Mock UrlFetchApp for GAS unit tests
 */

const mockValidPlan = {
  motor_task: {
    title: "Bài tập cân bằng trên gối",
    description: "Cho bé ngồi trên gối bơm hơi và giữ thăng bằng 30 giây. Lặp lại 3-5 lần mỗi buổi.",
    duration_minutes: 10,
    kb_reference: "KB-007"
  },
  nutrition_task: {
    title: "Cơm gạo lứt với rau luộc",
    description: "Thay mì sợi bằng cơm gạo lứt hôm nay. Thêm rau cải xanh luộc và trứng chiên.",
    gfcf_compliant: true,
    foods_mentioned: ["gạo lứt", "rau cải", "trứng"]
  },
  acupressure_task: {
    point_name: "Thần Môn",
    rationale: "Bé quấy và khó ngủ, huyệt Thần Môn giúp an thần.",
    technique_reminder: "Bấm nhẹ cổ tay trong phía ngón út, 30 giây × 2 lần/ngày."
  },
  encouragement: "Ba mẹ đang làm rất tốt, hãy kiên trì!"
};

const mockClaudeResponse = {
  id: "msg_mock",
  type: "message",
  role: "assistant",
  content: [
    {
      type: "tool_use",
      id: "tool_mock_001",
      name: "generate_daily_plan",
      input: mockValidPlan
    }
  ],
  usage: {
    input_tokens: 790,
    output_tokens: 350,
    cache_read_input_tokens: 900,
    cache_creation_input_tokens: 0
  }
};

global.UrlFetchApp = {
  _mockResponses: {},
  _calls: [],

  fetch: function(url, options) {
    this._calls.push({ url, options });
    const mockResp = this._mockResponses[url] || {
      getResponseCode: () => 200,
      getContentText: () => JSON.stringify(mockClaudeResponse)
    };
    return mockResp;
  },

  setMockResponse: function(url, responseBody, statusCode = 200) {
    this._mockResponses[url] = {
      getResponseCode: () => statusCode,
      getContentText: () => typeof responseBody === "string" ? responseBody : JSON.stringify(responseBody)
    };
  },

  reset: function() {
    this._mockResponses = {};
    this._calls = [];
  }
};

global.ContentService = {
  createTextOutput: (text) => ({
    _text: text,
    setMimeType: function(mime) { this._mime = mime; return this; }
  }),
  MimeType: { JSON: "application/json", TEXT: "text/plain" }
};

module.exports = { mockValidPlan, mockClaudeResponse };
