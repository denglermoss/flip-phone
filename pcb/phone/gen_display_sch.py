#!/usr/bin/env python3
"""Generate display.kicad_sch for the phone project."""
import uuid

DISPLAY_SCH_UUID = 'd7f57b90-9db7-4266-b1f1-7949b1054009'
ROOT_UUID = '451c3b43-1616-42cb-bf96-d436f4db82c2'

J_HINGE_X, J_HINGE_Y = 130.0, 130.0
J_DISP_X, J_DISP_Y   = 230.0, 80.0
J_DISP2_X, J_DISP2_Y = 230.0, 160.0
J_EAR_X, J_EAR_Y     = 230.0, 200.0
R14_X, R14_Y         = 195.0, 50.0
C37_X, C37_Y         = 195.0, 130.0
STUB = 5.08
PWR_START = 128

def gen_uuid():
    return str(uuid.uuid4())

FPC14_PINS = {1:16.51,2:13.97,3:11.43,4:8.89,5:6.35,6:3.81,7:1.27,8:-1.27,9:-3.81,10:-6.35,11:-8.89,12:-11.43,13:-13.97,14:-16.51}
FPC12_PINS = {1:13.97,2:11.43,3:8.89,4:6.35,5:3.81,6:1.27,7:-1.27,8:-3.81,9:-6.35,10:-8.89,11:-11.43,12:-13.97}
FPC8_PINS  = {1:8.89,2:6.35,3:3.81,4:1.27,5:-1.27,6:-3.81,7:-6.35,8:-8.89}

HINGE_PINS = {
    1:('PWR_3V3',),2:('PWR_GND',),3:('DISP_MOSI','input'),4:('DISP_SCK','input'),
    5:('DISP_CS','input'),6:('DISP_DC','input'),7:('DISP_RST','input'),
    8:('OUTER_CS','input'),9:('OUTER_DC','input'),10:('BL_PWM','input'),
    11:('NC',),12:('EARPIECE+','bidirectional'),13:('EARPIECE-','bidirectional'),14:('PWR_GND',),
}
DISP_PINS = {
    1:('PWR_GND',),2:('PWR_3V3',),3:('DISP_SCK','input'),4:('DISP_MOSI','input'),
    5:('DISP_RST','input'),6:('DISP_DC','input'),7:('DISP_CS','input'),
    8:('PWR_GND',),9:('LEDA','passive'),10:('BL_PWM','input'),11:('NC',),12:('NC',),
}
DISP2_PINS = {
    1:('PWR_GND',),2:('PWR_3V3',),3:('DISP_SCK','input'),4:('DISP_MOSI','input'),
    5:('DISP_RST','input'),6:('OUTER_DC','input'),7:('OUTER_CS','input'),8:('PWR_GND',),
}
EAR_PINS = {1:('EARPIECE+','bidirectional'),2:('EARPIECE-','bidirectional')}

def fw(x1,y1,x2,y2):
    return '\t\t(wire\n\t\t\t(pts\n\t\t\t\t(xy %.2f %.2f) (xy %.2f %.2f)\n\t\t\t)\n\t\t\t(stroke\n\t\t\t\t(width 0)\n\t\t\t\t(type default)\n\t\t\t)\n\t\t\t(uuid "%s")\n\t\t)\n' % (x1,y1,x2,y2,gen_uuid())

def fgl(name,shape,x,y,orient):
    j='left' if orient==0 else ('right' if orient==180 else ('bottom' if orient==90 else 'top'))
    s='\t\t(global_label "%s"\n' % name
    s+='\t\t\t(shape %s)\n' % shape
    s+='\t\t\t(at %.2f %.2f %d)\n' % (x,y,orient)
    s+='\t\t\t(fields_autoplaced yes)\n'
    s+='\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n'
    s+='\t\t\t\t(justify %s)\n\t\t\t)\n' % j
    s+='\t\t\t(uuid "%s")\n' % gen_uuid()
    s+='\t\t\t(property "Intersheetrefs" "${INTERSHEET_REFS}"\n'
    s+='\t\t\t\t(at %.2f %.2f 0)\n' % (x,y)
    s+='\t\t\t\t(hide yes)\n\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)\n'
    s+='\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n'
    s+='\t\t\t\t\t(justify %s)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n' % j
    return s

def fll(name,x,y,orient):
    j='left' if orient==0 else ('right' if orient==180 else ('bottom' if orient==90 else 'top'))
    s='\t\t(label "%s"\n' % name
    s+='\t\t\t(at %.2f %.2f %d)\n' % (x,y,orient)
    s+='\t\t\t(fields_autoplaced yes)\n'
    s+='\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n'
    s+='\t\t\t\t(justify %s)\n\t\t\t)\n' % j
    s+='\t\t\t(uuid "%s")\n\t\t)\n' % gen_uuid()
    return s

def fnc(x,y):
    return '\t\t(no_connect (at %.2f %.2f) (uuid "%s"))\n' % (x,y,gen_uuid())

def fpwr(lib_id,x,y,rot,ref,path):
    u=gen_uuid(); pu=gen_uuid()
    if '+3.3V' in lib_id:
        val='+3.3V'; desc='Power symbol creates a global label with name \\"+3.3V\\"'
    else:
        val='GND'; desc='Power symbol creates a global label with name \\"GND\\" , ground'
    s='\t\t(symbol\n'
    s+='\t\t\t(lib_id "%s")\n' % lib_id
    s+='\t\t\t(at %.2f %.2f %d)\n' % (x,y,rot)
    s+='\t\t\t(unit 1) (body_style 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no) (fields_autoplaced yes)\n'
    s+='\t\t\t(uuid "%s")\n' % u
    s+='\t\t\t(property "Reference" "%s"\n' % ref
    s+='\t\t\t\t(at %.2f %.2f 0)\n' % (x,y)
    s+='\t\t\t\t(hide yes) (show_name no) (do_not_autoplace no)\n'
    s+='\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s+='\t\t\t(property "Value" "%s"\n' % val
    s+='\t\t\t\t(at %.2f %.2f 0)\n' % (x,y)
    s+='\t\t\t\t(show_name no) (do_not_autoplace no)\n'
    s+='\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s+='\t\t\t(property "Footprint" ""\n'
    s+='\t\t\t\t(at %.2f %.2f 0)\n' % (x,y)
    s+='\t\t\t\t(hide yes) (show_name no) (do_not_autoplace no)\n'
    s+='\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s+='\t\t\t(property "Datasheet" ""\n'
    s+='\t\t\t\t(at %.2f %.2f 0)\n' % (x,y)
    s+='\t\t\t\t(hide yes) (show_name no) (do_not_autoplace no)\n'
    s+='\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s+='\t\t\t(property "Description" "%s"\n' % desc
    s+='\t\t\t\t(at %.2f %.2f 0)\n' % (x,y)
    s+='\t\t\t\t(hide yes) (show_name no) (do_not_autoplace no)\n'
    s+='\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s+='\t\t\t(pin "1" (uuid "%s"))\n' % pu
    s+='\t\t\t(instances (project "phone" (path "%s" (reference "%s") (unit 1))))\n' % (path,ref)
    s+='\t\t)\n'
    return s

def extract_sym(filepath,name):
    with open(filepath,'r',encoding='utf-8') as f:
        c=f.read()
    m='(symbol "'+name+'"'
    s=c.find(m)
    if s==-1: raise ValueError(name+' not found in '+filepath)
    d=0; i=s
    while i<len(c):
        if c[i]=='(': d+=1
        elif c[i]==')':
            d-=1
            if d==0: return c[s:i+1]
        i+=1

def fix_libid(sym,prefix):
    return sym.replace('(symbol "','(symbol "'+prefix+':',1)

def comp_sym(lib_id,x,y,rot,ref,value,footprint,datasheet,description,pin_count,path,hide_value=False):
    s='\t\t(symbol\n'
    s+='\t\t\t(lib_id "%s")\n' % lib_id
    s+='\t\t\t(at %.2f %.2f %d)\n' % (x,y,rot)
    s+='\t\t\t(unit 1) (body_style 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no) (fields_autoplaced yes)\n'
    s+='\t\t\t(uuid "%s")\n' % gen_uuid()
    s+='\t\t\t(property "Reference" "%s"\n' % ref
    s+='\t\t\t\t(at %.2f %.2f 0)\n' % (x,y-5.0)
    s+='\t\t\t\t(show_name no) (do_not_autoplace no)\n'
    s+='\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    hv=' (hide yes)' if hide_value else ''
    s+='\t\t\t(property "Value" "%s"\n' % value
    s+='\t\t\t\t(at %.2f %.2f 0)\n' % (x,y+5.0)
    s+='\t\t\t\t%s(show_name no) (do_not_autoplace no)\n' % hv
    s+='\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s+='\t\t\t(property "Footprint" "%s"\n' % footprint
    s+='\t\t\t\t(at %.2f %.2f 0)\n' % (x,y)
    s+='\t\t\t\t(hide yes) (show_name no) (do_not_autoplace no)\n'
    s+='\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s+='\t\t\t(property "Datasheet" "%s"\n' % datasheet
    s+='\t\t\t\t(at %.2f %.2f 0)\n' % (x,y)
    s+='\t\t\t\t(hide yes) (show_name no) (do_not_autoplace no)\n'
    s+='\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    s+='\t\t\t(property "Description" "%s"\n' % description
    s+='\t\t\t\t(at %.2f %.2f 0)\n' % (x,y)
    s+='\t\t\t\t(hide yes) (show_name no) (do_not_autoplace no)\n'
    s+='\t\t\t\t(effects (font (size 1.27 1.27)))\n\t\t\t)\n'
    for pn in range(1,pin_count+1):
        s+='\t\t\t(pin "%d" (uuid "%s"))\n' % (pn,gen_uuid())
    s+='\t\t\t(instances (project "phone" (path "%s" (reference "%s") (unit 1))))\n' % (path,ref)
    s+='\t\t)\n'
    return s

def generate():
    sp='/'+ROOT_UUID+'/'+DISPLAY_SCH_UUID
    syms=[]
    for fp,name,prefix in [
        ('lib/connectors.kicad_sym','0.5K-HX-14PWB','connectors'),
        ('lib/connectors.kicad_sym','0.5K-HX-12PWB','connectors'),
        ('lib/connectors.kicad_sym','0.5K-HX-8PWB','connectors'),
        ('lib/connectors.kicad_sym','S2B-PH-SM4-TB','connectors'),
        ('lib/passives.kicad_sym','CC0603KRX7R9BB104','passives'),
        ('lib/passives.kicad_sym','RC0603JR-07470RL','passives'),
    ]:
        syms.append(fix_libid(extract_sym(fp,name),prefix))
    for name in ['power:+3.3V','power:GND']:
        syms.append(extract_sym('modem.kicad_sch',name))

    ls='\t(lib_symbols\n'
    for sym in syms:
        for line in sym.split('\n'):
            ls+='\t\t'+line+'\n'
    ls+='\t)\n'

    comp=''; wires=''; labels=''; ncs=''
    pc=PWR_START

    comp+=comp_sym('connectors:0.5K-HX-14PWB',J_HINGE_X,J_HINGE_Y,0,'J_HINGE','0.5K-HX-14PWB','easyeda2kicad:FPC-SMD_14P-P0.50_HDGC_0.5K-HX-14PWB','https://www.lcsc.com/datasheet/C2919495.pdf','14-pin 0.5mm FPC hinge flex connector',16,sp,hide_value=True)
    comp+=comp_sym('connectors:0.5K-HX-12PWB',J_DISP_X,J_DISP_Y,0,'J_DISP','0.5K-HX-12PWB','easyeda2kicad:FPC-SMD_12P-P0.50_HDGC_0.5K-HX-12PWB','https://www.lcsc.com/datasheet/C2919494.pdf','12-pin 0.5mm FPC main display connector',14,sp,hide_value=True)
    comp+=comp_sym('connectors:0.5K-HX-8PWB',J_DISP2_X,J_DISP2_Y,0,'J_DISP2','0.5K-HX-8PWB','easyeda2kicad:FPC-SMD_8P-P0.50_HDGC_0.5K-HX-8PWB','https://www.lcsc.com/datasheet/C2919492.pdf','8-pin 0.5mm FPC outer display connector',10,sp,hide_value=True)
    comp+=comp_sym('connectors:S2B-PH-SM4-TB',J_EAR_X,J_EAR_Y,0,'J_EARPIECE','S2B-PH-SM4-TB','easyeda2kicad:CONN-SMD_P2.00_S2B-PH-SM4-TB-LF-SN','','2-pin JST PH earpiece speaker connector',4,sp,hide_value=True)
    comp+=comp_sym('passives:RC0603JR-07470RL',R14_X,R14_Y,0,'R14','4R7','easyeda2kicad:R0603','','4.7 ohm backlight current limit resistor',2,sp)
    comp+=comp_sym('passives:CC0603KRX7R9BB104',C37_X,C37_Y,90,'C37','100nF','easyeda2kicad:C0603','','100nF display decoupling cap',2,sp)

    # J_HINGE pins
    for pn,y_off in FPC14_PINS.items():
        px=J_HINGE_X+(-3.81); py=J_HINGE_Y+y_off
        a=HINGE_PINS[pn]
        if a[0]=='NC': ncs+=fnc(px,py)
        elif a[0]=='PWR_3V3':
            wx=px-STUB; wires+=fw(px,py,wx,py); comp+=fpwr('power:+3.3V',wx,py,0,'#PWR'+str(pc),sp); pc+=1
        elif a[0]=='PWR_GND':
            wx=px-STUB; wires+=fw(px,py,wx,py); comp+=fpwr('power:GND',wx,py,0,'#PWR'+str(pc),sp); pc+=1
        else:
            wx=px-STUB; wires+=fw(px,py,wx,py); labels+=fgl(a[0],a[1],wx,py,180)

    # J_HINGE mounting tabs
    for pnum,(mx,my) in [(15,(3.81,-20.32)),(16,(3.81,21.59))]:
        px=J_HINGE_X+mx; py=J_HINGE_Y+my
        wy=py-STUB if pnum==15 else py+STUB
        wires+=fw(px,py,px,wy); comp+=fpwr('power:GND',px,wy,0,'#PWR'+str(pc),sp); pc+=1

    # J_DISP pins
    for pn,y_off in FPC12_PINS.items():
        px=J_DISP_X+(-5.08); py=J_DISP_Y+y_off
        a=DISP_PINS[pn]
        if a[0]=='NC': ncs+=fnc(px,py)
        elif a[0]=='PWR_3V3':
            wx=px-STUB; wires+=fw(px,py,wx,py); comp+=fpwr('power:+3.3V',wx,py,0,'#PWR'+str(pc),sp); pc+=1
        elif a[0]=='PWR_GND':
            wx=px-STUB; wires+=fw(px,py,wx,py); comp+=fpwr('power:GND',wx,py,0,'#PWR'+str(pc),sp); pc+=1
        elif a[0]=='LEDA':
            wx=px-STUB; wires+=fw(px,py,wx,py); labels+=fll(a[0],wx,py,180)
        else:
            wx=px-STUB; wires+=fw(px,py,wx,py); labels+=fgl(a[0],a[1],wx,py,180)

    # J_DISP mounting tabs
    for pnum,(mx,my) in [(13,(3.81,-19.05)),(14,(3.81,19.05))]:
        px=J_DISP_X+mx; py=J_DISP_Y+my
        wy=py-STUB if pnum==13 else py+STUB
        wires+=fw(px,py,px,wy); comp+=fpwr('power:GND',px,wy,0,'#PWR'+str(pc),sp); pc+=1

    # J_DISP2 pins
    for pn,y_off in FPC8_PINS.items():
        px=J_DISP2_X+(-5.08); py=J_DISP2_Y+y_off
        a=DISP2_PINS[pn]
        if a[0]=='PWR_3V3':
            wx=px-STUB; wires+=fw(px,py,wx,py); comp+=fpwr('power:+3.3V',wx,py,0,'#PWR'+str(pc),sp); pc+=1
        elif a[0]=='PWR_GND':
            wx=px-STUB; wires+=fw(px,py,wx,py); comp+=fpwr('power:GND',wx,py,0,'#PWR'+str(pc),sp); pc+=1
        else:
            wx=px-STUB; wires+=fw(px,py,wx,py); labels+=fgl(a[0],a[1],wx,py,180)

    # J_DISP2 mounting tabs
    for pnum,(mx,my) in [(9,(2.54,-13.97)),(10,(2.54,13.97))]:
        px=J_DISP2_X+mx; py=J_DISP2_Y+my
        wy=py-STUB if pnum==9 else py+STUB
        wires+=fw(px,py,px,wy); comp+=fpwr('power:GND',px,wy,0,'#PWR'+str(pc),sp); pc+=1

    # J_EARPIECE pins
    for pn,y_off in {1:1.27,2:-1.27}.items():
        px=J_EAR_X+(-3.81); py=J_EAR_Y+y_off
        a=EAR_PINS[pn]
        wx=px-STUB; wires+=fw(px,py,wx,py); labels+=fgl(a[0],a[1],wx,py,180)

    # J_EARPIECE mounting tabs
    for pnum,(mx,my) in [(3,(3.81,-6.35)),(4,(3.81,6.35))]:
        px=J_EAR_X+mx; py=J_EAR_Y+my
        wy=py-STUB if pnum==3 else py+STUB
        wires+=fw(px,py,px,wy); comp+=fpwr('power:GND',px,wy,0,'#PWR'+str(pc),sp); pc+=1

    # R14: pin1 -> +3.3V, pin2 -> LEDA
    r14p1x=R14_X+(-5.08); r14p1y=R14_Y
    wx=r14p1x-STUB; wires+=fw(r14p1x,r14p1y,wx,r14p1y); comp+=fpwr('power:+3.3V',wx,r14p1y,0,'#PWR'+str(pc),sp); pc+=1
    r14p2x=R14_X+5.08; r14p2y=R14_Y
    wx=r14p2x+STUB; wires+=fw(r14p2x,r14p2y,wx,r14p2y); labels+=fll('LEDA',wx,r14p2y,0)

    # C37: vertical, pin1(bottom)->GND, pin2(top)->+3.3V
    c37p1x=C37_X; c37p1y=C37_Y+(-5.08)
    wy=c37p1y-STUB; wires+=fw(c37p1x,c37p1y,c37p1x,wy); comp+=fpwr('power:GND',c37p1x,wy,0,'#PWR'+str(pc),sp); pc+=1
    c37p2x=C37_X; c37p2y=C37_Y+5.08
    wy=c37p2y+STUB; wires+=fw(c37p2x,c37p2y,c37p2x,wy); comp+=fpwr('power:+3.3V',c37p2x,wy,0,'#PWR'+str(pc),sp); pc+=1

    sch='(kicad_sch\n'
    sch+='\t(version 20260306)\n'
    sch+='\t(generator "eeschema")\n'
    sch+='\t(generator_version "10.0")\n'
    sch+='\t(uuid "%s")\n' % DISPLAY_SCH_UUID
    sch+='\t(paper "A3")\n'
    sch+='\t(title_block\n\t\t(title "Display")\n\t)\n'
    sch+=ls
    sch+=wires
    sch+=labels
    sch+=ncs
    sch+=comp
    sch+='\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n'
    sch+='\t(embedded_fonts no)\n)\n'

    with open('display.kicad_sch','w',encoding='utf-8',newline='\n') as f:
        f.write(sch)
    print('Generated display.kicad_sch')
    print('  Sheet UUID: %s' % DISPLAY_SCH_UUID)
    print('  Power symbols: #PWR%d through #PWR%d' % (PWR_START,pc-1))

if __name__=='__main__':
    generate()