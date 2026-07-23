#!/usr/bin/env python3
"""
Split phone.kicad_sch into hierarchical sheets:
- phone.kicad_sch (root): power section + hierarchical sheet box for MCU
- mcu.kicad_sch (child): MCU section (STM32H743 + decoupling + crystal + labels)

Also fixes label name conflicts:
  USB_DM  -> USB_DN  (match power section canonical name)
  PWR_3V3_OK -> 3V3_OK  (match power section canonical name)

Global labels are kept (not converted to hierarchical labels) so they
connect across sheets automatically without needing sheet pins.
"""

import re
import uuid as uuid_module
import os

SCH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phone")
SCH_FILE = os.path.join(SCH_DIR, "phone.kicad_sch")
MCU_FILE = os.path.join(SCH_DIR, "mcu.kicad_sch")
ROOT_UUID = "451c3b43-1616-42cb-bf96-d436f4db82c2"
MCU_SHEET_UUID = str(uuid_module.uuid4())

# Label name fixes (MCU section had wrong names)
LABEL_FIXES = {
    "USB_DM": "USB_DN",
    "PWR_3V3_OK": "3V3_OK",
}

def read_lines(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.readlines()

def write_text(filename, text):
    with open(filename, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)

def find_matching_paren(lines, start_idx, open_char='(', close_char=')'):
    """Find the line index of the matching close paren for the open paren at start_idx."""
    depth = 0
    for i in range(start_idx, len(lines)):
        line = lines[i]
        in_string = False
        for ch in line:
            if ch == '"':
                in_string = not in_string
            elif not in_string:
                if ch == open_char:
                    depth += 1
                elif ch == close_char:
                    depth -= 1
                    if depth == 0:
                        return i
    return None

def extract_lib_symbol_block(lines, symbol_start):
    """Extract a complete lib_symbol block starting at (symbol "name" line.
    Returns (block_lines, end_line_index_exclusive)."""
    # Find the matching close paren
    end = find_matching_paren(lines, symbol_start)
    if end is None:
        return [], symbol_start
    return lines[symbol_start:end+1], end+1

def normalize_lib_symbol_indent(block_lines, target_indent='\t\t'):
    """Normalize a lib_symbol block so the (symbol line is at target_indent (2 tabs).
    Some blocks were inserted at 4-tab indentation by a subagent bug.
    """
    if not block_lines:
        return block_lines
    # Count tabs on first line
    first_line = block_lines[0]
    current_tabs = len(first_line) - len(first_line.lstrip('\t'))
    target_tabs = len(target_indent)
    if current_tabs == target_tabs:
        return block_lines  # Already correct
    # Calculate adjustment
    delta = current_tabs - target_tabs
    if delta > 0:
        # Remove excess tabs from each line
        result = []
        for line in block_lines:
            line_tabs = len(line) - len(line.lstrip('\t'))
            if line_tabs >= delta:
                result.append(line[delta:])
            else:
                result.append(line.lstrip('\t'))  # Less indented, just strip
        return result
    elif delta < 0:
        # Add tabs
        add = '\t' * (-delta)
        return [add + line if line.strip() else line for line in block_lines]
    return block_lines

def main():
    lines = read_lines(SCH_FILE)
    total = len(lines)
    print(f"Read {total} lines from {SCH_FILE}")

    # === Find structural boundaries ===

    # 1. lib_symbols block
    lib_symbols_start = None
    for i, line in enumerate(lines):
        if line.strip() == '(lib_symbols':
            lib_symbols_start = i
            break

    # Find end of lib_symbols using paren matching
    # The (lib_symbols at \t level opens with depth 1.
    # Find the matching \t) that closes it.
    lib_symbols_end = find_matching_paren(lines, lib_symbols_start)

    print(f"lib_symbols: lines {lib_symbols_start+1}-{lib_symbols_end+1}")

    # 2. Find all lib_symbol names and their line ranges
    # Note: some lib_symbols have wrong indentation (4 tabs instead of 2)
    # due to a subagent bug. Use a flexible regex.
    lib_symbols = {}  # name -> (start_line, end_line_exclusive)
    i = lib_symbols_start + 1
    while i < lib_symbols_end:
        line = lines[i]
        # Match (symbol "name" at any indentation level (2 or 4 tabs)
        m = re.match(r'\t+\(symbol "([^"]+)"', line)
        if m:
            name = m.group(1)
            block, next_i = extract_lib_symbol_block(lines, i)
            lib_symbols[name] = (i, next_i)
            i = next_i
        else:
            i += 1

    print(f"Found {len(lib_symbols)} lib_symbols")

    # 3. Find MCU section start (the (symbol line before ics:STM32H743ZIT6)
    mcu_start = None
    for i, line in enumerate(lines):
        if 'ics:STM32H743ZIT6' in line and 'lib_id' in line:
            # Go back to find the (symbol line
            for j in range(i, max(i-5, 0), -1):
                if lines[j].strip().startswith('(symbol'):
                    mcu_start = j
                    break
            break

    print(f"MCU section starts at line {mcu_start+1}")

    # 4. Find sheet_instances
    sheet_instances_start = None
    for i, line in enumerate(lines):
        if '\t(sheet_instances' in line:
            sheet_instances_start = i
            break

    print(f"sheet_instances starts at line {sheet_instances_start+1}")

    # 5. Find end of sheet_instances block
    sheet_instances_end = find_matching_paren(lines, sheet_instances_start)
    print(f"sheet_instances ends at line {sheet_instances_end+1}")

    # === Extract MCU section ===
    # MCU section = lines from mcu_start to sheet_instances_start (exclusive)
    mcu_raw = lines[mcu_start:sheet_instances_start]
    print(f"MCU section raw: {len(mcu_raw)} lines")

    # Get all lib_ids used by MCU section
    mcu_lib_ids = set()
    for line in mcu_raw:
        m = re.search(r'\(lib_id "([^"]+)"', line)
        if m:
            mcu_lib_ids.add(m.group(1))
    print(f"MCU lib_ids: {sorted(mcu_lib_ids)}")

    # Extract lib_symbols for MCU (with indentation normalization)
    mcu_lib_sym_lines = []
    for lib_id in sorted(mcu_lib_ids):
        if lib_id in lib_symbols:
            start, end = lib_symbols[lib_id]
            block = lines[start:end]
            mcu_lib_sym_lines.extend(normalize_lib_symbol_indent(block))
        else:
            print(f"  WARNING: lib_symbol '{lib_id}' not found!")

    print(f"MCU lib_symbols: {len(mcu_lib_sym_lines)} lines")

    # === Normalize MCU section ===
    # The MCU section uses inconsistent indentation (2-tab for top-level elements).
    # Normalize to 1-tab for top-level (symbol, wire, global_label, no_connect, junction)
    mcu_normalized = []
    for line in mcu_raw:
        stripped = line.rstrip('\n\r')
        # Check for 2-tab top-level elements
        if stripped.startswith('\t\t(') and not stripped.startswith('\t\t\t'):
            # This is a 2-tab top-level element - reduce to 1-tab
            # But only for known top-level element types
            element = stripped[2:]
            if element.startswith('(symbol ') or element.startswith('(wire ') or \
               element.startswith('(global_label ') or element.startswith('(no_connect ') or \
               element.startswith('(junction ') or element.startswith('(text '):
                line = '\t' + element + '\n'
        mcu_normalized.append(line)

    # Apply label name fixes
    mcu_text = ''.join(mcu_normalized)
    for old_name, new_name in LABEL_FIXES.items():
        count = mcu_text.count(f'"{old_name}"')
        if count > 0:
            mcu_text = mcu_text.replace(f'"{old_name}"', f'"{new_name}"')
            print(f"  Fixed label: {old_name} -> {new_name} ({count} occurrences)")

    # Update symbol instance paths: /ROOT_UUID -> /ROOT_UUID/MCU_SHEET_UUID
    old_path = f'"/{ROOT_UUID}"'
    new_path = f'"/{ROOT_UUID}/{MCU_SHEET_UUID}"'
    mcu_text = mcu_text.replace(old_path, new_path)

    # === Build mcu.kicad_sch ===
    mcu_sch = []
    mcu_sch.append('(kicad_sch\n')
    mcu_sch.append('\t(version 20260306)\n')
    mcu_sch.append('\t(generator "eeschema")\n')
    mcu_sch.append('\t(generator_version "10.0")\n')
    mcu_sch.append(f'\t(uuid "{MCU_SHEET_UUID}")\n')
    mcu_sch.append('\t(paper "A3")\n')
    mcu_sch.append('\t(lib_symbols\n')
    mcu_sch.extend(mcu_lib_sym_lines)
    mcu_sch.append('\t)\n')
    mcu_sch.append(mcu_text)
    # sheet_instances for MCU sheet
    mcu_sch.append('\t(sheet_instances\n')
    mcu_sch.append('\t\t(path "/"\n')
    mcu_sch.append('\t\t\t(page "1")\n')
    mcu_sch.append('\t\t)\n')
    mcu_sch.append('\t)\n')
    mcu_sch.append('\t(embedded_fonts no)\n')
    mcu_sch.append(')\n')

    write_text(MCU_FILE, ''.join(mcu_sch))
    print(f"Written mcu.kicad_sch ({len(''.join(mcu_sch))} bytes)")

    # === Build new phone.kicad_sch (root) ===
    root_sch = []

    # Header (lines 0 to lib_symbols_start)
    root_sch.extend(lines[:lib_symbols_start])

    # lib_symbols - only power section symbols
    # Get power section lib_ids (everything in the power section content)
    # Power section content starts after lib_symbols block
    power_content_start = lib_symbols_end + 1
    power_lib_ids = set()
    for i in range(power_content_start, mcu_start):
        line = lines[i]
        m = re.search(r'\(lib_id "([^"]+)"', line)
        if m:
            power_lib_ids.add(m.group(1))
    print(f"Power lib_ids: {sorted(power_lib_ids)}")

    root_sch.append('\t(lib_symbols\n')
    for lib_id in sorted(power_lib_ids):
        if lib_id in lib_symbols:
            start, end = lib_symbols[lib_id]
            block = lines[start:end]
            root_sch.extend(normalize_lib_symbol_indent(block))
        else:
            print(f"  WARNING: power lib_symbol '{lib_id}' not found!")
    root_sch.append('\t)\n')

    # Power section content: from after lib_symbols to MCU start
    root_sch.extend(lines[lib_symbols_end+1:mcu_start])

    # Add hierarchical sheet box for MCU
    # Place it below the power section (power section ends around Y=170)
    # Sheet box at (254, 200) - well clear of power section
    root_sch.append('\t(sheet\n')
    root_sch.append('\t\t(at 254 200)\n')
    root_sch.append('\t\t(size 55 25)\n')
    root_sch.append('\t\t(fields_autoplaced yes)\n')
    root_sch.append('\t\t(stroke (width 0.1524) (type solid) (color 0 0 0 0))\n')
    root_sch.append('\t\t(fill (type none) (color 0 0 0 0))\n')
    root_sch.append(f'\t\t(uuid "{MCU_SHEET_UUID}")\n')
    root_sch.append('\t\t(property "Sheetname" "MCU"\n')
    root_sch.append('\t\t\t(at 254 199 0)\n')
    root_sch.append('\t\t\t(effects (font (size 1.27 1.27)) (justify left bottom))\n')
    root_sch.append('\t\t)\n')
    root_sch.append('\t\t(property "Sheetfile" "mcu.kicad_sch"\n')
    root_sch.append('\t\t\t(at 254 226 0)\n')
    root_sch.append('\t\t\t(effects (font (size 1.27 1.27)) (justify left top))\n')
    root_sch.append('\t\t)\n')
    root_sch.append('\t)\n')

    # sheet_instances
    root_sch.append('\t(sheet_instances\n')
    root_sch.append(f'\t\t(path "/{ROOT_UUID}"\n')
    root_sch.append('\t\t\t(page "1")\n')
    root_sch.append('\t\t)\n')
    root_sch.append(f'\t\t(path "/{ROOT_UUID}/{MCU_SHEET_UUID}"\n')
    root_sch.append('\t\t\t(page "2")\n')
    root_sch.append('\t\t)\n')
    root_sch.append('\t)\n')
    root_sch.append('\t(embedded_fonts no)\n')
    root_sch.append(')\n')

    write_text(SCH_FILE, ''.join(root_sch))
    print(f"Written phone.kicad_sch ({len(''.join(root_sch))} bytes)")
    print(f"\nMCU sheet UUID: {MCU_SHEET_UUID}")
    print("Done!")

if __name__ == '__main__':
    main()
