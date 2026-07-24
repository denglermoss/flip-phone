"""Fix XFL4020-152MEC lib_symbol_mismatch by updating the library to match the schematic.
The schematic version is what KiCad saved, so it's the 'current' version."""
import re

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)

def find_block(content, pattern):
    m = re.search(pattern, content, re.MULTILINE)
    if not m:
        return None
    start = m.start()
    depth = 0
    i = start
    while i < len(content):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                break
        i += 1
    return (start, i + 1)

# Extract XFL4020-152MEC from power.kicad_sch (schematic version)
power_sch = read_file('power.kicad_sch')
sch_block = find_block(power_sch, r'\t\t\(symbol "passives:XFL4020-152MEC"')
if not sch_block:
    print("ERROR: XFL4020-152MEC not found in power.kicad_sch")
    exit(1)

sch_symbol = power_sch[sch_block[0]:sch_block[1]]
# Remove the passives: prefix for library format
sch_symbol_no_prefix = sch_symbol.replace('"passives:XFL4020-152MEC"', '"XFL4020-152MEC"', 1)

# Reindent from tab to 2-space for library
lines = sch_symbol_no_prefix.split('\n')
reformatted = []
for line in lines:
    stripped = line.lstrip('\t')
    tab_count = len(line) - len(stripped)
    space_count = (tab_count - 1) * 2  # -1 because schematic has 2 tabs base, library has 0
    if space_count < 0:
        space_count = 0
    reformatted.append(' ' * space_count + stripped)
lib_format = '\n'.join(reformatted)

# Replace in library
ics_lib = read_file('lib/passives.kicad_sym')
lib_block = find_block(ics_lib, r'  \(symbol "XFL4020-152MEC"')
if not lib_block:
    print("ERROR: XFL4020-152MEC not found in lib/passives.kicad_sym")
    exit(1)

old_lib_symbol = ics_lib[lib_block[0]:lib_block[1]]
ics_lib = ics_lib[:lib_block[0]] + lib_format + ics_lib[lib_block[1]:]
write_file('lib/passives.kicad_sym', ics_lib)
print(f"Updated XFL4020-152MEC in lib/passives.kicad_sym (old: {len(old_lib_symbol)} chars, new: {len(lib_format)} chars)")
print("Done.")
