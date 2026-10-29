"""provenance.py - Kiểm tra NGUỒN GỐC từng câu, thay cho việc model "tự nhớ" xem đã bịa gì.

Hai lỗi lặp lại nhiều nhất trong lịch sử dự án:
  (A) BỊA / thêm thắt chi tiết không có trong lời kể -> không tô xanh lá -> tác giả phát hiện.
  (B) CẮT XÉN bản gốc âm thầm (xóa không qua track change) -> mất chi tiết (cô bé chạy ra
      cánh đồng khi bà say rượu, làm giấy khai sinh...).

Module này đo bằng máy, không dựa vào trí nhớ:
  classify(sentence)          -> 'GỐC' | 'DIỄN GIẢI' | 'TỰ THÊM'
  audit_ai_insertions(doc)    -> tô XANH LÁ mọi w:ins của AI không phải 'GỐC'; trả báo cáo
  audit_final_text(doc, s, e) -> liệt kê câu trong bản cuối (Accept All) không có nguồn
  silent_cuts(doc, s, e, src) -> câu trong bản gốc .pages KHÔNG còn trong bản thảo (kể cả
                                 dạng gạch track change) = bị xóa lén -> PHẢI khôi phục

Nguồn so sánh: resources/sources/*.txt (chạy build_sources.py để cập nhật).
"""
import glob
import os
import re
import unicodedata

from docx_tc import NS, W, final_text, original_text

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(os.path.dirname(HERE), 'resources', 'sources')


def norm(s):
    s = unicodedata.normalize('NFC', s).lower()
    s = re.sub(r'\[\d+\]', ' ', s)              # bỏ số chú thích [1]
    s = re.sub(r'[^\w\s]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def sentences(text):
    parts = re.split(r'(?<=[\.\!\?…:;])\s+|\n+', text)
    return [p.strip() for p in parts if len(norm(p).split()) >= 4]


def ngrams(words, n):
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


class Sources:
    def __init__(self, files=None):
        files = files or glob.glob(os.path.join(SRC_DIR, '*.txt'))
        if not files:
            raise RuntimeError('Chưa có kho nguồn. Chạy scripts/build_sources.py trước.')
        self.texts = {os.path.basename(f): open(f, encoding='utf-8').read() for f in files}
        allw = norm(' '.join(self.texts.values())).split()
        self.g3 = ngrams(allw, 3)
        self.g2 = ngrams(allw, 2)
        self.flat = ' '.join(allw)

    def coverage(self, sentence):
        w = norm(sentence).split()
        if len(w) < 3:
            return 1.0 if ' '.join(w) in self.flat else 0.0
        g = ngrams(w, 3) if len(w) >= 6 else ngrams(w, 2)
        pool = self.g3 if len(w) >= 6 else self.g2
        return sum(1 for x in g if x in pool) / max(1, len(g))

    def classify(self, sentence):
        c = self.coverage(sentence)
        if c >= 0.6:
            return 'GỐC', c
        if c >= 0.3:
            return 'DIỄN GIẢI', c
        return 'TỰ THÊM', c


def audit_ai_insertions(doc, src, start=0, end=None, apply_green=True):
    """Mọi chữ AI chèn (author = doc.author) mà không phải 'GỐC' -> tô xanh lá."""
    ps = doc.paragraphs()
    end = len(ps) if end is None else end
    rows = []
    for i in range(start, end):
        for ins in ps[i].xpath('.//w:ins', namespaces=NS):
            if getattr(doc, 'created_ins', None):
                if ins not in doc.created_ins:
                    continue
            elif ins.get(W + 'author') != doc.author:
                continue
            txt = ''.join(ins.xpath('.//w:t/text()', namespaces=NS)).strip()
            if len(norm(txt).split()) < 3:
                continue  # sửa chính tả / dấu câu / 1-2 chữ: không cần xanh
            label, c = src.classify(txt)
            if label != 'GỐC' and apply_green:
                doc.set_green(ins)
            rows.append((i, label, round(c, 2), txt))
    return rows


def audit_final_text(src, doc, start, end):
    """Câu trong bản cuối không có trong nguồn (dù ai viết) -> để báo cáo cho tác giả."""
    ps = doc.paragraphs()
    out = []
    for i in range(start, end):
        for s in sentences(final_text(ps[i])):
            label, c = src.classify(s)
            if label == 'TỰ THÊM':
                out.append((i, round(c, 2), s))
    return out


def silent_cuts(doc, start, end, source_text, chapter_marker=None, next_marker=None):
    """Câu của bản gốc không còn trong 'bản gốc nhìn từ docx' (Reject All) của vùng [start,end).
    source_text: văn bản .pages; có thể cắt theo chapter_marker/next_marker (vd 'CHƯƠNG 6')."""
    st = source_text
    if chapter_marker:
        u = st.upper()
        a = u.find(chapter_marker.upper())
        b = u.find(next_marker.upper(), a + 1) if next_marker else -1
        st = st[a:b if b > 0 else None] if a >= 0 else st
    ps = doc.paragraphs()
    pool_words = norm(' '.join(original_text(ps[i]) for i in range(start, end))).split()
    g3 = ngrams(pool_words, 3)
    missing = []
    for s in sentences(st):
        w = norm(s).split()
        g = ngrams(w, 3)
        if not g:
            continue
        cov = sum(1 for x in g if x in g3) / len(g)
        if cov < 0.5:
            missing.append((round(cov, 2), s))
    return missing
