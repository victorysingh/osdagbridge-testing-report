**Title:** [Bug] Saved .osi section properties for G2-G4 do not match the entered sections (empirical defaults kept), web_depth wrong, numbers saved as 3-significant-figure strings

(The phantom `G0` key is already in #197 and stale segment tables are in #168 / #125, so they are not repeated here beyond one line.)

## Summary
In Custom mode with different sections per girder, the saved `.osi` file stores section properties that belong to a different (default) section, and a different type for G1.

## Trigger conditions
Basic inputs: span 20 m, carriageway 4.25 m, 4 girders, Design Type = Custom. Member Properties:
- G1: web 1200, flanges 360 x 18 (top and bottom)
- G2, G3: web 1120, top flange 340 x 16, bottom flange 340 x 18, web thickness 8
- G4: top 340 x 16, bottom 400 x 18
File > Save Input -> `inputscustom.osi`.

## Observed vs expected (hand calculation)
| Item | Saved in .osi | Expected |
|---|---|---|
| `section_properties.area.G2` and `G3` | 0.01559201 m² | 5440 + 6120 + 1086 x 8 = 20 248 mm² = **0.020248 m²** (202.48 cm², the value in the report) |
| `section_properties.area.G4` | 0.01741475 | 21 328 mm² = **0.021328** |
| `section_properties.area.G1` | `'2.23e-02'` (string, 3 sig. figs.) | 0.022272 float |
| `web_depth` G1 / G2 / G4 | 1092 / 1092 / 1090 | 1164 / 1086 / 1086 (this is what the area calculation uses) |
| un-suffixed keys (`depth`, `area`, `mass`, ...) | copy of G4 | no meaning for a multi-section bridge |

0.01559201 and mass 122.3973 are exactly the empirical default section of the Optimized run (same numbers in a plain default `.osi`). So the properties for G2-G4 were never recomputed from the entered dimensions.

## Root cause (partly traced)
The properties are written from the empirical sizing path, not from the entered plates. Welded properties are computed in `desktop/ui/dialogs/additional_input/additional_inputs.py::_compute_welded_section_properties()` (line ~1677). Per-girder results are not refreshed on edit/save for G2-G4. I did not trace which exact call writes the stale default values into the dict; start with where `section_properties.*` keys are assigned after Save and `solve_extend_basic_input_dict()` in `core/bridge_types/plate_girder/defaults.py`.

## Suggested fix
- Recompute `area`, `mass`, `Iz`, `web_depth`, ... for every girder from the current flange/web inputs on edit and again right before `saveOSI_inputs()` writes the file.
- Store floats at full precision, not formatted strings.
- Do not write the un-suffixed aggregate keys, or document them.

## Impact
Reloading the file, or any consumer of the input dictionary, shows section properties that do not belong to the section the user entered.

## Evidence to attach
`inputscustom.osi` (lines for `section_properties.area.G1..G4` and `web_depth`), screenshot of Member Properties, and the hand calculation above.
