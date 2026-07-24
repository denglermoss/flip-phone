# Schematic Generation Scripts

These Python scripts generate KiCad schematic sheets (`.kicad_sch`) via direct
s-expression manipulation. They were used during Phase 3 (schematic design) to
create the hierarchical sub-sheets from the block diagram.

## Scripts

| Script | Output |
|--------|--------|
| `gen_schematics.py` | Root sheet (`phone.kicad_sch`) — hierarchical sheet boxes |
| `gen_modem_sch.py` | `modem.kicad_sch` — MPCIe socket + TXB0108 level shifter |
| `gen_codec_sch.py` | `codec.kicad_sch` — ALC5651 codec + I2S shifter + transducers |
| `gen_display_sch.py` | `display.kicad_sch` + `display_daughter.kicad_sch` |
| `gen_keypad_sch.py` | `keypad.kicad_sch` — 5×4 tactile switch matrix |
| `gen_sim_sd.py` | `sim_sd.kicad_sch` — SIM socket + microSD |

## Usage

```powershell
cd pcb/phone/scripts
python gen_schematics.py   # generates root sheet
python gen_modem_sch.py    # generates modem sheet
# etc.
```

## Notes

- These scripts are snapshots of the initial schematic generation. The `.kicad_sch`
  files have since been edited directly (via MCP tools, Python scripts, and KiCad
  GUI). Re-running these scripts will **overwrite** manual edits.
- Library tools (rebuild, verify, extract pins) are in `pcb/phone/lib/`, not here.
