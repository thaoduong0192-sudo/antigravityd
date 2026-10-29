/**
 * DOM Coordinate & ComputedStyle Audit Script for AI-Native Design-to-Code Verification
 * Can be injected via Chrome DevTools MCP (`chrome_evaluate_js`) or executed via Playwright.
 *
 * Extracts normalized bounding boxes (x, y, width, height), text content, and key visual tokens
 * (color, backgroundColor, border, borderRadius, fontSize, fontWeight) to diff original design vs implementation.
 */

function extractDOMLayoutSnapshot(rootSelector = 'body') {
  const root = document.querySelector(rootSelector) || document.body;
  const elements = Array.from(root.querySelectorAll('*'));
  const records = [];

  for (const el of elements) {
    const rect = el.getBoundingClientRect();
    if (rect.width === 0 && rect.height === 0) continue;

    const style = window.getComputedStyle(el);
    if (style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity) === 0) {
      continue;
    }

    // Direct text content only (avoid duplicating parent containers' full text)
    const directText = Array.from(el.childNodes)
      .filter((n) => n.nodeType === Node.TEXT_NODE)
      .map((n) => n.textContent.trim())
      .filter(Boolean)
      .join(' ');

    const tag = el.tagName.toLowerCase();
    const isInteractive = ['button', 'a', 'input', 'select', 'textarea'].includes(tag) || el.getAttribute('role') === 'button';

    if (!directText && !isInteractive && style.borderTopWidth === '0px' && style.backgroundColor === 'rgba(0, 0, 0, 0)') {
      continue;
    }

    records.push({
      tag,
      id: el.id || undefined,
      text: directText ? directText.slice(0, 80) : undefined,
      rect: {
        x: Math.round(rect.x),
        y: Math.round(rect.y),
        w: Math.round(rect.width),
        h: Math.round(rect.height),
      },
      styles: {
        color: style.color,
        bg: style.backgroundColor,
        border: `${style.borderTopWidth} ${style.borderTopStyle} ${style.borderTopColor}`,
        radius: style.borderRadius,
        font: `${style.fontWeight} ${style.fontSize}/${style.lineHeight} ${style.fontFamily.split(',')[0].replace(/['"]/g, '').trim()}`,
      },
    });
  }

  // Sort deterministically by vertical position, then horizontal position, then tag/text
  records.sort((a, b) => {
    if (Math.abs(a.rect.y - b.rect.y) > 4) return a.rect.y - b.rect.y;
    if (Math.abs(a.rect.x - b.rect.x) > 4) return a.rect.x - b.rect.x;
    return (a.text || a.tag).localeCompare(b.text || b.tag);
  });

  return {
    viewport: { width: window.innerWidth, height: window.innerHeight },
    totalVisibleNodes: records.length,
    horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth,
    records,
  };
}

function compareDOMSnapshots(refSnapshot, implSnapshot, tolerancePx = 4) {
  const issues = [];

  if (implSnapshot.horizontalOverflow) {
    issues.push({
      type: 'HORIZONTAL_OVERFLOW',
      message: `Horizontal scroll detected at viewport ${implSnapshot.viewport.width}x${implSnapshot.viewport.height}`,
    });
  }

  const refByText = new Map();
  for (const item of refSnapshot.records) {
    if (item.text) {
      const key = `${item.tag}::${item.text}`;
      if (!refByText.has(key)) refByText.set(key, item);
    }
  }

  for (const implItem of implSnapshot.records) {
    if (!implItem.text) continue;
    const key = `${implItem.tag}::${implItem.text}`;
    const refItem = refByText.get(key);
    if (!refItem) continue;

    const dx = Math.abs(refItem.rect.x - implItem.rect.x);
    const dy = Math.abs(refItem.rect.y - implItem.rect.y);
    const dw = Math.abs(refItem.rect.w - implItem.rect.w);
    const dh = Math.abs(refItem.rect.h - implItem.rect.h);

    if (dx > tolerancePx || dy > tolerancePx || dw > tolerancePx || dh > tolerancePx) {
      issues.push({
        type: 'BOUNDING_RECT_MISMATCH',
        key,
        reference: refItem.rect,
        implementation: implItem.rect,
        delta: { dx, dy, dw, dh },
      });
    }

    if (
      refItem.styles.color !== implItem.styles.color ||
      refItem.styles.bg !== implItem.styles.bg ||
      refItem.styles.border !== implItem.styles.border
    ) {
      issues.push({
        type: 'STYLE_TOKEN_MISMATCH',
        key,
        reference: refItem.styles,
        implementation: implItem.styles,
      });
    }
  }

  return {
    viewport: implSnapshot.viewport,
    matchedCount: refByText.size,
    issueCount: issues.length,
    issues,
  };
}

if (typeof window !== 'undefined') {
  window.__extractDOMLayoutSnapshot = extractDOMLayoutSnapshot;
  window.__compareDOMSnapshots = compareDOMSnapshots;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { extractDOMLayoutSnapshot, compareDOMSnapshots };
}
