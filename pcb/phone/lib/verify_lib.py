import re
from collections import Counter

for lib in ['passives', 'ics', 'connectors', 'electromech']:
    with open(f'{lib}.kicad_sym', 'r', encoding='utf-8') as f:
        content = f.read()

    types = re.findall(r'\(pin\s+(\w+)\s+line', content)
    counts = Counter(types)

    has_desc = len(re.findall(r'ki_description', content))

    # Count top-level symbols (indent 2, not sub-symbols with _0_1)
    all_syms = re.findall(r'^  \(symbol "([^"]+)"', content, re.MULTILINE)
    top_syms = [s for s in all_syms if not re.search(r'_\d+_\d+$', s)]

    print(f'{lib}.kicad_sym: {len(top_syms)} symbols, {has_desc} ki_descriptions')
    for t, c in sorted(counts.items()):
        print(f'  {t:>15s}: {c}')
    print()

    # Show any remaining 'unspecified' or 'input' pins (should be none except where intended)
    bad = [(t) for t in types if t in ('unspecified',)]
    if bad:
        print(f'  WARNING: {len(bad)} unspecified pins remain!')
    print()
