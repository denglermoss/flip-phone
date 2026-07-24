"""Check keypad wiring for real issues:
1. Do column wires pass through NC flag positions (conflict)?
2. Do row wires actually connect to Pin 1?
3. Are rows and columns on separate nets?
"""
import re

with open('keypad.kicad_sch', 'r', encoding='utf-8') as f:
    c = f.read()

# Find all wires
wires = []
wire_pattern = r'\(wire\s+\(pts\s+\(xy\s+([\d.]+)\s+([\d.]+)\)\s+\(xy\s+([\d.]+)\s+([\d.]+)\)\)'
for m in re.finditer(wire_pattern, c):
    x1, y1, x2, y2 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
    wires.append((x1, y1, x2, y2))

# Find all NC flags
nc_flags = []
nc_pattern = r'\(no_connect\s+\(at\s+([\d.]+)\s+([\d.]+)\)'
for m in re.finditer(nc_pattern, c):
    nc_flags.append((float(m.group(1)), float(m.group(2))))

# Find all global labels
labels = []
label_pattern = r'\(global_label\s+"(\w+)"\s+\(at\s+([\d.]+)\s+([\d.]+)\s+(\d+)\)'
for m in re.finditer(label_pattern, c):
    labels.append((m.group(1), float(m.group(2)), float(m.group(3)), int(m.group(4))))

# Find all power symbols
power = []
pwr_pattern = r'\(lib_id "power:([^"]+)"\)\s+\(at\s+([\d.]+)\s+([\d.]+)\s+(\d+)\)'
for m in re.finditer(pwr_pattern, c):
    power.append((m.group(1), float(m.group(2)), float(m.group(3)), int(m.group(4))))

print(f"Total wires: {len(wires)}")
print(f"Total NC flags: {len(nc_flags)}")
print(f"Total labels: {len(labels)}")
print(f"Total power symbols: {len(power)}")

# Check 1: Do any NC flags coincide with wire points (not endpoints)?
print("\n=== NC flag vs wire crossing check ===")
for nc_x, nc_y in nc_flags:
    for i, (x1, y1, x2, y2) in enumerate(wires):
        # Check if NC flag is on this wire segment
        if x1 == x2:  # vertical wire
            if abs(nc_x - x1) < 0.01 and min(y1, y2) <= nc_y <= max(y1, y2):
                is_endpoint = (abs(nc_y - y1) < 0.01 or abs(nc_y - y2) < 0.01)
                print(f"  NC at ({nc_x},{nc_y}) on wire {i} ({x1},{y1})-({x2},{y2}) {'[ENDPOINT]' if is_endpoint else '[MIDDLE]'}")
        elif y1 == y2:  # horizontal wire
            if abs(nc_y - y1) < 0.01 and min(x1, x2) <= nc_x <= max(x1, x2):
                is_endpoint = (abs(nc_x - x1) < 0.01 or abs(nc_x - x2) < 0.01)
                print(f"  NC at ({nc_x},{nc_y}) on wire {i} ({x1},{y1})-({x2},{y2}) {'[ENDPOINT]' if is_endpoint else '[MIDDLE]'}")

# Check 2: Which pins do row wires connect to?
print("\n=== Row wire analysis ===")
# Switch positions: SW_X = [60.96, 86.36, 111.76, 137.16], SW_Y = [55.88, 81.28, 106.68, 132.08, 157.48]
# Pin 1 renders at (SW_X - 5.08, SW_Y - 1.27)
# Pin 2 renders at (SW_X + 5.08, SW_Y - 1.27)
# Pin 3 renders at (SW_X - 5.08, SW_Y + 3.81)
# Pin 4 renders at (SW_X + 5.08, SW_Y + 3.81)
SW_X = [60.96, 86.36, 111.76, 137.16]
SW_Y = [55.88, 81.28, 106.68, 132.08, 157.48]

for row_idx in range(5):
    sw_y = SW_Y[row_idx]
    pin1_y = sw_y - 1.27
    pin3_y = sw_y + 3.81

    # Find row wires at this Y
    row_wires = [(x1,y1,x2,y2) for x1,y1,x2,y2 in wires if abs(y1 - sw_y) < 0.01 and abs(y2 - sw_y) < 0.01]
    # Find vertical wires connecting Pin1 to row wire
    vert_wires = [(x1,y1,x2,y2) for x1,y1,x2,y2 in wires if x1 == x2 and abs(y1 - pin1_y) < 0.01 and abs(y2 - sw_y) < 0.01]

    print(f"  Row {row_idx} (SW_Y={sw_y}):")
    print(f"    Pin1 Y={pin1_y}, Pin3 Y={pin3_y}")
    print(f"    Row wires at Y={sw_y}: {len(row_wires)}")
    for w in row_wires:
        print(f"      ({w[0]},{w[1]})-({w[2]},{w[3]})")
    print(f"    Vertical wires Pin1->row: {len(vert_wires)}")
    for w in vert_wires:
        print(f"      ({w[0]},{w[1]})-({w[2]},{w[3]})")

# Check 3: Column wire analysis
print("\n=== Column wire analysis ===")
for col_idx in range(4):
    pin2_x = SW_X[col_idx] + 5.08
    pin2_y_first = SW_Y[0] - 1.27  # 54.61
    pin2_y_last = SW_Y[-1] - 1.27  # 156.21
    pin4_y_first = SW_Y[0] + 3.81  # 59.69
    pin4_y_last = SW_Y[-1] + 3.81  # 161.29

    # Find column wires at this X
    col_wires = [(x1,y1,x2,y2) for x1,y1,x2,y2 in wires if abs(x1 - pin2_x) < 0.01 and abs(x2 - pin2_x) < 0.01]

    print(f"  Col {col_idx} (Pin2_X={pin2_x}):")
    print(f"    Pin2 Y range: {pin2_y_first} to {pin2_y_last}")
    print(f"    Pin4 Y range: {pin4_y_first} to {pin4_y_last}")
    print(f"    Column wires at X={pin2_x}: {len(col_wires)}")
    for w in col_wires:
        print(f"      ({w[0]},{w[1]})-({w[2]},{w[3]})")

    # Check if column wire passes through Pin4 positions
    for row_idx in range(5):
        pin4_y = SW_Y[row_idx] + 3.81
        for w in col_wires:
            y_min, y_max = min(w[1], w[3]), max(w[1], w[3])
            if y_min <= pin4_y <= y_max:
                is_endpoint = abs(pin4_y - w[1]) < 0.01 or abs(pin4_y - w[3]) < 0.01
                # Check if NC flag is at this position
                has_nc = any(abs(nc[0] - pin2_x) < 0.01 and abs(nc[1] - pin4_y) < 0.01 for nc in nc_flags)
                print(f"      Passes through Pin4 row {row_idx} at Y={pin4_y} {'[ENDPOINT]' if is_endpoint else '[MIDDLE]'} NC={has_nc}")

# Check 4: Row-column crossing points
print("\n=== Row-column crossing check ===")
for col_idx in range(4):
    pin2_x = SW_X[col_idx] + 5.08
    for row_idx in range(5):
        sw_y = SW_Y[row_idx]
        # Check if any horizontal wire at sw_y crosses any vertical wire at pin2_x
        h_wires = [(x1,y1,x2,y2) for x1,y1,x2,y2 in wires if abs(y1 - sw_y) < 0.01 and abs(y2 - sw_y) < 0.01]
        v_wires = [(x1,y1,x2,y2) for x1,y1,x2,y2 in wires if abs(x1 - pin2_x) < 0.01 and abs(x2 - pin2_x) < 0.01]
        for hw in h_wires:
            for vw in v_wires:
                if min(hw[0], hw[2]) <= pin2_x <= max(hw[0], hw[2]):
                    if min(vw[1], vw[3]) <= sw_y <= max(vw[1], vw[3]):
                        # Check if crossing point is a wire endpoint
                        h_endpoint = abs(pin2_x - hw[0]) < 0.01 or abs(pin2_x - hw[2]) < 0.01
                        v_endpoint = abs(sw_y - vw[1]) < 0.01 or abs(sw_y - vw[3]) < 0.01
                        if not (h_endpoint and v_endpoint):
                            print(f"  Crossing at ({pin2_x},{sw_y}) - row {row_idx} x col {col_idx} - H_end={h_endpoint} V_end={v_endpoint}")
