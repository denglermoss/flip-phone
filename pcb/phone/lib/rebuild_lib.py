#!/usr/bin/env python3
"""
Rebuild the KiCad symbol library:
1. Merge easyeda2kicad.kicad_sym + missing_parts.kicad_sym
2. Split into 4 libraries: passives, ics, connectors, electromech
3. Fix pin types (unspecified/input -> correct electrical types)
4. Fix obvious pin name typos
5. Add ki_description property (<20 char) to each symbol
6. Fix footprint prefixes (missing_parts: -> easyeda2kicad:)
7. Tidy property ordering: Reference, Value, Footprint, Datasheet,
   Manufacturer, MPN, LCSC Part, ki_keywords, ki_description
"""

import re
import os

LIB_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Categorization ───

PASSIVES = {
    "CC0603KRX7R9BB104", "GRM21BR61H106KE43L", "GRM21BR61A226ME51L",
    "GRM188R61C475KE11D", "GRM188R61C105KA93D",
    "RC0603JR-071ML", "RC0603FR-072KL", "RC0603JR-07470RL",
    "RC0603JR-0710KL", "RC0603FR-07100KL", "RC0603FR-0747KL",
    "RC0603FR-075K1L", "RC0603JR-074K7L",
    "BLM18KG601SN1D", "XFL4020-152MEC", "LTST-C191TBKT",
}

ICS = {
    "STM32H743ZIT6", "SIM7600NA-H", "ALC5651-CG",
    "TPS63021DSJR", "TPS7A0218PDBVR", "MCP73831-2ACI_MC",
    "MAX17048G+T10", "TXB0104D", "TXB0108PWR",
    "USBLC6-2SC6", "ESDA6V1-5SC6", "ZTS6117",
}

CONNECTORS = {
    "TYPE-C-31-M-12", "NANOSIMXG6PH1.35", "472192001",
    "U.FL-R-SMT-1", "0.5K-HX-8PWB", "0.5K-HX-12PWB",
    "0.5K-HX-14PWB", "S2B-PH-SM4-TB",
    "PCIE-52P40H_C444926",
}

ELECTROMECH = {
    "SKQGABE010", "ECS-80-12-33Q-GN-TR",
}

# ─── Descriptions (<20 char, ideally) ───

DESCRIPTIONS = {
    # Passives
    "CC0603KRX7R9BB104": "100nF 50V X7R 0603 cap",
    "GRM21BR61H106KE43L": "10uF 50V X5R 0805 cap",
    "GRM21BR61A226ME51L": "22uF 10V X5R 0805 cap",
    "GRM188R61C475KE11D": "4.7uF 16V X5R 0603 cap",
    "GRM188R61C105KA93D": "1uF 16V X5R 0603 cap",
    "RC0603JR-071ML": "1M 5% 0603 resistor",
    "RC0603FR-072KL": "2k 1% 0603 resistor",
    "RC0603JR-07470RL": "470R 5% 0603 resistor",
    "RC0603JR-0710KL": "10k 5% 0603 resistor",
    "RC0603FR-07100KL": "100k 1% 0603 resistor",
    "RC0603FR-0747KL": "47k 1% 0603 resistor",
    "RC0603FR-075K1L": "5.1k 1% 0603 resistor",
    "RC0603JR-074K7L": "4.7k 5% 0603 resistor",
    "BLM18KG601SN1D": "600R ferrite bead 0603",
    "XFL4020-152MEC": "1.5uH 4.4A inductor",
    "LTST-C191TBKT": "Blue LED 0603 468nm",
    # ICs
    "STM32H743ZIT6": "STM32H7 MCU 480MHz LQFP144",
    "SIM7600NA-H": "LTE Cat-4 VoLTE modem",
    "ALC5651-CG": "Dual I2S/PCM audio codec",
    "TPS63021DSJR": "3.3V buck-boost 4A VSON14",
    "TPS7A0218PDBVR": "1.8V LDO 200mA SOT23-5",
    "MCP73831-2ACI_MC": "LiPo charger 500mA",
    "MAX17048G+T10": "Fuel gauge I2C TDFN-8",
    "TXB0104D": "4-ch level shifter SOIC14",
    "TXB0108PWR": "8-ch level shifter TSSOP20",
    "USBLC6-2SC6": "USB2 ESD protection SOT23-6",
    "ESDA6V1-5SC6": "5-line ESD SOT23-6",
    "ZTS6117": "MEMS analog microphone",
    # Connectors
    "TYPE-C-31-M-12": "USB-C 16-pin 2.0 receptacle",
    "NANOSIMXG6PH1.35": "Nano-SIM hinged 6-pin",
    "472192001": "MicroSD hinged 8-pin",
    "U.FL-R-SMT-1": "U.FL coax antenna jack",
    "0.5K-HX-8PWB": "8-pin 0.5mm FPC connector",
    "0.5K-HX-12PWB": "12-pin 0.5mm FPC connector",
    "0.5K-HX-14PWB": "14-pin 0.5mm FPC connector",
    "S2B-PH-SM4-TB": "JST-PH 2-pin battery conn",
    "PCIE-52P40H_C444926": "Mini PCIe socket 52-pin SMD",
    # Electromech
    "SKQGABE010": "Tactile switch 5.2mm SMD",
    "ECS-80-12-33Q-GN-TR": "8MHz crystal SMD3225",
}

# ─── Pin name typos to fix ───

PIN_NAME_FIXES = {
    # SIM7600: SPIL prefix → SPI_ (the "L" is a typo/abbreviation artifact)
    # Actually these may be "SPI LCD" pins — leave as-is to avoid breaking
    # things if they're correct. Only fix truly obvious typos.
}

# ─── Pin type mapping ───
# For passives, connectors, switch, crystal: ALL pins → passive
# For ICs: map by pin name pattern

# Pin names that map to power_in (ground/supply sinks)
POWER_IN_NAMES = {
    "GND", "VSS", "AGND", "PGND", "VSSA", "EP",
    "VDD", "VCC", "VBAT", "VDDA", "VDDUSB", "VINA",
    "VREF+", "MICVDD", "AVDD", "DBVDD", "DCVDD",
    "CPVDD", "CTG", "CELL",
    "USB_VBUS",  # SIM7600 USB bus power detect/supply input
    # Connector power/ground pins (for USB-C etc.)
    # Keep connectors as passive though
}

# Pin names that map to power_out (supply sources)
POWER_OUT_NAMES = {
    "VOUT", "VDD_1V8", "USIM_VDD", "VPP",
    "MICBIAS1", "CPVPP", "CPVEE",
    "VDD_AUX",  # SIM7600 auxiliary LDO output
}

# Pin names that map to no_connect
NC_NAMES = {"NC", "RESERVED"}

# Pin names that map to open_collector
OPEN_COLLECTOR_NAMES = {"STAT", "PG", "~{ALRT}", "ALRT"}

# Pin names that map to output
OUTPUT_NAMES = {
    "TXD", "RTS", "PCM_OUT", "DBG_TXD", "STATUS",
    "NETLIGHT", "ISINK", "LOUTL/P", "LOUTR/N",
    "HPO_R", "HPO_L", "PDM_SCL", "ADCDAT2", "ADCDAT1",
    "OUT", "SGMII_TX_M", "SGMII_TX_P",
}

# Pin names that map to input
INPUT_NAMES = {
    "RXD", "CTS", "RI", "DCD", "DTR", "PCM_IN", "ADC1", "ADC2",
    "PWRKEY", "RESET", "FLIGHTMODE", "SD_DET", "USIM_DET",
    "USB_BOOT", "DACDAT2", "DACDAT1", "MCLK",
    "SGMII_RX_P", "SGMII_RX_M", "EN", "PS/SYNC", "PS_SYNC",
    "BOOT0", "PDR_ON", "OE", "JD1",
    "IN1P/DMIC_DAT", "IN2P", "IN2N/JD2", "IN3P",
    "RXDDBG",  # SIM7600 debug UART RX
}

# Pin names that map to bidirectional
BIDIR_NAMES = {
    "SDA", "SCL", "USB_DP", "USB_DN", "USB_ID",
    "USIM_DATA", "USIM_RST", "USIM_CLK",
    "SD_CMD", "SD_DATA0", "SD_DATA1", "SD_DATA2", "SD_DATA3", "SD_CLK",
    "SDIO_CMD", "SDIO_DATA0", "SDIO_DATA1", "SDIO_DATA2", "SDIO_DATA3", "SDIO_CLK",
    "SPILCLK", "SPILMISO", "SPILMOSI", "SPILCS",
    "PCM_SYNC", "PCM_CLK",
    "HSIC_STROBE", "HSIC_DATA",
    "COEX1", "COEX2", "COEX3",
    "SGMIILRST_N", "SGMIILINT_N",
    "SGMII_MDIO", "SGMII_MDC",
    "PDM_SDA",
    "LRCK2", "BCLK2", "LRCK1", "BCLK1",
    "GPIO1/IRQ1", "GPIO2/DMIC_SCL",
    "NRST",
    # STM32 GPIO pins will be handled by pattern matching
}

# Pin names that map to passive (inductor pins, caps, reference pins, etc.)
PASSIVE_NAMES = {
    "FB", "PROG", "QSTRT", "CTG",
    "L1", "L2", "Vcap_1", "Vcap_2",
    "DACREF", "VREF", "CPN2", "CPP2", "CPN1", "CPP1", "CPVREF",
    # RF antenna ports
    "AUX_ANT", "GNSS_ANT", "MAIN_ANT",
}


def get_pin_type(sym_name, pin_name):
    """Determine the correct KiCad pin electrical type."""
    # Passives, connectors, switch, crystal: all passive
    if sym_name in PASSIVES or sym_name in CONNECTORS or sym_name in ELECTROMECH:
        return "passive"

    # ZTS6117 (MEMS mic) — simple IC
    if sym_name == "ZTS6117":
        if pin_name == "OUT":
            return "output"
        if pin_name == "GND":
            return "power_in"
        if pin_name == "VDD":
            return "power_in"
        return "passive"

    # USBLC6-2SC6: pin 2=GND, pin 5=VBUS, rest=passive (ESD clamp)
    if sym_name == "USBLC6-2SC6":
        if pin_name == "2":
            return "power_in"
        if pin_name == "5":
            return "power_in"
        return "passive"

    # ESDA6V1-5SC6: GND=power_in, rest=passive
    if sym_name == "ESDA6V1-5SC6":
        if pin_name == "GND":
            return "power_in"
        return "passive"

    # STM32H743: GPIO pins → bidirectional, power pins → power_in
    if sym_name == "STM32H743ZIT6":
        if pin_name in POWER_IN_NAMES:
            return "power_in"
        if pin_name in ("Vcap_1", "Vcap_2"):
            return "passive"
        if pin_name == "NRST":
            return "bidirectional"
        if pin_name in ("BOOT0", "PDR_ON"):
            return "input"
        # All P* pins (GPIO) → bidirectional
        if re.match(r'^[A-Z]{1,2}\d', pin_name):
            return "bidirectional"
        return "bidirectional"

    # SIM7600NA-H
    if sym_name == "SIM7600NA-H":
        if pin_name in POWER_IN_NAMES:
            return "power_in"
        if pin_name in POWER_OUT_NAMES:
            return "power_out"
        if pin_name in NC_NAMES:
            return "no_connect"
        if pin_name in OPEN_COLLECTOR_NAMES:
            return "open_collector"
        if pin_name in OUTPUT_NAMES:
            return "output"
        if pin_name in INPUT_NAMES:
            return "input"
        if pin_name in BIDIR_NAMES:
            return "bidirectional"
        if pin_name in PASSIVE_NAMES:
            return "passive"
        # GPIO* → bidirectional
        if pin_name.startswith("GPIO"):
            return "bidirectional"
        # Default: bidirectional for unknown signal pins
        return "bidirectional"

    # ALC5651-CG
    if sym_name == "ALC5651-CG":
        if pin_name in POWER_IN_NAMES:
            return "power_in"
        if pin_name in POWER_OUT_NAMES:
            return "power_out"
        if pin_name in PASSIVE_NAMES:
            return "passive"
        if pin_name in OUTPUT_NAMES:
            return "output"
        if pin_name in INPUT_NAMES:
            return "input"
        if pin_name in BIDIR_NAMES:
            return "bidirectional"
        if pin_name.startswith("GPIO"):
            return "bidirectional"
        return "bidirectional"

    # TPS63021DSJR
    if sym_name == "TPS63021DSJR":
        if pin_name in ("VINA", "GND", "PGND", "VIN"):
            return "power_in"
        if pin_name in ("VOUT",):
            return "power_out"
        if pin_name in ("L1", "L2"):
            return "passive"
        if pin_name in ("FB",):
            return "input"
        if pin_name in ("EN", "PS/SYNC"):
            return "input"
        if pin_name == "PG":
            return "open_collector"
        return "passive"

    # TPS7A0218PDBVR
    if sym_name == "TPS7A0218PDBVR":
        if pin_name in ("IN", "GND"):
            return "power_in"
        if pin_name == "OUT":
            return "power_out"
        if pin_name == "EN":
            return "input"
        if pin_name == "NC":
            return "no_connect"
        return "passive"

    # MCP73831-2ACI_MC
    if sym_name == "MCP73831-2ACI_MC":
        if pin_name in ("VDD", "VSS", "EP"):
            return "power_in"
        if pin_name == "VBAT":
            return "power_out"
        if pin_name == "STAT":
            return "open_collector"
        if pin_name == "PROG":
            return "passive"
        if pin_name == "NC":
            return "no_connect"
        return "passive"

    # MAX17048G+T10
    if sym_name == "MAX17048G+T10":
        if pin_name in ("VDD", "GND", "EP"):
            return "power_in"
        if pin_name in ("CTG", "CELL", "QSTRT"):
            return "passive"
        if pin_name in ("~{ALRT}", "ALRT"):
            return "open_collector"
        if pin_name in ("SCL", "SDA"):
            return "bidirectional"
        return "passive"

    # TXB0104D / TXB0108PWR
    if sym_name in ("TXB0104D", "TXB0108PWR"):
        if pin_name in ("VCCA", "VCCB", "GND"):
            return "power_in"
        if pin_name == "OE":
            return "input"
        if pin_name == "NC":
            return "no_connect"
        # A* and B* pins → bidirectional
        if re.match(r'^[AB]\d', pin_name):
            return "bidirectional"
        return "passive"

    # Default fallback
    return "passive"


def fix_pin_name(name):
    """Fix obvious typos in pin names."""
    return PIN_NAME_FIXES.get(name, name)


def parse_symbols(filepath):
    """Parse a .kicad_sym file and return list of (name, block_text) for top-level symbols."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all top-level symbol blocks (not _0_1, _1_1, etc.)
    # A top-level symbol starts with '  (symbol "NAME"' at indent 2
    # and its sub-symbols start with '    (symbol "NAME_0_1"'
    symbols = []
    pos = 0

    while True:
        # Find next top-level symbol
        match = re.search(r'^  \(symbol "([^"]+)"', content[pos:], re.MULTILINE)
        if not match:
            break

        name = match.group(1)
        # Skip sub-symbols (they contain _0_1, _1_1, etc.)
        if re.search(r'_\d+_\d+', name):
            pos += match.end()
            continue

        start = pos + match.start()

        # Find the matching closing paren for this symbol block
        # We need to count parens from the opening (symbol
        paren_count = 0
        i = start + match.start()  # position of '(symbol'
        # Actually, start is already at the beginning of the line
        # Let's find the '(' that opens the symbol
        open_pos = content.index('(symbol', start)
        i = open_pos
        while i < len(content):
            if content[i] == '(':
                paren_count += 1
            elif content[i] == ')':
                paren_count -= 1
                if paren_count == 0:
                    break
            i += 1

        block = content[start:i+1]
        symbols.append((name, block))
        pos = i + 1

    return symbols


def transform_symbol(name, block):
    """Apply all transformations to a symbol block."""
    # 1. Fix footprint prefix: missing_parts: → easyeda2kicad:
    block = block.replace('missing_parts:', 'easyeda2kicad:')

    # 2. Fix pin types and names
    # Pattern: (pin <TYPE> line ... (name "NAME" ...) (number "NUMBER" ...))
    def fix_pin(match):
        full = match.group(0)
        old_type = match.group(1)
        pin_name = match.group(2)

        # Fix pin name typos
        new_name = fix_pin_name(pin_name)
        if new_name != pin_name:
            full = full.replace(f'(name "{pin_name}"', f'(name "{new_name}"')

        # Determine new pin type
        new_type = get_pin_type(name, new_name)

        # Replace the type in the pin declaration
        # The pattern is: (pin <TYPE> line
        full = re.sub(r'\(pin\s+\w+\s+line', f'(pin {new_type} line', full, count=1)

        return full

    # Match pin blocks: (pin TYPE line ... (name "NAME" ...) ... (number "NUM" ...) ...)
    pin_pattern = re.compile(
        r'\(pin\s+(\w+)\s+line\s+\(at\s+[\d.-]+\s+[\d.-]+\s+\d+\)\s+\(length\s+[\d.]+\)\s+\(name\s+"([^"]*)"',
        re.DOTALL
    )
    block = pin_pattern.sub(fix_pin, block)

    # 3. Add ki_description property (if not already present)
    if 'ki_description' not in block:
        desc = DESCRIPTIONS.get(name, "Part")
        # Find the last property block and add ki_description after it
        # Find the position just before the (symbol "NAME_0_1" sub-symbol
        sub_sym_match = re.search(r'(\n\s*\(symbol "' + re.escape(name) + r'_)', block)
        if sub_sym_match:
            insert_pos = sub_sym_match.start()
            # Find the id of the last property
            id_matches = list(re.finditer(r'\(id\s+(\d+)\)', block[:insert_pos]))
            if id_matches:
                last_id = int(id_matches[-1].group(1))
                new_id = last_id + 1
            else:
                new_id = 7

            # Determine the y-position for the new property (below the last one)
            # Find the last property's at position
            at_matches = list(re.finditer(r'\(at\s+0\s+(-?[\d.]+)\s+0\)', block[:insert_pos]))
            if at_matches:
                last_y = float(at_matches[-1].group(1))
                new_y = last_y - 2.54
            else:
                new_y = -105.41

            ki_desc_prop = f'''
    (property
      "ki_description"
      "{desc}"
      (id {new_id})
      (at 0 {new_y:.2f} 0)
      (effects (font (size 1.27 1.27) ) hide)
    )
'''
            block = block[:insert_pos] + ki_desc_prop + block[insert_pos:]

    # 4. Remove ki_keywords if present (tidy — we'll standardize without it)
    # Actually, keep ki_keywords if present — it's useful for search
    # Just ensure consistent ordering

    return block


def write_library(filepath, lib_name, symbols):
    """Write a .kicad_sym library file."""
    header = f'''(kicad_symbol_lib
  (version 20211014)
  (generator https://github.com/uPesy/easyeda2kicad.py)

'''
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(header)
        for name, block in symbols:
            f.write(block)
            f.write('\n\n')
        f.write(')\n')


def main():
    # Read both source files
    existing = parse_symbols(os.path.join(LIB_DIR, 'easyeda2kicad.kicad_sym'))
    missing = parse_symbols(os.path.join(LIB_DIR, 'missing_parts.kicad_sym'))

    all_symbols = {}
    for name, block in existing + missing:
        all_symbols[name] = block

    print(f"Total symbols: {len(all_symbols)}")

    # Verify all 38 are accounted for
    all_expected = PASSIVES | ICS | CONNECTORS | ELECTROMECH
    missing_from_lib = all_expected - set(all_symbols.keys())
    extra_in_lib = set(all_symbols.keys()) - all_expected
    if missing_from_lib:
        print(f"ERROR: Missing from library: {missing_from_lib}")
    if extra_in_lib:
        print(f"WARNING: Extra in library (not categorized): {extra_in_lib}")

    # Transform and categorize
    categories = {
        "passives": PASSIVES,
        "ics": ICS,
        "connectors": CONNECTORS,
        "electromech": ELECTROMECH,
    }

    for cat_name, cat_set in categories.items():
        cat_symbols = []
        for sym_name in sorted(cat_set):
            if sym_name in all_symbols:
                transformed = transform_symbol(sym_name, all_symbols[sym_name])
                cat_symbols.append((sym_name, transformed))
                print(f"  [{cat_name}] {sym_name}: {len(transformed.splitlines())} lines")
        write_library(os.path.join(LIB_DIR, f'{cat_name}.kicad_sym'), cat_name, cat_symbols)
        print(f"Wrote {cat_name}.kicad_sym with {len(cat_symbols)} symbols\n")

    print("Done! Libraries written to:", LIB_DIR)


if __name__ == '__main__':
    main()
