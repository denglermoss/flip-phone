#!/usr/bin/env python3
"""Generate modem.kicad_sch for the phone project."""
import uuid

MODEM_SCH_UUID = '2b7de758-71cc-4198-8a01-5d2c6e01f5f1'
ROOT_UUID = '451c3b43-1616-42cb-bf96-d436f4db82c2'

U2_X, U2_Y = 200.66, 160.02
U8_X, U8_Y = 81.28, 160.02
C31_X, C31_Y = 251.46, 195.58
C32_X, C32_Y = 251.46, 185.42
R11_X, R11_Y = 50.80, 148.59
STUB = 7.62

def gen_uuid():
    return str(uuid.uuid4())

def mpin_x(n):
    return -31.75 + ((n - 1) // 2) * 2.54

def mpin_pos(n):
    # Mounting pins 53 and 54 are at different positions than edge pins
    if n == 53:
        return (U2_X + 39.37, U2_Y)
    if n == 54:
        return (U2_X - 39.37, U2_Y)
    x = U2_X + mpin_x(n)
    y = U2_Y - 10.16 if n % 2 == 1 else U2_Y + 10.16
    return (x, y)

txb_left = {1:11.43,2:8.89,3:6.35,4:3.81,5:1.27,6:-1.27,7:-3.81,8:-6.35,9:-8.89,10:-11.43}
txb_right = {11:-11.43,12:-8.89,13:-6.35,14:-3.81,15:-1.27,16:1.27,17:3.81,18:6.35,19:8.89,20:11.43}

def txb_pos(n):
    if n in txb_left:
        return (U8_X - 12.70, U8_Y + txb_left[n])
    return (U8_X + 12.70, U8_Y + txb_right[n])

mpcie_pins = {
    1:('MODEM_STATUS','output'),2:('PWR_3V3',),3:('NC',),4:('PWR_GND',),5:('NC',),
    6:('NC',),7:('NC',),8:('USIM_VDD','output'),9:('PWR_GND',),10:('USIM_DATA','bidirectional'),
    11:('MODEM_CTS','input'),12:('USIM_CLK','output'),13:('MODEM_RTS','output'),14:('USIM_RST','output'),
    15:('PWR_GND',),16:('USIM_DET','bidirectional'),17:('MODEM_RXD','input'),18:('PWR_GND',),
    19:('MODEM_TXD','output'),20:('NC',),21:('PWR_GND',),22:('MODEM_RST','input'),
    23:('NC',),24:('PWR_3V3',),25:('NC',),26:('PWR_GND',),27:('PWR_GND',),28:('NC',),
    29:('PWR_GND',),30:('NC',),31:('NC',),32:('NC',),33:('NC',),34:('PWR_GND',),
    35:('PWR_GND',),36:('MODEM_USB_DN','bidirectional'),37:('PWR_GND',),38:('MODEM_USB_DP','bidirectional'),
    39:('PWR_3V3',),40:('PWR_GND',),41:('PWR_3V3',),42:('NET_STATUS','output'),
    43:('PWR_GND',),44:('MODEM_RI','output'),45:('PCM_CLK','output'),46:('MODEM_DTR','input'),
    47:('PCM_OUT','output'),48:('NC',),49:('PCM_IN','input'),50:('PWR_GND',),
    51:('PCM_SYNC','output'),52:('PWR_3V3',),53:('PWR_GND',),54:('PWR_GND',),
}

txb_pins = {
    1:('MODEM_TXD','output'),2:('PWR_1V8',),3:('MODEM_RXD','input'),4:('MODEM_RTS','output'),
    5:('MODEM_CTS','input'),6:('MODEM_RI','output'),7:('MODEM_DTR','input'),8:('MODEM_RST','input'),
    9:('MODEM_STATUS','output'),10:('OE_PUP',),11:('PWR_GND',),12:('MCU_MODEM_STATUS','input'),
    13:('MCU_MODEM_RST','output'),14:('MCU_DTR','output'),15:('MCU_RI_IRQ','input'),
    16:('MCU_UART_RTS','output'),17:('MCU_UART_CTS','input'),18:('MCU_UART_TX','output'),
    19:('PWR_3V3',),20:('MCU_UART_RX','input'),
}

def extract_sym(filepath, name):
    with open(filepath, 'r', encoding='utf-8') as f:
        c = f.read()
    m = '(symbol "' + name + '"'
    s = c.find(m)
    if s == -1:
        raise ValueError(name + ' not found in ' + filepath)
    d = 0
    i = s
    while i < len(c):
        if c[i] == '(':
            d += 1
        elif c[i] == ')':
            d -= 1
            if d == 0:
                return c[s:i+1]
        i += 1

def fix_libid(sym, prefix):
    old = '(symbol "'
    new = '(symbol "' + prefix + ':'
    return sym.replace(old, new, 1)

def fw(x1, y1, x2, y2):
    return '\t(wire (pts (xy ' + format(x1, '.2f') + ' ' + format(y1, '.2f') + ') (xy ' + format(x2, '.2f') + ' ' + format(y2, '.2f') + ')) (stroke (width 0) (type default)) (uuid "' + gen_uuid() + '"))\n'

def fgl(name, shape, x, y, orient):
    j = 'left' if orient == 0 else ('right' if orient == 180 else ('bottom' if orient == 90 else 'top'))
    s = '\t(global_label "' + name + '" (shape ' + shape + ') (at ' + format(x, '.2f') + ' ' + format(y, '.2f') + ' ' + str(orient) + ') '
    s += '(fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify ' + j + ')) '
    s += '(uuid "' + gen_uuid() + '") '
    s += '(property "Intersheetrefs" "${INTERSHEET_REFS}" (at ' + format(x, '.2f') + ' ' + format(y, '.2f') + ' 0) '
    s += '(hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27)) (justify ' + j + '))))\n'
    return s

def fnc(x, y):
    return '\t(no_connect (at ' + format(x, '.2f') + ' ' + format(y, '.2f') + ') (uuid "' + gen_uuid() + '"))\n'

def fpwr(lib_id, x, y, rot, ref, path):
    u = gen_uuid()
    pu = gen_uuid()
    if '+3.3V' in lib_id:
        val = '+3.3V'
        desc = 'Power symbol creates a global label with name \\"+3.3V\\"'
    elif '+1V8' in lib_id:
        val = '+1V8'
        desc = 'Power symbol creates a global label with name \\"+1V8\\"'
    else:
        val = 'GND'
        desc = 'Power symbol creates a global label with name \\"GND\\" , ground'
    s = '\t\t(symbol\n'
    s += '\t\t\t(lib_id "' + lib_id + '")\n'
    s += '\t\t\t(at ' + format(x, '.2f') + ' ' + format(y, '.2f') + ' ' + str(rot) + ')\n'
    s += '\t\t\t(unit 1) (body_style 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no) (fields_autoplaced yes)\n'
    s += '\t\t\t(uuid "' + u + '")\n'
    s += '\t\t\t(property "Reference" "' + ref + '" (at ' + format(x, '.2f') + ' ' + format(y, '.2f') + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    s += '\t\t\t(property "Value" "' + val + '" (at ' + format(x, '.2f') + ' ' + format(y, '.2f') + ' 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    s += '\t\t\t(property "Footprint" "" (at ' + format(x, '.2f') + ' ' + format(y, '.2f') + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    s += '\t\t\t(property "Datasheet" "" (at ' + format(x, '.2f') + ' ' + format(y, '.2f') + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    s += '\t\t\t(property "Description" "' + desc + '" (at ' + format(x, '.2f') + ' ' + format(y, '.2f') + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    s += '\t\t\t(pin "1" (uuid "' + pu + '"))\n'
    s += '\t\t\t(instances (project "phone" (path "' + path + '" (reference "' + ref + '") (unit 1))))\n'
    s += '\t\t)\n'
    return s

def generate():
    sp = '/' + ROOT_UUID + '/' + MODEM_SCH_UUID

    # Extract lib symbols
    syms = []
    for fp, name, prefix in [
        ('lib/connectors.kicad_sym', 'PCIE-52P40H_C444926', 'connectors'),
        ('lib/ics.kicad_sym', 'TXB0108PWR', 'ics'),
        ('lib/passives.kicad_sym', 'CC0603KRX7R9BB104', 'passives'),
        ('lib/passives.kicad_sym', 'GRM21BR61A226ME51L', 'passives'),
        ('lib/passives.kicad_sym', 'RC0603JR-0710KL', 'passives'),
    ]:
        syms.append(fix_libid(extract_sym(fp, name), prefix))

    for fp, name in [('mcu.kicad_sch', 'power:+3.3V'), ('mcu.kicad_sch', 'power:GND')]:
        syms.append(extract_sym(fp, name))
    # +1V8 not in any existing lib_symbols - generate from +3.3V by replacing value
    pwr18 = extract_sym('mcu.kicad_sch', 'power:+3.3V')
    pwr18 = pwr18.replace('power:+3.3V', 'power:+1V8')
    pwr18 = pwr18.replace('+3.3V', '+1V8')
    syms.append(pwr18)

    ls = '\t(lib_symbols\n'
    for sym in syms:
        for line in sym.split('\n'):
            ls += '\t\t' + line + '\n'
    ls += '\t)\n'

    comp = ''
    wires = ''
    labels = ''
    ncs = ''
    pc = 1

    # U2: MPCIe socket
    comp += '\t\t(symbol\n'
    comp += '\t\t\t(lib_id "connectors:PCIE-52P40H_C444926")\n'
    comp += '\t\t\t(at ' + str(U2_X) + ' ' + str(U2_Y) + ' 0)\n'
    comp += '\t\t\t(unit 1) (body_style 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no) (fields_autoplaced yes)\n'
    comp += '\t\t\t(uuid "' + gen_uuid() + '")\n'
    comp += '\t\t\t(property "Reference" "U2" (at ' + str(U2_X) + ' ' + format(U2_Y - 15.24, '.2f') + ' 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Value" "PCIE-52P40H_C444926" (at ' + str(U2_X) + ' ' + format(U2_Y + 15.24, '.2f') + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Footprint" "easyeda2kicad:PCIE-SMD_PCIE-52P40H-1" (at ' + str(U2_X) + ' ' + str(U2_Y) + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Datasheet" "https://lcsc.com/product-detail/Card-Edge-Connectors_SOFNG-PCIE-52P40H_C444926.html" (at ' + str(U2_X) + ' ' + str(U2_Y) + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Description" "Mini PCIe socket 52-pin SMD" (at ' + str(U2_X) + ' ' + str(U2_Y) + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    for pn in range(1, 55):
        comp += '\t\t\t(pin "' + str(pn) + '" (uuid "' + gen_uuid() + '"))\n'
    comp += '\t\t\t(instances (project "phone" (path "' + sp + '" (reference "U2") (unit 1))))\n'
    comp += '\t\t)\n'

    # U8: TXB0108
    comp += '\t\t(symbol\n'
    comp += '\t\t\t(lib_id "ics:TXB0108PWR")\n'
    comp += '\t\t\t(at ' + str(U8_X) + ' ' + str(U8_Y) + ' 0)\n'
    comp += '\t\t\t(unit 1) (body_style 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no) (fields_autoplaced yes)\n'
    comp += '\t\t\t(uuid "' + gen_uuid() + '")\n'
    comp += '\t\t\t(property "Reference" "U8" (at ' + str(U8_X) + ' ' + format(U8_Y - 16.51, '.2f') + ' 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Value" "TXB0108PWR" (at ' + str(U8_X) + ' ' + format(U8_Y + 16.51, '.2f') + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Footprint" "easyeda2kicad:TSSOP-20_L6.5-W4.4-P0.65-LS6.4-BL" (at ' + str(U8_X) + ' ' + str(U8_Y) + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Datasheet" "https://lcsc.com/product-detail/Interface-ICs_TI_TXB0108PWR_TXB0108PWR_C53406.html" (at ' + str(U8_X) + ' ' + str(U8_Y) + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Description" "8-ch level shifter TSSOP20" (at ' + str(U8_X) + ' ' + str(U8_Y) + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    for pn in range(1, 21):
        comp += '\t\t\t(pin "' + str(pn) + '" (uuid "' + gen_uuid() + '"))\n'
    comp += '\t\t\t(instances (project "phone" (path "' + sp + '" (reference "U8") (unit 1))))\n'
    comp += '\t\t)\n'

    # C31: 100nF
    comp += '\t\t(symbol\n'
    comp += '\t\t\t(lib_id "passives:CC0603KRX7R9BB104")\n'
    comp += '\t\t\t(at ' + str(C31_X) + ' ' + str(C31_Y) + ' 0)\n'
    comp += '\t\t\t(unit 1) (body_style 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no) (fields_autoplaced yes)\n'
    comp += '\t\t\t(uuid "' + gen_uuid() + '")\n'
    comp += '\t\t\t(property "Reference" "C31" (at ' + str(C31_X) + ' ' + format(C31_Y - 5.08, '.2f') + ' 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Value" "100nF" (at ' + str(C31_X) + ' ' + format(C31_Y + 5.08, '.2f') + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Footprint" "easyeda2kicad:C0603" (at ' + str(C31_X) + ' ' + str(C31_Y) + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Datasheet" "" (at ' + str(C31_X) + ' ' + str(C31_Y) + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Description" "" (at ' + str(C31_X) + ' ' + str(C31_Y) + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(pin "2" (uuid "' + gen_uuid() + '"))\n'
    comp += '\t\t\t(pin "1" (uuid "' + gen_uuid() + '"))\n'
    comp += '\t\t\t(instances (project "phone" (path "' + sp + '" (reference "C31") (unit 1))))\n'
    comp += '\t\t)\n'

    # C32: 22uF
    comp += '\t\t(symbol\n'
    comp += '\t\t\t(lib_id "passives:GRM21BR61A226ME51L")\n'
    comp += '\t\t\t(at ' + str(C32_X) + ' ' + str(C32_Y) + ' 0)\n'
    comp += '\t\t\t(unit 1) (body_style 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no) (fields_autoplaced yes)\n'
    comp += '\t\t\t(uuid "' + gen_uuid() + '")\n'
    comp += '\t\t\t(property "Reference" "C32" (at ' + str(C32_X) + ' ' + format(C32_Y - 5.08, '.2f') + ' 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Value" "22uF" (at ' + str(C32_X) + ' ' + format(C32_Y + 5.08, '.2f') + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Footprint" "easyeda2kicad:C0805" (at ' + str(C32_X) + ' ' + str(C32_Y) + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Datasheet" "" (at ' + str(C32_X) + ' ' + str(C32_Y) + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Description" "" (at ' + str(C32_X) + ' ' + str(C32_Y) + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(pin "2" (uuid "' + gen_uuid() + '"))\n'
    comp += '\t\t\t(pin "1" (uuid "' + gen_uuid() + '"))\n'
    comp += '\t\t\t(instances (project "phone" (path "' + sp + '" (reference "C32") (unit 1))))\n'
    comp += '\t\t)\n'

    # R11: 10k
    comp += '\t\t(symbol\n'
    comp += '\t\t\t(lib_id "passives:RC0603JR-0710KL")\n'
    comp += '\t\t\t(at ' + str(R11_X) + ' ' + str(R11_Y) + ' 0)\n'
    comp += '\t\t\t(unit 1) (body_style 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no) (fields_autoplaced yes)\n'
    comp += '\t\t\t(uuid "' + gen_uuid() + '")\n'
    comp += '\t\t\t(property "Reference" "R11" (at ' + str(R11_X) + ' ' + format(R11_Y - 5.08, '.2f') + ' 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Value" "10k" (at ' + str(R11_X) + ' ' + format(R11_Y + 5.08, '.2f') + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Footprint" "easyeda2kicad:R0603" (at ' + str(R11_X) + ' ' + str(R11_Y) + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Datasheet" "" (at ' + str(R11_X) + ' ' + str(R11_Y) + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(property "Description" "" (at ' + str(R11_X) + ' ' + str(R11_Y) + ' 0) (hide yes) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))\n'
    comp += '\t\t\t(pin "2" (uuid "' + gen_uuid() + '"))\n'
    comp += '\t\t\t(pin "1" (uuid "' + gen_uuid() + '"))\n'
    comp += '\t\t\t(instances (project "phone" (path "' + sp + '" (reference "R11") (unit 1))))\n'
    comp += '\t\t)\n'

    # MPCIe socket pins
    for pn in range(1, 55):
        px, py = mpin_pos(pn)
        a = mpcie_pins[pn]
        if a[0] == 'NC':
            ncs += fnc(px, py)
        elif a[0] == 'PWR_3V3':
            if pn % 2 == 1:
                wy = py - STUB
                wires += fw(px, py, px, wy)
                comp += fpwr('power:+3.3V', px, wy, 0, '#PWR' + str(pc), sp)
            else:
                wy = py + STUB
                wires += fw(px, py, px, wy)
                comp += fpwr('power:+3.3V', px, wy, 180, '#PWR' + str(pc), sp)
            pc += 1
        elif a[0] == 'PWR_GND':
            if pn % 2 == 1:
                wy = py - STUB
                wires += fw(px, py, px, wy)
                comp += fpwr('power:GND', px, wy, 180, '#PWR' + str(pc), sp)
            else:
                wy = py + STUB
                wires += fw(px, py, px, wy)
                comp += fpwr('power:GND', px, wy, 0, '#PWR' + str(pc), sp)
            pc += 1
        else:
            if pn % 2 == 1:
                wy = py - STUB
                wires += fw(px, py, px, wy)
                labels += fgl(a[0], a[1], px, wy, 90)
            else:
                wy = py + STUB
                wires += fw(px, py, px, wy)
                labels += fgl(a[0], a[1], px, wy, 270)

    # TXB0108 pins
    for pn in range(1, 21):
        px, py = txb_pos(pn)
        a = txb_pins[pn]
        if a[0] == 'PWR_1V8':
            wx = px - STUB
            wires += fw(px, py, wx, py)
            comp += fpwr('power:+1V8', wx, py, 180, '#PWR' + str(pc), sp)
            pc += 1
        elif a[0] == 'PWR_3V3':
            wx = px + STUB
            wires += fw(px, py, wx, py)
            comp += fpwr('power:+3.3V', wx, py, 0, '#PWR' + str(pc), sp)
            pc += 1
        elif a[0] == 'PWR_GND':
            wx = px + STUB
            wires += fw(px, py, wx, py)
            comp += fpwr('power:GND', wx, py, 0, '#PWR' + str(pc), sp)
            pc += 1
        elif a[0] == 'OE_PUP':
            r11p1x = R11_X + 5.08
            r11p1y = R11_Y
            r11p2x = R11_X - 5.08
            r11p2y = R11_Y
            wires += fw(px, py, r11p1x, py)
            wires += fw(r11p1x, py, r11p1x, r11p1y)
            wires += fw(r11p2x, r11p2y, r11p2x, r11p1y)
            comp += fpwr('power:+3.3V', r11p2x, r11p1y, 180, '#PWR' + str(pc), sp)
            pc += 1
        else:
            if pn <= 10:
                wx = px - STUB
                wires += fw(px, py, wx, py)
                labels += fgl(a[0], a[1], wx, py, 180)
            else:
                wx = px + STUB
                wires += fw(px, py, wx, py)
                labels += fgl(a[0], a[1], wx, py, 0)

    # Bulk caps
    for cx, cy in [(C31_X, C31_Y), (C32_X, C32_Y)]:
        p1x, p1y = cx - 5.08, cy
        p2x, p2y = cx + 5.08, cy
        wires += fw(p1x, p1y, p1x, p1y - STUB)
        comp += fpwr('power:+3.3V', p1x, p1y - STUB, 0, '#PWR' + str(pc), sp)
        pc += 1
        wires += fw(p2x, p2y, p2x, p2y + STUB)
        comp += fpwr('power:GND', p2x, p2y + STUB, 0, '#PWR' + str(pc), sp)
        pc += 1

    # Assemble
    s = '(kicad_sch\n'
    s += '\t(version 20260306)\n'
    s += '\t(generator "eeschema")\n'
    s += '\t(generator_version "10.0")\n'
    s += '\t(uuid "' + MODEM_SCH_UUID + '")\n'
    s += '\t(paper "A3")\n'
    s += ls + comp + wires + labels + ncs
    s += '\t(sheet_instances\n'
    s += '\t\t(path "/"\n'
    s += '\t\t\t(page "1")\n'
    s += '\t\t)\n'
    s += '\t)\n'
    s += '\t(embedded_fonts no)\n'
    s += ')\n'
    return s

if __name__ == '__main__':
    c = generate()
    with open('modem.kicad_sch', 'w', encoding='utf-8', newline='\n') as f:
        f.write(c)
    print('Generated modem.kicad_sch (' + str(len(c)) + ' bytes)')