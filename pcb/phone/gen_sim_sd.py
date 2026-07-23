#!/usr/bin/env python3
"""Generate sim_sd.kicad_sch - SIM card + microSD card + ESD protection."""
import uuid

SIM_SD_SCH_UUID = '7fc639d9-249c-4f41-85eb-7c2617f3c206'
ROOT_UUID = '451c3b43-1616-42cb-bf96-d436f4db82c2'

# Component positions
J_SIM_X, J_SIM_Y = 140.0, 100.0
J_SD_X, J_SD_Y   = 200.0, 100.0
U10_X, U10_Y     = 95.0, 100.0    # ESD for SIM
U11_X, U11_Y     = 250.0, 100.0   # ESD for SD
C38_X, C38_Y     = 140.0, 130.0   # SIM decoupling
C39_X, C39_Y     = 200.0, 140.0   # SD decoupling
R15_X, R15_Y     = 95.0, 130.0    # SIM data pull-up

STUB = 5.08
PWR_START = 150

def gen_uuid():
    return str(uuid.uuid4())

# Pin offsets from symbol definitions (relative to symbol origin)
SIM_PINS = {
    1: (-8.89, 6.35),    # VCC
    2: (-8.89, 3.81),    # RST
    3: (-8.89, 1.27),    # CLK
    5: (-8.89, -1.27),   # GND
    6: (-8.89, -3.81),   # VPP
    7: (-8.89, -6.35),   # I/O
    8: (8.89, -6.35),    # GND
    9: (8.89, -3.81),    # GND
    10: (8.89, 3.81),    # GND
    11: (8.89, 6.35),    # GND
}

SD_PINS = {
    1: (-10.16, 8.89),   # DAT2
    2: (-10.16, 6.35),   # CD/DAT3
    3: (-10.16, 3.81),   # CMD
    4: (-10.16, 1.27),   # VDD
    5: (-10.16, -1.27),  # CLK
    6: (-10.16, -3.81),  # VSS
    7: (-10.16, -6.35),  # DAT0
    8: (-10.16, -8.89),  # DAT1
    9: (10.16, -3.81),   # Shell/CD
    10: (10.16, -1.27),  # Shell
    11: (10.16, 1.27),   # Shell
    12: (10.16, 3.81),   # Shell
}

ESD_PINS = {
    1: (-13.97, 5.08),   # IO1
    2: (-13.97, 0),      # GND
    3: (-13.97, -5.08),  # IO2
    4: (13.97, -5.08),   # IO3
    5: (13.97, 0),       # IO4
    6: (13.97, 5.08),    # IO5
}

def fw(x1, y1, x2, y2):
    return '\t\t(wire\n\t\t\t(pts\n\t\t\t\t(xy %.2f %.2f) (xy %.2f %.2f)\n\t\t\t)\n\t\t\t(stroke\n\t\t\t\t(width 0)\n\t\t\t\t(type default)\n\t\t\t)\n\t\t\t(uuid "%s")\n\t\t)\n' % (x1, y1, x2, y2, gen_uuid())

def fgl(name, shape, x, y, orient):
    j = 'left' if orient == 0 else ('right' if orient == 180 else ('bottom' if orient == 90 else 'top'))
    s = '\t\t(global_label "%s"\n' % name
    s += '\t\t\t(shape %s)\n' % shape
    s += '\t\t\t(at %.2f %.2f %d)\n' % (x, y, orient)
    s += '\t\t\t(fields_autoplaced yes)\n'
    s += '\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n'
    s += '\t\t\t\t(justify %s)\n\t\t\t)\n' % j
    s += '\t\t\t(uuid "%s")\n' % gen_uuid()
    s += '\t\t\t(property "Intersheetrefs" "${INTERSHEET_REFS}"\n'
    s += '\t\t\t\t(at %.2f %.2f 0)\n' % (x, y)
    s += '\t\t\t\t(hide yes) (show_name no) (do_not_autoplace no)\n'
    s += '\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n'
    s += '\t\t\t\t\t(justify %s)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n' % j
    return s

def fnc(x, y):
    return '\t\t(no_connect (at %.2f %.2f) (uuid "%s"))\n' % (x, y, gen_uuid())

def fpwr(lib_id, x, y, rot, ref, path):
    u = gen_uuid(); pu = gen_uuid()
    if '+3.3V' in lib_id:
        val = '+3.3V'; desc = 'Power symbol creates a global label with name \\"+3.3V\\"'
    else:
        val = 'GND'; desc = 'Power symbol creates a global label with name \\"GND\\" , ground'
    s = '\t\t(symbol\n'
    s += '\t\t\t(lib_id "%s")\n' % lib_id
    s += '\t\t\t(at %.2f %.2f %d)\n' % (x, y, rot)
    s += '\t\t\t(unit 1) (body_style 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no) (fields_autoplaced yes)\n'
    s += '\t\t\t(uuid "%s")\n' % u
    s += '\t\t\t(property "Reference" "%s"\n' % ref
    s += '\t\t\t\t(at %.2f %.2f 0)\n' % (x, y)
    s += '\t\t\t\t(hide yes) (show_name no) (do_not_autoplace no)\n'
    s += '\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s += '\t\t\t(property "Value" "%s"\n' % val
    s += '\t\t\t\t(at %.2f %.2f 0)\n' % (x, y)
    s += '\t\t\t\t(show_name no) (do_not_autoplace no)\n'
    s += '\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s += '\t\t\t(property "Footprint" ""\n'
    s += '\t\t\t\t(at %.2f %.2f 0)\n' % (x, y)
    s += '\t\t\t\t(hide yes) (show_name no) (do_not_autoplace no)\n'
    s += '\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s += '\t\t\t(property "Datasheet" ""\n'
    s += '\t\t\t\t(at %.2f %.2f 0)\n' % (x, y)
    s += '\t\t\t\t(hide yes) (show_name no) (do_not_autoplace no)\n'
    s += '\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s += '\t\t\t(property "Description" "%s"\n' % desc
    s += '\t\t\t\t(at %.2f %.2f 0)\n' % (x, y)
    s += '\t\t\t\t(hide yes) (show_name no) (do_not_autoplace no)\n'
    s += '\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s += '\t\t\t(pin "1" (uuid "%s"))\n' % pu
    s += '\t\t\t(instances (project "phone" (path "%s" (reference "%s") (unit 1))))\n' % (path, ref)
    s += '\t\t)\n'
    return s

def extract_sym(filepath, name):
    with open(filepath, 'r', encoding='utf-8') as f:
        c = f.read()
    m = '(symbol "' + name + '"'
    s = c.find(m)
    if s == -1:
        raise ValueError(name + ' not found in ' + filepath)
    d = 0; i = s
    while i < len(c):
        if c[i] == '(':
            d += 1
        elif c[i] == ')':
            d -= 1
            if d == 0:
                return c[s:i+1]
        i += 1

def fix_libid(sym, prefix):
    return sym.replace('(symbol "', '(symbol "' + prefix + ':', 1)

def comp_sym(lib_id, x, y, rot, ref, value, footprint, datasheet, description, pin_count, path, hide_value=False):
    s = '\t\t(symbol\n'
    s += '\t\t\t(lib_id "%s")\n' % lib_id
    s += '\t\t\t(at %.2f %.2f %d)\n' % (x, y, rot)
    s += '\t\t\t(unit 1) (body_style 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no) (fields_autoplaced yes)\n'
    s += '\t\t\t(uuid "%s")\n' % gen_uuid()
    s += '\t\t\t(property "Reference" "%s"\n' % ref
    s += '\t\t\t\t(at %.2f %.2f 0)\n' % (x, y - 5.0)
    s += '\t\t\t\t(show_name no) (do_not_autoplace no)\n'
    s += '\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    hv = ' (hide yes)' if hide_value else ''
    s += '\t\t\t(property "Value" "%s"\n' % value
    s += '\t\t\t\t(at %.2f %.2f 0)\n' % (x, y + 5.0)
    s += '\t\t\t\t%s(show_name no) (do_not_autoplace no)\n' % hv
    s += '\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s += '\t\t\t(property "Footprint" "%s"\n' % footprint
    s += '\t\t\t\t(at %.2f %.2f 0)\n' % (x, y)
    s += '\t\t\t\t(hide yes) (show_name no) (do_not_autoplace no)\n'
    s += '\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s += '\t\t\t(property "Datasheet" "%s"\n' % datasheet
    s += '\t\t\t\t(at %.2f %.2f 0)\n' % (x, y)
    s += '\t\t\t\t(hide yes) (show_name no) (do_not_autoplace no)\n'
    s += '\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s += '\t\t\t(property "Description" "%s"\n' % description
    s += '\t\t\t\t(at %.2f %.2f 0)\n' % (x, y)
    s += '\t\t\t\t(hide yes) (show_name no) (do_not_autoplace no)\n'
    s += '\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    for pn in range(1, pin_count + 1):
        s += '\t\t\t(pin "%d" (uuid "%s"))\n' % (pn, gen_uuid())
    s += '\t\t\t(instances (project "phone" (path "%s" (reference "%s") (unit 1))))\n' % (path, ref)
    s += '\t\t)\n'
    return s

def pin_pos(cx, cy, offset, rot=0):
    """Calculate absolute pin position given component center and pin offset."""
    dx, dy = offset
    if rot == 0:
        return (cx + dx, cy + dy)
    elif rot == 90:
        return (cx - dy, cy + dx)
    elif rot == 180:
        return (cx - dx, cy - dy)
    elif rot == 270:
        return (cx + dy, cy - dx)
    return (cx + dx, cy + dy)

def generate():
    sp = '/' + ROOT_UUID + '/' + SIM_SD_SCH_UUID

    # Extract lib_symbols
    syms = []
    for fp, name, prefix in [
        ('lib/connectors.kicad_sym', 'NANOSIMXG6PH1.35', 'connectors'),
        ('lib/connectors.kicad_sym', '472192001', 'connectors'),
        ('lib/ics.kicad_sym', 'ESDA6V1-5SC6', 'ics'),
        ('lib/passives.kicad_sym', 'CC0603KRX7R9BB104', 'passives'),
        ('lib/passives.kicad_sym', 'RC0603JR-0710KL', 'passives'),
    ]:
        syms.append(fix_libid(extract_sym(fp, name), prefix))
    for name in ['power:+3.3V', 'power:GND']:
        syms.append(extract_sym('modem.kicad_sch', name))

    ls = '\t(lib_symbols\n'
    for sym in syms:
        for line in sym.split('\n'):
            ls += '\t\t' + line + '\n'
    ls += '\t)\n'

    comp = ''; wires = ''; labels = ''; ncs = ''
    pc = PWR_START

    # === Place components ===
    comp += comp_sym('connectors:NANOSIMXG6PH1.35', J_SIM_X, J_SIM_Y, 0, 'J_SIM',
                     'NANOSIMXG6PH1.35', 'easyeda2kicad:SIM-SMD_NANO-SIM-XG6P-H1.35',
                     'https://www.lcsc.com/datasheet/C7529386.pdf',
                     'Nano-SIM hinged 6-pin', 10, sp, hide_value=True)
    comp += comp_sym('connectors:472192001', J_SD_X, J_SD_Y, 0, 'J_SD',
                     '472192001', 'easyeda2kicad:TF-SMD_472192001',
                     'https://lcsc.com/product-detail/Card-Sockets_MOLEX_472192001_472192001_C164170.html',
                     'MicroSD hinged 8-pin', 12, sp, hide_value=True)
    comp += comp_sym('ics:ESDA6V1-5SC6', U10_X, U10_Y, 0, 'U10',
                     'ESDA6V1-5SC6', 'easyeda2kicad:SOT-23-6_L2.9-W1.6-P0.95-LS2.8-BR',
                     'https://lcsc.com/product-detail/TVS_STMicroelectronics_ESDA6V1-5SC6_ESDA6V1-5SC6_C6650.html',
                     'ESD protection for SIM', 6, sp, hide_value=True)
    comp += comp_sym('ics:ESDA6V1-5SC6', U11_X, U11_Y, 0, 'U11',
                     'ESDA6V1-5SC6', 'easyeda2kicad:SOT-23-6_L2.9-W1.6-P0.95-LS2.8-BR',
                     'https://lcsc.com/product-detail/TVS_STMicroelectronics_ESDA6V1-5SC6_ESDA6V1-5SC6_C6650.html',
                     'ESD protection for SD card', 6, sp, hide_value=True)
    comp += comp_sym('passives:CC0603KRX7R9BB104', C38_X, C38_Y, 90, 'C38',
                     '100nF', 'easyeda2kicad:C0603', '',
                     '100nF SIM decoupling cap', 2, sp)
    comp += comp_sym('passives:CC0603KRX7R9BB104', C39_X, C39_Y, 90, 'C39',
                     '100nF', 'easyeda2kicad:C0603', '',
                     '100nF SD card decoupling cap', 2, sp)
    comp += comp_sym('passives:RC0603JR-0710KL', R15_X, R15_Y, 0, 'R15',
                     '10k', 'easyeda2kicad:R0603', '',
                     '10k SIM data pull-up resistor', 2, sp)

    # === SIM connector wiring ===
    # J_SIM left pins (signals)
    sim_pin_map = {
        1: ('USIM_VDD', 'bidirectional'),
        2: ('USIM_RST', 'bidirectional'),
        3: ('USIM_CLK', 'bidirectional'),
        7: ('USIM_DATA', 'bidirectional'),
    }
    for pnum, (net, shape) in sim_pin_map.items():
        px, py = pin_pos(J_SIM_X, J_SIM_Y, SIM_PINS[pnum])
        wx = px - STUB
        wires += fw(px, py, wx, py)
        labels += fgl(net, shape, wx, py, 180)

    # J_SIM pin 5 (GND, left side)
    px, py = pin_pos(J_SIM_X, J_SIM_Y, SIM_PINS[5])
    wx = px - STUB
    wires += fw(px, py, wx, py)
    comp += fpwr('power:GND', wx, py, 0, '#PWR%d' % pc, sp); pc += 1

    # J_SIM pin 6 (VPP) - no connect
    px, py = pin_pos(J_SIM_X, J_SIM_Y, SIM_PINS[6])
    ncs += fnc(px, py)

    # J_SIM right pins (all GND)
    for pnum in [8, 9, 10, 11]:
        px, py = pin_pos(J_SIM_X, J_SIM_Y, SIM_PINS[pnum])
        wx = px + STUB
        wires += fw(px, py, wx, py)
        comp += fpwr('power:GND', wx, py, 0, '#PWR%d' % pc, sp); pc += 1

    # === U10 (ESD for SIM) wiring ===
    # Pin 1 (IO1) -> USIM_DATA
    px, py = pin_pos(U10_X, U10_Y, ESD_PINS[1])
    wx = px - STUB
    wires += fw(px, py, wx, py)
    labels += fgl('USIM_DATA', 'bidirectional', wx, py, 180)

    # Pin 2 (GND)
    px, py = pin_pos(U10_X, U10_Y, ESD_PINS[2])
    wx = px - STUB
    wires += fw(px, py, wx, py)
    comp += fpwr('power:GND', wx, py, 0, '#PWR%d' % pc, sp); pc += 1

    # Pin 3 (IO2) -> USIM_RST
    px, py = pin_pos(U10_X, U10_Y, ESD_PINS[3])
    wx = px - STUB
    wires += fw(px, py, wx, py)
    labels += fgl('USIM_RST', 'bidirectional', wx, py, 180)

    # Pin 4 (IO3) -> USIM_CLK
    px, py = pin_pos(U10_X, U10_Y, ESD_PINS[4])
    wx = px + STUB
    wires += fw(px, py, wx, py)
    labels += fgl('USIM_CLK', 'bidirectional', wx, py, 0)

    # Pin 5 (IO4) -> USIM_VDD
    px, py = pin_pos(U10_X, U10_Y, ESD_PINS[5])
    wx = px + STUB
    wires += fw(px, py, wx, py)
    labels += fgl('USIM_VDD', 'bidirectional', wx, py, 0)

    # Pin 6 (IO5) - no connect (unused)
    px, py = pin_pos(U10_X, U10_Y, ESD_PINS[6])
    ncs += fnc(px, py)

    # === C38 (SIM decoupling) wiring ===
    # Pin 1 (top, original offset -5.08,0 with rot 90 -> above center) -> USIM_VDD
    px, py = pin_pos(C38_X, C38_Y, (-5.08, 0), 90)
    wy = py - STUB
    wires += fw(px, py, px, wy)
    labels += fgl('USIM_VDD', 'bidirectional', px, wy, 90)

    # Pin 2 (bottom, original offset 5.08,0 with rot 90 -> below center) -> GND
    px, py = pin_pos(C38_X, C38_Y, (5.08, 0), 90)
    wy = py + STUB
    wires += fw(px, py, px, wy)
    comp += fpwr('power:GND', px, wy, 0, '#PWR%d' % pc, sp); pc += 1

    # === R15 (SIM data pull-up) wiring ===
    # Pin 1 (left) -> USIM_VDD
    px, py = pin_pos(R15_X, R15_Y, (-5.08, 0), 0)
    wx = px - STUB
    wires += fw(px, py, wx, py)
    labels += fgl('USIM_VDD', 'bidirectional', wx, py, 180)

    # Pin 2 (right) -> USIM_DATA
    px, py = pin_pos(R15_X, R15_Y, (5.08, 0), 0)
    wx = px + STUB
    wires += fw(px, py, wx, py)
    labels += fgl('USIM_DATA', 'bidirectional', wx, py, 0)

    # === SD connector wiring ===
    # J_SD left pins (signals)
    sd_signal_map = {
        1: ('SD_D2', 'bidirectional'),
        2: ('SD_D3', 'bidirectional'),
        3: ('SD_CMD', 'bidirectional'),
        5: ('SD_CLK', 'bidirectional'),
        7: ('SD_D0', 'bidirectional'),
        8: ('SD_D1', 'bidirectional'),
    }
    for pnum, (net, shape) in sd_signal_map.items():
        px, py = pin_pos(J_SD_X, J_SD_Y, SD_PINS[pnum])
        wx = px - STUB
        wires += fw(px, py, wx, py)
        labels += fgl(net, shape, wx, py, 180)

    # J_SD pin 4 (VDD) -> +3.3V
    px, py = pin_pos(J_SD_X, J_SD_Y, SD_PINS[4])
    wx = px - STUB
    wires += fw(px, py, wx, py)
    comp += fpwr('power:+3.3V', wx, py, 0, '#PWR%d' % pc, sp); pc += 1

    # J_SD pin 6 (VSS) -> GND
    px, py = pin_pos(J_SD_X, J_SD_Y, SD_PINS[6])
    wx = px - STUB
    wires += fw(px, py, wx, py)
    comp += fpwr('power:GND', wx, py, 0, '#PWR%d' % pc, sp); pc += 1

    # J_SD right pins (shell/CD)
    # Pin 9 -> SD_DET
    px, py = pin_pos(J_SD_X, J_SD_Y, SD_PINS[9])
    wx = px + STUB
    wires += fw(px, py, wx, py)
    labels += fgl('SD_DET', 'bidirectional', wx, py, 0)

    # Pins 10, 11, 12 -> GND (shell/mounting)
    for pnum in [10, 11, 12]:
        px, py = pin_pos(J_SD_X, J_SD_Y, SD_PINS[pnum])
        wx = px + STUB
        wires += fw(px, py, wx, py)
        comp += fpwr('power:GND', wx, py, 0, '#PWR%d' % pc, sp); pc += 1

    # === U11 (ESD for SD) wiring ===
    # Pin 1 (IO1) -> SD_D0
    px, py = pin_pos(U11_X, U11_Y, ESD_PINS[1])
    wx = px - STUB
    wires += fw(px, py, wx, py)
    labels += fgl('SD_D0', 'bidirectional', wx, py, 180)

    # Pin 2 (GND)
    px, py = pin_pos(U11_X, U11_Y, ESD_PINS[2])
    wx = px - STUB
    wires += fw(px, py, wx, py)
    comp += fpwr('power:GND', wx, py, 0, '#PWR%d' % pc, sp); pc += 1

    # Pin 3 (IO2) -> SD_D1
    px, py = pin_pos(U11_X, U11_Y, ESD_PINS[3])
    wx = px - STUB
    wires += fw(px, py, wx, py)
    labels += fgl('SD_D1', 'bidirectional', wx, py, 180)

    # Pin 4 (IO3) -> SD_D2
    px, py = pin_pos(U11_X, U11_Y, ESD_PINS[4])
    wx = px + STUB
    wires += fw(px, py, wx, py)
    labels += fgl('SD_D2', 'bidirectional', wx, py, 0)

    # Pin 5 (IO4) -> SD_D3
    px, py = pin_pos(U11_X, U11_Y, ESD_PINS[5])
    wx = px + STUB
    wires += fw(px, py, wx, py)
    labels += fgl('SD_D3', 'bidirectional', wx, py, 0)

    # Pin 6 (IO5) -> SD_CMD
    px, py = pin_pos(U11_X, U11_Y, ESD_PINS[6])
    wx = px + STUB
    wires += fw(px, py, wx, py)
    labels += fgl('SD_CMD', 'bidirectional', wx, py, 0)

    # === C39 (SD decoupling) wiring ===
    # Pin 1 (top, original offset -5.08,0 with rot 90 -> above center) -> +3.3V
    px, py = pin_pos(C39_X, C39_Y, (-5.08, 0), 90)
    wy = py - STUB
    wires += fw(px, py, px, wy)
    comp += fpwr('power:+3.3V', px, wy, 0, '#PWR%d' % pc, sp); pc += 1

    # Pin 2 (bottom, original offset 5.08,0 with rot 90 -> below center) -> GND
    px, py = pin_pos(C39_X, C39_Y, (5.08, 0), 90)
    wy = py + STUB
    wires += fw(px, py, px, wy)
    comp += fpwr('power:GND', px, wy, 0, '#PWR%d' % pc, sp); pc += 1

    # === Assemble schematic ===
    sch = '(kicad_sch\n'
    sch += '\t(version 20260306)\n'
    sch += '\t(generator "eeschema")\n'
    sch += '\t(generator_version "10.0")\n'
    sch += '\t(uuid "%s")\n' % SIM_SD_SCH_UUID
    sch += '\t(paper "A3")\n'
    sch += '\t(title_block\n\t\t(title "SIM_SD")\n\t)\n'
    sch += ls
    sch += wires
    sch += labels
    sch += ncs
    sch += comp
    sch += '\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n'
    sch += '\t(embedded_fonts no)\n)\n'

    with open('sim_sd.kicad_sch', 'w', encoding='utf-8', newline='\n') as f:
        f.write(sch)
    print('Generated sim_sd.kicad_sch')
    print('  Sheet UUID: %s' % SIM_SD_SCH_UUID)
    print('  Power symbols: #PWR%d through #PWR%d' % (PWR_START, pc - 1))
    print('  Components: J_SIM, J_SD, U10, U11, C38, C39, R15')
    print('  Wires: %d, Labels: %d, No-connects: %d' % (
        wires.count('(wire'), labels.count('(global_label'), ncs.count('(no_connect')))

if __name__ == '__main__':
    generate()