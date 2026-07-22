#!/usr/bin/env python3
"""Update schematic symbol references from easyeda2kicad: to new library names."""

import re

SCH_PATH = r'C:\Users\dengle\Documents\personal_projects\phone\pcb\phone\phone.kicad_sch'

# Map symbol names to new library prefixes
SYM_TO_LIB = {
    # Passives
    "CC0603KRX7R9BB104": "passives",
    "GRM188R61C105KA93D": "passives",
    "GRM188R61C475KE11D": "passives",
    "GRM21BR61A226ME51L": "passives",
    "GRM21BR61H106KE43L": "passives",
    "LTST-C191TBKT": "passives",
    "RC0603FR-072KL": "passives",
    "RC0603FR-075K1L": "passives",
    "RC0603JR-0710KL": "passives",
    "RC0603JR-071ML": "passives",
    "RC0603JR-07470RL": "passives",
    "XFL4020-152MEC": "passives",
    # ICs
    "MAX17048G+T10": "ics",
    "MCP73831-2ACI_MC": "ics",
    "TPS63021DSJR": "ics",
    "TPS7A0218PDBVR": "ics",
    "USBLC6-2SC6": "ics",
    # Connectors
    "S2B-PH-SM4-TB": "connectors",
    "TYPE-C-31-M-12": "connectors",
}

with open(SCH_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = 0
for sym_name, lib_name in SYM_TO_LIB.items():
    old = f'easyeda2kicad:{sym_name}'
    new = f'{lib_name}:{sym_name}'
    count = content.count(old)
    if count:
        content = content.replace(old, new)
        replacements += count
        print(f'  {old} -> {new} ({count} occurrences)')

with open(SCH_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nTotal replacements: {replacements}')

# Verify no remaining easyeda2kicad: references (except footprints)
remaining = re.findall(r'"easyeda2kicad:([^"]+)"', content)
sym_refs = [r for r in remaining if not r.startswith(('C0603', 'C0805', 'R0603', 'L0603', 'LED', 'TDFN', 'VSON', 'SOT', 'SOIC', 'TSSOP', 'QFN', 'LQFP', 'USB-C', 'CONN', 'SIM', 'TF', 'ANT', 'FPC', 'IND', 'KEY', 'MIC', 'CRYSTAL', 'COMM'))]
if sym_refs:
    print(f'WARNING: Remaining easyeda2kicad symbol references: {sym_refs}')
else:
    print('OK: No remaining easyeda2kicad symbol references (footprint refs are fine)')
