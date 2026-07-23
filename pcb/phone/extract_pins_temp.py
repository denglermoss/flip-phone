import re

def extract_pins(filename, sym_name):
    text = open(filename, 'r', encoding='utf-8').read()
    pattern2 = r'\(symbol "' + re.escape(sym_name) + r'_0_1"'
    m2 = re.search(pattern2, text)
    if not m2:
        print(f'Sub-symbol {sym_name}_0_1 not found')
        return []
    start = m2.start()
    depth = 0
    i = start
    in_str = False
    while i < len(text):
        ch = text[i]
        if ch == '"':
            in_str = not in_str
        elif not in_str:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    break
        i += 1
    block = text[start:i+1]
    pins = []
    # Pin format: (pin <type> line\n (at X Y ROT)\n (length L)\n (name "N" ...)\n (number "N" ...)\n)
    for pm in re.finditer(r'\(pin\s+(\w+)\s+line\s*\(at\s+([-\d.]+)\s+([-\d.]+)\s+(\d+)\)\s*\(length\s+([\d.]+)\)\s*\(name\s+"([^"]*)"\s*\(effects.*?\)\s*\)\s*\(number\s+"([^"]*)"', block, re.DOTALL):
        pins.append({
            'type': pm.group(1),
            'x': float(pm.group(2)),
            'y': float(pm.group(3)),
            'rot': int(pm.group(4)),
            'len': float(pm.group(5)),
            'name': pm.group(6),
            'number': pm.group(7),
        })
    return pins

print('=== MPCIe socket pins ===')
pins = extract_pins('connectors.kicad_sym', 'PCIE-52P40H_C444926')
for p in sorted(pins, key=lambda x: int(x['number'])):
    side = "TOP" if p['y'] > 0 else "BOT"
    print(f"  pin {p['number']:>3s} ({p['name']:>5s}) at ({p['x']:7.2f},{p['y']:6.2f}) rot={p['rot']} side={side}")
print(f"Total: {len(pins)} pins")

print()
print('=== TXB0108PWR pins ===')
pins = extract_pins('ics.kicad_sym', 'TXB0108PWR')
for p in sorted(pins, key=lambda x: int(x['number'])):
    side = "LEFT" if p['x'] < 0 else "RIGHT" if p['x'] > 0 else "MID"
    print(f"  pin {p['number']:>3s} ({p['name']:>10s}) at ({p['x']:7.2f},{p['y']:6.2f}) rot={p['rot']} side={side}")
print(f"Total: {len(pins)} pins")

print()
print('=== ALC5651-CG pins ===')
pins = extract_pins('ics.kicad_sym', 'ALC5651-CG')
for p in sorted(pins, key=lambda x: int(x['number']) if x['number'].isdigit() else 999):
    side = "LEFT" if p['x'] < 0 else "RIGHT" if p['x'] > 0 else "MID"
    print(f"  pin {p['number']:>3s} ({p['name']:>15s}) at ({p['x']:7.2f},{p['y']:6.2f}) rot={p['rot']} side={side}")
print(f"Total: {len(pins)} pins")
