#!/usr/bin/env python3
"""Generate keypad.kicad_sch - 5x4 keypad matrix with 20 tactile switches,
5 row pull-up resistors, and 4 column pull-down resistors."""

import uuid

KEYPAD_SHEET_UUID = "a554b0c9-2abf-4ff9-b53b-f19190990074"
ROOT_UUID = "451c3b43-1616-42cb-bf96-d436f4db82c2"
SHEET_PATH = f"/{ROOT_UUID}/{KEYPAD_SHEET_UUID}"

def new_uuid():
    return str(uuid.uuid4())

# Layout constants
COL_X = [60, 85, 110, 135]
ROW_Y = [55, 80, 105, 130, 155]
PIN1_DX, PIN1_DY = -5.08, 1.27
PIN2_DX, PIN2_DY = 5.08, -1.27
PIN3_DX, PIN3_DY = -5.08, 3.81
PIN4_DX, PIN4_DY = 5.08, 3.81
ROW_BUS_Y = [y - 1.27 for y in ROW_Y]
COL_BUS_X = [x - 5.08 for x in COL_X]
ROW_LABEL_X = 25
COL_LABEL_Y = 40
PULLUP_X = 160
# Pin 3 bottom Y for row 4: ROW_Y[4] + 3.81 = 158.81
# Pull-down resistor center: pin2 at 158.81, so center at 158.81 + 5.08 = 163.89
PULLDOWN_Y = 163.89

def fmt_wire(x1, y1, x2, y2):
    return f'\t(wire\n\t\t(pts\n\t\t\t(xy {x1} {y1}) (xy {x2} {y2})\n\t\t)\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid "{new_uuid()}")\n\t)'

def fmt_junction(x, y):
    return f'\t(junction\n\t\t(at {x} {y})\n\t\t(diameter 0)\n\t\t(color 0 0 0 0)\n\t\t(uuid "{new_uuid()}")\n\t)'

def fmt_global_label(name, x, y, direction):
    justify = "right" if direction == 180 else "left"
    return f'\t(global_label "{name}"\n\t\t(shape bidirectional)\n\t\t(at {x} {y} {direction})\n\t\t(fields_autoplaced yes)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {justify})\n\t\t)\n\t\t(uuid "{new_uuid()}")\n\t\t(property "Intersheetrefs" "${{INTERSHEET_REFS}}"\n\t\t\t(at {x} {y} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)'

def fmt_switch(ref, cx, cy):
    u = new_uuid()
    return f'\t(symbol\n\t\t(lib_id "electromech:SKQGABE010")\n\t\t(at {cx} {cy} 0)\n\t\t(unit 1)\n\t\t(body_style 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(in_pos_files yes)\n\t\t(dnp no)\n\t\t(fields_autoplaced yes)\n\t\t(uuid "{u}")\n\t\t(property "Reference" "{ref}"\n\t\t\t(at {cx} {cy-7.62} 0)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "Value" "SKQGABE010"\n\t\t\t(at {cx} {cy+8.89} 0)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "Footprint" "easyeda2kicad:KEY-SMD_4P-L5.2-W5.2-P3.70-LS6.4"\n\t\t\t(at {cx} {cy+11.43} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "Datasheet" "https://lcsc.com/product-detail/Tactile-Switches_ALPS_SKQGABE010_5-2-5-2-1-5-1-57N_C115351.html"\n\t\t\t(at {cx} {cy+13.97} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "Description" "Tactile switch 5.2mm SMD"\n\t\t\t(at {cx} {cy} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "Manufacturer" "ALPSALPINE"\n\t\t\t(at {cx} {cy+16.51} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "MPN" "SKQGABE010"\n\t\t\t(at {cx} {cy+19.05} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "LCSC Part" "C115351"\n\t\t\t(at {cx} {cy+21.59} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(pin "1"\n\t\t\t(uuid "{new_uuid()}")\n\t\t)\n\t\t(pin "2"\n\t\t\t(uuid "{new_uuid()}")\n\t\t)\n\t\t(pin "3"\n\t\t\t(uuid "{new_uuid()}")\n\t\t)\n\t\t(pin "4"\n\t\t\t(uuid "{new_uuid()}")\n\t\t)\n\t\t(instances\n\t\t\t(project "phone"\n\t\t\t\t(path "{SHEET_PATH}"\n\t\t\t\t\t(reference "{ref}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)'

def fmt_resistor(ref, x, y, rotation, value):
    return f'\t(symbol\n\t\t(lib_id "passives:RC0603JR-0710KL")\n\t\t(at {x} {y} {rotation})\n\t\t(unit 1)\n\t\t(body_style 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(in_pos_files yes)\n\t\t(dnp no)\n\t\t(fields_autoplaced yes)\n\t\t(uuid "{new_uuid()}")\n\t\t(property "Reference" "{ref}"\n\t\t\t(at {x+2.54} {y} 0)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "Value" "{value}"\n\t\t\t(at {x+2.54} {y+2.54} 0)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "Footprint" ""\n\t\t\t(at {x} {y} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "Datasheet" "~"\n\t\t\t(at {x} {y} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "Description" "10k 5% 0603 resistor"\n\t\t\t(at {x} {y} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(pin "1"\n\t\t\t(uuid "{new_uuid()}")\n\t\t)\n\t\t(pin "2"\n\t\t\t(uuid "{new_uuid()}")\n\t\t)\n\t\t(instances\n\t\t\t(project "phone"\n\t\t\t\t(path "{SHEET_PATH}"\n\t\t\t\t\t(reference "{ref}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)'

def fmt_gnd(x, y, pwr_num):
    return f'\t(symbol\n\t\t(lib_id "power:GND")\n\t\t(at {x} {y} 0)\n\t\t(unit 1)\n\t\t(body_style 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(in_pos_files yes)\n\t\t(dnp no)\n\t\t(fields_autoplaced yes)\n\t\t(uuid "{new_uuid()}")\n\t\t(property "Reference" "#PWR{pwr_num}"\n\t\t\t(at {x} {y-2.54} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "Value" "GND"\n\t\t\t(at {x} {y+2.54} 0)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "Footprint" ""\n\t\t\t(at {x} {y} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "Datasheet" "~"\n\t\t\t(at {x} {y} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "Description" ""\n\t\t\t(at {x} {y} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(pin "1"\n\t\t\t(uuid "{new_uuid()}")\n\t\t)\n\t\t(instances\n\t\t\t(project "phone"\n\t\t\t\t(path "{SHEET_PATH}"\n\t\t\t\t\t(reference "#PWR{pwr_num}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)'

def fmt_3v3(x, y, pwr_num):
    return f'\t(symbol\n\t\t(lib_id "power:+3.3V")\n\t\t(at {x} {y} 0)\n\t\t(unit 1)\n\t\t(body_style 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(in_pos_files yes)\n\t\t(dnp no)\n\t\t(fields_autoplaced yes)\n\t\t(uuid "{new_uuid()}")\n\t\t(property "Reference" "#PWR{pwr_num}"\n\t\t\t(at {x} {y-2.54} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "Value" "+3.3V"\n\t\t\t(at {x} {y-5.08} 0)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "Footprint" ""\n\t\t\t(at {x} {y} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "Datasheet" "~"\n\t\t\t(at {x} {y} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(property "Description" ""\n\t\t\t(at {x} {y} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t\t(pin "1"\n\t\t\t(uuid "{new_uuid()}")\n\t\t)\n\t\t(instances\n\t\t\t(project "phone"\n\t\t\t\t(path "{SHEET_PATH}"\n\t\t\t\t\t(reference "#PWR{pwr_num}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)'

# Read lib_symbols from a template file
LIB_SYMBOLS = open("lib_symbols_template.txt", "r").read()

# Generate content
parts = []
wires = []
junctions = []
labels = []

# Switches SW1-SW20
sw = 1
for row in range(5):
    for col in range(4):
        parts.append(fmt_switch(f"SW{sw}", COL_X[col], ROW_Y[row]))
        sw += 1

# Pull-up resistors R16-R20 and +3.3V symbols
pwr = 501
for row in range(5):
    by = ROW_BUS_Y[row]
    rcy = by - 5.08
    parts.append(fmt_resistor(f"R{16+row}", PULLUP_X, rcy, 90, "10k"))
    parts.append(fmt_3v3(PULLUP_X, rcy - 5.08, pwr))
    pwr += 1

# Pull-down resistors R21-R24 and GND symbols
for col in range(4):
    bx = COL_BUS_X[col]
    parts.append(fmt_resistor(f"R{21+col}", bx, PULLDOWN_Y, 90, "10k"))
    parts.append(fmt_gnd(bx, PULLDOWN_Y + 5.08, pwr))
    pwr += 1

# Row bus wires
for row in range(5):
    by = ROW_BUS_Y[row]
    wires.append(fmt_wire(ROW_LABEL_X, by, PULLUP_X, by))

# Column bus wires
for col in range(4):
    bx = COL_BUS_X[col]
    wires.append(fmt_wire(bx, COL_LABEL_Y, bx, PULLDOWN_Y - 5.08))

# Pin 3 to pin 4 wires
sw = 1
for row in range(5):
    for col in range(4):
        cx, cy = COL_X[col], ROW_Y[row]
        wires.append(fmt_wire(cx+PIN3_DX, cy+PIN3_DY, cx+PIN4_DX, cy+PIN4_DY))
        sw += 1

# Junctions at pin positions on bus wires
sw = 1
for row in range(5):
    for col in range(4):
        cx, cy = COL_X[col], ROW_Y[row]
        junctions.append(fmt_junction(cx+PIN1_DX, cy+PIN1_DY))
        junctions.append(fmt_junction(cx+PIN2_DX, cy+PIN2_DY))
        junctions.append(fmt_junction(cx+PIN3_DX, cy+PIN3_DY))
        sw += 1

# Global labels
for row in range(5):
    labels.append(fmt_global_label(f"KEY_ROW{row}", ROW_LABEL_X, ROW_BUS_Y[row], 180))
for col in range(4):
    labels.append(fmt_global_label(f"KEY_COL{col}", COL_BUS_X[col], COL_LABEL_Y, 90))

# Assemble
header = f'(kicad_sch\n\t(version 20260306)\n\t(generator "eeschema")\n\t(generator_version "10.0")\n\t(uuid "{KEYPAD_SHEET_UUID}")\n\t(paper "A3")\n\t(title_block\n\t\t(title "Keypad")\n\t)\n'
footer = '\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)\n'

content = header + LIB_SYMBOLS + "\n"
content += "\n".join(junctions) + "\n"
content += "\n".join(wires) + "\n"
content += "\n".join(labels) + "\n"
content += "\n".join(parts) + "\n"
content += footer

with open("keypad.kicad_sch", "w", newline="\n") as f:
    f.write(content)

print(f"Generated keypad.kicad_sch ({len(content)} bytes)")
print(f"  Switches: 20, Pull-ups: 5, Pull-downs: 4, Labels: 9")
print(f"  Wires: {len(wires)}, Junctions: {len(junctions)}")
