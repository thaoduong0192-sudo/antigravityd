#!/usr/bin/env node
/**
 * Antigravity SessionStart Memory Hook
 * Injects a concise ephemeral reminder pointing to PROJECT_MEMORY.md at session startup.
 */

const fs = require('fs');
const path = require('path');

let rawInput = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => {
  rawInput += chunk;
});

process.stdin.on('end', () => {
  try {
    const memoryPath = path.join(__dirname, '..', 'memory', 'PROJECT_MEMORY.md');
    if (fs.existsSync(memoryPath)) {
      process.stdout.write(
        JSON.stringify({
          injectSteps: [
            {
              ephemeralMessage:
                '[Antigravity Session Memory] Bản đồ kiến trúc & bộ nhớ xuyên phiên của toàn bộ dự án được lưu tại d:/Antigravity/_agent/memory/PROJECT_MEMORY.md. Khi làm việc với dự án có sẵn hoặc phát hiện bài học kỹ thuật mới, hãy tham chiếu và cập nhật file này.',
            },
          ],
        })
      );
      return;
    }
  } catch (_err) {
    // Ignore errors and return empty object
  }
  process.stdout.write(JSON.stringify({}));
});
