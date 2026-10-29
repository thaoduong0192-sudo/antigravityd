"""docx_tc.py - Bộ công cụ Track Changes AN TOÀN cho bản thảo hồi ký.

MỤC ĐÍCH: thay cho việc mỗi lần tự viết script XML mới (nguyên nhân gây mất
track change, mất namespace, file Word phải "khôi phục"/mở sang file mới).

Cam kết kỹ thuật của module:
  1. Chỉ sửa trên văn bản CHƯA bị track (run trực tiếp trong đoạn). Không bao giờ
     chạm vào w:ins / w:del đã có của người khác (Huong Thao, các vòng trước).
  2. Mọi thay đổi đều là w:del + w:ins có author = AI_AUTHOR -> người duyệt Accept/Reject.
  3. Không bao giờ xóa thẳng chữ trong bản gốc (chỉ bọc w:del).
  4. Lưu bằng lxml, giữ nguyên toàn bộ namespace gốc + mọi part khác trong zip.
  5. Trước khi lưu: kiểm tra toàn bộ revision cũ còn nguyên (đếm theo author/loại/nội dung).
     Thiếu 1 cái -> từ chối lưu.
  6. Không ghi đè file đầu vào nếu chưa tạo bản sao lưu có dấu thời gian.

Cách dùng tối thiểu:
    from docx_tc import Doc
    d = Doc(r'...\\V7_CHUAN_HOA.docx')
    s, e = d.manuscript_range(6)              # vùng văn bản gốc của Chương 6
    i = d.find_paragraph('cụm chữ duy nhất', s, e)
    d.replace(i, 'cụm cũ', 'cụm mới')           # sửa chữ (không tô xanh)
    d.replace(i, 'cụm cũ 2', 'câu diễn giải', green=True)   # BTV viết thêm -> xanh lá
    d.delete_text(i, 'đoạn lặp ý cần bỏ')
    d.insert_paragraph_after(i, 'Câu nối ý ...', green=True)
    d.save(r'...\\OUTPUT.docx')                   # tự kiểm tra revision cũ
    verify_word(r'...\\OUTPUT.docx')              # mở thử bằng Microsoft Word
"""
import copy
import datetime
import os
import shutil
import zipfile
from collections import Counter

from lxml import etree

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W = '{%s}' % W_NS
NS = {'w': W_NS}
XML_SPACE = '{http://www.w3.org/XML/1998/namespace}space'

# Tên tác giả revision của biên tập viên: theo yêu cầu dứt khoát của tác giả, dùng 'Huong Thao', không để chữ AI
AI_AUTHOR = 'Huong Thao'
PROTECTED_AUTHORS = ()

# Thứ tự phần tử trong w:rPr theo schema OOXML (sai thứ tự -> Word báo lỗi nội dung)
RPR_ORDER = ['rStyle', 'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps', 'strike',
             'dstrike', 'outline', 'shadow', 'emboss', 'imprint', 'noProof', 'snapToGrid',
             'vanish', 'webHidden', 'color', 'spacing', 'w', 'kern', 'position', 'sz', 'szCs',
             'highlight', 'u', 'effect', 'bdr', 'shd', 'fitText', 'vertAlign', 'rtl', 'cs',
             'em', 'lang', 'eastAsianLayout', 'specVanish', 'oMath', 'rPrChange']


class EditError(Exception):
    pass


# ---------------------------------------------------------------- tiện ích
def final_text(p):
    """Văn bản sau khi Accept All (bỏ phần bị xóa)."""
    return ''.join(p.xpath('.//w:t[not(ancestor::w:del)]/text()', namespaces=NS))


def original_text(p):
    """Văn bản trước mọi chỉnh sửa (Reject All): bỏ phần chèn, giữ phần bị xóa."""
    out = []
    for el in p.xpath('.//w:t[not(ancestor::w:ins)] | .//w:delText[not(ancestor::w:ins)]',
                      namespaces=NS):
        out.append(el.text or '')
    return ''.join(out)


def revision_snapshot(root):
    c = Counter()
    for el in root.xpath('//w:ins | //w:del', namespaces=NS):
        txt = ''.join(el.xpath('.//w:t/text() | .//w:delText/text()', namespaces=NS))
        c[(el.get(W + 'author'), etree.QName(el).localname, txt)] += 1
    return c


def set_highlight(rpr, color):
    """Đặt highlight đúng vị trí schema. color=None để gỡ highlight."""
    old = rpr.find(W + 'highlight')
    if old is not None:
        rpr.remove(old)
    if color is None:
        return
    hl = etree.Element(W + 'highlight')
    hl.set(W + 'val', color)
    idx = RPR_ORDER.index('highlight')
    for i, child in enumerate(rpr):
        name = etree.QName(child).localname
        if name in RPR_ORDER and RPR_ORDER.index(name) > idx:
            rpr.insert(i, hl)
            return
    rpr.append(hl)


def _is_text_run(el):
    if el.tag != W + 'r':
        return False
    ts = el.findall(W + 't')
    return len(ts) == 1 and all(c.tag in (W + 'rPr', W + 't') for c in el)


def _segments(p):
    for pe in p.findall(W + 'proofErr'):
        p.remove(pe)
    segs, cur = [], []
    for c in p:
        if _is_text_run(c):
            cur.append(c)
        else:
            if cur:
                segs.append(cur)
            cur = []
    if cur:
        segs.append(cur)
    return segs


def _split_run(r, k):
    t = r.find(W + 't')
    s = t.text or ''
    if k <= 0 or k >= len(s):
        return r, None
    r2 = copy.deepcopy(r)
    t.text = s[:k]
    t.set(XML_SPACE, 'preserve')
    t2 = r2.find(W + 't')
    t2.text = s[k:]
    t2.set(XML_SPACE, 'preserve')
    r.addnext(r2)
    return r, r2


def _isolate(seg, a, b):
    pos, out = 0, []
    for r in list(seg):
        s = r.find(W + 't').text or ''
        rs, re_ = pos, pos + len(s)
        pos = re_
        if re_ <= a or rs >= b:
            continue
        cur = r
        if rs < a:
            _, cur = _split_run(cur, a - rs)
            rs = a
        if re_ > b:
            _split_run(cur, b - rs)
        out.append(cur)
    return out


# ---------------------------------------------------------------- lớp chính
class Doc:
    def __init__(self, path, author=AI_AUTHOR):
        if author in PROTECTED_AUTHORS:
            raise EditError(f'Không được dùng tên "{author}" cho revision.')
        self.path = path
        self.author = author
        with zipfile.ZipFile(path) as z:
            self.root = etree.fromstring(z.read('word/document.xml'))
        self.body = self.root.find(W + 'body')
        self.date = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        self._next_id = self._max_id() + 1
        self.baseline = revision_snapshot(self.root)
        self.log = []  # nhật ký thay đổi -> dùng cho báo cáo
        self.created_ins = []  # danh sách các w:ins vừa được tạo trong phiên này

    # ---- định vị
    def _max_id(self):
        m = 0
        for el in self.root.iter():
            v = el.get(W + 'id')
            if v and v.lstrip('-').isdigit():
                m = max(m, int(v))
        return m

    def _attrs(self, el):
        el.set(W + 'id', str(self._next_id))
        self._next_id += 1
        el.set(W + 'author', self.author)
        el.set(W + 'date', self.date)
        return el

    def paragraphs(self):
        return self.root.xpath('//w:body//w:p', namespaces=NS)

    def chapter_range(self, n):
        """(start, end) chỉ số đoạn của 'CHƯƠNG n:' tới trước chương kế tiếp."""
        ps = self.paragraphs()
        start = end = None
        for i, p in enumerate(ps):
            t = final_text(p).strip().upper()
            if start is None and (t.startswith(f'CHƯƠNG {n}:') or t.startswith(f'CHƯƠNG {n} ')):
                start = i
            elif start is not None and (t.startswith('CHƯƠNG ') or t.startswith('LỜI KẾT')):
                end = i
                break
        if start is None:
            raise EditError(f'Không thấy tiêu đề CHƯƠNG {n}')
        return start, end if end is not None else len(ps)

    def manuscript_range(self, n):
        """Vùng VĂN BẢN BẢN THẢO của chương (bỏ qua khối 'ĐỀ XUẤT BIÊN TẬP')."""
        s, e = self.chapter_range(n)
        ps = self.paragraphs()
        for i in range(s, e):
            t = final_text(ps[i]).upper()
            if 'TOÀN VĂN BẢN THẢO GỐC' in t or 'BẢN THẢO BIÊN TẬP TRACK CHANGES' in t:
                return i + 1, e
        raise EditError(f'Chương {n}: không thấy dòng mở đầu bản thảo ("TOÀN VĂN BẢN THẢO GỐC" '
                        f'hoặc "BẢN THẢO BIÊN TẬP TRACK CHANGES") -> kiểm tra thủ công.')

    def find_paragraph(self, snippet, start=0, end=None):
        ps = self.paragraphs()
        end = len(ps) if end is None else end
        hits = [i for i in range(start, end) if snippet in final_text(ps[i])]
        if len(hits) != 1:
            raise EditError(f'Tìm "{snippet[:50]}" thấy {len(hits)} đoạn (cần đúng 1).')
        return hits[0]

    # ---- thao tác sửa
    def _locate(self, p, old):
        if final_text(p).count(old) != 1:
            raise EditError(f'"{old[:50]}" xuất hiện {final_text(p).count(old)} lần trong đoạn (cần 1).')
        for seg in _segments(p):
            text = ''.join(r.find(W + 't').text or '' for r in seg)
            k = text.find(old)
            if k >= 0:
                return _isolate(seg, k, k + len(old))
        raise EditError(f'"{old[:50]}" nằm trong phần đã có track change của người khác '
                        f'hoặc vắt qua định dạng đặc biệt -> KHÔNG sửa đè. Chọn cụm khác.')

    def _make_del(self, runs):
        d = self._attrs(etree.Element(W + 'del'))
        runs[0].addprevious(d)
        for r in runs:
            r.find(W + 't').tag = W + 'delText'
            d.append(r)
        return d

    def _make_ins(self, text, rpr_src, green):
        ins = self._attrs(etree.Element(W + 'ins'))
        r = etree.SubElement(ins, W + 'r')
        rpr = copy.deepcopy(rpr_src) if rpr_src is not None else etree.Element(W + 'rPr')
        for bad in rpr.findall(W + 'rPrChange'):
            rpr.remove(bad)
        if green:
            set_highlight(rpr, 'green')
        r.append(rpr)
        t = etree.SubElement(r, W + 't')
        t.text = text
        t.set(XML_SPACE, 'preserve')
        self.created_ins.append(ins)
        return ins

    def replace(self, idx, old, new, green=False, reason=''):
        p = self.paragraphs()[idx]
        runs = self._locate(p, old)
        rpr = runs[0].find(W + 'rPr')
        d = self._make_del(runs)
        if new:
            d.addnext(self._make_ins(new, rpr, green))
        self.log.append(('SỬA' if new else 'XÓA', idx, old, new, green, reason))

    def delete_text(self, idx, old, reason=''):
        self.replace(idx, old, '', reason=reason)

    def insert_text(self, idx, anchor, new, before=False, green=False, reason=''):
        """Chèn chữ ngay sau (hoặc trước) cụm 'anchor' (anchor giữ nguyên)."""
        p = self.paragraphs()[idx]
        runs = self._locate(p, anchor)
        rpr = runs[0].find(W + 'rPr')
        ins = self._make_ins(new, rpr, green)
        (runs[0].addprevious if before else runs[-1].addnext)(ins)
        self.log.append(('CHÈN', idx, anchor, new, green, reason))

    def insert_paragraph_after(self, idx, text, green=False, reason=''):
        p = self.paragraphs()[idx]
        newp = etree.Element(W + 'p')
        ppr = p.find(W + 'pPr')
        ppr = copy.deepcopy(ppr) if ppr is not None else etree.Element(W + 'pPr')
        for bad in ppr.findall(W + 'sectPr') + ppr.findall(W + 'pPrChange'):
            ppr.remove(bad)
        prpr = ppr.find(W + 'rPr')
        if prpr is None:
            prpr = etree.SubElement(ppr, W + 'rPr')
        for old in prpr.findall(W + 'ins') + prpr.findall(W + 'del'):
            prpr.remove(old)
        prpr.insert(0, self._attrs(etree.Element(W + 'ins')))  # dấu ¶ được chèn
        newp.append(ppr)
        first = p.find('.//' + W + 'r')
        rpr = first.find(W + 'rPr') if first is not None else None
        newp.append(self._make_ins(text, rpr, green))
        p.addnext(newp)
        self.log.append(('THÊM ĐOẠN', idx, '', text, green, reason))
        return idx + 1

    def delete_paragraph(self, idx, reason=''):
        p = self.paragraphs()[idx]
        if p.xpath('.//w:ins | .//w:del', namespaces=NS):
            raise EditError('Đoạn đã có track change của người khác -> không xóa cả đoạn. '
                            'Dùng delete_text cho phần chưa track.')
        old = final_text(p)
        for seg in _segments(p):
            self._make_del(seg)
        ppr = p.find(W + 'pPr')
        if ppr is None:
            ppr = etree.Element(W + 'pPr')
            p.insert(0, ppr)
        prpr = ppr.find(W + 'rPr')
        if prpr is None:
            prpr = etree.SubElement(ppr, W + 'rPr')
        prpr.insert(0, self._attrs(etree.Element(W + 'del')))
        self.log.append(('XÓA ĐOẠN', idx, old, '', False, reason))

    def set_green(self, ins_el):
        for r in ins_el.findall('.//' + W + 'r'):
            rpr = r.find(W + 'rPr')
            if rpr is None:
                rpr = etree.Element(W + 'rPr')
                r.insert(0, rpr)
            set_highlight(rpr, 'green')

    # ---- lưu
    def check_integrity(self):
        now = revision_snapshot(self.root)
        missing = self.baseline - now
        if missing:
            lines = '\n'.join(f'  {k[0]} | {k[1]} | {k[2][:60]}' for k in list(missing)[:20])
            raise EditError(f'MẤT {sum(missing.values())} track change cũ -> HỦY LƯU:\n{lines}')
        return True

    def save(self, out_path):
        self.check_integrity()
        src = self.path
        if os.path.abspath(out_path) == os.path.abspath(src):
            stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            bak = src.replace('.docx', f'_BACKUP_{stamp}.docx')
            shutil.copy2(src, bak)
            print(f'Đã sao lưu bản trước khi ghi đè: {bak}')
        lock = os.path.join(os.path.dirname(out_path), '~$' + os.path.basename(out_path)[2:])
        if os.path.exists(lock):
            raise EditError('File đích đang mở trong Word. Yêu cầu người dùng đóng file trước.')
        data = etree.tostring(self.root, xml_declaration=True, encoding='UTF-8', standalone=True)
        tmp = out_path + '.tmp'
        with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                zout.writestr(item, data if item.filename == 'word/document.xml'
                              else zin.read(item.filename))
        os.replace(tmp, out_path)
        print(f'Đã lưu {out_path} | revision AI mới: {len(self.log)} | revision cũ giữ nguyên: '
              f'{sum(self.baseline.values())}')
        return out_path


def verify_word(path):
    """Mở bằng Microsoft Word thật. Trả về (số đoạn, số revision). Lỗi -> raise."""
    import win32com.client
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        doc = word.Documents.Open(os.path.abspath(path), ReadOnly=True, AddToRecentFiles=False)
        res = (doc.Paragraphs.Count, doc.Revisions.Count)
        doc.Close(False)
        return res
    finally:
        word.Quit()


def revision_report(path):
    """Đếm revision theo tác giả x chương - dùng trước và sau mỗi lần sửa."""
    d = Doc(path)
    ps = d.paragraphs()
    chap, out = 'MỞ ĐẦU', Counter()
    for p in ps:
        t = final_text(p).strip().upper()
        if t.startswith('CHƯƠNG ') or t.startswith('LỜI MỞ ĐẦU') or t.startswith('LỜI KẾT'):
            chap = t.split(':')[0][:12]
        for r in p.xpath('.//w:ins | .//w:del', namespaces=NS):
            out[(r.get(W + 'author'), chap)] += 1
    return out
