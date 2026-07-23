import re
with open('keypad.kicad_sch', 'r', encoding='utf-8') as f:
    c = f.read()

# Find all RC0603 resistor symbols with their positions and references
p = r'\(symbol\s+\(lib_id "passives:RC0603JR-0710KL"\)\s+\(at ([\d.]+)\s+([\d.]+)\s+(\d+)\)'
for m in re.finditer(p, c):
    x, y, rot = m.group(1), m.group(2), m.group(3)
    if float(x) > 140 and int(rot) == 90:
        # Find the reference designator
        block_start = m.start()
        block = c[block_start:block_start+2000]
        ref_match = re.search(r'\(property "Reference" "(R\d+)"', block)
        ref = ref_match.group(1) if ref_match else "?"
        print(f"{ref} at ({x}, {y}) rot={rot}")
        print(f"  Y repr: {repr(y)}")
