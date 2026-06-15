# -*- coding: utf-8 -*-
import sys, json, re, time, os
sys.stdout.reconfigure(encoding='utf-8')
from qwen_manager import chat_with_qwen

keyword = "phan mem bao hanh QR code"
prompt = (
    f"Ban la chuyen gia SEO. Hay tao 10 goc nhin khac nhau de viet bai ve: {keyword}\n"
    "Chi tra ve JSON array, khong co gi khac:\n"
    '[\"goc nhin 1\", \"goc nhin 2\", ...]'
)

print("Goi Qwen...")
raw = chat_with_qwen(prompt, max_tokens=500, temperature=0.7)
print(f"Raw output: {raw[:400] if raw else 'NONE'}")

if raw:
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match:
        try:
            arr = json.loads(match.group())
            print(f"JSON OK: {len(arr)} items")
            for item in arr[:3]:
                print(f"  - {item}")
        except Exception as e:
            print(f"JSON parse loi: {e}")
            print(f"Raw JSON: {match.group()[:300]}")
    else:
        print("KHONG tim thay JSON array!")
else:
    print("Qwen tra ve None - tat ca model deu loi!")
