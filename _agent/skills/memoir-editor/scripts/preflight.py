"""preflight.py - BẮT BUỘC chạy trước khi sửa bất kỳ file nào.

Lỗi từng xảy ra: làm việc trên file cũ trong khi người dùng đã sửa ở file khác/bản chưa lưu
-> mất toàn bộ phần sửa Chương 4-5 của người duyệt (phải cứu từ AutoRecover .asd).

    python preflight.py "<đường dẫn file định sửa>"

In ra: thời gian sửa, Word có đang mở không, các bản docx cùng họ mới hơn, file AutoRecover
mới hơn, và bảng revision theo tác giả x chương. Có cảnh báo -> DỪNG, hỏi người dùng.
"""
import glob
import os
import sys
import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_tc import revision_report  # noqa: E402

target = sys.argv[1]
mt = os.path.getmtime(target)
fmt = lambda t: datetime.datetime.fromtimestamp(t).strftime('%d/%m %H:%M')
warn = []
print(f'File: {target}\nSửa lần cuối: {fmt(mt)} | {os.path.getsize(target):,} bytes')

lock = os.path.join(os.path.dirname(target), '~$' + os.path.basename(target)[2:])
if os.path.exists(lock):
    warn.append('Word ĐANG MỞ file này -> yêu cầu người dùng Lưu + Đóng trước khi sửa.')

stem = os.path.basename(target)[:25]
for folder in {os.path.dirname(target), r'C:\Users\US\Downloads',
               r'C:\Users\US\Downloads\Hoi ky chi Hanh'}:
    for f in glob.glob(os.path.join(folder, '*.docx')):
        if os.path.basename(f).startswith('~$') or os.path.abspath(f) == os.path.abspath(target):
            continue
        if os.path.basename(f)[:25] == stem and os.path.getmtime(f) > mt:
            warn.append(f'Có bản MỚI HƠN: {f} ({fmt(os.path.getmtime(f))})')

ar = os.path.expandvars(r'%APPDATA%\Microsoft\Word')
for f in glob.glob(os.path.join(ar, '**', '*.asd'), recursive=True):
    if os.path.getmtime(f) > mt:
        warn.append(f'Có file AutoRecover mới hơn (phần sửa chưa lưu?): {f} ({fmt(os.path.getmtime(f))})')

print('\nRevision theo tác giả x chương:')
for (author, chap), n in sorted(revision_report(target).items(), key=lambda x: (x[0][1], str(x[0][0]))):
    print(f'  {chap:<12} {author:<28} {n}')

print('\n' + ('CẢNH BÁO - DỪNG LẠI HỎI NGƯỜI DÙNG:\n  ' + '\n  '.join(warn) if warn
              else 'OK - không phát hiện bản mới hơn / file đang mở.'))
