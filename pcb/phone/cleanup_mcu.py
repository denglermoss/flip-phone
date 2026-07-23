#!/usr/bin/env python3
"""
MCU sheet cleanup: fix power symbol spacing to prevent visual overlap.

For each cluster of power symbols < 5mm apart, move one symbol further away
and update the connecting wire endpoint.

Strategy:
- For horizontal pairs (same Y, close X): move one up/down by 2.54mm
- For vertical pairs (same X, close Y): move one left/right by 2.54mm
- Update the symbol's (at x y rot) line
- Update the wire endpoint that matches the old position
"""
import re
import sys

SCH_FILE = 'mcu.kicad_sch'

with open(SCH_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# Step 1: Find all power symbols and their positions
# Each power symbol is a (symbol ...) block with (lib_id "power:...")
# We need: reference, value (net name), position (x, y, rot), and the line number
power_syms = []
i = 0
while i < len(lines):
    line = lines[i].strip()
    if line == '(symbol' or (line.startswith('(symbol') and 'lib_id' not in line and 'lib_symbols' not in line):
        # Check if this is a power symbol instance
        ref = None
        val = None
        at_x = None
        at_y = None
        at_rot = 0
        at_line = None
        block_start = i
        for j in range(i+1, min(i+30, len(lines))):
            l = lines[j].strip()
            m = re.search(r'"Reference" "([^"]+)"', l)
            if m and not ref:
                ref = m.group(1)
            m = re.search(r'"Value" "([^"]+)"', l)
            if m and not val:
                val = m.group(1)
            m = re.match(r'\(at ([\d.]+) ([\d.]+)(?: (\d+))?\)', l)
            if m and at_x is None:
                at_x = float(m.group(1))
                at_y = float(m.group(2))
                at_rot = int(m.group(3)) if m.group(3) else 0
                at_line = j
            if ref and val and at_x is not None:
                break
        if ref and ref.startswith('#PWR') and val and at_x is not None:
            power_syms.append({
                'ref': ref,
                'net': val,
                'x': at_x,
                'y': at_y,
                'rot': at_rot,
                'at_line': at_line,
                'block_start': block_start,
            })
    i += 1

print(f"Found {len(power_syms)} power symbols")

# Step 2: Find clusters of power symbols < 5mm apart
clusters = []
used = set()
for i, p1 in enumerate(power_syms):
    if i in used:
        continue
    cluster = [i]
    used.add(i)
    for j, p2 in enumerate(power_syms):
        if j in used:
            continue
        for ci in cluster:
            pc = power_syms[ci]
            dist = ((pc['x']-p2['x'])**2 + (pc['y']-p2['y'])**2)**0.5
            if dist < 4.0:  # < 4mm = overlapping
                cluster.append(j)
                used.add(j)
                break
    if len(cluster) > 1:
        clusters.append(cluster)

print(f"Found {len(clusters)} clusters of overlapping power symbols")

# Step 3: For each cluster, calculate moves
# Strategy: for each pair in a cluster, move the second one away
moves = {}  # ref -> (new_x, new_y)
for cluster in clusters:
    syms = [power_syms[i] for i in cluster]
    # Sort by position to determine which to move
    syms.sort(key=lambda s: (s['x'], s['y']))
    
    for idx in range(1, len(syms)):
        s = syms[idx]
        prev = syms[idx-1]
        dx = s['x'] - prev['x']
        dy = s['y'] - prev['y']
        
        if abs(dx) < 3.0 and abs(dy) < 0.1:
            # Horizontal pair — move this one further in X by 2.54mm
            new_x = s['x'] + (2.54 if dx >= 0 else -2.54)
            new_y = s['y']
        elif abs(dy) < 3.0 and abs(dx) < 0.1:
            # Vertical pair — move this one further in Y by 2.54mm
            new_x = s['x']
            new_y = s['y'] + (2.54 if dy >= 0 else -2.54)
        else:
            # Diagonal — move in the direction of least separation
            if abs(dx) < abs(dy):
                new_x = s['x'] + (2.54 if dx >= 0 else -2.54)
                new_y = s['y']
            else:
                new_x = s['x']
                new_y = s['y'] + (2.54 if dy >= 0 else -2.54)
        
        moves[s['ref']] = (new_x, new_y)
        print(f"  Move {s['ref']} ({s['net']}) from ({s['x']:.2f}, {s['y']:.2f}) to ({new_x:.2f}, {new_y:.2f})")

# Step 4: Apply moves to the file
# For each moved power symbol:
#   a) Update the (at x y rot) line in the symbol block
#   b) Find wires that have an endpoint at the old position and update them
for sym in power_syms:
    if sym['ref'] not in moves:
        continue
    new_x, new_y = moves[sym['ref']]
    old_x, old_y = sym['x'], sym['y']
    
    # Update the (at ...) line in the symbol block
    at_line_idx = sym['at_line']
    old_at = lines[at_line_idx]
    # Preserve indentation
    indent = old_at[:len(old_at) - len(old_at.lstrip())]
    if sym['rot'] != 0:
        new_at = f"{indent}(at {new_x:.2f} {new_y:.2f} {sym['rot']})"
    else:
        new_at = f"{indent}(at {new_x:.2f} {new_y:.2f})"
    lines[at_line_idx] = new_at
    
    # Find and update wires with endpoint at old position
    for k, line in enumerate(lines):
        line_s = line.strip()
        if line_s.startswith('(wire (pts'):
            # Check if this wire has an endpoint at (old_x, old_y)
            # Format: (wire (pts (xy X1 Y1) (xy X2 Y2)) ...)
            m = re.match(r'\(wire \(pts \(xy ([\d.]+) ([\d.]+)\) \(xy ([\d.]+) ([\d.]+)\)\)', line_s)
            if m:
                x1, y1, x2, y2 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
                changed = False
                if abs(x1 - old_x) < 0.01 and abs(y1 - old_y) < 0.01:
                    x1, y1 = new_x, new_y
                    changed = True
                if abs(x2 - old_x) < 0.01 and abs(y2 - old_y) < 0.01:
                    x2, y2 = new_x, new_y
                    changed = True
                if changed:
                    indent = line[:len(line) - len(line.lstrip())]
                    # Reconstruct the wire line preserving the rest after pts
                    rest = line_s[line_s.index('))') + 2:]
                    lines[k] = f"{indent}(wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f})){rest}"

# Step 5: Write the updated file
new_content = '\n'.join(lines)
with open(SCH_FILE, 'w', encoding='utf-8', newline='\n') as f:
    f.write(new_content)

print(f"\nApplied {len(moves)} moves. File updated.")
