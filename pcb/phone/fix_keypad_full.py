#!/usr/bin/env python3
"""Fix keypad.kicad_sch: complete rewrite with correct matrix wiring.

The correct approach for a keypad matrix in KiCad:
- Row wires run horizontally at SW_Y (switch center Y), NOT at Pin1 Y
- Column wires run vertically at Pin2 X (right side)
- Short vertical wires connect Pin1 (top-left) down to the row wire
- Pin3 and Pin4 are internally connected to Pin1/Pin2, add NC flags

This avoids the row wire passing through Pin2 (which would short row to column).
"""

import re
import uuid as uuidmod

with open(r'C:\Users\dengle\Documents\personal_projects\phone\pcb\phone\keypad.kicad_sch', 'r', encoding='utf-8') as f:
    content = f.read()

# =============================================================================
# Step 1: Snap switch positions to 1.27mm grid (same as before)
# =============================================================================

OLD_SW_X = [60.0, 85.0, 110.0, 135.0]
OLD_SW_Y = [55.0, 80.0, 105.0, 130.0, 155.0]
NEW_SW_X = [60.96, 86.36, 111.76, 137.16]
NEW_SW_Y = [55.88, 81.28, 106.68, 132.08, 157.48]

PIN1_DX, PIN1_DY = -5.08, -1.27
PIN2_DX, PIN2_DY = 5.08, -1.27
PIN3_DX, PIN3_DY = -5.08, 3.81
PIN4_DX, PIN4_DY = 5.08, 3.81

def fmt(val):
    rounded = round(val, 2)
    if abs(rounded - int(rounded)) < 0.001:
        return str(int(rounded))
    return f"{rounded:.2f}".rstrip('0').rstrip('.')

# Build and apply coordinate map (same as before)
coord_map = {}
for old, new in zip(OLD_SW_X, NEW_SW_X):
    coord_map[str(int(old))] = fmt(new); coord_map[str(old)] = fmt(new)
for old, new in zip(OLD_SW_Y, NEW_SW_Y):
    coord_map[str(int(old))] = fmt(new); coord_map[str(old)] = fmt(new)

OLD_ROW_WIRE_Y = [53.73, 78.73, 103.73, 128.73, 153.73]
NEW_ROW_WIRE_Y = [y + PIN1_DY for y in NEW_SW_Y]
for old, new in zip(OLD_ROW_WIRE_Y, NEW_ROW_WIRE_Y):
    coord_map[str(old)] = fmt(new)

OLD_COL_WIRE_X = [54.92, 79.92, 104.92, 129.92]
NEW_PIN1_X = [x + PIN1_DX for x in NEW_SW_X]
for old, new in zip(OLD_COL_WIRE_X, NEW_PIN1_X):
    coord_map[str(old)] = fmt(new)

OLD_PIN2_X = [x + 5.08 for x in OLD_SW_X]
NEW_PIN2_X = [x + 5.08 for x in NEW_SW_X]
for old, new in zip(OLD_PIN2_X, NEW_PIN2_X):
    coord_map[str(old)] = fmt(new)

coord_map["160"] = "147.32"; coord_map["160.0"] = "147.32"
coord_map["25"] = "25.4"
coord_map["40"] = "40.64"

for old_sw, new_sw in zip(OLD_SW_Y, NEW_SW_Y):
    coord_map[str(old_sw - 6.35)] = fmt(new_sw - 6.35)
    coord_map[str(old_sw - 11.43)] = fmt(new_sw - 11.43)
coord_map[str(OLD_SW_Y[-1] + 8.89)] = fmt(NEW_SW_Y[-1] + 8.89)
coord_map[str(OLD_SW_Y[-1] + 13.97)] = fmt(NEW_SW_Y[-1] + 13.97)
coord_map["158.81"] = "161.29"
coord_map["158.80999999999997"] = "161.29"
coord_map["158.80999999999998"] = "161.29"

def replace_in_context(content, old_str, new_str):
    content = re.sub(r'(\(xy\s+)' + re.escape(old_str) + r'(?=\s)', r'\g<1>' + new_str, content)
    content = re.sub(r'(\(at\s+)' + re.escape(old_str) + r'(?=\s)', r'\g<1>' + new_str, content)
    content = re.sub(r'(\(xy\s+[\d.]+\s+)' + re.escape(old_str) + r'(?=[\s\)])', r'\g<1>' + new_str, content)
    content = re.sub(r'(\(at\s+[\d.]+\s+)' + re.escape(old_str) + r'(?=[\s\)])', r'\g<1>' + new_str, content)
    return content

# Build numeric coordinate map (handles floating point artifacts in the file)
# The file may have values like '123.64999999999999' instead of '123.65'
# We need to match numerically, not by string
numeric_map = {}
for old_str, new_str in coord_map.items():
    numeric_map[float(old_str)] = new_str

def replace_coords_numeric(content, numeric_map):
    """Replace coordinates in (at X Y) and (xy X Y) using numeric comparison."""
    def repl_at(match):
        prefix = match.group(1)  # (at or (xy
        nums = match.group(2).split()
        if len(nums) >= 2:
            x, y = float(nums[0]), float(nums[1])
            # Check if X matches any old value
            for old_val, new_str in numeric_map.items():
                if abs(x - old_val) < 0.001:
                    nums[0] = new_str
                    break
            # Check if Y matches any old value
            for old_val, new_str in numeric_map.items():
                if abs(y - old_val) < 0.001:
                    nums[1] = new_str
                    break
            rest = ' '.join(nums[2:])
            if rest:
                return prefix + ' '.join(nums[:2]) + ' ' + rest + match.group(3)
            else:
                return prefix + ' '.join(nums[:2]) + match.group(3)
        return match.group(0)

    # Match (at X Y [rot]) and (xy X Y) with any numeric format
    content = re.sub(r'(\(at\s+)([\d.]+(?:e[+-]?\d+)?\s+[\d.]+(?:e[+-]?\d+)?(?:\s+[\d.]+)?)(\))', repl_at, content)
    content = re.sub(r'(\(xy\s+)([\d.]+(?:e[+-]?\d+)?\s+[\d.]+(?:e[+-]?\d+)?)(\))', repl_at, content)
    return content

content = replace_coords_numeric(content, numeric_map)

# Move column labels to Pin2 X (numeric matching for floating point safety)
for pin1_x, pin2_x in zip(NEW_PIN1_X, NEW_PIN2_X):
    def repl_col_label(m):
        x = float(m.group(2))
        if abs(x - pin1_x) < 0.01:
            return m.group(1) + fmt(pin2_x) + m.group(3)
        return m.group(0)
    content = re.sub(r'(\(at\s+)([\d.]+)(\s+[\d.]+\s+90\))', repl_col_label, content)

# Move pull-down resistors to Pin2 X
for pin1_x, pin2_x in zip(NEW_PIN1_X, NEW_PIN2_X):
    def repl_pulldown(m):
        x = float(m.group(2))
        if abs(x - pin1_x) < 0.01:
            return m.group(1) + fmt(pin2_x) + m.group(3)
        return m.group(0)
    content = re.sub(r'(\(at\s+)([\d.]+)(\s+166\.37\s+90\))', repl_pulldown, content)

# Move pull-down GND to Pin2 X
for pin1_x, pin2_x in zip(NEW_PIN1_X, NEW_PIN2_X):
    def repl_gnd(m):
        x = float(m.group(2))
        if abs(x - pin1_x) < 0.01:
            return m.group(1) + fmt(pin2_x) + m.group(3)
        return m.group(0)
    content = re.sub(r'(\(at\s+)([\d.]+)(\s+171\.45\s+0\))', repl_gnd, content)

# Move row labels from Pin1_Y to SW_Y (row wire Y)
# Row labels are at (25.4, Pin1_Y, 180) -> change to (25.4, SW_Y, 180)
for sw_y in NEW_SW_Y:
    old_y_val = sw_y + PIN1_DY  # Pin1_Y = SW_Y - 1.27
    new_y_str = fmt(sw_y)       # SW_Y
    def repl_row_label(m):
        y = float(m.group(2))
        if abs(y - old_y_val) < 0.01:
            return m.group(1) + new_y_str + m.group(3)
        return m.group(0)
    content = re.sub(r'(\(at\s+25\.4\s+)([\d.]+)(\s+180\))', repl_row_label, content)

# =============================================================================
# Step 2: Remove ALL existing wires
# =============================================================================

def remove_wire_blocks(text):
    result = []
    i = 0
    while i < len(text):
        wire_start = text.find('(wire', i)
        if wire_start < 0:
            result.append(text[i:])
            break
        result.append(text[i:wire_start])
        depth = 0
        j = wire_start
        while j < len(text):
            if text[j] == '(': depth += 1
            elif text[j] == ')':
                depth -= 1
                if depth == 0:
                    j += 1
                    while j < len(text) and text[j] in '\n\r\t ': j += 1
                    break
            j += 1
        i = j
    return ''.join(result)

content = remove_wire_blocks(content)

# =============================================================================
# Step 3: Generate new wires with correct matrix wiring
# =============================================================================

new_wires = []

# Row wires: run horizontally at Pin3_Y (SW_Y + 3.81), connecting Pin3 of all switches in a row
# Pin3 is at (SW_X - 5.08, SW_Y + 3.81) - bottom left
# The row wire at Pin3_Y passes through Pin4 (SW_X + 5.08, SW_Y + 3.81) - bottom right
# Pin4 is internally connected to Pin2, so connecting to Pin4 is same as connecting to Pin2
# This would short the row and column!
#
# BETTER APPROACH: Run row wire at a Y between Pin1 and Pin3, e.g., at SW_Y (switch center)
# Then connect Pin1 to row wire with a short vertical wire
# The row wire at SW_Y does NOT pass through any pin (pins are at SW_Y-1.27 and SW_Y+3.81)

ROW_WIRE_Y = NEW_SW_Y  # Run row wire at switch center Y

for row_idx in range(5):
    y = ROW_WIRE_Y[row_idx]
    # Wire from row label (X=25.4) to first Pin1 X
    uid = str(uuidmod.uuid4())
    new_wires.append(f'\t\t(wire (pts (xy 25.4 {y}) (xy {NEW_PIN1_X[0]} {y})) (stroke (width 0) (type default)) (uuid "{uid}"))')

    # Row wire broken into segments between adjacent Pin1 X positions
    # This ensures vertical wire endpoints land on row wire endpoints (not middles)
    for col_idx in range(3):  # 3 segments connecting 4 Pin1 positions
        x1 = NEW_PIN1_X[col_idx]
        x2 = NEW_PIN1_X[col_idx + 1]
        uid = str(uuidmod.uuid4())
        new_wires.append(f'\t\t(wire (pts (xy {x1} {y}) (xy {x2} {y})) (stroke (width 0) (type default)) (uuid "{uid}"))')

    # Vertical wires from Pin1 (top-left) down to row wire for each switch in this row
    for col_idx in range(4):
        pin1_x = NEW_PIN1_X[col_idx]
        pin1_y = NEW_SW_Y[row_idx] + PIN1_DY  # SW_Y - 1.27
        uid = str(uuidmod.uuid4())
        new_wires.append(f'\t\t(wire (pts (xy {pin1_x} {pin1_y}) (xy {pin1_x} {y})) (stroke (width 0) (type default)) (uuid "{uid}"))')

# Column wires: run vertically at Pin2 X, connecting Pin2 of all switches in a column
# Pin2 is at (SW_X + 5.08, SW_Y - 1.27) - top right
# The column wire at Pin2_X passes through Pin2 Y positions
# It does NOT pass through the row wire (which is at SW_Y, not SW_Y - 1.27)
# But it DOES pass through Pin4 (SW_X + 5.08, SW_Y + 3.81) - bottom right
# Pin4 is internally connected to Pin2, so that's fine (same net)

for col_idx in range(4):
    x = NEW_PIN2_X[col_idx]
    y_start = NEW_SW_Y[0] + PIN2_DY  # 54.61 (Pin2 Y of first row)
    y_end = NEW_SW_Y[-1] + PIN2_DY   # 156.21 (Pin2 Y of last row)
    uid = str(uuidmod.uuid4())
    new_wires.append(f'\t\t(wire (pts (xy {x} {y_start}) (xy {x} {y_end})) (stroke (width 0) (type default)) (uuid "{uid}"))')

    # Wire from column label (at Y=40.64) to column wire start
    uid = str(uuidmod.uuid4())
    new_wires.append(f'\t\t(wire (pts (xy {x} 40.64) (xy {x} {y_start})) (stroke (width 0) (type default)) (uuid "{uid}"))')

# Row-to-pullup wires: from row wire end to pull-up resistor Pin1
# Pull-up resistors at (147.32, SW_Y - 6.35) rotation 90
# Resistor pin offset is ±5.08 (not ±2.54):
#   Pin1 at (147.32, R_Y + 5.08) = (147.32, SW_Y - 6.35 + 5.08) = (147.32, SW_Y - 1.27)
#   Pin2 at (147.32, R_Y - 5.08) = (147.32, SW_Y - 11.43) — connects to +3.3V
# Row wire is at SW_Y, Pin1 is at SW_Y - 1.27, need vertical wire connecting them
for row_idx in range(5):
    y_row = ROW_WIRE_Y[row_idx]
    y_pin1 = NEW_SW_Y[row_idx] - 1.27  # resistor Pin1 Y = SW_Y - 1.27
    x_row_end = NEW_PIN1_X[-1]  # 132.08
    x_res = 147.32

    # Horizontal wire from row wire end to resistor X
    uid = str(uuidmod.uuid4())
    new_wires.append(f'\t\t(wire (pts (xy {x_row_end} {y_row}) (xy {x_res} {y_row})) (stroke (width 0) (type default)) (uuid "{uid}"))')

    # Vertical wire from resistor Pin1 to row wire Y
    uid = str(uuidmod.uuid4())
    new_wires.append(f'\t\t(wire (pts (xy {x_res} {y_pin1}) (xy {x_res} {y_row})) (stroke (width 0) (type default)) (uuid "{uid}"))')

# Column-to-pulldown wires: from column wire bottom to pull-down resistor Pin2
# Pull-down resistors at (Pin2_X, 166.37) rotation 90
# Pin offset ±5.08: Pin1 at (X, 171.45) [GND], Pin2 at (X, 161.29) [column wire]
for col_idx in range(4):
    x = NEW_PIN2_X[col_idx]
    y_col_end = NEW_SW_Y[-1] + PIN2_DY  # 156.21
    y_pin2 = 166.37 - 5.08  # 161.29 (resistor Pin2)
    uid = str(uuidmod.uuid4())
    new_wires.append(f'\t\t(wire (pts (xy {x} {y_col_end}) (xy {x} {y_pin2})) (stroke (width 0) (type default)) (uuid "{uid}"))')

# Insert new wires before (sheet_instances
new_wires_str = '\n'.join(new_wires) + '\n'
content = content.replace('\t(sheet_instances', new_wires_str + '\t(sheet_instances')

# =============================================================================
# Step 4: Add no-connect (NC) flags to Pin 3 and Pin 4 of all switches
# =============================================================================
# Pin 3 (bottom-left) and Pin 4 (bottom-right) are internally connected to
# Pin 1 and Pin 2 respectively in the tactile switch. They don't need wires.
nc_entries = []
for row_idx in range(5):
    for col_idx in range(4):
        sw_x = NEW_SW_X[col_idx]
        sw_y = NEW_SW_Y[row_idx]
        # Pin 3 at (SW_X - 5.08, SW_Y + 3.81) — always safe (not on any wire)
        pin3_x = sw_x + PIN3_DX
        pin3_y = sw_y + PIN3_DY
        uid = str(uuidmod.uuid4())
        nc_entries.append(f'\t(no_connect (at {pin3_x} {pin3_y}) (uuid "{uid}"))')
        # Pin 4 at (SW_X + 5.08, SW_Y + 3.81) — on column wire path
        # Only add NC if Pin 4 is NOT at a wire endpoint (i.e., not last row)
        # Last row Pin 4 is at the pull-down wire endpoint, so it's connected
        if row_idx < 4:
            pin4_x = sw_x + PIN4_DX
            pin4_y = sw_y + PIN4_DY
            uid = str(uuidmod.uuid4())
            nc_entries.append(f'\t(no_connect (at {pin4_x} {pin4_y}) (uuid "{uid}"))')

nc_str = '\n'.join(nc_entries) + '\n'
content = content.replace('\t(sheet_instances', nc_str + '\t(sheet_instances')

# Write the fixed file
with open(r'C:\Users\dengle\Documents\personal_projects\phone\pcb\phone\keypad.kicad_sch', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print(f"Keypad fully fixed with correct matrix wiring:")
print(f"  - Row wires at SW_Y (switch center), NOT at Pin Y")
print(f"  - Short vertical wires from Pin1 down to row wire")
print(f"  - Column wires at Pin2 X (right side)")
print(f"  - {len(new_wires)} wires total")
print(f"  - Row wires DON'T pass through Pin2 (no row-column short)")
