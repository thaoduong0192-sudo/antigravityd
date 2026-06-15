import os
import re

new_models = [
    'qwen-max',
    'qwen3-max-preview',
    'qwen3.7-max-preview',
    'qwen3.5-flash',
    'qwen3.6-flash',
    'qwen3-coder-plus',
    'deepseek-v3.2',
    'deepseek-v4-flash',
    'deepseek-v4-pro',
    'qwen3-coder-next',
    'qwen3-max-2026-01-23',
    'qwen3.7-max-2026-05-17',
    'qwen3-next-80b-a3b-thinking',
    'qwen-mt-flash',
    'qwen3.5-55b-a3b',
    'qwen3-30b-a3b',
    'qwen3.6-27b',
    'qwen3.5-27b',
    'qwen3-14b'
]

replacement = 'FREE_MODELS = [\n    ' + ',\n    '.join(f'"{m}"' for m in new_models) + '\n]'

paths = [
    r'D:\Antigravity\helloconsen_seo\qwen_manager.py',
    r'D:\Antigravity\ecopets_seo\qwen_manager.py',
    r'D:\Antigravity\hoiky_seo\qwen_manager.py'
]

for p in paths:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = re.sub(r'FREE_MODELS\s*=\s*\[(.*?)\]', replacement, content, flags=re.DOTALL)
        
        with open(p, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {p}')
    else:
        print(f'Not found: {p}')
