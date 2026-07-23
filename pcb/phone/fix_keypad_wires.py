#!/usr/bin/env python3
"""Regenerate keypad wires to properly connect row/column matrix.

The subagent's wiring connected the wrong switch pins. This script:
1. Removes all existing wires in the keypad sheet
2. Regenerates correct row/column wires
3. Adds short connecting wires from switch pins to row/column buses

Matrix wiring:
- Row wire (horizontal) at Pin1 Y, connects to Pin1 (left-top) of each switch in the row
- Column wire (vertical) at Pin2 X, connects to Pin2 (right-top) of each switch in the column
- Pin3 and Pin4 (bottom pins) are internally connected to Pin1/Pin2 respectively in the switch
  (tactile switches have pins 1-3 on one side, 2-4 on other, but 1-3 and 2-4 are connected internally)
  Actually, for SKQGABE010: Pin1=Pin3 (left side), Pin2=Pin4 (right side)
  When pressed: Pin1 connected to Pin2 (and thus Pin3 to Pin4)
  
  So: Row wire -> Pin1 (or Pin3), Column wire -> Pin2 (or Pin4)
  We connect Row to Pin1, Column to Pin2.
  Pin3 and Pin4 are redundant (internally connected to Pin1/Pin2).
  We should add NC flags to Pin3 and Pin4, OR just leave them unconnected (they're passive pins).
"""

import re
import uuid as uuidmod

with open(r'C:\Users\dengle\Documents\personal_projects\phone\pcb\phone\keypad.kicad_sch', 'r', encoding='utf-8') as f:
    content = f.read()

# Switch positions (on-grid, already fixed)
SWITCH_X = [60.96, 86.36, 111.76, 137.16]  # 4 columns
SWITCH_Y = [55.88, 81.28, 106.68, 132.08, 157.48]  # 5 rows

# Pin offsets
PIN1_DX, PIN1_DY = -5.08, -1.27  # left top
PIN2_DX, PIN2_DY = 5.08, -1.27   # right top
PIN3_DX, PIN3_DY = -5.08, 3.81   # left bottom
PIN4_DX, PIN4_DY = 5.08, 3.81    # right bottom

# Row wire Y = Pin1 Y for each row
ROW_WIRE_Y = [y + PIN1_DY for y in SWITCH_Y]
# Column wire X = Pin2 X for each column (NOT Pin1 X!)
COL_WIRE_X = [x + PIN2_DX for x in SWITCH_X]  # 66.04, 91.44, 116.84, 142.24

# Remove all existing wire blocks
# Wire blocks look like:
# (wire
#   (pts
#     (xy X1 Y1) (xy X2 Y2)
#   )
#   (stroke
#     (width 0)
#     (type default)
#   )
#   (uuid "...")
# )

# Pattern to match wire blocks (with tab indentation)
wire_pattern = r'\t\t\(wire\s+\(pts\s+\(xy [^)]+\) \(xy [^)]+\)\)\s+\(stroke\s+\(width 0\)\s+\(type default\)\)\s+\(uuid "[^"]+"\)\s+\)\s*'
content = re.sub(wire_pattern, '', content)

# Generate new wires
new_wires = []

# 1. Row wires (horizontal) - connect Pin1 of all switches in each row
for row_idx in range(5):
    y = ROW_WIRE_Y[row_idx]
    # Wire from first switch Pin1 to last switch Pin1
    x_start = SWITCH_X[0] + PIN1_DX
    x_end = SWITCH_X[-1] + PIN1_DX
    uid = str(uuidmod.uuid4())
    new_wires.append(f'\t\t(wire (pts (xy {x_start} {y}) (xy {x_end} {y})) (stroke (width 0) (type default)) (uuid "{uid}"))')

# 2. Column wires (vertical) - connect Pin2 of all switches in each column
for col_idx in range(4):
    x = COL_WIRE_X[col_idx]
    # Wire from first switch Pin2 to last switch Pin2
    y_start = SWITCH_Y[0] + PIN2_DY
    y_end = SWITCH_Y[-1] + PIN2_DY
    uid = str(uuidmod.uuid4())
    new_wires.append(f'\t\t(wire (pts (xy {x} {y_start}) (xy {x} {y_end})) (stroke (width 0) (type default)) (uuid "{uid}"))')

# 3. Short connecting wires from Pin1 to row wire (if Pin1 is not already on the row wire)
# Pin1 is at (SW_X + PIN1_DX, SW_Y + PIN1_DY) = (SW_X - 5.08, SW_Y - 1.27)
# Row wire is at Y = SW_Y + PIN1_DY, running from first to last column
# Pin1 X = SW_X + PIN1_DX, which is within the row wire range
# So Pin1 is already ON the row wire - no extra wire needed!

# 4. Short connecting wires from Pin2 to column wire
# Pin2 is at (SW_X + PIN2_DX, SW_Y + PIN2_DY) = (SW_X + 5.08, SW_Y - 1.27)
# Column wire is at X = SW_X + PIN2_DX, running from first to last row
# Pin2 Y = SW_Y + PIN2_DY, which is within the column wire range
# So Pin2 is already ON the column wire - no extra wire needed!

# 5. Column wire extensions to pull-down resistors
# Pull-down resistors are at the bottom of each column
# R21-R24 are at (COL_WIRE_X, 166.37) with rotation 90
# Need wires from column wire bottom to resistor Pin 1
PULLDOWN_RES_Y = 166.37  # resistor center Y
# Resistor pin positions: Pin 1 at (X, Y - 2.54) for rotation 90, Pin 2 at (X, Y + 2.54)
# Actually for rotation 90, the pins are: Pin1 at (X-2.54, Y), Pin2 at (X+2.54, Y)
# No wait - for a horizontal resistor rotated 90 degrees:
# Original: Pin1 at (-2.54, 0), Pin2 at (2.54, 0)
# Rotated 90: Pin1 at (0, -2.54), Pin2 at (0, 2.54) relative to origin
# So Pin1 at (X, Y-2.54), Pin2 at (X, Y+2.54)

# The column wire ends at y_end = SWITCH_Y[-1] + PIN2_DY = 157.48 - 1.27 = 156.21
# Resistor is at Y=166.37, Pin1 at Y=166.37-2.54=163.83
# Need wire from (COL_X, 156.21) to (COL_X, 163.83)

for col_idx in range(4):
    x = COL_WIRE_X[col_idx]
    y_top = SWITCH_Y[-1] + PIN2_DY  # 156.21
    y_bot = PULLDOWN_RES_Y - 2.54   # 163.83 (Pin1 of resistor)
    uid = str(uuidmod.uuid4())
    new_wires.append(f'\t\t(wire (pts (xy {x} {y_top}) (xy {x} {y_bot})) (stroke (width 0) (type default)) (uuid "{uid}"))')

# 6. Pull-up resistor wires (R16-R20 on row lines, right side)
# Pull-up resistors at (147.32, SW_Y - 6.35) with rotation 90
# Pin1 at (147.32, SW_Y - 6.35 - 2.54), Pin2 at (147.32, SW_Y - 6.35 + 2.54)
# Row wire ends at x_end = SWITCH_X[-1] + PIN1_DX = 137.16 - 5.08 = 132.08
# Need wire from (132.08, ROW_Y) to (147.32, ROW_Y) to connect row to resistor Pin2
# Then resistor Pin1 connects to +3.3V

for row_idx in range(5):
    y = ROW_WIRE_Y[row_idx]
    x_row_end = SWITCH_X[-1] + PIN1_DX  # 132.08
    x_res = 147.32
    # Wire from row wire end to resistor Pin2
    uid = str(uuidmod.uuid4())
    new_wires.append(f'\t\t(wire (pts (xy {x_row_end} {y}) (xy {x_res} {y})) (stroke (width 0) (type default)) (uuid "{uid}"))')

# Insert new wires before (sheet_instances
new_wires_str = '\n'.join(new_wires) + '\n'
content = content.replace('\t(sheet_instances', new_wires_str + '\t(sheet_instances')

# Write the fixed file
with open(r'C:\Users\dengle\Documents\personal_projects\phone\pcb\phone\keypad.kicad_sch', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print(f"Keypad wires regenerated: {len(new_wires)} wires")
print(f"  5 row wires (horizontal, at Pin1 Y)")
print(f"  4 column wires (vertical, at Pin2 X)")
print(f"  4 column-to-pulldown wires")
print(f"  5 row-to-pullup wires")
