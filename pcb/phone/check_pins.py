import re
c = open("lib/connectors.kicad_sym","r",encoding="utf-8").read()
idx = c.find("PCIE-52P40H_C444926")
idx = c.rfind("(symbol", 0, idx)
d = 0
i = idx
while i < len(c):
    if c[i] == "(":
        d += 1
    elif c[i] == ")":
        d -= 1
        if d == 0:
            break
    i += 1
sym = c[idx:i+1]
pins = re.findall(r'\(pin "([^"]+)"', sym)
print("Pin count:", len(pins))
print("Pins:", pins)
for p in pins[-4:]:
    pidx = sym.find('(pin "' + p + '"')
    atidx = sym.find("(at", pidx)
    atend = sym.find(")", atidx)
    print("Pin", p, "at:", sym[atidx:atend+1])
