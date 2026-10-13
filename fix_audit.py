# Fix audit.py with debug prints
with open('studio/cloud/audit.py', 'r') as f:
    content = f.read()

old = "need(source.read_text(encoding='utf-8') in html_text, 'editable HTML/SVG mismatch')"
new = """        print(f'DEBUG: source={str(source)}, editable={str(editable)}')
        print(f'DEBUG: source_text in html_text = {source.read_text(encoding="utf-8") in html_text}')
        print(f'DEBUG: source len={len(source.read_text(encoding="utf-8"))}, html len={len(html_text)}')
        need(source.read_text(encoding="utf-8") in html_text, 'editable HTML/SVG mismatch')"""

if old in content:
    content = content.replace(old, new)
    with open('studio/cloud/audit.py', 'w') as f:
        f.write(content)
    print('Modified successfully')
else:
    print('Could not find the line to replace')