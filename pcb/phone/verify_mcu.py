import re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('mcu.kicad_sch', 'r', encoding='utf-8') as f:
    content = f.read()
depth = 0
ok = True
for i, c in enumerate(content):
    if c == '(':
        depth += 1
    elif c == ')':
        depth -= 1
        if depth < 0:
            print(f'ERROR: extra closing paren at position {i}')
            ok = False
            break
if ok:
    if depth != 0:
        print(f'ERROR: final depth = {depth}')
    else:
        print('S-expression balance OK')
for ref in ['R11', 'R12', 'R13']:
    if f'"{ref}"' in content:
        print(f'{ref}: found')
    else:
        print(f'{ref}: NOT found')
for label in ['MCU_MODEM_PWR_EN', 'VBUS_SENSE']:
    count = len(re.findall(rf'global_label "{label}"', content))
    print(f'Global label {label}: {count} found')
