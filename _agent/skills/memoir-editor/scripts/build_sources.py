"""Trích toàn bộ bản gốc .pages + Google Doc chị Thủy bổ sung thành kho văn bản nguồn.
Chạy lại mỗi khi tác giả gửi bản gốc/ghi chú mới.
    python build_sources.py
"""
import os, sys, glob, urllib.request, unicodedata
import pages

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), 'resources', 'sources')
os.makedirs(OUT, exist_ok=True)

MANUSCRIPT_DIR = r'C:\Users\US\Downloads\Hoi ky chi Hanh'
GDOC_IDS = {
    # Google Doc chị Thủy / tác giả Hạnh bổ sung chi tiết + đề xuất của tác giả
    'gdoc_bo_sung_chi_thuy': '15M38L4HifB0DVfFE3k6wqOmHM8-lI6xMm_cQQ27Pnz8',
}

# Bản gốc .pages theo cụm chương (nguồn sự thật duy nhất về lời kể)
PAGES = {
    'goc_loimodau_ch1-5': 'Master Manuscript of Lời mở đầu -Chapter 5.pages',
    'goc_ch6-11': 'Master Manuscript of Chapter 6-7-8-9-10-11.pages',
    'goc_ch12-16': 'Mater Chapter 12-13-14-14-15-16.pages',
    'goc_ch17-22_loiket': 'Final Chuong 17-  18,19,20,21,22, Lời kết.pages',
}

def _nfc(s):
    return unicodedata.normalize('NFC', s)


def find_pages(name):
    # tên file có dấu kiểu NFD (macOS) -> so khớp sau khi chuẩn hóa NFC, phải KHỚP CHÍNH XÁC
    for f in glob.glob(os.path.join(MANUSCRIPT_DIR, '*.pages')):
        if _nfc(os.path.basename(f)) == _nfc(name):
            return f
    return None

for key, name in PAGES.items():
    path = find_pages(name)
    if not path:
        print(f'[THIẾU] Không tìm thấy {name}')
        continue
    doc = pages.Document(path)
    text = '\n'.join(p.text.strip() for p in doc.paragraphs if p.text.strip())
    with open(os.path.join(OUT, key + '.txt'), 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'[OK] {key}: {len(text):,} ký tự  <- {os.path.basename(path)}')

for key, gid in GDOC_IDS.items():
    url = f'https://docs.google.com/document/d/{gid}/export?format=txt'
    try:
        t = urllib.request.urlopen(url, timeout=30).read().decode('utf-8-sig')
        with open(os.path.join(OUT, key + '.txt'), 'w', encoding='utf-8') as f:
            f.write(t)
        print(f'[OK] {key}: {len(t):,} ký tự')
    except Exception as e:
        print(f'[LỖI] {key}: {e} (giữ bản cache cũ nếu có)')
