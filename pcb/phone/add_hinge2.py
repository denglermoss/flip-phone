"""Add J_HINGE2 (14-pin hinge FPC connector) to display_daughter.kicad_sch.

The daughterboard needs its own hinge connector to receive the flex cable
from the main board's J_HINGE. J_HINGE2 connects to the same nets as
J_DISP, J_DISP2, and J_EARPIECE via global labels.

Hinge pin mapping:
  1: +3.3V      8: OUTER_CS    15: GND (mounting)
  2: GND        9: OUTER_DC    16: GND (mounting)
  3: DISP_MOSI  10: BL_PWM
  4: DISP_SCK   11: NC (spare)
  5: DISP_CS    12: EARPIECE+
  6: DISP_DC    13: EARPIECE-
  7: DISP_RST   14: GND
"""
import re
import uuid as uuid_module

def gen_uuid():
    return str(uuid_module.uuid4())

# === Step 1: Extract 0.5K-HX-14PWB lib_symbol from display.kicad_sch ===
with open('display.kicad_sch', 'r', encoding='utf-8') as f:
    display_content = f.read()

# Find the lib_symbol block for 0.5K-HX-14PWB
pattern = r'\t\t\(symbol "connectors:0\.5K-HX-14PWB"'
m = re.search(pattern, display_content)
if not m:
    raise ValueError("Could not find 0.5K-HX-14PWB in display.kicad_sch")

sym_start = m.start()
# Find the end of this symbol block by counting parens
depth = 0
i = sym_start
while i < len(display_content):
    if display_content[i] == '(':
        depth += 1
    elif display_content[i] == ')':
        depth -= 1
        if depth == 0:
            break
    i += 1
sym_end = i + 1
lib_symbol_block = display_content[sym_start:sym_end]
print("Extracted 0.5K-HX-14PWB lib_symbol from display.kicad_sch")

# === Step 2: Read display_daughter.kicad_sch ===
with open('display_daughter.kicad_sch', 'r', encoding='utf-8') as f:
    daughter_content = f.read()

# === Step 3: Add lib_symbol to daughterboard ===
# Find the end of lib_symbols section in daughterboard
lib_sym_start = daughter_content.find('\t(lib_symbols')
if lib_sym_start < 0:
    raise ValueError("Could not find lib_symbols in display_daughter.kicad_sch")

depth = 0
i = lib_sym_start
while i < len(daughter_content):
    if daughter_content[i] == '(':
        depth += 1
    elif daughter_content[i] == ')':
        depth -= 1
        if depth == 0:
            break
    i += 1
lib_sym_end = i + 1

# Insert the new lib_symbol before the closing ) of lib_symbols
daughter_content = daughter_content[:lib_sym_end-1] + '\n' + lib_symbol_block + '\n' + daughter_content[lib_sym_end-1:]
print("Added 0.5K-HX-14PWB to daughterboard lib_symbols")

# === Step 4: Add J_HINGE2 symbol instance + wires + labels ===
# Place J_HINGE2 at (130, 130) — same as J_HINGE on main board
hinge_x, hinge_y = 130, 130
hinge_uuid = gen_uuid()

# Pin positions (absolute) = symbol position with Y negated from symbol definition
# KiCad negates Y when placing symbols (symbol editor Y-up → schematic Y-down)
# Pin 1: relative (-3.81, 16.51) → absolute (x-3.81, y-16.51)
# Pin 14: relative (-3.81, -16.51) → absolute (x-3.81, y+16.51)
# Pin 15: relative (3.81, -20.32) → absolute (x+3.81, y+20.32)
# Pin 16: relative (3.81, 21.59) → absolute (x+3.81, y-21.59)
pin_positions = {}
for pin_num in range(1, 15):
    rel_y = 16.51 - (pin_num - 1) * 2.54
    pin_positions[pin_num] = (hinge_x - 3.81, hinge_y - rel_y)
pin_positions[15] = (hinge_x + 3.81, hinge_y + 20.32)
pin_positions[16] = (hinge_x + 3.81, hinge_y - 21.59)

# Net assignments
pin_nets = {
    1: ('power', '+3.3V'),
    2: ('power', 'GND'),
    3: ('global', 'DISP_MOSI'),
    4: ('global', 'DISP_SCK'),
    5: ('global', 'DISP_CS'),
    6: ('global', 'DISP_DC'),
    7: ('global', 'DISP_RST'),
    8: ('global', 'OUTER_CS'),
    9: ('global', 'OUTER_DC'),
    10: ('global', 'BL_PWM'),
    11: ('nc', None),
    12: ('global', 'EARPIECE+'),
    13: ('global', 'EARPIECE-'),
    14: ('power', 'GND'),
    15: ('power', 'GND'),
    16: ('power', 'GND'),
}

# Build the J_HINGE2 symbol instance
hinge_symbol = f'''	(symbol
		(lib_id "connectors:0.5K-HX-14PWB")
		(at {hinge_x} {hinge_y} 0)
		(unit 1)
		(body_style 1)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(dnp no)
		(fields_autoplaced yes)
		(uuid "{hinge_uuid}")
		(property "Reference" "J_HINGE2"
			(at {hinge_x + 6.35} {hinge_y} 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left bottom)
			)
		)
		(property "Value" "0.5K-HX-14PWB"
			(at {hinge_x + 6.35} {hinge_y - 2.54} 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left top)
			)
		)
		(property "Footprint" ""
			(at {hinge_x} {hinge_y} 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Datasheet" ""
			(at {hinge_x} {hinge_y} 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(instances
			(project "phone"
				(path "/451c3b43-1616-42cb-bf96-d436f4db82c2/6e22c91a-fb49-47df-bf31-2f484b0239c9"
					(reference "J_HINGE2")
					(unit 1)
				)
			)
		)
	)
'''

# Build wires and labels for each pin
wires = []
labels = []
power_symbols = []
no_connects = []
power_ref_counter = 200  # Start from #PWR200 to avoid conflicts

for pin_num in range(1, 17):
    px, py = pin_positions[pin_num]
    net_type, net_name = pin_nets[pin_num]
    
    if net_type == 'nc':
        # Add no_connect marker at pin position
        no_connects.append(f'''	(no_connect
		(at {px} {py})
		(uuid "{gen_uuid()}")
	)
''')
        continue
    
    # Wire from pin to a point 5mm away
    # Signal pins (1-14) extend left, so wire goes left
    # Mounting pins (15, 16) are on the right side, so wire goes right
    if pin_num <= 14:
        wire_end_x = px - 5.08
    else:
        wire_end_x = px + 5.08
    wire_end_y = py
    wires.append(f'''	(wire
		(pts
			(xy {px} {py}) (xy {wire_end_x} {wire_end_y})
		)
		(stroke
			(width 0)
			(type default)
		)
		(uuid "{gen_uuid()}")
	)
''')
    
    if net_type == 'global':
        # Add global label at wire end (facing right toward the wire)
        labels.append(f'''	(global_label "{net_name}"
		(at {wire_end_x} {wire_end_y} 0)
		(effects
			(font
				(size 1.27 1.27)
			)
			(justify right)
		)
		(uuid "{gen_uuid()}")
		(property "Intersheetsref" ""
			(at {wire_end_x} {wire_end_y} 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
	)
''')
    elif net_type == 'power':
        # Add power symbol at wire end
        power_ref = f"#PWR{power_ref_counter}"
        power_ref_counter += 1
        power_symbols.append(f'''	(symbol
		(lib_id "power:{net_name}")
		(at {wire_end_x} {wire_end_y} 0)
		(unit 1)
		(body_style 1)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(dnp no)
		(fields_autoplaced yes)
		(uuid "{gen_uuid()}")
		(property "Reference" "{power_ref}"
			(at {wire_end_x - 3.81} {wire_end_y - 3.81} 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Value" "{net_name}"
			(at {wire_end_x} {wire_end_y + 2.54} 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" ""
			(at {wire_end_x} {wire_end_y} 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(property "Datasheet" ""
			(at {wire_end_x} {wire_end_y} 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(instances
			(project "phone"
				(path "/451c3b43-1616-42cb-bf96-d436f4db82c2/6e22c91a-fb49-47df-bf31-2f484b0239c9"
					(reference "{power_ref}")
					(unit 1)
				)
			)
		)
	)
''')

# Also need to add power lib_symbols if they don't exist
# Check if power:+3.3V and power:GND are already in the daughterboard
power_libs_needed = []
if 'power:+3.3V' not in daughter_content:
    power_libs_needed.append('+3.3V')
if 'power:GND' not in daughter_content:
    power_libs_needed.append('GND')

# Extract power lib_symbols from display.kicad_sch if needed
for power_name in power_libs_needed:
    pattern = rf'\t\t\(symbol "power:{re.escape(power_name)}"'
    m = re.search(pattern, display_content)
    if m:
        sym_start = m.start()
        depth = 0
        i = sym_start
        while i < len(display_content):
            if display_content[i] == '(':
                depth += 1
            elif display_content[i] == ')':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        power_sym_block = display_content[sym_start:i+1]
        # Insert into daughterboard lib_symbols
        daughter_content = daughter_content[:lib_sym_end-1] + '\n' + power_sym_block + '\n' + daughter_content[lib_sym_end-1:]
        # Update lib_sym_end since we inserted content
        lib_sym_end += len('\n' + power_sym_block + '\n')
        print(f"Added power:{power_name} lib_symbol to daughterboard")

# === Step 5: Insert J_HINGE2 + wires + labels before sheet_instances ===
sheet_inst_idx = daughter_content.find('\t(sheet_instances')
if sheet_inst_idx < 0:
    sheet_inst_idx = daughter_content.find('(sheet_instances')

new_content = hinge_symbol + '\n' + ''.join(wires) + ''.join(labels) + ''.join(power_symbols) + ''.join(no_connects)
daughter_content = daughter_content[:sheet_inst_idx] + new_content + daughter_content[sheet_inst_idx:]
print("Added J_HINGE2 symbol, wires, labels, and power symbols")

# === Step 6: Verify s-expression balance ===
depth = 0
for i, c in enumerate(daughter_content):
    if c == '(':
        depth += 1
    elif c == ')':
        depth -= 1
        if depth < 0:
            line = daughter_content[:i].count('\n') + 1
            print(f"ERROR: Extra closing paren at line {line}")
            break
else:
    if depth != 0:
        print(f"ERROR: Final depth = {depth}")
    else:
        print("S-expression balance OK")

with open('display_daughter.kicad_sch', 'w', encoding='utf-8', newline='\n') as f:
    f.write(daughter_content)
print("Done. Run ERC to verify.")
