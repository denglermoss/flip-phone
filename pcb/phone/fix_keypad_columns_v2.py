"""Fix keypad: break column wires into segments at each Pin2 position.

The column wires are currently single long wires from (COL_X, 54.61) to
(COL_X, 156.21). KiCad only connects wires to pins at endpoints/junctions,
not at midpoints. So Pin2 of SW5, SW9, SW13 (rows 1-3) are NOT connected.

Fix: Replace each long column wire with segments between consecutive Pin2
positions. This makes each Pin2 position a wire endpoint, ensuring connection.

Also remove junctions that are no longer needed (the old junctions were at
incorrect positions from the original generation).
"""
import re
import uuid

def gen_uuid():
    return str(uuid.uuid4())

def make_wire(x1, y1, x2, y2):
    return f'\t\t(wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))\n'

with open('keypad.kicad_sch', 'r', encoding='utf-8') as f:
    content = f.read()

COL_X = [66.04, 91.44, 116.84, 142.24]
PIN2_Y = [54.61, 80.01, 105.41, 130.81, 156.21]  # SW_Y - 1.27 for each row
LABEL_Y = 40.64
PULLDOWN_Y = 161.29

# Remove the 4 long column wires: (COL_X, 54.61) -> (COL_X, 156.21)
# And the 4 label wires: (COL_X, 40.64) -> (COL_X, 54.61)
# And the 4 pull-down wires: (COL_X, 156.21) -> (COL_X, 161.29)
removed = 0
for cx in COL_X:
    # Remove long column wire
    pattern1 = r'\t\t\(wire \(pts \(xy ' + re.escape(str(cx)) + r' 54\.61\) \(xy ' + re.escape(str(cx)) + r' 156\.20999999999998\)\) \(stroke \(width 0\) \(type default\)\) \(uuid "[^"]+"\)\)\n'
    content, n = re.subn(pattern1, '', content)
    removed += n
    
    # Remove label wire
    pattern2 = r'\t\t\(wire \(pts \(xy ' + re.escape(str(cx)) + r' 40\.64\) \(xy ' + re.escape(str(cx)) + r' 54\.61\)\) \(stroke \(width 0\) \(type default\)\) \(uuid "[^"]+"\)\)\n'
    content, n = re.subn(pattern2, '', content)
    removed += n
    
    # Remove pull-down wire
    pattern3 = r'\t\t\(wire \(pts \(xy ' + re.escape(str(cx)) + r' 156\.20999999999998\) \(xy ' + re.escape(str(cx)) + r' 161\.29\)\) \(stroke \(width 0\) \(type default\)\) \(uuid "[^"]+"\)\)\n'
    content, n = re.subn(pattern3, '', content)
    removed += n

print(f"Removed {removed} old column/label/pulldown wires")

# Generate new segmented column wires
new_wires = ""
for cx in COL_X:
    # Label to first Pin2
    new_wires += make_wire(cx, LABEL_Y, cx, PIN2_Y[0])
    # Segments between consecutive Pin2 positions
    for i in range(4):
        new_wires += make_wire(cx, PIN2_Y[i], cx, PIN2_Y[i + 1])
    # Last Pin2 to pull-down resistor
    new_wires += make_wire(cx, PIN2_Y[4], cx, PULLDOWN_Y)

print(f"Generated {5 * 4 + 4} new column wire segments")  # 6 segments per column × 4 columns = 24

# Remove all existing junctions (they're at incorrect positions)
junction_pattern = r'\t\t\(junction \(at [^)]+\) \(diameter [^)]+\) \(uuid "[^"]+"\)\)\n'
content, n = re.subn(junction_pattern, '', content)
print(f"Removed {n} old junctions")

# Insert new wires before sheet_instances
sheet_inst_match = re.search(r'(\t*\(sheet_instances)', content)
if sheet_inst_match:
    insert_pos = sheet_inst_match.start()
    content = content[:insert_pos] + new_wires + content[insert_pos:]
else:
    print("ERROR: Could not find sheet_instances")

# Clean up blank lines
content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)

with open('keypad.kicad_sch', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print("Done. Run ERC to verify.")
