"""Remove specific no_connect markers to prepare for adding deferred components."""
import re

def remove_no_connects(path, target_positions):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    removed = 0
    for tx, ty, name in target_positions:
        # Find the no_connect block at this position
        pattern = rf'\t\(no_connect\s*\n\t\t\(at {re.escape(str(tx))} {re.escape(str(ty))}\)\s*\n\t\t\(uuid "[^"]+"\)\s*\n\t\)'
        m = re.search(pattern, content)
        if m:
            # Remove the block and the preceding newline
            start = m.start()
            if start > 0 and content[start-1] == '\n':
                start -= 1
            content = content[:start] + content[m.end():]
            print(f"  Removed {name} no_connect at ({tx}, {ty})")
            removed += 1
        else:
            print(f"  WARNING: {name} no_connect at ({tx}, {ty}) not found")
    
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    return removed

# MCU sheet
print("=== Removing no_connects from mcu.kicad_sch ===")
mcu_targets = [
    (172.72, 101.6, 'MCU_MODEM_PWR_EN'),
    (172.72, 175.26, 'VBUS_SENSE'),
    (274.32, 78.74, 'SWCLK'),
    (287.02, 99.06, 'SWDIO'),
]
remove_no_connects('mcu.kicad_sch', mcu_targets)

# Modem sheet
print("\n=== Removing no_connects from modem.kicad_sch ===")
modem_targets = [
    (119.38, 85.09, 'NET_STATUS'),
]
remove_no_connects('modem.kicad_sch', modem_targets)

# Verify s-expression balance
print("\n=== Verifying balance ===")
for fname in ['mcu.kicad_sch', 'modem.kicad_sch']:
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    depth = 0
    ok = True
    for i, c in enumerate(content):
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth < 0:
                print(f"  {fname}: ERROR extra closing paren")
                ok = False
                break
    if ok:
        if depth != 0:
            print(f"  {fname}: ERROR final depth = {depth}")
        else:
            print(f"  {fname}: OK")

print("\nDone. Now use MCP tools to add components.")
