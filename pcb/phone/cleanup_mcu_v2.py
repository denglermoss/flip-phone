#!/usr/bin/env python3
"""
MCU sheet cleanup v2: fix power symbol spacing to prevent visual overlap.
More robust wire detection and update logic.
Works on mcu_test.kicad_sch for safe testing.
"""
import re
import sys

SCH_FILE = 'mcu_test.kicad_sch'

with open(SCH_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# Step 1: Find all power symbol instances with their positions
# Power symbols have (lib_id "power:...") 
power_syms = []
i = 0
while i < len(lines):
    line = lines[i].strip()
    # Look for symbol instance blocks (start with (symbol on its own line)
    if line == '(symbol' or (line.startswith('(symbol') and not line.startswith('(symbol "')):
        # Check if this has a lib_id for a power symbol
        is_power = False
        ref = None
        val = None
        at_x = None
        at_y = None
        at_rot = 0
        at_line_idx = None
        for j in range(i+1, min(i+30, len(lines))):
            l = lines[j].strip()
            if 'lib_id "power:' in l:
                is_power = True
            m = re.search(r'"Reference" "([^"]+)"', l)
            if m and not ref:
                ref = m.group(1)
            m = re.search(r'"Value" "([^"]+)"', l)
            if m and not val:
                val = m.group(1)
            # The FIRST (at ...) after lib_id is the symbol position
            # But we need to skip property (at ...) lines
            # Property lines have "property" before "at"
            if is_power and at_x is None:
                m = re.match(r'\(at ([\d.]+) ([\d.]+)(?: (\d+))?\)$', l)
                if m:
                    at_x = float(m.group(1))
                    at_y = float(m.group(2))
                    at_rot = int(m.group(3)) if m.group(3) else 0
                    at_line_idx = j
            if ref and val and at_x is not None:
                break
        if is_power and ref and ref.startswith('#PWR') and at_x is not None:
            power_syms.append({
                'ref': ref,
                'net': val,
                'x': at_x,
                'y': at_y,
                'rot': at_rot,
                'at_line': at_line_idx,
            })
    i += 1

print(f"Found {len(power_syms)} power symbols")

# Step 2: Find all wires and their endpoints
wires = []
for k, line in enumerate(lines):
    line_s = line.strip()
    if line_s.startswith('(wire (pts'):
        m = re.search(r'\(wire \(pts \(xy ([\d.]+) ([\d.]+)\) \(xy ([\d.]+) ([\d.]+)\)\)', line_s)
        if m:
            wires.append({
                'line': k,
                'x1': float(m.group(1)),
                'y1': float(m.group(2)),
                'x2': float(m.group(3)),
                'y2': float(m.group(4)),
                'raw': line,
            })

print(f"Found {len(wires)} wires")

# Step 3: Find clusters of power symbols < 4mm apart
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
            if dist < 4.0:
                cluster.append(j)
                used.add(j)
                break
    if len(cluster) > 1:
        clusters.append(cluster)

print(f"Found {len(clusters)} clusters")

# Step 4: Calculate moves
moves = {}  # ref -> (new_x, new_y, old_x, old_y)
for cluster in clusters:
    syms = [power_syms[i] for i in cluster]
    syms.sort(key=lambda s: (s['x'], s['y']))
    
    for idx in range(1, len(syms)):
        s = syms[idx]
        prev = syms[idx-1]
        dx = s['x'] - prev['x']
        dy = s['y'] - prev['y']
        
        if abs(dx) < 3.0 and abs(dy) < 0.1:
            new_x = s['x'] + (2.54 if dx >= 0 else -2.54)
            new_y = s['y']
        elif abs(dy) < 3.0 and abs(dx) < 0.1:
            new_x = s['x']
            new_y = s['y'] + (2.54 if dy >= 0 else -2.54)
        else:
            if abs(dx) < abs(dy):
                new_x = s['x'] + (2.54 if dx >= 0 else -2.54)
                new_y = s['y']
            else:
                new_x = s['x']
                new_y = s['y'] + (2.54 if dy >= 0 else -2.54)
        
        moves[s['ref']] = (new_x, new_y, s['x'], s['y'])
        print(f"  Move {s['ref']} ({s['net']}) ({s['x']:.2f}, {s['y']:.2f}) -> ({new_x:.2f}, {new_y:.2f})")

# Step 5: Apply moves
for sym in power_syms:
    if sym['ref'] not in moves:
        continue
    new_x, new_y, old_x, old_y = moves[sym['ref']]
    
    # Update symbol (at ...) line — ALWAYS include rotation (KiCad requires it)
    at_idx = sym['at_line']
    old_line = lines[at_idx]
    indent = old_line[:len(old_line) - len(old_line.lstrip())]
    lines[at_idx] = f"{indent}(at {new_x:.2f} {new_y:.2f} {sym['rot']})"
    
    # Update ALL property (at old_x old_y ...) lines within this symbol block
    # Find the symbol block boundaries
    block_start = sym['at_line'] - 1  # The (symbol line is before (at ...)
    # Go back to find the (symbol line
    for bi in range(at_idx, max(at_idx-10, 0), -1):
        if lines[bi].strip() == '(symbol' or lines[bi].strip().startswith('(symbol'):
            block_start = bi
            break
    # Find the end of the block (matching closing paren)
    depth = 0
    block_end = block_start
    for bi in range(block_start, len(lines)):
        stripped = lines[bi]
        depth += stripped.count('(') - stripped.count(')')
        if depth <= 0:
            block_end = bi
            break
    
    # Update property (at ...) lines within the block
    for bi in range(block_start, block_end+1):
        l = lines[bi]
        # Match property at lines: (property "..." "..." (at OLD_X OLD_Y ...
        if '(at ' in l and 'property' in l:
            # Replace old x,y with new x,y in the (at ...) part
            # Be careful to only replace the position, not other numbers
            l_new = re.sub(
                r'\(at ' + re.escape(f"{old_x:.2f}") + r' ' + re.escape(f"{old_y:.2f}") + r'',
                f'(at {new_x:.2f} {new_y:.2f}',
                l
            )
            if l_new != l:
                lines[bi] = l_new
    
    # Update wires that have an endpoint at (old_x, old_y)
    for w in wires:
        changed = False
        w1x, w1y, w2x, w2y = w['x1'], w['y1'], w['x2'], w['y2']
        if abs(w1x - old_x) < 0.01 and abs(w1y - old_y) < 0.01:
            w1x, w1y = new_x, new_y
            changed = True
        if abs(w2x - old_x) < 0.01 and abs(w2y - old_y) < 0.01:
            w2x, w2y = new_x, new_y
            changed = True
        if changed:
            old_w = lines[w['line']]
            indent = old_w[:len(old_w) - len(old_w.lstrip())]
            # Reconstruct: keep everything after the pts block
            old_s = old_w.strip()
            pts_end = old_s.index('))')  # End of (pts ...)
            rest = old_s[pts_end+2:]  # Everything after pts
            lines[w['line']] = f"{indent}(wire (pts (xy {w1x:.2f} {w1y:.2f}) (xy {w2x:.2f} {w2y:.2f})){rest}"
            print(f"    Updated wire: ({w1x:.2f}, {w1y:.2f}) -> ({w2x:.2f}, {w2y:.2f})")
    
    # If no wire was found connecting to the old position, the power symbol
    # was placed directly on a pin. Add a wire from old position to new position.
    wire_found = False
    for w in wires:
        if (abs(w['x1'] - old_x) < 0.01 and abs(w['y1'] - old_y) < 0.01) or \
           (abs(w['x2'] - old_x) < 0.01 and abs(w['y2'] - old_y) < 0.01):
            wire_found = True
            break
    if not wire_found:
        # Add a wire from old position (pin) to new position (power symbol)
        import uuid as uuid_module
        new_wire = f'\t(wire (pts (xy {old_x:.2f} {old_y:.2f}) (xy {new_x:.2f} {new_y:.2f})) (stroke (width 0) (type default)) (uuid "{uuid_module.uuid4()}"))'
        # Insert before sheet_instances
        for k, line in enumerate(lines):
            if '(sheet_instances' in line:
                lines.insert(k, new_wire)
                break
        print(f"    Added wire: ({old_x:.2f}, {old_y:.2f}) -> ({new_x:.2f}, {new_y:.2f})")

# Step 6: Write updated file
new_content = '\n'.join(lines)
with open(SCH_FILE, 'w', encoding='utf-8', newline='\n') as f:
    f.write(new_content)

print(f"\nApplied {len(moves)} moves to {SCH_FILE}")
