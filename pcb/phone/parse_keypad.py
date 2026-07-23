import re

with open('keypad.kicad_sch', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all symbol blocks with SKQGABE010
pattern = r'\(symbol\s+\(lib_id "electromech:SKQGABE010"\)\s+\(at ([\d.]+) ([\d.]+) (\d+)\)'
matches = re.findall(pattern, content)
for i, m in enumerate(matches[:5]):
    print(f'Switch {i+1}: at ({m[0]}, {m[1]}) rot={m[2]}')
print(f'Total SKQGABE010 symbols: {len(matches)}')

# Find all wire blocks
wire_pattern = r'\(wire\s+\(pts\s+\(xy ([\d.]+) ([\d.]+)\)\s+\(xy ([\d.]+) ([\d.]+)\)\)'
wires = re.findall(wire_pattern, content)
print(f'\nTotal wires: {len(wires)}')
for w in wires[:10]:
    print(f'  Wire: ({w[0]}, {w[1]}) -> ({w[2]}, {w[3]})')

# Find all global_label blocks
label_pattern = r'\(global_label "([^"]+)"\s+\(shape (\w+)\)\s+\(at ([\d.]+) ([\d.]+) (\d+)\)'
labels = re.findall(label_pattern, content)
print(f'\nTotal global labels: {len(labels)}')
for l in labels:
    print(f'  Label: {l[0]} shape={l[1]} at ({l[2]}, {l[3]}) rot={l[4]}')

# Find pull-down resistors
res_pattern = r'\(symbol\s+\(lib_id "passives:RC0603JR-0710KL"\)\s+\(at ([\d.]+) ([\d.]+) (\d+)\)'
resistors = re.findall(res_pattern, content)
print(f'\nTotal pull-down resistors: {len(resistors)}')
for r in resistors:
    print(f'  Resistor at ({r[0]}, {r[1]}) rot={r[2]}')

# Find power symbols
pwr_pattern = r'\(symbol\s+\(lib_id "power:([^"]+)"\)\s+\(at ([\d.]+) ([\d.]+) (\d+)\)'
pwrs = re.findall(pwr_pattern, content)
print(f'\nTotal power symbols: {len(pwrs)}')
for p in pwrs[:10]:
    print(f'  Power: {p[0]} at ({p[1]}, {p[2]}) rot={p[3]}')
