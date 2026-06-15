import glob, re
for f in glob.glob('*.py'):
    if f in ['qwen_manager.py', 'b2b_nutrition_campaign.py', 'apply_silo_seo.py', 'refactor_qwen.py', 'replace_qwen.py']:
        continue
    content = open(f, 'r', encoding='utf-8').read()
    if 'qwen_client, QWEN_MODEL = _detect_working_client' in content:
        content = re.sub(r'_CANDIDATE_ENDPOINTS\s*=\s*\[.*?\]', '', content, flags=re.DOTALL)
        content = re.sub(r'def _detect_working_client.*?return None, None', '', content, flags=re.DOTALL)
        content = re.sub(r'qwen_client, QWEN_MODEL = _detect_working_client\(QWEN_API_KEY\)', 'from qwen_manager import chat_with_qwen', content)
        content = re.sub(r'try:\s*resp = qwen_client\.chat\.completions\.create\(\s*model=QWEN_MODEL,\s*messages=\[\{"role": "user", "content": prompt\}\],\s*max_tokens=\d+,\s*temperature=0\.8\s*\)\s*raw = resp\.choices\[0\]\.message\.content\.strip\(\)\s*except Exception as e:\s*print\(f"  \[-\] L?i Qwen API: \{e\}"\)\s*return None(?:, None, None)?', 'raw = chat_with_qwen(prompt, max_tokens=8000, temperature=0.8)\n    if not raw:\n        return None', content)
        open(f, 'w', encoding='utf-8').write(content)
        print(f'Refactored {f}')
