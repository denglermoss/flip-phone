#!/usr/bin/env python3
"""Fix keypad.kicad_sch: snap all coordinates to 1.27mm grid.

The subagent placed switches at 5mm spacing (off-grid), causing endpoint_off_grid
warnings and pin_not_connected errors.

Strategy: Direct string replacement of coordinate values, handling both
integer and float formats.
"""

import re

with open(r'C:\Users\dengle\Documents\personal_projects\phone\pcb\phone\keypad.kicad_sch', 'r', encoding='utf-8') as f:
    content = f.read()

# Old positions (off-grid, 5mm spacing)
OLD_SW_X = [60.0, 85.0, 110.0, 135.0]
OLD_SW_Y = [55.0, 80.0, 105.0, 130.0, 155.0]

# New positions (on-grid, 1.27mm multiples, 25.4mm spacing)
NEW_SW_X = [60.96, 86.36, 111.76, 137.16]
NEW_SW_Y = [55.88, 81.28, 106.68, 132.08, 157.48]

# Pin offsets
PIN1_DX = -5.08  # Pin 1 X offset from switch origin
PIN1_DY = -1.27  # Pin 1 Y offset

# Old wire/label positions
OLD_ROW_WIRE_Y = [53.73, 78.73, 103.73, 128.73, 153.73]
OLD_COL_WIRE_X = [54.92, 79.92, 104.92, 129.92]

# New wire/label positions
NEW_ROW_WIRE_Y = [y + PIN1_DY for y in NEW_SW_Y]
NEW_COL_WIRE_X = [x + PIN1_DX for x in NEW_SW_X]

# Build coordinate replacement map
# Key: old value (as it appears in file), Value: new value (formatted)
def fmt(val):
    """Format a coordinate value: integer if whole, else float."""
    rounded = round(val, 2)
    if abs(rounded - int(rounded)) < 0.001:
        return str(int(rounded))
    # Avoid floating point artifacts
    return f"{rounded:.2f}".rstrip('0').rstrip('.')

# Map old coordinate strings to new coordinate strings
# We need to handle both "60" and "60.0" formats
coord_map = {}

# X coordinates
x_pairs = list(zip(OLD_SW_X, NEW_SW_X))
x_pairs += list(zip(OLD_COL_WIRE_X, NEW_COL_WIRE_X))
# Pin2 X (SW_X + 5.08)
x_pairs += [(ox + 5.08, nx + 5.08) for ox, nx in zip(OLD_SW_X, NEW_SW_X)]
# Right edge (pull-up resistors at X=160)
x_pairs += [(160.0, 147.32)]
# Label X (25)
x_pairs += [(25.0, 25.4)]

for old, new in x_pairs:
    # Map both integer and float string representations
    coord_map[str(int(old)) if old == int(old) else str(old)] = fmt(new)
    coord_map[f"{old}"] = fmt(new)

# Y coordinates
y_pairs = list(zip(OLD_SW_Y, NEW_SW_Y))
y_pairs += list(zip(OLD_ROW_WIRE_Y, NEW_ROW_WIRE_Y))
# Pull-up resistor Y (SW_Y - 6.35)
y_pairs += [(oy - 6.35, ny - 6.35) for oy, ny in zip(OLD_SW_Y, NEW_SW_Y)]
# Pull-up +3.3V Y (SW_Y - 11.43)
y_pairs += [(oy - 11.43, ny - 11.43) for oy, ny in zip(OLD_SW_Y, NEW_SW_Y)]
# Pull-down resistor Y (last SW_Y + 8.89)
y_pairs += [(OLD_SW_Y[-1] + 8.89, NEW_SW_Y[-1] + 8.89)]
# Pull-down GND Y (last SW_Y + 13.97)
y_pairs += [(OLD_SW_Y[-1] + 13.97, NEW_SW_Y[-1] + 13.97)]
# Column label Y (40)
y_pairs += [(40.0, 40.64)]
# Column wire bottom Y (158.81 = last SW_Y + 3.81)
y_pairs += [(158.81, 161.29)]

for old, new in y_pairs:
    coord_map[str(int(old)) if old == int(old) else str(old)] = fmt(new)
    coord_map[f"{old}"] = fmt(new)

print("Coordinate map:")
for old, new in sorted(coord_map.items(), key=lambda x: float(x[0]) if x[0].replace('.','').isdigit() else 0):
    print(f"  {old} -> {new}")

# Now replace coordinates in the file
# We need to replace numbers that appear as coordinates in (at X Y ...) and (xy X Y)
# Be careful not to replace numbers that are part of other values

# Strategy: Replace in (at ...) and (xy ...) contexts only
# Process from largest values to smallest to avoid partial matches

def replace_in_context(content, old_str, new_str):
    """Replace old_str with new_str only in (at ...) and (xy ...) coordinate contexts."""
    # Replace in (xy X Y) - X is first number after xy
    # Replace in (at X Y [rot]) - X is first number after at
    # Replace in (xy X Y) - Y is second number
    # Replace in (at X Y [rot]) - Y is second number
    
    # X coordinate: (xy OLD or (at OLD
    content = re.sub(
        r'(\(xy\s+)' + re.escape(old_str) + r'(?=\s)',
        r'\g<1>' + new_str,
        content
    )
    content = re.sub(
        r'(\(at\s+)' + re.escape(old_str) + r'(?=\s)',
        r'\g<1>' + new_str,
        content
    )
    
    # Y coordinate: (xy X OLD or (at X OLD
    # Match the second number in the coordinate pair
    content = re.sub(
        r'(\(xy\s+[\d.]+\s+)' + re.escape(old_str) + r'(?=[\s\)])',
        r'\g<1>' + new_str,
        content
    )
    content = re.sub(
        r'(\(at\s+[\d.]+\s+)' + re.escape(old_str) + r'(?=[\s\)])',
        r'\g<1>' + new_str,
        content
    )
    
    return content

# Sort by numeric value descending to avoid partial match issues
# (e.g., replace "160" before "60")
sorted_coords = sorted(coord_map.items(), key=lambda x: float(x[0]), reverse=True)

for old_str, new_str in sorted_coords:
    content = replace_in_context(content, old_str, new_str)

# Write the fixed file
with open(r'C:\Users\dengle\Documents\personal_projects\phone\pcb\phone\keypad.kicad_sch', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print("\nKeypad sheet fixed - coordinates snapped to 1.27mm grid")

# Verify
with open(r'C:\Users\dengle\Documents\personal_projects\phone\pcb\phone\keypad.kicad_sch', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'\(symbol\s+\(lib_id "electromech:SKQGABE010"\)\s+\(at ([\d.]+) ([\d.]+) (\d+)\)'
matches = re.findall(pattern, content)
print(f"\nVerification - switch positions after fix:")
for i, m in enumerate(matches[:5]):
    print(f"  Switch {i+1}: at ({m[0]}, {m[1]}) rot={m[2]}")
print(f"  ... ({len(matches)} total)")
