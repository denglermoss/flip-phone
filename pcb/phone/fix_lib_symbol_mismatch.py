"""Fix lib_symbol_mismatch warnings by syncing embedded symbols with library versions.

Fixes 33 of 35 warnings (skips 2 codec ALC5651/TXB0108 that are intentionally flipped):
- power.kicad_sch: PWR_FLAG (2), XFL4020-152MEC (1)
- mcu.kicad_sch: STM32H743ZIT6 (1) — just fix Manufacturer property
- keypad.kicad_sch: SKQGABE010 (20), RC0603JR-0710KL (9)
"""
import re

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)

def find_symbol_block(content, symbol_name):
    """Find a (symbol "name" ... ) block in lib_symbols section of a .kicad_sch file.
    Handles both "name" and "lib:name" formats. Returns (start, end) indices or None."""
    patterns = [
        rf'\t\t\(symbol "{re.escape(symbol_name)}"$',
        rf'\t\t\(symbol "[\w]+:{re.escape(symbol_name)}"$',
    ]
    for pattern in patterns:
        m = re.search(pattern, content, re.MULTILINE)
        if m:
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
    return None

def extract_symbol_from_library(lib_path, symbol_name):
    """Extract a symbol definition from a .kicad_sym library file."""
    content = read_file(lib_path)
    patterns = [
        rf'  \(symbol "{re.escape(symbol_name)}"$',
        rf'\t\(symbol "{re.escape(symbol_name)}"$',
    ]
    for pattern in patterns:
        m = re.search(pattern, content, re.MULTILINE)
        if m:
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
            return content[start:i+1]
    return None

def reindent_to_tabs(content, source_indent='  '):
    """Reindent from 2-space or tab indent to tab indent (for .kicad_sch files)."""
    lines = content.split('\n')
    result = []
    for line in lines:
        stripped = line.lstrip()
        indent_str = line[:len(line) - len(stripped)]
        if source_indent == '  ':
            indent_count = len(indent_str) // 2
        else:  # tab
            indent_count = len(indent_str)
        # Schematic lib_symbols uses 2 tabs for first level
        result.append('\t' * (indent_count + 1) + stripped)
    return '\n'.join(result)

def get_lib_prefix(content, symbol_name):
    """Get the library prefix used for a symbol in a schematic file (e.g., 'passives:')."""
    m = re.search(rf'\t\t\(symbol "([\w]+):{re.escape(symbol_name)}"$', content, re.MULTILINE)
    if m:
        return m.group(1) + ':'
    return ''

# === Fix 1: PWR_FLAG in power.kicad_sch ===
print("=== Fix 1: PWR_FLAG in power.kicad_sch ===")
power_sch = read_file('power.kicad_sch')

# Extract PWR_FLAG from KiCad system library
system_power_lib = r'C:\Users\dengle\AppData\Local\Programs\KiCad\10.0\share\kicad\symbols\power.kicad_sym'
pwr_flag_lib = extract_symbol_from_library(system_power_lib, 'PWR_FLAG')
if pwr_flag_lib:
    # System library uses tab indent. Reindent to match schematic (2 tabs for first level)
    # The system library starts with \t(symbol, we need \t\t(symbol
    pwr_flag_sch = pwr_flag_lib.replace('\t(symbol', '\t\t(symbol', 1)
    # Fix all inner indentation: add one more tab to each line
    lines = pwr_flag_sch.split('\n')
    fixed = []
    for line in lines:
        if line.startswith('\t\t'):
            fixed.append('\t' + line)
        elif line.startswith('\t'):
            fixed.append('\t\t' + line.lstrip('\t'))
        else:
            fixed.append(line)
    pwr_flag_sch = '\n'.join(fixed)
    
    # Get the prefix used in the schematic
    prefix = get_lib_prefix(power_sch, 'PWR_FLAG')
    if prefix:
        pwr_flag_sch = pwr_flag_sch.replace('"PWR_FLAG"', f'"{prefix}PWR_FLAG"', 1)
    
    block = find_symbol_block(power_sch, 'PWR_FLAG')
    if block:
        old_block = power_sch[block[0]:block[1]]
        power_sch = power_sch[:block[0]] + pwr_flag_sch + power_sch[block[1]:]
        print(f"  Replaced PWR_FLAG (old: {len(old_block)} chars, new: {len(pwr_flag_sch)} chars)")
    else:
        print("  ERROR: PWR_FLAG not found in power.kicad_sch")
else:
    print("  ERROR: PWR_FLAG not found in system library")

# === Fix 2: XFL4020-152MEC in power.kicad_sch ===
print("\n=== Fix 2: XFL4020-152MEC in power.kicad_sch ===")
xfl_lib = extract_symbol_from_library('lib/passives.kicad_sym', 'XFL4020-152MEC')
if xfl_lib:
    # Library uses 2-space indent, schematic uses tab indent with 2-tab base
    xfl_sch = reindent_to_tabs(xfl_lib, '  ')
    # Add the passives: prefix
    prefix = get_lib_prefix(power_sch, 'XFL4020-152MEC')
    if prefix:
        xfl_sch = xfl_sch.replace('"XFL4020-152MEC"', f'"{prefix}XFL4020-152MEC"', 1)
    
    block = find_symbol_block(power_sch, 'XFL4020-152MEC')
    if block:
        old_block = power_sch[block[0]:block[1]]
        power_sch = power_sch[:block[0]] + xfl_sch + power_sch[block[1]:]
        print(f"  Replaced XFL4020-152MEC (old: {len(old_block)} chars, new: {len(xfl_sch)} chars)")
    else:
        print("  ERROR: XFL4020-152MEC not found in power.kicad_sch")
else:
    print("  ERROR: XFL4020-152MEC not found in passives library")

write_file('power.kicad_sch', power_sch)
print("  Wrote power.kicad_sch")

# === Fix 3: STM32H743ZIT6 in mcu.kicad_sch ===
print("\n=== Fix 3: STM32H743ZIT6 in mcu.kicad_sch ===")
mcu_sch = read_file('mcu.kicad_sch')
old_mfr = '"ST (意法半导体)"'
new_mfr = '"ST(意法半导体)"'
if old_mfr in mcu_sch:
    mcu_sch = mcu_sch.replace(old_mfr, new_mfr)
    print("  Fixed Manufacturer property (removed space after ST)")
else:
    print("  NOTE: Manufacturer property already correct or not found")
write_file('mcu.kicad_sch', mcu_sch)

# === Fix 4: SKQGABE010 in keypad.kicad_sch ===
print("\n=== Fix 4: SKQGABE010 in keypad.kicad_sch ===")
keypad_sch = read_file('keypad.kicad_sch')
skq_lib = extract_symbol_from_library('lib/electromech.kicad_sym', 'SKQGABE010')
if skq_lib:
    skq_sch = reindent_to_tabs(skq_lib, '  ')
    prefix = get_lib_prefix(keypad_sch, 'SKQGABE010')
    if prefix:
        skq_sch = skq_sch.replace('"SKQGABE010"', f'"{prefix}SKQGABE010"', 1)
    
    block = find_symbol_block(keypad_sch, 'SKQGABE010')
    if block:
        old_block = keypad_sch[block[0]:block[1]]
        keypad_sch = keypad_sch[:block[0]] + skq_sch + keypad_sch[block[1]:]
        print(f"  Replaced SKQGABE010 (old: {len(old_block)} chars, new: {len(skq_sch)} chars)")
    else:
        print("  ERROR: SKQGABE010 not found in keypad.kicad_sch")
else:
    print("  ERROR: SKQGABE010 not found in electromech library")

# === Fix 5: RC0603JR-0710KL in keypad.kicad_sch ===
print("\n=== Fix 5: RC0603JR-0710KL in keypad.kicad_sch ===")
rc_lib = extract_symbol_from_library('lib/passives.kicad_sym', 'RC0603JR-0710KL')
if rc_lib:
    rc_sch = reindent_to_tabs(rc_lib, '  ')
    prefix = get_lib_prefix(keypad_sch, 'RC0603JR-0710KL')
    if prefix:
        rc_sch = rc_sch.replace('"RC0603JR-0710KL"', f'"{prefix}RC0603JR-0710KL"', 1)
    
    block = find_symbol_block(keypad_sch, 'RC0603JR-0710KL')
    if block:
        old_block = keypad_sch[block[0]:block[1]]
        keypad_sch = keypad_sch[:block[0]] + rc_sch + keypad_sch[block[1]:]
        print(f"  Replaced RC0603JR-0710KL (old: {len(old_block)} chars, new: {len(rc_sch)} chars)")
    else:
        print("  ERROR: RC0603JR-0710KL not found in keypad.kicad_sch")
else:
    print("  ERROR: RC0603JR-0710KL not found in passives library")

write_file('keypad.kicad_sch', keypad_sch)
print("  Wrote keypad.kicad_sch")

# === Fix 6: ALC5651-CG + TXB0108PWR in codec.kicad_sch ===
# SKIPPED: Intentionally flipped in codec to fix easyeda2kicad Y-mirroring.
print("\n=== Fix 6: ALC5651-CG + TXB0108PWR in codec.kicad_sch ===")
print("  SKIPPED: Intentionally flipped in codec. 2 warnings will remain.")

# Verify s-expression balance for all modified files
print("\n=== Verifying s-expression balance ===")
for fname in ['power.kicad_sch', 'mcu.kicad_sch', 'keypad.kicad_sch']:
    content = read_file(fname)
    depth = 0
    ok = True
    for i, c in enumerate(content):
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth < 0:
                line = content[:i].count('\n') + 1
                print(f"  {fname}: ERROR extra closing paren at line {line}")
                ok = False
                break
    if ok:
        if depth != 0:
            print(f"  {fname}: ERROR final depth = {depth}")
        else:
            print(f"  {fname}: OK (balanced)")

print("\n=== Done. Run ERC to verify. ===")
