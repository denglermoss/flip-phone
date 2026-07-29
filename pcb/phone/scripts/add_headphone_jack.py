#!/usr/bin/env python3
"""Add headphone jack (54-00298) to codec.kicad_sch -- targeted edit v2."""
import uuid as uuid_module
import os

SCH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CODEC_FILE = os.path.join(SCH_DIR, "codec.kicad_sch")
ROOT_UUID = "451c3b43-1616-42cb-bf96-d436f4db82c2"
CODEC_SHEET_UUID = "1c9f5800-c30c-48b4-b4f4-4248c9c52b8c"
SHEET_PATH = f"/{ROOT_UUID}/{CODEC_SHEET_UUID}"

def gen_uuid():
    return str(uuid_module.uuid4())

# Read the codec schematic
with open(CODEC_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Original file: {len(content)} chars, {len(content.splitlines())} lines")

# --- Step 1: Remove the 4 blocks ---

# 1a. Remove wire from HPO_R to GND
wire_hpo_r = '\t(wire\n\t\t(pts\n\t\t\t(xy 166.37 154.94) (xy 173.99 154.94)\n\t\t)\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid "1c7a2a09-c876-4928-9d11-2c3f89ae9288")\n\t)\n'
if wire_hpo_r in content:
    content = content.replace(wire_hpo_r, '')
    print("Removed wire HPO_R -> GND")
else:
    print("WARNING: wire HPO_R -> GND not found!")

# 1b. Remove wire from HPO_L to +1V8
wire_hpo_l = '\t(wire\n\t\t(pts\n\t\t\t(xy 166.37 149.86) (xy 173.99 149.86)\n\t\t)\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid "f94acddd-425e-4568-9035-0e0ff0139c70")\n\t)\n'
if wire_hpo_l in content:
    content = content.replace(wire_hpo_l, '')
    print("Removed wire HPO_L -> +1V8")
else:
    print("WARNING: wire HPO_L -> +1V8 not found!")

# 1c. Remove GND power symbol #PWR0111
pwr111_uuid = "0dcd2128-f582-4180-8a6d-10cd3ce7b972"
pos = content.find(f'uuid "{pwr111_uuid}"')
if pos != -1:
    sym_start = content.rfind('\t(symbol\n', 0, pos)
    open_pos = content.index('(symbol', sym_start)
    depth = 0
    i = open_pos
    while i < len(content):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                break
        i += 1
    end = i + 1
    while end < len(content) and content[end] == '\n':
        end += 1
    content = content[:sym_start] + content[end:]
    print("Removed GND power symbol #PWR0111")
else:
    print("WARNING: GND power symbol #PWR0111 not found!")

# 1d. Remove +1V8 power symbol #PWR0107
pwr107_uuid = "c06f4259-4ac3-420a-a110-9cb1bd3390f4"
pos = content.find(f'uuid "{pwr107_uuid}"')
if pos != -1:
    sym_start = content.rfind('\t(symbol\n', 0, pos)
    open_pos = content.index('(symbol', sym_start)
    depth = 0
    i = open_pos
    while i < len(content):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                break
        i += 1
    end = i + 1
    while end < len(content) and content[end] == '\n':
        end += 1
    content = content[:sym_start] + content[end:]
    print("Removed +1V8 power symbol #PWR0107")
else:
    print("WARNING: +1V8 power symbol #PWR0107 not found!")

# --- Step 2: Add 54-00298 to lib_symbols section ---
# Write a clean lib_symbol entry matching the format of other entries

jack_lib_symbol = """\t\t(symbol "connectors:54-00298"
\t\t\t(exclude_from_sim no)
\t\t\t(in_bom yes)
\t\t\t(on_board yes)
\t\t\t(in_pos_files yes)
\t\t\t(duplicate_pin_numbers_are_jumpers no)
\t\t\t(property "Reference" "J"
\t\t\t\t(at 0 7.62 0)
\t\t\t\t(show_name no)
\t\t\t\t(do_not_autoplace no)
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(property "Value" "54-00298"
\t\t\t\t(at 0 -7.62 0)
\t\t\t\t(show_name no)
\t\t\t\t(do_not_autoplace no)
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(property "Footprint" "tensility:TENSILITY_54-00298"
\t\t\t\t(at 0 -10.16 0)
\t\t\t\t(show_name no)
\t\t\t\t(do_not_autoplace no)
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t\t(hide yes)
\t\t\t\t)
\t\t\t)
\t\t\t(property "Datasheet" "~"
\t\t\t\t(at 0 0 0)
\t\t\t\t(show_name no)
\t\t\t\t(do_not_autoplace no)
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t\t(hide yes)
\t\t\t\t)
\t\t\t)
\t\t\t(property "Manufacturer" "Tensility"
\t\t\t\t(at 0 0 0)
\t\t\t\t(show_name no)
\t\t\t\t(do_not_autoplace no)
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t\t(hide yes)
\t\t\t\t)
\t\t\t)
\t\t\t(property "MPN" "54-00298"
\t\t\t\t(at 0 0 0)
\t\t\t\t(show_name no)
\t\t\t\t(do_not_autoplace no)
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t\t(hide yes)
\t\t\t\t)
\t\t\t)
\t\t\t(symbol "connectors:54-00298_0_1"
\t\t\t\t(pin passive line
\t\t\t\t\t(at 5.08 7.62 180)
\t\t\t\t\t(length 5.08)
\t\t\t\t\t(name "1" (effects (font (size 1.27 1.27))))
\t\t\t\t\t(number "1" (effects (font (size 1.27 1.27))))
\t\t\t\t)
\t\t\t\t(pin passive line
\t\t\t\t\t(at 5.08 -2.54 180)
\t\t\t\t\t(length 5.08)
\t\t\t\t\t(name "2" (effects (font (size 1.27 1.27))))
\t\t\t\t\t(number "2" (effects (font (size 1.27 1.27))))
\t\t\t\t)
\t\t\t\t(pin passive line
\t\t\t\t\t(at 5.08 5.08 180)
\t\t\t\t\t(length 5.08)
\t\t\t\t\t(name "3" (effects (font (size 1.27 1.27))))
\t\t\t\t\t(number "3" (effects (font (size 1.27 1.27))))
\t\t\t\t)
\t\t\t\t(pin passive line
\t\t\t\t\t(at 5.08 -5.08 180)
\t\t\t\t\t(length 5.08)
\t\t\t\t\t(name "4" (effects (font (size 1.27 1.27))))
\t\t\t\t\t(number "4" (effects (font (size 1.27 1.27))))
\t\t\t\t)
\t\t\t\t(pin passive line
\t\t\t\t\t(at 5.08 0 180)
\t\t\t\t\t(length 5.08)
\t\t\t\t\t(name "5" (effects (font (size 1.27 1.27))))
\t\t\t\t\t(number "5" (effects (font (size 1.27 1.27))))
\t\t\t\t)
\t\t\t\t(pin passive line
\t\t\t\t\t(at 5.08 2.54 180)
\t\t\t\t\t(length 5.08)
\t\t\t\t\t(name "6" (effects (font (size 1.27 1.27))))
\t\t\t\t\t(number "6" (effects (font (size 1.27 1.27))))
\t\t\t\t)
\t\t\t)
\t\t)
"""

# Find the end of lib_symbols section by paren matching
ls_start = content.find('\t(lib_symbols\n')
if ls_start == -1:
    raise RuntimeError("Could not find lib_symbols section")
open_pos = content.index('(lib_symbols', ls_start)
depth = 0
i = open_pos
while i < len(content):
    if content[i] == '(':
        depth += 1
    elif content[i] == ')':
        depth -= 1
        if depth == 0:
            break
    i += 1
ls_end = i  # position of the closing ')' of lib_symbols
# The ')' is preceded by '\t' — insert before '\t)' to keep it intact
if content[ls_end - 1] == '\t':
    ls_end = ls_end - 1
content = content[:ls_end] + '\n' + jack_lib_symbol + content[ls_end:]
print("Added 54-00298 to lib_symbols section")

# --- Step 3: Add new components, wires, labels ---
elements = []

def aw(x1, y1, x2, y2):
    elements.append(f'\t(wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))\n')

def aj(x, y):
    elements.append(f'\t(junction (at {x} {y}) (diameter 0) (color 0 0 0 0) (uuid "{gen_uuid()}"))\n')

def anc(x, y):
    elements.append(f'\t(no_connect (at {x} {y}) (uuid "{gen_uuid()}"))\n')

def agl(name, x, y, rot=0, shape="bidirectional"):
    j = "left" if rot == 0 else "right" if rot == 180 else "bottom" if rot == 90 else "top"
    rx = x + 1.27 if rot == 0 else x - 1.27 if rot == 180 else x
    elements.append(f'\t(global_label "{name}" (shape {shape}) (at {x} {y} {rot}) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify {j} {j})) (uuid "{gen_uuid()}") (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {rx} {y} 0) (hide yes) (effects (font (size 1.27 1.27)) (justify {j} {j}))))\n')

pwr_ctr = 500

def apw(net, x, y, rot, ref):
    global pwr_ctr
    su = gen_uuid()
    pu = gen_uuid()
    if rot == 0:
        rx, ry, vx, vy = x, y - 2.54, x, y + 1.27
    elif rot == 180:
        rx, ry, vx, vy = x, y + 2.54, x, y - 1.27
    elif rot == 90:
        rx, ry, vx, vy = x + 2.54, y, x - 1.27, y
    else:
        rx, ry, vx, vy = x - 2.54, y, x + 1.27, y
    s = f'\t(symbol\n\t\t(lib_id "power:{net}")\n\t\t(at {x} {y} {rot})\n\t\t(unit 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(fields_autoplaced yes)\n\t\t(uuid "{su}")\n'
    s += f'\t\t(property "Reference" "{ref}"\n\t\t\t(at {rx} {ry} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n'
    s += f'\t\t(property "Value" "{net}"\n\t\t\t(at {vx} {vy} 0)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n'
    s += f'\t\t(property "Footprint" ""\n\t\t\t(at {x} {y} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n'
    s += f'\t\t(property "Datasheet" ""\n\t\t\t(at {x} {y} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n\t\t)\n'
    s += f'\t\t(pin "1"\n\t\t\t(uuid "{pu}")\n\t\t)\n'
    s += f'\t\t(instances\n\t\t\t(project "phone"\n\t\t\t\t(path "{SHEET_PATH}"\n\t\t\t\t\t(reference "{ref}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n'
    elements.append(s)
    pwr_ctr += 1

def ac(lib_id, ref, val, cx, cy, rot=0):
    su = gen_uuid()
    ry = cy - 5.0 if rot == 0 else cy + 5.0
    vy = cy + 5.0 if rot == 0 else cy - 5.0
    s = f'\t(symbol\n\t\t(lib_id "{lib_id}")\n\t\t(at {cx} {cy} {rot})\n\t\t(unit 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid "{su}")\n'
    s += f'\t\t(property "Reference" "{ref}"\n\t\t\t(at {cx} {ry} 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n'
    s += f'\t\t(property "Value" "{val}"\n\t\t\t(at {cx} {vy} 0)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n'
    s += f'\t\t(property "Footprint" ""\n\t\t\t(at {cx} {cy} 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n'
    s += f'\t\t(property "Datasheet" "~"\n\t\t\t(at {cx} {cy} 0)\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t)\n'
    s += f'\t\t(instances\n\t\t\t(project "phone"\n\t\t\t\t(path "{SHEET_PATH}"\n\t\t\t\t\t(reference "{ref}") (unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n'
    elements.append(s)

# Component positions
C_HPL_X, C_HPL_Y = 180.0, 147.32
C_HPR_X, C_HPR_Y = 180.0, 157.48
JACK_X, JACK_Y = 200.0, 152.4
R_HPDET_X, R_HPDET_Y = 190.0, 165.0

# Pin positions
c_hpl_p1 = (C_HPL_X - 5.08, C_HPL_Y)
c_hpl_p2 = (C_HPL_X + 5.08, C_HPL_Y)
c_hpr_p1 = (C_HPR_X - 5.08, C_HPR_Y)
c_hpr_p2 = (C_HPR_X + 5.08, C_HPR_Y)

jack_p1 = (JACK_X + 5.08, JACK_Y + 7.62)   # Sleeve
jack_p2 = (JACK_X + 5.08, JACK_Y - 2.54)   # Ring2
jack_p3 = (JACK_X + 5.08, JACK_Y + 5.08)   # Ring1
jack_p4 = (JACK_X + 5.08, JACK_Y - 5.08)   # Tip
jack_p5 = (JACK_X + 5.08, JACK_Y)          # Switch NC to 4
jack_p6 = (JACK_X + 5.08, JACK_Y + 2.54)   # Switch NC to 3

r_hpdet_p1 = (R_HPDET_X, R_HPDET_Y - 5.08)
r_hpdet_p2 = (R_HPDET_X, R_HPDET_Y + 5.08)

# Place components
ac("passives:GRM21BR61H106KE43L", "C_HPL", "10uF", C_HPL_X, C_HPL_Y)
ac("passives:GRM21BR61H106KE43L", "C_HPR", "10uF", C_HPR_X, C_HPR_Y)
ac("passives:RC0603JR-0710KL", "R_HPDET", "10k", R_HPDET_X, R_HPDET_Y, 90)
ac("connectors:54-00298", "J_PHONES", "54-00298", JACK_X, JACK_Y)

# Wires: HPO_L -> C_HPL -> Tip
aw(166.37, 149.86, 166.37, 147.32)
aw(166.37, 147.32, c_hpl_p1[0], c_hpl_p1[1])
aw(c_hpl_p2[0], c_hpl_p2[1], jack_p4[0], jack_p4[1])

# Wires: HPO_R -> C_HPR -> Ring1
aw(166.37, 154.94, 166.37, 157.48)
aw(166.37, 157.48, c_hpr_p1[0], c_hpr_p1[1])
aw(c_hpr_p2[0], c_hpr_p2[1], jack_p3[0], jack_p3[1])

# Wire: Tip -> R_HPDET pin1 (branch off the C_HPL->Tip wire at x=190)
aw(190.0, 147.32, 190.0, r_hpdet_p1[1])
aj(190.0, 147.32)

# Wire: R_HPDET pin2 -> GND
aw(r_hpdet_p2[0], r_hpdet_p2[1], R_HPDET_X, 172.72)
apw("GND", R_HPDET_X, 172.72, 0, f"#PWR0{pwr_ctr}")

# Wire: Pin 1 (Sleeve) -> GND
aw(jack_p1[0], jack_p1[1], 210.0, 160.02)
apw("GND", 210.0, 160.02, 180, f"#PWR0{pwr_ctr}")

# Wire: Pin 2 (Ring2) -> GND
aw(jack_p2[0], jack_p2[1], 210.0, 149.86)
apw("GND", 210.0, 149.86, 180, f"#PWR0{pwr_ctr}")

# Wire: Pin 5 (Switch) -> HP_DET global label
aw(jack_p5[0], jack_p5[1], 215.0, 152.4)
agl("HP_DET", 215.0, 152.4, 0, "input")

# No-connect on Pin 6
anc(jack_p6[0], jack_p6[1])

# Insert elements before the sheet_instances section
elements_text = ''.join(elements)
si_pos = content.find('\t(sheet_instances\n')
if si_pos == -1:
    raise RuntimeError("Could not find sheet_instances section")
content = content[:si_pos] + elements_text + content[si_pos:]

# Write the file
with open(CODEC_FILE, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print(f"Modified file: {len(content)} chars, {len(content.splitlines())} lines")
print(f"Added {len(elements)} elements")
print("Done!")
