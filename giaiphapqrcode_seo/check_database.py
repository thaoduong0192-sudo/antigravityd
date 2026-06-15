# -*- coding: utf-8 -*-
import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')

if not os.path.exists('database.json'):
    print('MISSING: database.json')
else:
    size = os.path.getsize('database.json')
    with open('database.json', encoding='utf-8') as f:
        db = json.load(f)
    kws  = db.get('keywords', [])
    arts = db.get('articles', [])
    available = [k for k in kws if k.get('published_count', 0) < 10]
    exhausted  = [k for k in kws if k.get('published_count', 0) >= 10]
    print(f'database.json: {size:,} bytes')
    print(f'Total keywords: {len(kws)}')
    print(f'Total articles: {len(arts)}')
    print(f'Keywords con bai (< 10): {len(available)}')
    print(f'Keywords da xong (>= 10): {len(exhausted)}')
    if available:
        k = available[0]
        kw = k.get("keyword", "")
        cnt = k.get("published_count", 0)
        print(f'Kw hien tai: {kw[:60]} ({cnt}/10)')
    else:
        print('')
        print('!!! TAT CA KW DA HET -> DAY LA NGUYEN NHAN KHONG DANG BAI !!!')
        print('   -> Can reset published_count hoac them KW moi')
