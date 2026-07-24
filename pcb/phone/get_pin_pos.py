import re
with open('display.kicad_sch', 'r', encoding='utf-8') as f:
    content = f.read()
m = re.search(r'\(symbol "connectors:0\.5K-HX-14PWB"', content)
sym_start = m.start()
depth = 0
i = sym_start
while i < len(content):
    if content[i] == '(':
        depth += 1
    elif content[i] == ')':
        depth -= 1
        if depth == 0:
            break
    i += 1
block = content[sym_start:i+1]
for pm in re.finditer(r'\(pin\s+\w+\s+line\s+\(at\s+([\d.-]+)\s+([\d.-]+)\s+(\d+)\)\s+\(length\s+([\d.]+)\).*?\(number\s+"(\d+)"', block, re.DOTALL):
    x, y, angle, length, num = pm.groups()
    print(f'Pin {num}: at ({x}, {y}) angle {angle} length {length}')
