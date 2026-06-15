/**
 * Mock SpreadsheetApp for GAS unit tests
 */

class MockSheet {
  constructor(name) {
    this.name = name;
    this.data = [];        // rows as arrays
    this.appendedRows = [];
  }

  getDataRange() {
    return {
      getValues: () => [
        // header row (index 0), then data rows
        ...this.data
      ]
    };
  }

  appendRow(row) {
    this.appendedRows.push(row);
    this.data.push(row);
  }

  getRange(row, col, numRows, numCols) {
    const self = this;
    return {
      getValues: () => {
        const result = [];
        for (let r = row - 1; r < row - 1 + numRows; r++) {
          const rowData = [];
          for (let c = col - 1; c < col - 1 + numCols; c++) {
            rowData.push(self.data[r] ? self.data[r][c] || "" : "");
          }
          result.push(rowData);
        }
        return result;
      },
      setValue: (val) => {
        if (!self.data[row - 1]) self.data[row - 1] = [];
        self.data[row - 1][col - 1] = val;
      },
      setValues: (vals) => {
        for (let r = 0; r < numRows; r++) {
          if (!self.data[row - 1 + r]) self.data[row - 1 + r] = [];
          for (let c = 0; c < numCols; c++) {
            self.data[row - 1 + r][col - 1 + c] = vals[r][c];
          }
        }
      }
    };
  }

  getLastRow() {
    return this.data.length;
  }

  clear() {
    this.data = [];
  }
}

class MockSpreadsheet {
  constructor() {
    this.sheets = {};
  }

  getSheetByName(name) {
    if (!this.sheets[name]) {
      this.sheets[name] = new MockSheet(name);
    }
    return this.sheets[name];
  }
}

const mockSpreadsheet = new MockSpreadsheet();

global.SpreadsheetApp = {
  openById: () => mockSpreadsheet,
  getActiveSpreadsheet: () => mockSpreadsheet
};

global.PropertiesService = {
  getScriptProperties: () => ({
    getProperty: (key) => {
      const props = {
        SPREADSHEET_ID: "mock_sheet_id",
        BOT_TOKEN: "mock_bot_token",
        CLAUDE_API_KEY: "sk-ant-mock",
        CLAUDE_MODEL: "claude-haiku-3-5-20241022",
        ALLOWED_CHAT_IDS: "111,222",
        LEGAL_FOOTER_TEXT: "Lưu ý: Ứng dụng chỉ cung cấp thông tin tham khảo nhắc việc sinh hoạt, không thay thế chẩn đoán y khoa."
      };
      return props[key] || null;
    }
  })
};

global.Utilities = {
  formatDate: (date, tz, fmt) => {
    const d = new Date(date);
    const pad = (n) => String(n).padStart(2, "0");
    if (fmt === "yyyyMMdd") return `${d.getFullYear()}${pad(d.getMonth()+1)}${pad(d.getDate())}`;
    if (fmt === "yyyy-MM-dd") return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
    return d.toISOString();
  },
  computeDigest: () => [],
  base64Encode: (s) => Buffer.from(s).toString("base64")
};

global.console = { ...console };

module.exports = { mockSpreadsheet, MockSheet };
