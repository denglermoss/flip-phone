import re

with open(r'C:\Users\dengle\Documents\personal_projects\phone\pcb\phone\lib\easyeda2kicad.kicad_sym', 'r', encoding='utf-8') as f:
    content = f.read()

syms = re.findall(r'\(symbol "([^"]+)"', content)
top = [s for s in syms if '_0_1' not in s]

for s in top:
    idx = content.find('(symbol "' + s + '"')
    chunk = content[idx:idx+8000]
    m = re.search(r'"Description"\s*\n\s*"([^"]*)"', chunk)
    desc_val = m.group(1) if m else 'NONE'
    m2 = re.search(r'"ki_description"\s*\n\s*"([^"]*)"', chunk)
    ki_desc = m2.group(1) if m2 else 'NONE'
    print(f'{s}: Description="{desc_val}" ki_description="{ki_desc}"'.encode('ascii', 'replace').decode('ascii'))
