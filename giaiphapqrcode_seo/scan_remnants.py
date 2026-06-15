# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os

TERMS = [
    'thu cung', 'cho meo', 'helloconsen', 'HelloConsen', 'eco-pets', 'ecopets',
    'placedog', 'real animal', 'veterinary', 'cham soc', 'Cham soc',
    'placedog.net', 'animal', 'pollinations',
    'ch\u0103m s\u00f3c', 'th\u00fa c\u01b0ng', 'ch\u00f3', 'm\u00e8o', 'th\u00fa y',
    'eco_pets', 'danh-muc/eco-pets'
]

found = []
for root, dirs, files in os.walk('.'):
    # Skip virtual environments and cache
    dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', 'env']]
    for fn in files:
        if fn.endswith(('.py', '.bat', '.vbs', '.txt', '.env')):
            path = os.path.join(root, fn)
            try:
                with open(path, encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, 1):
                        for t in TERMS:
                            if t.lower() in line.lower():
                                found.append((path, i, t, line.rstrip()[:120]))
                                break  # one match per line is enough
            except:
                pass

# Group by file
from collections import defaultdict
by_file = defaultdict(list)
for path, lineno, term, line in found:
    by_file[path].append((lineno, term, line))

for path, matches in sorted(by_file.items()):
    print(f'\n=== {path} ===')
    for lineno, term, line in matches:
        print(f'  L{lineno} [{term}]: {line}')

print(f'\n=== TOTAL: {len(found)} matches in {len(by_file)} files ===')
