import re, sys

files = sys.argv[1:] or ['easyeda2kicad.kicad_sym', 'missing_parts.kicad_sym']
content = ''
for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        content += fh.read() + '\n'

symbol_pattern = re.compile(r'\(symbol "([^"]+)"', re.MULTILINE)
symbols = symbol_pattern.findall(content)
top_symbols = [s for s in symbols if '_0_1' not in s and '_1_1' not in s and '_2_1' not in s]

for sym_name in top_symbols:
    sym_start = content.find(f'(symbol "{sym_name}"')
    if sym_start == -1:
        continue
    sub_start = content.find(f'(symbol "{sym_name}_0_1"', sym_start)
    if sub_start == -1:
        continue
    next_sym = content.find('\n  (symbol "', sub_start)
    if next_sym == -1:
        next_sym = len(content)
    sub_block = content[sub_start:next_sym]

    pin_pattern = re.compile(r'\(pin\s+(\w+)\s+line\s+\(at\s+[\d.-]+\s+[\d.-]+\s+\d+\)\s+\(length\s+[\d.]+\)\s+\(name\s+"([^"]*)".*?\(number\s+"([^"]*)"', re.DOTALL)
    pins = pin_pattern.findall(sub_block)

    if pins:
        print(f'\n=== {sym_name} ({len(pins)} pins) ===')
        for ptype, pname, pnum in pins:
            print(f'  {pnum:>3s}: [{ptype:>12s}] {pname}')
