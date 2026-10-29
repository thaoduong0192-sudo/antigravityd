#!/usr/bin/env node
/**
 * Antigravity Deterministic PreToolUse Guard (Claude Code Hookify Pattern)
 * Protects workspace against destructive shell commands and accidental secret/preservation violations.
 */

let rawInput = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => {
  rawInput += chunk;
});

process.stdin.on('end', () => {
  try {
    const payload = rawInput ? JSON.parse(rawInput) : {};
    const toolCall = payload.toolCall || {};
    const toolName = String(toolCall.name || '').toLowerCase();
    const args = toolCall.args || {};

    // 1. Guard run_command against destructive operations
    if (toolName === 'run_command') {
      const cmd = String(args.CommandLine || '');

      // Hard-deny catastrophic workspace-wiping commands
      const denyPatterns = [
        /\bgit\s+reset\s+--hard\b/i,
        /\bgit\s+clean\s+-[a-z]*f/i,
        /\bFormat-Volume\b/i,
        /\bdel\s+\/[fqs]\s+[a-z]:\\$/i,
        /\brm\s+-rf\s+(\/|d:\\antigravity\/?$|c:\\)/i,
      ];

      for (const pattern of denyPatterns) {
        if (pattern.test(cmd)) {
          process.stdout.write(
            JSON.stringify({
              decision: 'force_ask',
              reason: `[Hook Safety Guard] Lệnh chứa thao tác có nguy cơ xóa dữ liệu hàng loạt (${pattern}). Yêu cầu người dùng xác nhận tường minh trước khi chạy.`,
            })
          );
          return;
        }
      }
    }

    // 2. Guard write_file / edit_file on sensitive credential files
    if (toolName === 'write_file' || toolName === 'edit_file') {
      const targetPath = String(args.Path || '').replace(/\\/g, '/');
      const baseName = targetPath.split('/').pop() || '';

      const isSensitiveSecretFile =
        /^(\.env(\.(local|production|development|staging))?|credentials\.json|.*\.(pem|key))$/i.test(
          baseName
        ) && !/\.example$/i.test(baseName);

      if (isSensitiveSecretFile) {
        process.stdout.write(
          JSON.stringify({
            decision: 'force_ask',
            reason: `[Hook Secret Guard] Đang chuẩn bị ghi vào file nhạy cảm (${baseName}). Vui lòng xác nhận để đảm bảo không làm lộ hoặc ghi đè khóa bí mật.`,
          })
        );
        return;
      }
    }

    process.stdout.write(JSON.stringify({ decision: 'allow' }));
  } catch (_err) {
    // Fail-open to avoid blocking normal execution on malformed hook stdin
    process.stdout.write(JSON.stringify({ decision: 'allow' }));
  }
});
