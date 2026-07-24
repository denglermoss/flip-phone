"""Extract the power section from phone.kicad_sch into power.kicad_sch.

The root sheet (phone.kicad_sch) currently contains:
- Header (version, generator, uuid, paper)
- lib_symbols section (all power ICs, connectors, passives, power ports)
- text annotations
- junctions
- wires
- global_labels
- symbol instances (all power components)
- sheet blocks (7 hierarchical sub-sheets)
- sheet_instances
- embedded_fonts

After extraction:
- power.kicad_sch will contain: header + lib_symbols + text + junctions + wires + global_labels + symbol instances + sheet_instances
- phone.kicad_sch will contain: header + sheet blocks (8, including new Power sheet) + sheet_instances + embedded_fonts
"""
import re
import uuid as uuid_module
import json

# Generate a new UUID for the power sub-sheet
POWER_SHEET_UUID = str(uuid_module.uuid4())
ROOT_UUID = "451c3b43-1616-42cb-bf96-d436f4db82c2"

print(f"Power sheet UUID: {POWER_SHEET_UUID}")

# === Read phone.kicad_sch ===
with open('phone.kicad_sch', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# === Find section boundaries by parsing top-level elements ===
# Top-level elements start with exactly one tab then (
sections = []
i = 0
while i < len(lines):
    line = lines[i]
    if line.startswith('\t(') and not line.startswith('\t\t'):
        # Found a top-level element
        tag = line.strip().split('(')[1].split()[0].strip('"')
        
        # Find the end of this block by counting parens
        depth = 0
        j = i
        while j < len(lines):
            for c in lines[j]:
                if c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
                    if depth == 0:
                        break
            if depth == 0:
                break
            j += 1
        
        sections.append({
            'tag': tag,
            'start_line': i,
            'end_line': j,
            'start_idx': sum(len(l) + 1 for l in lines[:i]),
            'end_idx': sum(len(l) + 1 for l in lines[:j+1]),
        })
        i = j + 1
    else:
        i += 1

print("\nTop-level sections found:")
for s in sections:
    print(f"  {s['tag']}: lines {s['start_line']+1}-{s['end_line']+1}")

# === Categorize sections ===
header_lines = []  # version, generator, generator_version, uuid, paper
lib_symbols_section = None
text_sections = []
junction_sections = []
wire_sections = []
global_label_sections = []
symbol_sections = []
sheet_sections = []
sheet_instances_section = None
embedded_fonts_section = None
title_block_section = None

for s in sections:
    tag = s['tag']
    if tag in ('version', 'generator', 'generator_version', 'uuid', 'paper'):
        header_lines.append(s)
    elif tag == 'lib_symbols':
        lib_symbols_section = s
    elif tag == 'title_block':
        title_block_section = s
    elif tag == 'text':
        text_sections.append(s)
    elif tag == 'junction':
        junction_sections.append(s)
    elif tag == 'wire':
        wire_sections.append(s)
    elif tag == 'global_label':
        global_label_sections.append(s)
    elif tag == 'symbol':
        symbol_sections.append(s)
    elif tag == 'sheet':
        sheet_sections.append(s)
    elif tag == 'sheet_instances':
        sheet_instances_section = s
    elif tag == 'embedded_fonts':
        embedded_fonts_section = s

print(f"\nCategorization:")
print(f"  Header lines: {len(header_lines)}")
print(f"  lib_symbols: {'found' if lib_symbols_section else 'NOT FOUND'}")
print(f"  title_block: {'found' if title_block_section else 'none'}")
print(f"  text: {len(text_sections)}")
print(f"  junctions: {len(junction_sections)}")
print(f"  wires: {len(wire_sections)}")
print(f"  global_labels: {len(global_label_sections)}")
print(f"  symbols: {len(symbol_sections)}")
print(f"  sheets: {len(sheet_sections)}")
print(f"  sheet_instances: {'found' if sheet_instances_section else 'NOT FOUND'}")
print(f"  embedded_fonts: {'found' if embedded_fonts_section else 'NOT FOUND'}")

# === Extract section content ===
def get_section_content(s):
    return '\n'.join(lines[s['start_line']:s['end_line']+1])

def get_section_lines(s):
    return lines[s['start_line']:s['end_line']+1]

# Get lib_symbols content (without the wrapping (lib_symbols ... ) tags)
lib_sym_lines = lines[lib_symbols_section['start_line']+1:lib_symbols_section['end_line']]
lib_sym_content = '\n'.join(lib_sym_lines)

# Get all power section content
text_content = '\n'.join(get_section_content(s) for s in text_sections)
junction_content = '\n'.join(get_section_content(s) for s in junction_sections)
wire_content = '\n'.join(get_section_content(s) for s in wire_sections)
global_label_content = '\n'.join(get_section_content(s) for s in global_label_sections)

# Get symbol instances and update their instance paths
symbol_lines = []
for s in symbol_sections:
    sym_content = get_section_content(s)
    # Update the instance path from root to root/power
    # Old: (path "/451c3b43-1616-42cb-bf96-d436f4db82c2"
    # New: (path "/451c3b43-1616-42cb-bf96-d436f4db82c2/POWER_SHEET_UUID"
    sym_content = sym_content.replace(
        f'(path "/{ROOT_UUID}"',
        f'(path "/{ROOT_UUID}/{POWER_SHEET_UUID}"'
    )
    symbol_lines.append(sym_content)
symbol_content = '\n'.join(symbol_lines)

# === Create power.kicad_sch ===
power_sch = f"""(kicad_sch
	(version 20260306)
	(generator "eeschema")
	(generator_version "10.0")
	(uuid "{POWER_SHEET_UUID}")
	(paper "A4")
	(title_block
		(title "Power")
	)
	(lib_symbols
{lib_sym_content}
	)
{text_content}
{junction_content}
{wire_content}
{global_label_content}
{symbol_content}
	(sheet_instances
		(path "/"
			(page "8")
		)
	)
	(embedded_fonts no)
)
"""

# Verify s-expression balance for power.kicad_sch
depth = 0
for i, c in enumerate(power_sch):
    if c == '(':
        depth += 1
    elif c == ')':
        depth -= 1
        if depth < 0:
            line = power_sch[:i].count('\n') + 1
            print(f"ERROR: power.kicad_sch has extra closing paren at line {line}")
            break
else:
    if depth != 0:
        print(f"ERROR: power.kicad_sch final depth = {depth}")
    else:
        print("power.kicad_sch s-expression balance OK")

with open('power.kicad_sch', 'w', encoding='utf-8', newline='\n') as f:
    f.write(power_sch)
print("Created power.kicad_sch")

# === Create new phone.kicad_sch (root) ===
# Keep: header, sheet blocks (+ new Power sheet), sheet_instances, embedded_fonts
# Remove: lib_symbols, text, junctions, wires, global_labels, symbol instances

# Build new root sheet
new_root_lines = []

# Header (lines 1-6: version, generator, generator_version, uuid, paper)
for s in header_lines:
    new_root_lines.extend(get_section_lines(s))

# Sheet blocks (keep existing 7 + add new Power sheet)
for s in sheet_sections:
    new_root_lines.extend(get_section_lines(s))

# Add new Power sheet block
# Place it at a position that doesn't overlap with existing sheets
# Existing sheets are at Y=200-360, X=254. Let's place Power at (254, 200)
# But we need to check for overlaps. Let me place it at a new position.
# Actually, let me place it before the other sheets (top-left area)
power_sheet_block = f"""	(sheet
		(at 50 200)
		(size 30.48 20.32)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(dnp no)
		(fields_autoplaced yes)
		(stroke
			(width 0.1524)
			(type solid)
		)
		(fill
			(color 0 0 0 0)
		)
		(uuid "{POWER_SHEET_UUID}")
		(property "Sheetname" "Power"
			(at 50 199 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left bottom)
			)
		)
		(property "Sheetfile" "power.kicad_sch"
			(at 50 221 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left top)
			)
		)
		(instances
			(project "phone"
				(path "/{ROOT_UUID}"
					(page "8")
				)
			)
		)
	)"""
new_root_lines.extend(power_sheet_block.split('\n'))

# sheet_instances
if sheet_instances_section:
    new_root_lines.extend(get_section_lines(sheet_instances_section))

# embedded_fonts
if embedded_fonts_section:
    new_root_lines.extend(get_section_lines(embedded_fonts_section))

# Close
new_root_lines.append(')')

new_root = '\n'.join(new_root_lines)

# Verify s-expression balance for new root
depth = 0
for i, c in enumerate(new_root):
    if c == '(':
        depth += 1
    elif c == ')':
        depth -= 1
        if depth < 0:
            line = new_root[:i].count('\n') + 1
            print(f"ERROR: new root has extra closing paren at line {line}")
            break
else:
    if depth != 0:
        print(f"ERROR: new root final depth = {depth}")
    else:
        print("New root s-expression balance OK")

with open('phone.kicad_sch', 'w', encoding='utf-8', newline='\n') as f:
    f.write(new_root)
print("Updated phone.kicad_sch (root sheet)")

# === Update phone.kicad_pro ===
with open('phone.kicad_pro', 'r', encoding='utf-8') as f:
    pro_content = f.read()

# Add Power to sheets list
# Find the sheets array and add the new entry
power_sheet_entry = f'''    [
      "{POWER_SHEET_UUID}",
      "Power"
    ],'''

# Add it at the beginning of the sheets list (after the opening [)
pro_content = re.sub(
    r'("sheets": \[\n)',
    rf'\1{power_sheet_entry}\n',
    pro_content,
    count=1
)

with open('phone.kicad_pro', 'w', encoding='utf-8') as f:
    f.write(pro_content)
print("Updated phone.kicad_pro (added Power to sheets list)")

print(f"\nPower sheet UUID: {POWER_SHEET_UUID}")
print("Done. Run ERC to verify.")
