"""lint.py - Đo chất lượng biên tập bằng con số (chống sửa "hời hợt").

    python lint.py "<docx>" <số chương> [--before]

Báo cáo trên văn bản cuối (Accept All) của vùng bản thảo chương:
  - tỷ lệ cô đọng (độ dài cuối / độ dài gốc)
  - câu dài > 35 chữ còn sót
  - danh xưng viết hoa sai giữa câu (Ba, Má, Chị, Bà Cố, Bà Nội, Cô, Dì...)
  - cụm "rào đón" của người kể còn sót (Tôi không biết..., Trong trí tưởng tượng...)
  - từ lặp dày trong cùng đoạn
  - ghi chú nội bộ còn sót trong thân bài ([Đoạn tư liệu...], [Chi tiết biên tập viên...])
"""
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, __file__.rsplit('\\', 1)[0])
from docx_tc import Doc, final_text, original_text  # noqa: E402

KIN = r'(Ba|Má|Mẹ|Cha|Chị|Anh|Em|Bà Cố|Bà Nội|Bà Ngoại|Ông Nội|Ông Ngoại|Cô|Dì|Cậu|Chú|Bác)'
META = ['tôi không biết', 'trong trí tưởng tượng', 'tôi không muốn', 'tôi chỉ muốn kể',
        'tôi không có mặt', 'tôi sinh sau', 'có lẽ', 'tôi nghĩ rằng', 'tôi tin rằng',
        'nhìn lại từ hôm nay', 'khi nhìn lại']
NOTE = re.compile(r'\[(Đoạn tư liệu|Chi tiết biên tập|Ghi chú|Đoạn mở đầu chuyển tiếp)', re.I)
STOP = set('và của là có không những một các được cho với trong đã người này đó khi thì mà '
           'lại cũng như rằng để từ ra vào đến tôi chị em ấy nhưng còn rất'.split())


def run(path, n):
    d = Doc(path)
    s, e = d.manuscript_range(n)
    ps = d.paragraphs()
    # dừng trước khối chú thích cuối chương
    for i in range(s, e):
        if final_text(ps[i]).upper().startswith('CHÚ THÍCH DÀNH CHO'):
            e = i
            break
    fin = [final_text(ps[i]) for i in range(s, e)]
    org = [original_text(ps[i]) for i in range(s, e)]
    lf, lo = sum(len(x.split()) for x in fin), sum(len(x.split()) for x in org)
    print(f'CHƯƠNG {n}: gốc {lo} chữ -> cuối {lf} chữ | còn {lf / max(1, lo):.0%}')
    long_s, caps, metas, notes, reps = [], [], [], [], []
    for k, t in enumerate(fin):
        i = s + k
        for sent in re.split(r'(?<=[\.\!\?…])\s+', t):
            if len(sent.split()) > 35:
                long_s.append((i, len(sent.split()), sent[:90]))
        for m in re.finditer(r'(?<=[a-zà-ỹ,]\s)' + KIN + r'\b', t):
            caps.append((i, m.group(0), t[max(0, m.start() - 25):m.end() + 15]))
        low = t.lower()
        for mm in META:
            if mm in low:
                metas.append((i, mm))
        if NOTE.search(t):
            notes.append((i, t[:80]))
        words = [w for w in re.findall(r'\w+', low) if w not in STOP and len(w) > 1]
        for w, c in Counter(words).items():
            if c >= 4:
                reps.append((i, w, c))
    sec = lambda title, rows: print(f'  {title}: {len(rows)}' + ''.join(f'\n     P{r[0]} {r[1:]}' for r in rows[:8]))
    sec('Câu > 35 chữ', long_s)
    sec('Danh xưng viết hoa giữa câu', caps)
    sec('Cụm rào đón người kể', metas)
    sec('Ghi chú nội bộ trong thân bài', notes)
    sec('Từ lặp >= 4 lần/đoạn', reps)


if __name__ == '__main__':
    run(sys.argv[1], int(sys.argv[2]))
