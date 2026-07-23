#!/usr/bin/env python3
"""
Generate hierarchical schematic sheets for the phone project:
- modem.kicad_sch: MPCIe socket + TXB0108 level shifter
- codec.kicad_sch: ALC5651 codec + SN74AXC4T774 I2S-2 shifter + transducers
- display.kicad_sch: Display connectors + hinge flex + backlight PWM
- sim_sd.kicad_sch: SIM socket + microSD socket + ESD
- keypad.kicad_sch: 5x4 keypad matrix

Each sheet gets its own UUID. Global labels connect across sheets.
The root phone.kicad_sch gets sheet boxes for each child sheet.
"""

import re
import uuid as uuid_module
import os
import sys

SCH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phone")
LIB_DIR = os.path.join(SCH_DIR, "lib")
ROOT_UUID = "451c3b43-1616-42cb-bf96-d436f4db82c2"

# ============================================================
# Helper functions
# ============================================================

def read_text(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def write_text(filename, text):
    with open(filename, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)

def gen_uuid():
    return str(uuid_module.uuid4())

def extract_lib_symbol(filename, sym_name):
    """Extract a complete lib_symbol block from a .kicad_sym file."""
    text = read_text(filename)
    # Find the symbol definition (not the _0_1 sub-symbol)
    pattern = r'(\(symbol "' + re.escape(sym_name) + r'"\s*\n.*?(?=\n  \(symbol "|\n\)))'
    m = re.search(pattern, text, re.DOTALL)
    if m:
        return m.group(1)
    # Try a different approach - find by line
    lines = text.split('\n')
    start = None
    for i, line in enumerate(lines):
        if line.strip() == f'(symbol "{sym_name}"':
            start = i
            break
    if start is None:
        return None
    # Find matching close paren
    depth = 0
    for i in range(start, len(lines)):
        in_str = False
        for ch in lines[i]:
            if ch == '"':
                in_str = not in_str
            elif not in_str:
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                    if depth == 0:
                        return '\n'.join(lines[start:i+1])
    return None

def normalize_indent(text, target_indent='  '):
    """Normalize indentation so the first (symbol line is at 2-space indent."""
    lines = text.split('\n')
    if not lines:
        return text
    # Count leading spaces/tabs on first line
    first = lines[0]
    current_indent = len(first) - len(first.lstrip())
    target_len = len(target_indent)
    if current_indent == target_len:
        return text
    delta = current_indent - target_len
    result = []
    for line in lines:
        if delta > 0 and len(line) >= delta:
            result.append(line[delta:])
        elif delta < 0:
            result.append(' ' * (-delta) + line)
        else:
            result.append(line)
    return '\n'.join(result)

# ============================================================
# Schematic element generators
# ============================================================

def make_symbol_instance(lib_id, x, y, rot, refdes, value, unit=1, sheet_path="/", uuid_str=None):
    """Generate a symbol instance (component placement)."""
    if uuid_str is None:
        uuid_str = gen_uuid()
    pin_uuids = ""
    # We need pin UUIDs but we don't know how many pins - generate placeholder
    # Actually, in KiCad 10 format, pin UUIDs are in the symbol definition
    # For placed symbols, we just reference the lib_id
    return f"""	(symbol
		(lib_id "{lib_id}")
		(at {x} {y} {rot})
		(unit {unit})
		(body_style 1)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(dnp no)
		(fields_autoplaced yes)
		(uuid "{uuid_str}")
		(property "Reference" "{refdes}"
			(at {x} {y - 15} 0)
			(effects (font (size 1.27 1.27)))
		)
		(property "Value" "{value}"
			(at {x} {y + 15} 0)
			(effects (font (size 1.27 1.27)))
		)
		(instances
			(project "phone"
				(path "{sheet_path}"
					(reference "{refdes}")
					(unit {unit})
				)
			)
		)
	)"""

def make_power_symbol(power_net, x, y, rot, refdes, sheet_path="/", uuid_str=None):
    """Generate a power symbol (GND, +3.3V, +1V8, +BATT, VBUS)."""
    if uuid_str is None:
        uuid_str = gen_uuid()
    lib_id = f"power:{power_net}"
    return f"""	(symbol
		(lib_id "{lib_id}")
		(at {x} {y} {rot})
		(unit 1)
		(body_style 1)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(dnp no)
		(fields_autoplaced yes)
		(uuid "{uuid_str}")
		(property "Reference" "{refdes}"
			(at {x + 3.81 if rot == 90 else x - 3.81 if rot == 270 else x} {y} 0)
			(effects (font (size 1.27 1.27)))
		)
		(property "Value" "{power_net}"
			(at {x} {y - 2.54 if rot == 0 else y + 2.54} 0)
			(effects (font (size 1.27 1.27)))
		)
		(instances
			(project "phone"
				(path "{sheet_path}"
					(reference "{refdes}")
					(unit 1)
				)
			)
		)
	)"""

def make_global_label(name, x, y, rot=0, shape="bidirectional", uuid_str=None):
    """Generate a global label.
    rot: 0=right, 90=up, 180=left, 270=down
    """
    if uuid_str is None:
        uuid_str = gen_uuid()
    justify = "left" if rot == 0 else "right" if rot == 180 else "bottom" if rot == 90 else "top"
    return f"""	(global_label "{name}"
		(shape {shape})
		(at {x} {y} {rot})
		(fields_autoplaced yes)
		(effects (font (size 1.27 1.27)) (justify {justify}))
		(uuid "{uuid_str}")
		(property "Intersheetrefs" "${{INTERSHEET_REFS}}"
			(at {x + 14 if rot == 0 else x - 14 if rot == 180 else x} {y} 0)
			(hide yes)
			(effects (font (size 1.27 1.27)) (justify {justify}))
		)
	)"""

def make_wire(x1, y1, x2, y2, uuid_str=None):
    """Generate a wire segment."""
    if uuid_str is None:
        uuid_str = gen_uuid()
    return f'	(wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid "{uuid_str}"))\n'

def make_no_connect(x, y, uuid_str=None):
    """Generate a no-connect marker."""
    if uuid_str is None:
        uuid_str = gen_uuid()
    return f'	(no_connect (at {x} {y}) (uuid "{uuid_str}"))\n'

def make_junction(x, y, uuid_str=None):
    """Generate a junction marker."""
    if uuid_str is None:
        uuid_str = gen_uuid()
    return f'	(junction (at {x} {y}) (diameter 0) (color 0 0 0 0) (uuid "{uuid_str}"))\n'

# ============================================================
# Sheet builder
# ============================================================

def build_sheet(sheet_uuid, paper, lib_symbol_blocks, content):
    """Build a complete .kicad_sch file."""
    s = []
    s.append('(kicad_sch\n')
    s.append('\t(version 20260306)\n')
    s.append('\t(generator "eeschema")\n')
    s.append('\t(generator_version "10.0")\n')
    s.append(f'\t(uuid "{sheet_uuid}")\n')
    s.append(f'\t(paper "{paper}")\n')
    s.append('\t(lib_symbols\n')
    for block in lib_symbol_blocks:
        if block:
            normalized = normalize_indent(block)
            s.append(normalized)
            s.append('\n')
    s.append('\t)\n')
    s.append(content)
    s.append('\t(sheet_instances\n')
    s.append('\t\t(path "/"\n')
    s.append('\t\t\t(page "1")\n')
    s.append('\t\t)\n')
    s.append('\t)\n')
    s.append('\t(embedded_fonts no)\n')
    s.append(')\n')
    return ''.join(s)

# ============================================================
# Modem sheet
# ============================================================

def create_modem_sheet():
    sheet_uuid = gen_uuid()
    sheet_path = f"/{ROOT_UUID}/{sheet_uuid}"

    # Extract lib symbols
    mpice_lib = extract_lib_symbol(os.path.join(LIB_DIR, "connectors.kicad_sym"), "PCIE-52P40H_C444926")
    txb0108_lib = extract_lib_symbol(os.path.join(LIB_DIR, "ics.kicad_sym"), "TXB0108PWR")
    # Power symbols
    gnd_lib = extract_lib_symbol(os.path.join(LIB_DIR, "connectors.kicad_sym"), "GND") or ""
    # Power symbols are in the power library - we need to reference them
    # Actually power symbols in KiCad are built-in, we just need the lib_id reference

    # MPCIe socket pin mapping (from block-diagram.md)
    # Odd pins on bottom (y=-10.16 relative to symbol), even pins on top (y=10.16)
    # Socket placed at (100, 100), so:
    #   bottom pins at y = 100 - 10.16 = 89.84
    #   top pins at y = 100 + 10.16 = 110.16
    # Pin x positions: pin N at x = 100 + (-31.75 + (N-1)*2.54) for odd, same for even

    mpice_x = 100.0
    mpice_y = 100.0

    # Pin positions relative to socket center
    # Pin N: x = -31.75 + (N-1)*2.54, odd=bottom(y=-10.16), even=top(y=10.16)
    def mpice_pin_pos(pin_num):
        rel_x = -31.75 + (pin_num - 1) * 2.54
        if pin_num % 2 == 1:  # odd = bottom
            rel_y = -10.16
        else:  # even = top
            rel_y = 10.16
        return (mpice_x + rel_x, mpice_y + rel_y)

    # TXB0108 placed to the right of MPCIe
    txb_x = 180.0
    txb_y = 100.0

    # TXB0108 pin positions (relative to symbol center)
    # Left side (A): x=-12.70, Right side (B): x=12.70
    def txb_pin_pos(pin_num):
        pin_positions = {
            1: (-12.70, 11.43),   # A1
            2: (-12.70, 8.89),    # VCCA
            3: (-12.70, 6.35),    # A2
            4: (-12.70, 3.81),    # A3
            5: (-12.70, 1.27),    # A4
            6: (-12.70, -1.27),   # A5
            7: (-12.70, -3.81),   # A6
            8: (-12.70, -6.35),   # A7
            9: (-12.70, -8.89),   # A8
            10: (-12.70, -11.43), # OE
            11: (12.70, -11.43),  # GND
            12: (12.70, -8.89),   # B8
            13: (12.70, -6.35),   # B7
            14: (12.70, -3.81),   # B6
            15: (12.70, -1.27),   # B5
            16: (12.70, 1.27),    # B4
            17: (12.70, 3.81),    # B3
            18: (12.70, 6.35),    # B2
            19: (12.70, 8.89),    # VCCB
            20: (12.70, 11.43),   # B1
        }
        rx, ry = pin_positions[pin_num]
        return (txb_x + rx, txb_y + ry)

    content = []

    # === Place MPCIe socket (U2) ===
    content.append(make_symbol_instance(
        "connectors:PCIE-52P40H_C444926", mpice_x, mpice_y, 0,
        "U2", "PCIE-52P40H_C444926", sheet_path=sheet_path
    ))

    # === Place TXB0108 (U8) ===
    content.append(make_symbol_instance(
        "ics:TXB0108PWR", txb_x, txb_y, 0,
        "U8", "TXB0108PWR", sheet_path=sheet_path
    ))

    # === Power pins on MPCIe ===
    # VCC pins: 2, 24, 39, 41, 52 -> +3.3V
    # GND pins: 4, 9, 15, 18, 21, 26, 27, 29, 34, 35, 37, 40, 43, 50 -> GND
    # Mounting: 53, 54 -> GND

    vcc_pins = [2, 24, 39, 41, 52]
    gnd_pins = [4, 9, 15, 18, 21, 26, 27, 29, 34, 35, 37, 40, 43, 50, 53, 54]

    # Place +3.3V power symbols above VCC pins
    pwr_ref = 100  # Starting power refdes number
    for pin in vcc_pins:
        px, py = mpice_pin_pos(pin)
        # Power symbol above (for top pins) or below (for bottom pins)
        if pin % 2 == 0:  # top pin
            pwr_y = py + 7.62
            pwr_rot = 0
        else:
            pwr_y = py - 7.62
            pwr_rot = 180
        content.append(make_power_symbol("+3.3V", px, pwr_y, pwr_rot, f"#PWR{pwr_ref}", sheet_path))
        content.append(make_wire(px, py, px, pwr_y))
        pwr_ref += 1

    # Place GND power symbols
    for pin in gnd_pins:
        px, py = mpice_pin_pos(pin)
        if pin % 2 == 0:  # top pin - GND above
            pwr_y = py + 7.62
            pwr_rot = 180
        else:  # bottom pin - GND below
            pwr_y = py - 7.62
            pwr_rot = 0
        content.append(make_power_symbol("GND", px, pwr_y, pwr_rot, f"#PWR{pwr_ref}", sheet_path))
        content.append(make_wire(px, py, px, pwr_y))
        pwr_ref += 1

    # === UART/Control signals through TXB0108 ===
    # MPCIe pin -> global label (modem side) -> TXB0108 A-side
    # TXB0108 B-side -> global label (MCU side)

    uart_mapping = [
        # (mpcie_pin, modem_label, txb_a_pin, mcu_label, txb_b_pin, direction)
        (19, "MODEM_TXD", 1, "MCU_UART_RX", 20, "output"),     # A1->B1
        (17, "MODEM_RXD", 3, "MCU_UART_TX", 18, "input"),       # A2->B2
        (13, "MODEM_RTS", 4, "MCU_UART_CTS", 17, "output"),     # A3->B3
        (11, "MODEM_CTS", 5, "MCU_UART_RTS", 16, "input"),      # A4->B4
        (44, "MODEM_RI", 6, "MCU_RI_IRQ", 15, "output"),        # A5->B5
        (46, "MODEM_DTR", 7, "MCU_DTR", 14, "input"),           # A6->B6
        (22, "MODEM_RST", 8, "MCU_MODEM_RST", 13, "input"),     # A7->B7
        (1, "MODEM_STATUS", 9, "MCU_MODEM_STATUS", 12, "output"), # A8->B8
    ]

    for mpice_pin, modem_label, txb_a_pin, mcu_label, txb_b_pin, direction in uart_mapping:
        # MPCIe pin -> wire -> global label (modem side)
        mpx, mpy = mpice_pin_pos(mpice_pin)
        # Label placed near the MPCIe pin
        if mpice_pin % 2 == 1:  # bottom pin - label below
            label_y = mpy - 5.08
            label_rot = 180  # pointing left
        else:  # top pin - label above
            label_y = mpy + 5.08
            label_rot = 0  # pointing right

        # Wire from pin to label
        content.append(make_wire(mpx, mpy, mpx, label_y))
        content.append(make_global_label(modem_label, mpx, label_y, label_rot,
                                          shape="output" if "output" in direction else "input"))

        # TXB0108 A-side -> global label (modem side, same name)
        ax, ay = txb_pin_pos(txb_a_pin)
        # Label to the left of A-side pin
        content.append(make_wire(ax, ay, ax - 5.08, ay))
        content.append(make_global_label(modem_label, ax - 5.08, ay, 180,
                                          shape="input" if "output" in direction else "output"))

        # TXB0108 B-side -> global label (MCU side)
        bx, by = txb_pin_pos(txb_b_pin)
        # Label to the right of B-side pin
        content.append(make_wire(bx, by, bx + 5.08, by))
        content.append(make_global_label(mcu_label, bx + 5.08, by, 0,
                                          shape="output" if "input" in direction else "input"))

    # === TXB0108 power ===
    # VCCA (pin 2) -> +1V8
    vx, vy = txb_pin_pos(2)
    content.append(make_power_symbol("+1V8", vx - 7.62, vy, 0, f"#PWR{pwr_ref}", sheet_path))
    content.append(make_wire(vx, vy, vx - 7.62, vy))
    pwr_ref += 1

    # VCCB (pin 19) -> +3.3V
    vx, vy = txb_pin_pos(19)
    content.append(make_power_symbol("+3.3V", vx + 7.62, vy, 180, f"#PWR{pwr_ref}", sheet_path))
    content.append(make_wire(vx, vy, vx + 7.62, vy))
    pwr_ref += 1

    # GND (pin 11) -> GND
    gx, gy = txb_pin_pos(11)
    content.append(make_power_symbol("GND", gx + 7.62, gy, 180, f"#PWR{pwr_ref}", sheet_path))
    content.append(make_wire(gx, gy, gx + 7.62, gy))
    pwr_ref += 1

    # OE (pin 10) -> +3.3V via pullup (R11)
    oe_x, oe_y = txb_pin_pos(10)
    # Place R11 (10k pullup) between OE and +3.3V
    r11_x = oe_x - 12.7
    r11_y = oe_y - 5.08
    content.append(make_symbol_instance(
        "passives:RC0603JR-0710KL", r11_x, r11_y, 90,
        "R11", "10k", sheet_path=sheet_path
    ))
    # Wire from OE to R11 pin 1, R11 pin 2 to +3.3V
    content.append(make_wire(oe_x, oe_y, oe_x, r11_y + 3.81))
    content.append(make_wire(r11_x, r11_y + 3.81, oe_x, r11_y + 3.81))
    content.append(make_junction(oe_x, r11_y + 3.81))
    content.append(make_power_symbol("+3.3V", r11_x, r11_y - 3.81, 0, f"#PWR{pwr_ref}", sheet_path))
    content.append(make_wire(r11_x, r11_y - 3.81, r11_x, r11_y - 2.54))
    pwr_ref += 1

    # === PCM/I2S signals (direct to codec, no level shifter) ===
    pcm_mapping = [
        (45, "PCM_CLK"),
        (47, "PCM_OUT"),
        (49, "PCM_IN"),
        (51, "PCM_SYNC"),
    ]
    for pin, label in pcm_mapping:
        px, py = mpice_pin_pos(pin)
        if pin % 2 == 1:  # bottom pin
            label_y = py - 5.08
            label_rot = 180
        else:
            label_y = py + 5.08
            label_rot = 0
        content.append(make_wire(px, py, px, label_y))
        content.append(make_global_label(label, px, label_y, label_rot, shape="bidirectional"))

    # === USB signals ===
    usb_mapping = [
        (38, "MODEM_USB_DP"),
        (36, "MODEM_USB_DN"),
    ]
    for pin, label in usb_mapping:
        px, py = mpice_pin_pos(pin)
        if pin % 2 == 1:
            label_y = py - 5.08
            label_rot = 180
        else:
            label_y = py + 5.08
            label_rot = 0
        content.append(make_wire(px, py, px, label_y))
        content.append(make_global_label(label, px, label_y, label_rot, shape="bidirectional"))

    # === SIM signals ===
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
            label_y = py - 5.08
            label_rot = 180
        else:
            label_y = py + 5.08
            label_rot = 0
        content.append(make_wire(px, py, px, label_y))
        content.append(make_global_label(label, px, label_y, label_rot, shape="bidirectional"))

    # === NET_STATUS (pin 42) ===
    px, py = mpice_pin_pos(42)
    content.append(make_wire(px, py, px, py + 5.08))
    content.append(make_global_label("NET_STATUS", px, py + 5.08, 0, shape="output"))

    # === No-connect pins ===
    nc_pins = [3, 5, 6, 7, 20, 23, 25, 28, 30, 31, 32, 33, 48]
    for pin in nc_pins:
        px, py = mpice_pin_pos(pin)
        content.append(make_no_connect(px, py))

    # === Bulk caps on VCC (C31, C32) ===
    # Place near VCC pins
    c31_x = mpice_x + 40
    c31_y = mpice_y + 25
    content.append(make_symbol_instance(
        "passives:GRM21BR61H106KE43L", c31_x, c31_y, 0,
        "C31", "10uF", sheet_path=sheet_path
    ))
    # C31 to +3.3V and GND
    content.append(make_power_symbol("+3.3V", c31_x, c31_y - 5.08, 0, f"#PWR{pwr_ref}", sheet_path))
    content.append(make_wire(c31_x, c31_y - 2.54, c31_x, c31_y - 5.08))
    pwr_ref += 1
    content.append(make_power_symbol("GND", c31_x, c31_y + 5.08, 180, f"#PWR{pwr_ref}", sheet_path))
    content.append(make_wire(c31_x, c31_y + 2.54, c31_x, c31_y + 5.08))
    pwr_ref += 1

    c32_x = c31_x + 10
    c32_y = c31_y
    content.append(make_symbol_instance(
        "passives:CC0603KRX7R9BB104", c32_x, c32_y, 0,
        "C32", "100nF", sheet_path=sheet_path
    ))
    content.append(make_power_symbol("+3.3V", c32_x, c32_y - 5.08, 0, f"#PWR{pwr_ref}", sheet_path))
    content.append(make_wire(c32_x, c32_y - 2.54, c32_x, c32_y - 5.08))
    pwr_ref += 1
    content.append(make_power_symbol("GND", c32_x, c32_y + 5.08, 180, f"#PWR{pwr_ref}", sheet_path))
    content.append(make_wire(c32_x, c32_y + 2.54, c32_x, c32_y + 5.08))
    pwr_ref += 1

    # Build the sheet
    lib_blocks = [mpice_lib, txb0108_lib]
    # Also need power symbol lib blocks
    for net in ["+3.3V", "+1V8", "GND"]:
        # Power symbols are built-in to KiCad, but we need them in lib_symbols
        # Extract from the existing phone.kicad_sch
        pass

    sheet_text = build_sheet(sheet_uuid, "A3", lib_blocks, ''.join(content))
    write_text(os.path.join(SCH_DIR, "modem.kicad_sch"), sheet_text)
    print(f"Created modem.kicad_sch ({len(sheet_text)} bytes, UUID: {sheet_uuid})")
    return sheet_uuid

# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    print("Generating schematic sheets...")
    modem_uuid = create_modem_sheet()
    print(f"\nSheet UUIDs:")
    print(f"  Modem: {modem_uuid}")
    print("Done!")
