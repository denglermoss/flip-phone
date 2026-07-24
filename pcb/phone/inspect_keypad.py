"""Inspect keypad schematic for labels, resistors, and power symbols."""
import re

with open('keypad.kicad_sch', 'r', encoding='utf-8') as f:
    c = f.read()

# Find all global labels
print("=== Global Labels ===")
for m in re.finditer(r'\(global_label\s+"(\w+)"\s+\(at\s+([\d.]+)\s+([\d.]+)\s+(\d+)\)', c):
    print(f'  {m.group(1)} at ({m.group(2)}, {m.group(3)}) rot={m.group(4)}')

# Find all hierarchical labels
print("\n=== Hierarchical Labels ===")
for m in re.finditer(r'\(hierarchical_label\s+"(\w+)"\s+\(at\s+([\d.]+)\s+([\d.]+)\s+(\d+)\)', c):
    print(f'  {m.group(1)} at ({m.group(2)}, {m.group(3)}) rot={m.group(4)}')

# Find all symbol instances (resistors, power, switches)
print("\n=== Symbol Instances ===")
sym_pattern = r'\(symbol\s+\(lib_id\s+"([^"]+)"\)\s+\(at\s+([\d.]+)\s+([\d.]+)\s+(\d+)\)'
for m in re.finditer(sym_pattern, c):
    lib_id = m.group(1)
    x, y, rot = float(m.group(2)), float(m.group(3)), int(m.group(4))
    # Find the reference designator
    block_start = m.end()
    block_end = c.find('(symbol', block_start)
    if block_end < 0:
        block_end = len(c)
    block = c[block_start:block_end]
    ref_match = re.search(r'\(property\s+"Reference"\s+"(\w+)"', block)
    ref = ref_match.group(1) if ref_match else "?"
    print(f'  {ref}: {lib_id} at ({x}, {y}) rot={rot}')

# Find all junctions
print("\n=== Junctions ===")
for m in re.finditer(r'\(junction\s+\(at\s+([\d.]+)\s+([\d.]+)\)', c):
    print(f'  Junction at ({m.group(1)}, {m.group(2)})')
