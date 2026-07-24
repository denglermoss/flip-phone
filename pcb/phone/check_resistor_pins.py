"""Check resistor pin positions in keypad schematic."""
import re

with open('keypad.kicad_sch', 'r', encoding='utf-8') as f:
    c = f.read()

# Find RC0603 resistor symbol pin positions
m = re.search(r'\(symbol "passives:RC0603JR-0710KL"', c)
if m:
    start = m.start()
    depth = 0
    i = start
    while i < len(c):
        if c[i] == '(':
            depth += 1
        elif c[i] == ')':
            depth -= 1
            if depth == 0:
                break
        i += 1
    block = c[start:i+1]
    # Find pins
    for pm in re.finditer(r'\(pin\s+\w+\s+\w+\s+\(at\s+([\d.-]+)\s+([\d.-]+)\s+(\d+)\)\s+\(length\s+([\d.]+)\)', block):
        print(f'Pin at ({pm.group(1)}, {pm.group(2)}) rot={pm.group(3)} len={pm.group(4)}')
    # Find rectangle
    for rm in re.finditer(r'\(rectangle\s+\(start\s+([\d.-]+)\s+([\d.-]+)\)\s+\(end\s+([\d.-]+)\s+([\d.-]+)\)', block):
        print(f'Rect: ({rm.group(1)}, {rm.group(2)}) to ({rm.group(3)}, {rm.group(4)})')

# Now find all wires and print them
print("\n=== All Wires ===")
for m in re.finditer(r'\(wire \(pts \(xy ([\d.]+) ([\d.]+)\) \(xy ([\d.]+) ([\d.]+)\)\)', c):
    x1, y1, x2, y2 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
    print(f'  ({x1}, {y1}) -> ({x2}, {y2})')
