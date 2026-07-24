"""Fix root sheet ERC errors:
1. Add PWR_FLAG lib_symbol definition
2. Add PWR_FLAG instances for GND and VBUS nets
3. Add +BATT power symbol for U4 VINA pin
4. Add wires to connect the new symbols

Pin type changes (power_out -> passive for U4 Pin5 and U6 Pin4) 
were already done via edit tool.
"""
import re
import uuid

def gen_uuid():
    return str(uuid.uuid4())

with open('phone.kicad_sch', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add PWR_FLAG lib_symbol before the closing ) of lib_symbols
# Find the end of lib_symbols section
lib_sym_start = content.find('(lib_symbols')
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
lib_sym_end = i  # position of the closing )

pwr_flag_lib = '''		(symbol "power:PWR_FLAG"
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(in_pos_files yes)
			(duplicate_pin_numbers_are_jumpers no)
			(property "Reference" "#FLG"
				(at 0 1.905 0)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
					(justify left bottom)
				)
			)
			(property "Value" "PWR_FLAG"
				(at 0 3.81 0)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
					(justify left bottom)
				)
			)
			(property "Footprint" ""
				(at 0 0 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(property "Datasheet" ""
				(at 0 0 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(symbol "PWR_FLAG_0_1"
				(pin power_out line
					(at 0 0 0)
					(length 0)
					(name "pwr_flag"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "1"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
			)
			(embedded_fonts no)
		)
'''

content = content[:lib_sym_end] + pwr_flag_lib + content[lib_sym_end:]
print("Added PWR_FLAG lib_symbol")

# 2. Add PWR_FLAG instances and +BATT symbol before sheet_instances
# Find sheet_instances
sheet_inst_idx = content.find('\t(sheet_instances')
if sheet_inst_idx < 0:
    sheet_inst_idx = content.find('(sheet_instances')

# PWR_FLAG for GND net at (33.02, 43.18) — near #PWR2 at (36.83, 46.99)
# PWR_FLAG for VBUS net at (25.4, 153.67) — near #PWR16 at (52.07, 153.67)
# +BATT power symbol at (119.38, 44.45) — for U4 VINA pin

flg1_uuid = gen_uuid()
flg2_uuid = gen_uuid()
pwr024_uuid = gen_uuid()

new_symbols = f'''		(symbol
			(lib_id "power:PWR_FLAG")
			(at 33.02 43.18 0)
			(unit 1)
			(body_style 1)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(in_pos_files yes)
			(dnp no)
			(fields_autoplaced yes)
			(uuid "{flg1_uuid}")
			(property "Reference" "#FLG025"
				(at 33.02 38.1 0)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
					(justify left bottom)
				)
			)
			(property "Value" "PWR_FLAG"
				(at 33.02 40.64 0)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
					(justify left bottom)
				)
			)
			(property "Footprint" ""
				(at 33.02 43.18 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(property "Datasheet" ""
				(at 33.02 43.18 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(instances
				(project "phone"
					(path "/451c3b43-1616-42cb-bf96-d436f4db82c2"
						(reference "#FLG025")
						(unit 1)
					)
				)
			)
		)
		(symbol
			(lib_id "power:PWR_FLAG")
			(at 25.4 153.67 0)
			(unit 1)
			(body_style 1)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(in_pos_files yes)
			(dnp no)
			(fields_autoplaced yes)
			(uuid "{flg2_uuid}")
			(property "Reference" "#FLG026"
				(at 25.4 148.59 0)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
					(justify left bottom)
				)
			)
			(property "Value" "PWR_FLAG"
				(at 25.4 151.13 0)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
					(justify left bottom)
				)
			)
			(property "Footprint" ""
				(at 25.4 153.67 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(property "Datasheet" ""
				(at 25.4 153.67 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(instances
				(project "phone"
					(path "/451c3b43-1616-42cb-bf96-d436f4db82c2"
						(reference "#FLG026")
						(unit 1)
					)
				)
			)
		)
		(symbol
			(lib_id "power:+BATT")
			(at 119.38 44.45 0)
			(unit 1)
			(body_style 1)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(in_pos_files yes)
			(dnp no)
			(fields_autoplaced yes)
			(uuid "{pwr024_uuid}")
			(property "Reference" "#PWR024"
				(at 119.38 48.26 0)
				(hide yes)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Value" "+BATT"
				(at 119.38 39.37 0)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Footprint" ""
				(at 119.38 44.45 0)
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
				(at 119.38 44.45 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(instances
				(project "phone"
					(path "/451c3b43-1616-42cb-bf96-d436f4db82c2"
						(reference "#PWR024")
						(unit 1)
					)
				)
			)
		)
		(wire
			(pts
				(xy 33.02 43.18) (xy 36.83 43.18)
			)
			(stroke
				(width 0)
				(type default)
			)
			(uuid "{gen_uuid()}")
		)
		(wire
			(pts
				(xy 36.83 43.18) (xy 36.83 46.99)
			)
			(stroke
				(width 0)
				(type default)
			)
			(uuid "{gen_uuid()}")
		)
		(wire
			(pts
				(xy 25.4 153.67) (xy 52.07 153.67)
			)
			(stroke
				(width 0)
				(type default)
			)
			(uuid "{gen_uuid()}")
		)
		(wire
			(pts
				(xy 119.38 44.45) (xy 118.11 44.45)
			)
			(stroke
				(width 0)
				(type default)
			)
			(uuid "{gen_uuid()}")
		)
'''

content = content[:sheet_inst_idx] + new_symbols + content[sheet_inst_idx:]
print("Added PWR_FLAG instances, +BATT symbol, and connecting wires")

# Verify s-expression balance
depth = 0
for i, c in enumerate(content):
    if c == '(':
        depth += 1
    elif c == ')':
        depth -= 1
        if depth < 0:
            line = content[:i].count('\n') + 1
            print(f"ERROR: Extra closing paren at line {line}")
            break
else:
    if depth != 0:
        print(f"ERROR: Final depth = {depth} (should be 0)")
    else:
        print("S-expression balance OK")

with open('phone.kicad_sch', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print("Done. Run ERC to verify.")
