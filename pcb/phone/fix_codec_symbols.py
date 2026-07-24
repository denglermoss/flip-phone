"""Fix codec sheet: flip ALC5651-CG and TXB0108PWR embedded symbols.

The codec subagent placed wires at lib_symbol Y positions (without accounting
for KiCad's Y-axis negation). Flipping these two symbols moves the pins to
where the wires already are, fixing all connections.

Only flips these two symbols in codec.kicad_sch's embedded lib_symbols.
Does NOT touch any other file or symbol.
"""
import re

def flip_symbol_block(block):
    """Flip Y coordinates within a symbol block."""
    def flip_pin_at(m):
        x = m.group(1)
        y = float(m.group(2))
        rot = int(m.group(3))
        new_y = -y
        if rot == 90:
            new_rot = 270
        elif rot == 270:
            new_rot = 90
        else:
            new_rot = rot
        y_str = str(new_y)
        return f'(at {x} {y_str} {new_rot})'

    block = re.sub(r'\(at\s+([\d.-]+)\s+([\d.-]+)\s+(\d+)\)', flip_pin_at, block)

    def flip_start(m):
        return f'(start {m.group(1)} {-float(m.group(2))})'
    def flip_end(m):
        return f'(end {m.group(1)} {-float(m.group(2))})'
    def flip_center(m):
        return f'(center {m.group(1)} {-float(m.group(2))})'

    block = re.sub(r'\(start\s+([\d.-]+)\s+([\d.-]+)\)', flip_start, block)
    block = re.sub(r'\(end\s+([\d.-]+)\s+([\d.-]+)\)', flip_end, block)
    block = re.sub(r'\(center\s+([\d.-]+)\s+([\d.-]+)\)', flip_center, block)
    return block


sch_path = r'C:\Users\dengle\Documents\personal_projects\phone\pcb\phone\codec.kicad_sch'
with open(sch_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find lib_symbols section
lib_start = content.find('(lib_symbols')
depth = 0
i = lib_start
while i < len(content):
    if content[i] == '(':
        depth += 1
    elif content[i] == ')':
        depth -= 1
        if depth == 0:
            break
    i += 1
lib_end = i + 1
lib_section = content[lib_start:lib_end]

# Flip only ALC5651-CG and TXB0108PWR
targets = ['ics:ALC5651-CG', 'ics:TXB0108PWR']
for target in targets:
    # Find the symbol block
    pattern = r'\(symbol "' + re.escape(target) + r'"'
    match = re.search(pattern, lib_section)
    if not match:
        print(f"  {target} not found!")
        continue

    sym_start = match.start()
    depth = 0
    j = sym_start
    while j < len(lib_section):
        if lib_section[j] == '(':
            depth += 1
        elif lib_section[j] == ')':
            depth -= 1
            if depth == 0:
                break
        j += 1
    block_end = j + 1
    block = lib_section[sym_start:block_end]

    flipped = flip_symbol_block(block)
    lib_section = lib_section[:sym_start] + flipped + lib_section[block_end:]
    print(f"  Flipped {target}")

content = content[:lib_start] + lib_section + content[lib_end:]
with open(sch_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print("Done. Run ERC to verify.")
