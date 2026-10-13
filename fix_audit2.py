with open('studio/cloud/audit.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'need(source.read_text(encoding=' in line and 'editable HTML/SVG mismatch' in line:
        # Add debug prints before this line with correct indentation (8 spaces)
        indent = ' ' * 8
        new_lines.append(f'        print(f"DEBUG: source={str(source)}, editable={str(editable)}")\n')
        new_lines.append(f'        print(f"DEBUG: source_text in html_text = {source.read_text(encoding="utf-8") in html_text}")\n')
        new_lines.append(f'        print(f"DEBUG: source len={len(source.read_text(encoding="utf-8"))}, html len={len(html_text)}")\n')
        new_lines.append(line)
    else:
        new_lines.append(line)

with open('studio/cloud/audit.py', 'w') as f:
    f.writelines(new_lines)
print('Modified')