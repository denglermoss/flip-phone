#!/usr/bin/env python3
"""Generate codec.kicad_sch and add sheet box to phone.kicad_sch."""
import uuid as uuid_module
import os

SCH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phone")
CODEC_FILE = os.path.join(SCH_DIR, "codec.kicad_sch")
ROOT_FILE = os.path.join(SCH_DIR, "phone.kicad_sch")
ROOT_UUID = "451c3b43-1616-42cb-bf96-d436f4db82c2"
CODEC_SHEET_UUID = "1c9f5800-c30c-48b4-b4f4-4248c9c52b8c"
LIB_DIR = os.path.join(SCH_DIR, "lib")
ICS_LIB = os.path.join(LIB_DIR, "ics.kicad_sym")
PASSIVES_LIB = os.path.join(LIB_DIR, "passives.kicad_sym")
CONNECTORS_LIB = os.path.join(LIB_DIR, "connectors.kicad_sym")
POWER_LIB = r"C:\Users\dengle\AppData\Local\Programs\KiCad\10.0\share\kicad\symbols\power.kicad_sym"

def gen_uuid():
    return str(uuid_module.uuid4())

def extract_symbol(lib_path, sym_name, prefix):
    with open(lib_path, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = f'  (symbol "{sym_name}"'
    start = content.find(pattern)
    if start == -1:
        raise RuntimeError(f"Could not find symbol {sym_name} in {lib_path}")
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
    sym_def = content[start:i+1]
    sym_def = sym_def.replace(f'(symbol "{sym_name}"', f'(symbol "{prefix}:{sym_name}"', 1)
    return sym_def

def extract_power_symbol(sym_name):
    with open(POWER_LIB, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = f'\t(symbol "{sym_name}"'
    start = content.find(pattern)
    if start == -1:
        raise RuntimeError(f"Could not find power symbol {sym_name}")
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
    sym_def = content[start:i+1]
    sym_def = sym_def.replace(f'(symbol "{sym_name}"', f'(symbol "power:{sym_name}"')
    return sym_def

print("Extracting lib_symbols...")
lib_symbols_list = []
lib_symbols_list.append(extract_symbol(ICS_LIB, "ALC5651-CG", "ics"))
lib_symbols_list.append(extract_symbol(ICS_LIB, "TXB0108PWR", "ics"))
lib_symbols_list.append(extract_symbol(PASSIVES_LIB, "GRM21BR61H106KE43L", "passives"))
lib_symbols_list.append(extract_symbol(PASSIVES_LIB, "CC0603KRX7R9BB104", "passives"))
lib_symbols_list.append(extract_symbol(PASSIVES_LIB, "RC0603JR-0710KL", "passives"))
lib_symbols_list.append(extract_symbol(CONNECTORS_LIB, "S2B-PH-SM4-TB", "connectors"))
lib_symbols_list.append(extract_power_symbol("+3.3V"))
lib_symbols_list.append(extract_power_symbol("GND"))
lib_symbols_list.append(extract_power_symbol("+1V8"))
lib_symbols_text = '\n'.join(lib_symbols_list)

# Component positions
U3_X, U3_Y = 140, 130
U3_LEFT_X = U3_X - 27.94
U3_RIGHT_X = U3_X + 27.94
U9_X, U9_Y = 220, 130
U9_LEFT_X = U9_X - 12.70
U9_RIGHT_X = U9_X + 12.70

alc5651_pins = {
    1:("MICVDD","L",22.86), 2:("MICBIAS1","L",20.32), 3:("JD1","L",17.78),
    4:("IN1P","L",15.24), 5:("IN2P","L",12.70), 6:("IN2N","L",10.16),
    7:("IN3P","L",7.62), 8:("DACREF","L",5.08), 9:("AVDD","L",2.54),
    10:("AGND","L",0.00), 11:("VREF","L",-2.54), 12:("LOUTL_P","L",-5.08),
    13:("LOUTR_N","L",-7.62), 14:("CPN2","L",-10.16), 15:("CPP2","L",-12.70),
    16:("CPN1","L",-15.24), 17:("CPP1","L",-17.78), 18:("CPVDD","L",-20.32),
    19:("CPVPP","L",-22.86), 20:("CPVREF","L",-25.40),
    21:("HPO_R","R",-25.40), 22:("CPVEE","R",-22.86), 23:("HPO_L","R",-20.32),
    24:("PDM_SDA","R",-17.78), 25:("PDM_SCL","R",-15.24), 26:("ADCDAT2","R",-12.70),
    27:("DACDAT2","R",-10.16), 28:("LRCK2","R",-7.62), 29:("BCLK2","R",-5.08),
    30:("ADCDAT1","R",-2.54), 31:("DACDAT1","R",0.00), 32:("LRCK1","R",2.54),
    33:("BCLK1","R",5.08), 34:("MCLK","R",7.62), 35:("SCL","R",10.16),
    36:("SDA","R",12.70), 37:("GPIO1","R",15.24), 38:("GPIO2","R",17.78),
    39:("DBVDD","R",20.32), 40:("DCVDD","R",22.86), 41:("EP","R",25.40),
}

def u3p(n):
    _,side,off = alc5651_pins[n]
    x = U3_LEFT_X if side=="L" else U3_RIGHT_X
    return (round(x,2), round(U3_Y+off,2))

txb_pins = {
    1:("A1","L",11.43), 2:("VCCA","L",8.89), 3:("A2","L",6.35),
    4:("A3","L",3.81), 5:("A4","L",1.27), 6:("A5","L",-1.27),
    7:("A6","L",-3.81), 8:("A7","L",-6.35), 9:("A8","L",-8.89),
    10:("OE","L",-11.43), 11:("GND","R",-11.43), 12:("B8","R",-8.89),
    13:("B7","R",-6.35), 14:("B6","R",-3.81), 15:("B5","R",-1.27),
    16:("B4","R",1.27), 17:("B3","R",3.81), 18:("B2","R",6.35),
    19:("VCCB","R",8.89), 20:("B1","R",11.43),
}

def u9p(n):
    _,side,off = txb_pins[n]
    x = U9_LEFT_X if side=="L" else U9_RIGHT_X
    return (round(x,2), round(U9_Y+off,2))

def cpp(cx,cy,p):
    return (round(cx-5.08 if p==1 else cx+5.08,2), cy)

def cnp(cx,cy,p):
    if p==1: return (round(cx+3.81,2), round(cy-1.27,2))
    elif p==2: return (round(cx+3.81,2), round(cy+1.27,2))
    elif p==3: return (round(cx-3.81,2), round(cy+6.35,2))
    else: return (round(cx-3.81,2), round(cy-6.35,2))

elements = []
pwr_ctr = 401

def aw(x1,y1,x2,y2):
    elements.append(f'\t\t(wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))\n')

def agl(name,x,y,rot=0,shape="bidirectional"):
    j = "left" if rot==0 else "right" if rot==180 else "bottom" if rot==90 else "top"
    rx = x+1.27 if rot==0 else x-1.27 if rot==180 else x
    elements.append(f'\t\t(global_label "{name}" (shape {shape}) (at {x} {y} {rot}) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify {j} {j})) (uuid "{gen_uuid()}") (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {rx} {y} 0) (hide yes) (effects (font (size 1.27 1.27)) (justify {j} {j}))))\n')

def anc(x,y):
    elements.append(f'\t\t(no_connect (at {x} {y}) (uuid "{gen_uuid()}"))\n')

def apw(net,x,y,rot,ref):
    global pwr_ctr
    su = gen_uuid(); pu = gen_uuid()
    if rot==0: rx,ry,vx,vy = x,y-2.54,x,y+1.27
    elif rot==180: rx,ry,vx,vy = x,y+2.54,x,y-1.27
    elif rot==90: rx,ry,vx,vy = x+2.54,y,x-1.27,y
    else: rx,ry,vx,vy = x-2.54,y,x+1.27,y
    s = f'\t\t(symbol\n\t\t\t(lib_id "power:{net}")\n\t\t\t(at {x} {y} {rot})\n\t\t\t(unit 1)\n\t\t\t(exclude_from_sim no)\n\t\t\t(in_bom yes)\n\t\t\t(on_board yes)\n\t\t\t(dnp no)\n\t\t\t(fields_autoplaced yes)\n\t\t\t(uuid "{su}")\n'
    s += f'\t\t\t(property "Reference" "{ref}"\n\t\t\t\t(at {rx} {ry} 0)\n\t\t\t\t(hide yes)\n\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)\n\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n'
    s += f'\t\t\t(property "Value" "{net}"\n\t\t\t\t(at {vx} {vy} 0)\n\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)\n\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n'
    s += f'\t\t\t(property "Footprint" ""\n\t\t\t\t(at {x} {y} 0)\n\t\t\t\t(hide yes)\n\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)\n\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n'
    s += f'\t\t\t(property "Datasheet" ""\n\t\t\t\t(at {x} {y} 0)\n\t\t\t\t(hide yes)\n\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)\n\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t\t(hide yes)\n\t\t\t\t)\n\t\t\t)\n'
    s += f'\t\t\t(pin "1"\n\t\t\t\t(uuid "{pu}")\n\t\t\t)\n'
    s += f'\t\t\t(instances\n\t\t\t\t(project "phone"\n\t\t\t\t\t(path "/{ROOT_UUID}/{CODEC_SHEET_UUID}"\n\t\t\t\t\t\t(reference "{ref}")\n\t\t\t\t\t\t(unit 1)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n'
    elements.append(s)
    pwr_ctr += 1

def ac(lib_id,ref,val,cx,cy,rot=0):
    su = gen_uuid()
    ry = cy-5.0 if rot==0 else cy+5.0
    vy = cy+5.0 if rot==0 else cy-5.0
    s = f'\t\t(symbol\n\t\t\t(lib_id "{lib_id}")\n\t\t\t(at {cx} {cy} {rot})\n\t\t\t(unit 1)\n\t\t\t(exclude_from_sim no)\n\t\t\t(in_bom yes)\n\t\t\t(on_board yes)\n\t\t\t(dnp no)\n\t\t\t(uuid "{su}")\n'
    s += f'\t\t\t(property "Reference" "{ref}"\n\t\t\t\t(at {cx} {ry} 0)\n\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s += f'\t\t\t(property "Value" "{val}"\n\t\t\t\t(at {cx} {vy} 0)\n\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s += f'\t\t\t(property "Footprint" ""\n\t\t\t\t(at {cx} {cy} 0)\n\t\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t\t)\n'
    s += f'\t\t\t(property "Datasheet" "~"\n\t\t\t\t(at {cx} {cy} 0)\n\t\t\t\t(effects (font (size 1.27 1.27)) (hide yes))\n\t\t\t)\n'
    s += f'\t\t\t(instances\n\t\t\t\t(project "phone"\n\t\t\t\t\t(path "/{CODEC_SHEET_UUID}"\n\t\t\t\t\t\t(reference "{ref}") (unit 1)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n'
    elements.append(s)

print("Placing components...")
ac("ics:ALC5651-CG","U3","ALC5651-CG",U3_X,U3_Y)
ac("ics:TXB0108PWR","U9","TXB0108PWR",U9_X,U9_Y)
C33_X,C33_Y=85,170; ac("passives:GRM21BR61H106KE43L","C33","10uF",C33_X,C33_Y)
C34_X,C34_Y=100,170; ac("passives:CC0603KRX7R9BB104","C34","100nF",C34_X,C34_Y)
C35_X,C35_Y=210,170; ac("passives:CC0603KRX7R9BB104","C35","100nF",C35_X,C35_Y)
C36_X,C36_Y=225,170; ac("passives:CC0603KRX7R9BB104","C36","100nF",C36_X,C36_Y)
JSPK_X,JSPK_Y=60,120; ac("connectors:S2B-PH-SM4-TB","J_SPK","S2B-PH-SM4-TB",JSPK_X,JSPK_Y,180)
JMIC_X,JMIC_Y=60,150; ac("connectors:S2B-PH-SM4-TB","J_MIC","S2B-PH-SM4-TB",JMIC_X,JMIC_Y,180)
R12_X,R12_Y=180,80; ac("passives:RC0603JR-0710KL","R12","4.7k",R12_X,R12_Y)
R13_X,R13_Y=200,80; ac("passives:RC0603JR-0710KL","R13","4.7k",R13_X,R13_Y)

print("Wiring codec power...")
for pin,net in [(1,"+3.3V"),(9,"+1V8"),(10,"GND"),(18,"+1V8")]:
    px,py=u3p(pin)
    apw(net,px-7.06,py,270,f"#PWR{pwr_ctr}"); aw(px-7.06,py,px,py)
for pin,net,off in [(39,"+1V8",7.06),(40,"+1V8",12.06),(41,"GND",7.06)]:
    px,py=u3p(pin)
    apw(net,px+off,py,90,f"#PWR{pwr_ctr}"); aw(px,py,px+off,py)

print("Wiring PCM/I2S-1...")
for pin,label,shape in [(30,"PCM_IN","output"),(31,"PCM_OUT","input"),(32,"PCM_SYNC","bidirectional"),(33,"PCM_CLK","bidirectional")]:
    px,py=u3p(pin); aw(px,py,px+7.06,py); agl(label,px+7.06,py,0,shape)

print("Wiring I2C...")
for pin,label in [(35,"I2C_SCL"),(36,"I2C_SDA")]:
    px,py=u3p(pin); aw(px,py,px+7.06,py); agl(label,px+7.06,py,0,"bidirectional")
for rx,ry,label in [(R12_X,R12_Y,"I2C_SCL"),(R13_X,R13_Y,"I2C_SDA")]:
    p1=cpp(rx,ry,1); p2=cpp(rx,ry,2)
    apw("+1V8",p1[0],p1[1]-5.08,0,f"#PWR{pwr_ctr}"); aw(p1[0],p1[1],p1[0],p1[1]-5.08)
    aw(p2[0],p2[1],p2[0]+5.08,p2[1]); agl(label,p2[0]+5.08,p2[1],0,"bidirectional")

print("Wiring I2S-2 through TXB0108...")
for cp,tx,bx in [(29,1,180),(28,3,185),(27,4,190),(26,5,195)]:
    cx,cy=u3p(cp); ax,ay=u9p(tx)
    aw(cx,cy,bx,cy); aw(bx,cy,bx,ay); aw(bx,ay,ax,ay)
for tp,label,shape in [(20,"I2S2_BCLK","input"),(18,"I2S2_LRCK","input"),(17,"I2S2_DACDAT","input"),(16,"I2S2_ADCDAT","output")]:
    bx,by=u9p(tp); aw(bx,by,bx+7.62,by); agl(label,bx+7.62,by,0,shape)

print("Wiring TXB0108 power...")
for pin,net in [(2,"+1V8"),(10,"+1V8")]:
    px,py=u9p(pin); apw(net,px-7.30,py,270,f"#PWR{pwr_ctr}"); aw(px-7.30,py,px,py)
for pin,net in [(19,"+3.3V"),(11,"GND")]:
    px,py=u9p(pin); apw(net,px+7.30,py,90,f"#PWR{pwr_ctr}"); aw(px,py,px+7.30,py)

print("Wiring speaker/mic...")
j1=cnp(JSPK_X,JSPK_Y,1); c1=u3p(12)
aw(j1[0],j1[1],90,j1[1]); aw(90,j1[1],90,c1[1]); aw(90,c1[1],c1[0],c1[1])
j2=cnp(JSPK_X,JSPK_Y,2); c2=u3p(13)
aw(j2[0],j2[1],85,j2[1]); aw(85,j2[1],85,c2[1]); aw(85,c2[1],c2[0],c2[1])
j3=cnp(JSPK_X,JSPK_Y,3); apw("GND",j3[0],j3[1]+5.08,180,f"#PWR{pwr_ctr}"); aw(j3[0],j3[1],j3[0],j3[1]+5.08)
j4=cnp(JSPK_X,JSPK_Y,4); apw("GND",j4[0],j4[1]-5.08,0,f"#PWR{pwr_ctr}"); aw(j4[0],j4[1],j4[0],j4[1]-5.08)
j1=cnp(JMIC_X,JMIC_Y,1); c1=u3p(2)
aw(j1[0],j1[1],90,j1[1]); aw(90,j1[1],90,c1[1]); aw(90,c1[1],c1[0],c1[1])
j2=cnp(JMIC_X,JMIC_Y,2); c2=u3p(4)
aw(j2[0],j2[1],85,j2[1]); aw(85,j2[1],85,c2[1]); aw(85,c2[1],c2[0],c2[1])
j3=cnp(JMIC_X,JMIC_Y,3); apw("GND",j3[0],j3[1]+5.08,180,f"#PWR{pwr_ctr}"); aw(j3[0],j3[1],j3[0],j3[1]+5.08)
j4=cnp(JMIC_X,JMIC_Y,4); apw("GND",j4[0],j4[1]-5.08,0,f"#PWR{pwr_ctr}"); aw(j4[0],j4[1],j4[0],j4[1]-5.08)

print("Wiring decoupling caps...")
for cx,cy,net in [(C33_X,C33_Y,"+1V8"),(C34_X,C34_Y,"+1V8"),(C35_X,C35_Y,"+1V8"),(C36_X,C36_Y,"+3.3V")]:
    p1=cpp(cx,cy,1); p2=cpp(cx,cy,2)
    apw("GND",p1[0],p1[1]+5.08,180,f"#PWR{pwr_ctr}"); aw(p1[0],p1[1],p1[0],p1[1]+5.08)
    apw(net,p2[0],p2[1]-5.08,0,f"#PWR{pwr_ctr}"); aw(p2[0],p2[1],p2[0],p2[1]-5.08)

print("Adding no-connect markers...")
for n in [3,5,6,7,8,11,14,15,16,17,19,20,21,22,23,24,25,34,37,38]:
    px,py=u3p(n); anc(px,py)
for n in [6,7,8,9,12,13,14,15]:
    px,py=u9p(n); anc(px,py)

print("Assembling codec.kicad_sch...")
header = f'(kicad_sch\n\t(version 20260306)\n\t(generator "eeschema")\n\t(generator_version "10.0")\n\t(uuid "{CODEC_SHEET_UUID}")\n\t(paper "A3")\n\t(title_block\n\t\t(title "Codec")\n\t)\n\t(lib_symbols\n{lib_symbols_text}\n\t)\n'
footer = f'\t(sheet_instances\n\t\t(path "/{CODEC_SHEET_UUID}"\n\t\t\t(page "1")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)\n'
content = header + '\t' + ''.join(elements) + footer
with open(CODEC_FILE,'w',encoding='utf-8',newline='\n') as f:
    f.write(content)
print(f"Written {CODEC_FILE}")

print("Adding sheet box to phone.kicad_sch...")
with open(ROOT_FILE,'r',encoding='utf-8') as f:
    rc = f.read()
codec_sheet = f'\t(sheet\n\t\t(at 254 280)\n\t\t(size 30.48 20.32)\n\t\t(fields_autoplaced yes)\n\t\t(stroke (width 0.1524) (type solid) (color 0 0 0 0))\n\t\t(fill (type none) (color 0 0 0 0))\n\t\t(uuid "{CODEC_SHEET_UUID}")\n\t\t(property "Sheetname" "Codec"\n\t\t\t(at 254 279 0)\n\t\t\t(effects (font (size 1.27 1.27)) (justify left bottom))\n\t\t)\n\t\t(property "Sheetfile" "codec.kicad_sch"\n\t\t\t(at 254 301 0)\n\t\t\t(effects (font (size 1.27 1.27)) (justify left top))\n\t\t)\n\t)\n'
modem_end = '\t\t(property "Sheetfile" "modem.kicad_sch"\n\t\t\t(at 254 271.19 0)\n\t\t\t(effects (font (size 1.27 1.27)) (justify left top))\n\t\t)\n\t)\n'
rc = rc.replace(modem_end, modem_end + codec_sheet, 1)
modem_inst = '\t\t(path "/451c3b43-1616-42cb-bf96-d436f4db82c2/2b7de758-71cc-4198-8a01-5d2c6e01f5f1"\n\t\t\t(page "3")\n\t\t)\n'
codec_inst = f'\t\t(path "/451c3b43-1616-42cb-bf96-d436f4db82c2/{CODEC_SHEET_UUID}"\n\t\t\t(page "4")\n\t\t)\n'
rc = rc.replace(modem_inst, modem_inst + codec_inst, 1)
with open(ROOT_FILE,'w',encoding='utf-8',newline='\n') as f:
    f.write(rc)
print(f"Updated {ROOT_FILE}")
print("Done!")
