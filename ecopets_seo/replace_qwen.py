import glob
for f in glob.glob('*.py'):
    content = open(f, 'r', encoding='utf-8').read()
    if '"qwen-plus-latest"' in content:
        open(f, 'w', encoding='utf-8').write(content.replace('"qwen-plus-latest"', '"qwen-plus-latest"'))
