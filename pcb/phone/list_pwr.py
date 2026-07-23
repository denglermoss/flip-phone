#!/usr/bin/env python3
"""List all power symbols with their net values and positions."""
import re

with open('mcu.kicad_sch', 'r', encoding='utf-8') as f:
    lines = f.readlines()

i = 0
results = []
while i < len(lines):
    line = lines[i].strip()
    if line == '(symbol' or (line.startswith('(symbol') and 'lib_id' not in line and 'lib_symbols' not in line):
        ref = None
        val = None
        at_val = None
        for j in range(i+1, min(i+25, len(lines))):
            l = lines[j].strip()
            m = re.search(r'"Reference" "([^"]+)"', l)
            if m and not ref:
                ref = m.group(1)
            m = re.search(r'"Value" "([^"]+)"', l)
            if m and not val:
                val = m.group(1)
            m = re.match(r'\(at ([\d.]+) ([\d.]+)(?: (\d+))?\)', l)
            if m and not at_val:
                at_val = (float(m.group(1)), float(m.group(2)))
            if ref and val and at_val:
                break
        if ref and ref.startswith('#PWR') and val and at_val:
            results.append((ref, val, at_val[0], at_val[1]))
    i += 1

results.sort(key=lambda r: (round(r[3]), r[2]))
for ref, val, x, y in results:
    print(f"{ref:<8} {val:<8} ({x:>7.2f}, {y:>7.2f})")
