import re
with open('keypad.kicad_sch', 'r', encoding='utf-8') as f:
    c = f.read()

p = r'\(symbol\s+\(lib_id "power:\+3\.3V"\)\s+\(at ([\d.]+) ([\d.]+) (\d+)\)'
print('+3.3V symbols:')
for x, y, r in re.findall(p, c):
    print(f'  at ({x}, {y}) rot={r}')

print()
p2 = r'\(symbol\s+\(lib_id "power:GND"\)\s+\(at ([\d.]+) ([\d.]+) (\d+)\)'
print('GND symbols (bottom):')
for x, y, r in re.findall(p2, c):
    if float(y) > 160:
        print(f'  at ({x}, {y}) rot={r}')
