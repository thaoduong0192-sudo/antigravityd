#!/usr/bin/env node
/**
 * Antigravity PostToolUse Diagnostic Hook
 * Validates JSON syntax integrity immediately after editing configuration files.
 */

const fs = require('fs');

let rawInput = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => {
  rawInput += chunk;
});

process.stdin.on('end', () => {
  try {
    const payload = rawInput ? JSON.parse(rawInput) : {};
    const toolCall = payload.toolCall || {};
    const args = toolCall.args || {};
    const targetPath = String(args.Path || '');

    if (targetPath && /\.json$/i.test(targetPath) && fs.existsSync(targetPath)) {
      const content = fs.readFileSync(targetPath, 'utf8');
      JSON.parse(content);
    }
  } catch (_err) {
    // PostToolUse contract requires returning an empty JSON object {}
  }
  process.stdout.write(JSON.stringify({}));
});
