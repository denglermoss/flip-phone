#!/usr/bin/env python3
"""Analyze MCU sheet for spacing/rotation issues and generate a cleanup plan."""
import re

with open('mcu.kicad_sch', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Parse all symbol instances (not lib_symbol defs)
# Symbol instances are at the top level inside (kicad_sch ...)
# They start with (symbol and have (lib_id ...) on the next line
components = []
i = 0
while i < len(lines):
    line = lines[i].strip()
    if line == '(symbol' or (line.startswith('(symbol') and not line.startswith('(symbol ')):
        # Check if next non-empty line has lib_id
        for j in range(i+1, min(i+5, len(lines))):
            if 'lib_id' in lines[j]:
                at_val = None
                ref_val = None
                lib_id = None
                for k in range(i+1, min(i+25, len(lines))):
                    l = lines[k].strip()
                    m = re.match(r'\(at ([\d.]+) ([\d.]+)(?: (\d+))?\)', l)
                    if m and not at_val:
                        at_val = (float(m.group(1)), float(m.group(2)), int(m.group(3)) if m.group(3) else 0)
                    m = re.search(r'"Reference" "([^"]+)"', l)
                    if m and not ref_val:
                        ref_val = m.group(1)
                    m = re.search(r'lib_id "([^"]+)"', l)
                    if m and not lib_id:
                        lib_id = m.group(1)
                    if at_val and ref_val and lib_id:
                        break
                if at_val and ref_val:
                    components.append({
                        'ref': ref_val,
                        'x': at_val[0],
                        'y': at_val[1],
                        'rot': at_val[2],
                        'lib_id': lib_id
                    })
                break
    i += 1

# Categorize
real = [c for c in components if not c['ref'].startswith('#')]
power = [c for c in components if c['ref'].startswith('#')]

print(f"=== Real components ({len(real)}) ===")
real.sort(key=lambda c: (round(c['y']), c['x']))
for c in real:
    print(f"  {c['ref']:<8} ({c['x']:>7.2f}, {c['y']:>7.2f}) rot={c['rot']:>3}  {c['lib_id']}")

print(f"\n=== Power symbols ({len(power)}) ===")
power.sort(key=lambda c: (round(c['y']), c['x']))

# Group power symbols by proximity to identify clusters
clusters = []
used = set()
for i, p1 in enumerate(power):
    if i in used:
        continue
    cluster = [p1]
    used.add(i)
    for j, p2 in enumerate(power):
        if j in used:
            continue
        dist = ((p1['x']-p2['x'])**2 + (p1['y']-p2['y'])**2)**0.5
        if dist < 5.0:
            cluster.append(p2)
            used.add(j)
    clusters.append(cluster)

print(f"\n=== Power symbol clusters (< 5mm apart) ===")
for ci, cluster in enumerate(clusters):
    if len(cluster) > 1:
        print(f"\n  Cluster {ci+1} ({len(cluster)} symbols):")
        for c in cluster:
            print(f"    {c['ref']:<8} ({c['x']:>7.2f}, {c['y']:>7.2f}) rot={c['rot']:>3}")

# Check for ghost components at (0, 5.08)
print(f"\n=== Ghost components (at origin) ===")
for c in real:
    if c['x'] < 5 and c['y'] < 10:
        print(f"  {c['ref']:<8} ({c['x']:>7.2f}, {c['y']:>7.2f}) rot={c['rot']:>3}  {c['lib_id']}")

# Check rotation issues - components that might need rotation
print(f"\n=== Rotation summary ===")
rot_counts = {}
for c in real:
    rot_counts[c['rot']] = rot_counts.get(c['rot'], 0) + 1
for rot, count in sorted(rot_counts.items()):
    print(f"  rot={rot}: {count} components")
