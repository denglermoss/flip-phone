#!/usr/bin/env python3
"""
Add wiring, labels, power symbols, and no-connect markers to modem.kicad_sch.
The components (U2 MPCIe, U8 TXB0108, C31, C32, R11) are already placed via MCP tools.
This script adds the connections between them.

Power symbol format matches the known-good format in phone.kicad_sch:
- Includes (pin "1" (uuid ...)) block so KiCad recognizes the connection point
- Proper property formatting with hide/show_name/do_not_autoplace fields
"""

import uuid as uuid_module
import os

SCH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phone")
MODEM_FILE = os.path.join(SCH_DIR, "modem.kicad_sch")
SHEET_UUID = "2b7de758-71cc-4198-8a01-5d2c6e01f5f1"
ROOT_UUID = "451c3b43-1616-42cb-bf96-d436f4db82c2"

def gen_uuid():
    return str(uuid_module.uuid4())

# MPCIe socket U2 at (100.33, 100.33), rot=0
# Pin positions verified via sch_get_pin_positions MCP tool.
# Pins 1-52 interleave: odd=bottom(y=110.49), even=top(y=90.17)
# Pin N (1-52): x = 68.58 + ((N-1)//2) * 2.54
# Pins 53,54 are mounting tabs at the edges (NOT following the interleaved formula):
#   Pin 53: (139.70, 100.33)  — right side
#   Pin 54: (60.96, 100.33)   — left side
mpcie_actual_pins = {}
for pin in range(1, 53):
    x_index = (pin - 1) // 2
    x = 68.58 + x_index * 2.54
    y = 110.49 if pin % 2 == 1 else 90.17
    mpcie_actual_pins[pin] = (round(x, 2), round(y, 2))
mpcie_actual_pins[53] = (139.70, 100.33)
mpcie_actual_pins[54] = (60.96, 100.33)

def mpice_pin_pos(pin):
    return mpcie_actual_pins[pin]

# TXB0108 U8 at (180.34, 100.33), rot=0
txb_pins = {
    1: (167.64, 88.90),    # A1
    2: (167.64, 91.44),    # VCCA
    3: (167.64, 93.98),    # A2
    4: (167.64, 96.52),    # A3
    5: (167.64, 99.06),    # A4
    6: (167.64, 101.60),   # A5
    7: (167.64, 104.14),   # A6
    8: (167.64, 106.68),   # A7
    9: (167.64, 109.22),   # A8
    10: (167.64, 111.76),  # OE
    11: (193.04, 111.76),  # GND
    12: (193.04, 109.22),  # B8
    13: (193.04, 106.68),  # B7
    14: (193.04, 104.14),  # B6
    15: (193.04, 101.60),  # B5
    16: (193.04, 99.06),   # B4
    17: (193.04, 96.52),   # B3
    18: (193.04, 93.98),   # B2
    19: (193.04, 91.44),   # VCCB
    20: (193.04, 88.90),   # B1
}

def txb_pin_pos(pin):
    x, y = txb_pins[pin]
    return (round(x, 2), round(y, 2))

# ============================================================
# Extract power symbol lib_symbols from KiCad's power library
# We need: +3.3V, GND, +1V8, PWR_FLAG
# Without these in lib_symbols, KiCad can't resolve pin types
# and PWR_FLAG won't satisfy power_pin_not_driven ERC checks.
# ============================================================
POWER_LIB = r"C:\Users\dengle\AppData\Local\Programs\KiCad\10.0\share\kicad\symbols\power.kicad_sym"
NEEDED_POWER_SYMS = ["+3.3V", "GND", "+1V8"]

def extract_power_symbols():
    with open(POWER_LIB, 'r', encoding='utf-8') as f:
        lib_content = f.read()
    # The power.kicad_sym file wraps symbols in (lib_symbols ... (symbol "name" ...) ...)
    # Each symbol def starts with (symbol "NAME" and ends with the matching )
    extracted = {}
    for sym_name in NEEDED_POWER_SYMS:
        # Find the symbol definition
        pattern = f'\t(symbol "{sym_name}"'
        start = lib_content.find(pattern)
        if start == -1:
            print(f"WARNING: Could not find {sym_name} in power library")
            continue
        # Find the matching closing paren by counting
        depth = 0
        i = start
        while i < len(lib_content):
            if lib_content[i] == '(':
                depth += 1
            elif lib_content[i] == ')':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        # Extract the full symbol definition (including the leading tab)
        sym_def = lib_content[start:i+1]
        # Add the power: prefix to the symbol name
        sym_def_prefixed = sym_def.replace(f'(symbol "{sym_name}"', f'(symbol "power:{sym_name}"')
        extracted[sym_name] = sym_def_prefixed
    return extracted

power_syms = extract_power_symbols()

# Read the current modem.kicad_sch (component-only version from MCP placement)
with open(MODEM_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Insert power symbol definitions inside the existing (lib_symbols ...) block.
# The MCP tool already added component lib_symbols, so we need to find the
# closing paren of lib_symbols and insert before it.
# Strategy: find (lib_symbols, then find its matching closing paren.
lib_sym_start = content.find('(lib_symbols')
if lib_sym_start == -1:
    raise RuntimeError("Could not find (lib_symbols in modem.kicad_sch")

# Find the matching closing paren
depth = 0
i = lib_sym_start
while i < len(content):
    if content[i] == '(':
        depth += 1
    elif content[i] == ')':
        depth -= 1
        if depth == 0:
            break
    i += 1

# Insert power symbol definitions before the closing paren
power_defs_text = '\n' + '\n'.join(power_syms.values()) + '\n'
content = content[:i] + power_defs_text + content[i:]

# Find the insertion point (before sheet_instances)
insert_marker = '\t(sheet_instances'
insert_idx = content.index(insert_marker)

# Build all the new elements
elements = []

def add_wire(x1, y1, x2, y2):
    elements.append(f'\t(wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))\n')

def add_global_label(name, x, y, rot=0, shape="bidirectional"):
    justify = "left" if rot == 0 else "right" if rot == 180 else "bottom" if rot == 90 else "top"
    ref_x = x + 1.27 if rot == 0 else x - 1.27 if rot == 180 else x
    elements.append(
        f'\t(global_label "{name}" (shape {shape}) (at {x} {y} {rot}) (fields_autoplaced yes) '
        f'(effects (font (size 1.27 1.27)) (justify {justify} {justify})) '
        f'(uuid "{gen_uuid()}") '
        f'(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {ref_x} {y} 0) (hide yes) '
        f'(effects (font (size 1.27 1.27)) (justify {justify} {justify}))))\n'
    )

def add_no_connect(x, y):
    elements.append(f'\t(no_connect (at {x} {y}) (uuid "{gen_uuid()}"))\n')

def add_power_symbol(net, x, y, rot, refdes):
    """Power symbol matching the known-good format in phone.kicad_sch.
    The (pin "1" (uuid ...)) block is REQUIRED for KiCad to recognize the connection point."""
    lib_id = f"power:{net}"
    sym_uuid = gen_uuid()
    pin_uuid = gen_uuid()
    # Reference position depends on rotation
    if rot == 0:  # pin points up
        ref_x, ref_y = x, y - 2.54
    elif rot == 180:  # pin points down
        ref_x, ref_y = x, y + 2.54
    elif rot == 90:  # pin points right
        ref_x, ref_y = x + 2.54, y
    elif rot == 270:  # pin points left
        ref_x, ref_y = x - 2.54, y
    else:
        ref_x, ref_y = x, y

    # Value position: opposite side from pin
    if rot == 0:
        val_x, val_y = x, y + 1.27
    elif rot == 180:
        val_x, val_y = x, y - 1.27
    elif rot == 90:
        val_x, val_y = x - 1.27, y
    elif rot == 270:
        val_x, val_y = x + 1.27, y
    else:
        val_x, val_y = x, y

    s = []
    s.append(f'\t(symbol\n')
    s.append(f'\t\t(lib_id "{lib_id}")\n')
    s.append(f'\t\t(at {x} {y} {rot})\n')
    s.append(f'\t\t(unit 1)\n')
    s.append(f'\t\t(exclude_from_sim no)\n')
    s.append(f'\t\t(in_bom yes)\n')
    s.append(f'\t\t(on_board yes)\n')
    s.append(f'\t\t(dnp no)\n')
    s.append(f'\t\t(fields_autoplaced yes)\n')
    s.append(f'\t\t(uuid "{sym_uuid}")\n')
    s.append(f'\t\t(property "Reference" "{refdes}"\n')
    s.append(f'\t\t\t(at {ref_x} {ref_y} 0)\n')
    s.append(f'\t\t\t(hide yes)\n')
    s.append(f'\t\t\t(show_name no)\n')
    s.append(f'\t\t\t(do_not_autoplace no)\n')
    s.append(f'\t\t\t(effects\n')
    s.append(f'\t\t\t\t(font\n')
    s.append(f'\t\t\t\t\t(size 1.27 1.27)\n')
    s.append(f'\t\t\t\t)\n')
    s.append(f'\t\t\t)\n')
    s.append(f'\t\t)\n')
    s.append(f'\t\t(property "Value" "{net}"\n')
    s.append(f'\t\t\t(at {val_x} {val_y} 0)\n')
    s.append(f'\t\t\t(show_name no)\n')
    s.append(f'\t\t\t(do_not_autoplace no)\n')
    s.append(f'\t\t\t(effects\n')
    s.append(f'\t\t\t\t(font\n')
    s.append(f'\t\t\t\t\t(size 1.27 1.27)\n')
    s.append(f'\t\t\t\t)\n')
    s.append(f'\t\t\t)\n')
    s.append(f'\t\t)\n')
    s.append(f'\t\t(property "Footprint" ""\n')
    s.append(f'\t\t\t(at {x} {y} 0)\n')
    s.append(f'\t\t\t(hide yes)\n')
    s.append(f'\t\t\t(show_name no)\n')
    s.append(f'\t\t\t(do_not_autoplace no)\n')
    s.append(f'\t\t\t(effects\n')
    s.append(f'\t\t\t\t(font\n')
    s.append(f'\t\t\t\t\t(size 1.27 1.27)\n')
    s.append(f'\t\t\t\t)\n')
    s.append(f'\t\t\t)\n')
    s.append(f'\t\t)\n')
    s.append(f'\t\t(property "Datasheet" ""\n')
    s.append(f'\t\t\t(at {x} {y} 0)\n')
    s.append(f'\t\t\t(hide yes)\n')
    s.append(f'\t\t\t(show_name no)\n')
    s.append(f'\t\t\t(do_not_autoplace no)\n')
    s.append(f'\t\t\t(effects\n')
    s.append(f'\t\t\t\t(font\n')
    s.append(f'\t\t\t\t\t(size 1.27 1.27)\n')
    s.append(f'\t\t\t\t)\n')
    s.append(f'\t\t\t\t(hide yes)\n')
    s.append(f'\t\t\t)\n')
    s.append(f'\t\t)\n')
    s.append(f'\t\t(pin "1"\n')
    s.append(f'\t\t\t(uuid "{pin_uuid}")\n')
    s.append(f'\t\t)\n')
    s.append(f'\t\t(instances\n')
    s.append(f'\t\t\t(project "phone"\n')
    s.append(f'\t\t\t\t(path "/{ROOT_UUID}/{SHEET_UUID}"\n')
    s.append(f'\t\t\t\t\t(reference "{refdes}")\n')
    s.append(f'\t\t\t\t\t(unit 1)\n')
    s.append(f'\t\t\t\t)\n')
    s.append(f'\t\t\t)\n')
    s.append(f'\t\t)\n')
    s.append(f'\t)\n')
    elements.append(''.join(s))

# ============================================================
# Power pins on MPCIe
# ============================================================
pwr_counter = 100

# VCC pins: 2, 24, 39, 41, 52 -> +3.3V
vcc_pins = [2, 24, 39, 41, 52]
for pin in vcc_pins:
    px, py = mpice_pin_pos(pin)
    if pin % 2 == 0:  # top pin -> power symbol above
        pwr_y = py - 5.08
        pwr_rot = 0  # +3.3V pin points down to connect
    else:  # bottom pin -> power symbol below
        pwr_y = py + 5.08
        pwr_rot = 180
    add_power_symbol("+3.3V", px, pwr_y, pwr_rot, f"#PWR{pwr_counter}")
    add_wire(px, py, px, pwr_y)
    pwr_counter += 1

# GND pins: 4, 9, 15, 18, 21, 26, 27, 29, 34, 35, 37, 40, 43, 50, 53, 54
gnd_pins = [4, 9, 15, 18, 21, 26, 27, 29, 34, 35, 37, 40, 43, 50, 53, 54]
for pin in gnd_pins:
    px, py = mpice_pin_pos(pin)
    # Pins 53,54 are at y=100.33 (middle) — put GND below them
    if pin in (53, 54):
        pwr_y = py + 5.08
        pwr_rot = 180  # GND pin points up to connect
    elif pin % 2 == 0:  # top pin -> GND symbol above
        pwr_y = py - 5.08
        pwr_rot = 0  # GND pin points down to connect
    else:  # bottom pin -> GND symbol below
        pwr_y = py + 5.08
        pwr_rot = 180
    add_power_symbol("GND", px, pwr_y, pwr_rot, f"#PWR{pwr_counter}")
    add_wire(px, py, px, pwr_y)
    pwr_counter += 1

# ============================================================
# UART/Control signals through TXB0108
# ============================================================
# (mpcie_pin, modem_label, txb_a_pin, mcu_label, txb_b_pin, direction)
uart_mapping = [
    (19, "MODEM_TXD", 1, "MCU_UART_RX", 20, "output"),
    (17, "MODEM_RXD", 3, "MCU_UART_TX", 18, "input"),
    (13, "MODEM_RTS", 4, "MCU_UART_CTS", 17, "output"),
    (11, "MODEM_CTS", 5, "MCU_UART_RTS", 16, "input"),
    (44, "MODEM_RI", 6, "MCU_RI_IRQ", 15, "output"),
    (46, "MODEM_DTR", 7, "MCU_DTR", 14, "input"),
    (22, "MODEM_RST", 8, "MCU_MODEM_RST", 13, "input"),
    (1, "MODEM_STATUS", 9, "MCU_MODEM_STATUS", 12, "output"),
]

for mpice_pin, modem_label, txb_a_pin, mcu_label, txb_b_pin, direction in uart_mapping:
    # MPCIe pin -> wire -> global label (modem side)
    mpx, mpy = mpice_pin_pos(mpice_pin)
    if mpice_pin % 2 == 1:  # bottom pin
        label_y = mpy + 5.08
        label_rot = 0  # pointing right
    else:  # top pin
        label_y = mpy - 5.08
        label_rot = 180  # pointing left
    add_wire(mpx, mpy, mpx, label_y)
    add_global_label(modem_label, mpx, label_y, label_rot,
                     shape="output" if direction == "output" else "input")

    # TXB0108 A-side -> global label (modem side)
    ax, ay = txb_pin_pos(txb_a_pin)
    add_wire(ax, ay, ax - 5.08, ay)
    add_global_label(modem_label, ax - 5.08, ay, 180,
                     shape="input" if direction == "output" else "output")

    # TXB0108 B-side -> global label (MCU side)
    bx, by = txb_pin_pos(txb_b_pin)
    add_wire(bx, by, bx + 5.08, by)
    add_global_label(mcu_label, bx + 5.08, by, 0,
                     shape="output" if direction == "input" else "input")

# ============================================================
# TXB0108 power
# ============================================================
# VCCA (pin 2) -> +1V8
vx, vy = txb_pin_pos(2)
add_power_symbol("+1V8", vx - 7.62, vy, 90, f"#PWR{pwr_counter}")
add_wire(vx, vy, vx - 7.62, vy)
pwr_counter += 1

# VCCB (pin 19) -> +3.3V
vx, vy = txb_pin_pos(19)
add_power_symbol("+3.3V", vx + 7.62, vy, 270, f"#PWR{pwr_counter}")
add_wire(vx, vy, vx + 7.62, vy)
pwr_counter += 1

# GND (pin 11) -> GND
gx, gy = txb_pin_pos(11)
add_power_symbol("GND", gx + 7.62, gy, 270, f"#PWR{pwr_counter}")
add_wire(gx, gy, gx + 7.62, gy)
pwr_counter += 1

# NOTE: No PWR_FLAGs needed — +3.3V, +1V8, and GND are all driven by
# regulators on the root sheet (U4 VOUT for +3.3V, U5 OUT for +1V8).
# Adding PWR_FLAGs here would cause "Power output + Power output" conflicts.

# OE (pin 10) -> wire to global label TXB_OE (MCU controls enable)
# R11 is the pullup: Pin 1 (160.02, 85.09) -> +3.3V, Pin 2 (170.18, 85.09) -> TXB_OE
oe_x, oe_y = txb_pin_pos(10)
add_wire(oe_x, oe_y, oe_x - 5.08, oe_y)
add_global_label("TXB_OE", oe_x - 5.08, oe_y, 180, shape="input")

# R11 wiring (horizontal pins at ±5.08 from center 165.1, 85.09)
# Pin 1 at (160.02, 85.09) -> +3.3V (left)
# Pin 2 at (170.18, 85.09) -> TXB_OE label (right)
r11_p1_x, r11_p1_y = 160.02, 85.09
r11_p2_x, r11_p2_y = 170.18, 85.09
add_power_symbol("+3.3V", r11_p1_x - 5.08, r11_p1_y, 270, f"#PWR{pwr_counter}")
add_wire(r11_p1_x, r11_p1_y, r11_p1_x - 5.08, r11_p1_y)
pwr_counter += 1
add_wire(r11_p2_x, r11_p2_y, r11_p2_x + 5.08, r11_p2_y)
add_global_label("TXB_OE", r11_p2_x + 5.08, r11_p2_y, 0, shape="input")

# ============================================================
# PCM/I2S signals (direct to codec, no level shifter)
# ============================================================
pcm_mapping = [
    (45, "PCM_CLK"),
    (47, "PCM_OUT"),
    (49, "PCM_IN"),
    (51, "PCM_SYNC"),
]
for pin, label in pcm_mapping:
    px, py = mpice_pin_pos(pin)
    if pin % 2 == 1:  # bottom pin
        label_y = py + 5.08
        label_rot = 0
    else:
        label_y = py - 5.08
        label_rot = 180
    add_wire(px, py, px, label_y)
    add_global_label(label, px, label_y, label_rot, shape="bidirectional")

# ============================================================
# USB signals
# ============================================================
usb_mapping = [
    (38, "MODEM_USB_DP"),
    (36, "MODEM_USB_DN"),
]
for pin, label in usb_mapping:
    px, py = mpice_pin_pos(pin)
    if pin % 2 == 1:
        label_y = py + 5.08
        label_rot = 0
    else:
        label_y = py - 5.08
        label_rot = 180
    add_wire(px, py, px, label_y)
    add_global_label(label, px, label_y, label_rot, shape="bidirectional")

# ============================================================
# SIM signals
# ============================================================
sim_mapping = [
    (8, "USIM_VDD"),
    (10, "USIM_DATA"),
    (12, "USIM_CLK"),
    (14, "USIM_RST"),
    (16, "USIM_DET"),
]
for pin, label in sim_mapping:
    px, py = mpice_pin_pos(pin)
    if pin % 2 == 1:
        label_y = py + 5.08
        label_rot = 0
    else:
        label_y = py - 5.08
        label_rot = 180
    add_wire(px, py, px, label_y)
    add_global_label(label, px, label_y, label_rot, shape="bidirectional")

# ============================================================
# NET_STATUS (pin 42)
# ============================================================
px, py = mpice_pin_pos(42)
add_wire(px, py, px, py - 5.08)
add_global_label("NET_STATUS", px, py - 5.08, 180, shape="output")

# ============================================================
# No-connect pins
# ============================================================
nc_pins = [3, 5, 6, 7, 20, 23, 25, 28, 30, 31, 32, 33, 48]
for pin in nc_pins:
    px, py = mpice_pin_pos(pin)
    add_no_connect(px, py)

# ============================================================
# Bulk caps wiring (C31, C32)
# Caps have HORIZONTAL pins at ±5.08 from center:
# C31 at (139.70, 124.46): Pin 1 at (134.62, 124.46), Pin 2 at (144.78, 124.46)
# C32 at (149.86, 124.46): Pin 1 at (144.78, 124.46), Pin 2 at (154.94, 124.46)
# C31 Pin 2 and C32 Pin 1 share position (144.78, 124.46) = shared GND node
# Wiring: C31 Pin 1 -> +3.3V (left), shared node -> GND (down), C32 Pin 2 -> +3.3V (right)
# ============================================================
# C31 Pin 1 (134.62, 124.46) -> wire left to +3.3V
add_power_symbol("+3.3V", 129.54, 124.46, 270, f"#PWR{pwr_counter}")
add_wire(134.62, 124.46, 129.54, 124.46)
pwr_counter += 1

# C31 Pin 2 / C32 Pin 1 (144.78, 124.46) -> wire down to GND
add_power_symbol("GND", 144.78, 129.54, 180, f"#PWR{pwr_counter}")
add_wire(144.78, 124.46, 144.78, 129.54)
pwr_counter += 1

# C32 Pin 2 (154.94, 124.46) -> wire right to +3.3V
add_power_symbol("+3.3V", 160.02, 124.46, 90, f"#PWR{pwr_counter}")
add_wire(154.94, 124.46, 160.02, 124.46)
pwr_counter += 1

# ============================================================
# Insert all elements before sheet_instances
# ============================================================
new_content = content[:insert_idx] + ''.join(elements) + content[insert_idx:]

with open(MODEM_FILE, 'w', encoding='utf-8', newline='\n') as f:
    f.write(new_content)

print(f"Added {len(elements)} elements to modem.kicad_sch")
print(f"File size: {len(new_content)} bytes")
