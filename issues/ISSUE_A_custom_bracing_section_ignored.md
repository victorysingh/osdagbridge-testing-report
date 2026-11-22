**Title:** [Bug] Custom cross-bracing / end-diaphragm section is ignored: design always picks the lightest angle from a hard-coded catalogue list

**Labels (if you can set them):** bug

## Summary
In Additional Inputs > Member Properties > Cross Bracing (Design Type = Custom) I entered a section (`L 100 x 100 x 10` for G1-G2, `IS 100 x 100 x 10` for the other pairs). The design and the report ignore it and print `40 x 40 x 3` for every pair, the same result as the Optimized run. The grade problem is already reported in #43; this issue is only about the section designation. The root cause below is shared with #43 (I am posting the grade part as a comment there).

## Trigger conditions (worked vs failed)
| Run | Design Type | Cross-bracing input | Design Tables 5.24 - 5.28 |
|---|---|---|---|
| 1 | Optimized | default | 40 x 40 x 3 |
| 2 | Custom, 4 girders | L 100x100x10 (G1-G2), IS 100x100x10 (others), grade E 350A | 40 x 40 x 3 for every pair |
| 3 | Same as 2, Cross Bracing grade E 250A, End Diaphragm grade E 410A | same | tables identical to run 2, line by line |

So the girder and deck inputs reach the design (changing the girder grade to E 450A and the deck to M50 changed the output), but the bracing and end-diaphragm inputs never do.

Environment: dev branch, commit d74f56d, Windows, conda env `osdagbridge-env`. Basic inputs: span 20 m, carriageway 4.25 m (also a 4-girder Custom case), skew 0, Pehalgam J&K.

## Root cause
The bracing design does not use the user's inputs at all.

1. `src/osdagbridge/core/bridge_types/plate_girder/crossbracingforces.py`, `run_member_designs()` (about lines 619-626) builds each job like this:
```python
d = copy.deepcopy(design_dict_tension_bolted)   # or design_dict_struts_bolted
d["Load.Axial"]    = str(float(vals[t_key]))
d["Member.Length"] = str(L_mm)
```
Only the load and the length are overwritten.

2. `src/osdagbridge/core/utils/connect.py`, `design_dict_tension_bolted` (line 130) and `design_dict_struts_bolted` (line 376), hard-code:
```python
"Material": "E 250 (Fe 410 W)A",
"Connector.Material": "E 250 (Fe 410 W)A",
"Member.Designation": ["20 x 20 x 3", "20 x 20 x 4", ... ]   # full angle catalogue
```
Osdag then picks the lightest angle in that list that passes. For these small forces that is 40 x 40 x 3. The user's section never enters the job, so it cannot be used.

3. The same pattern is repeated for the end diaphragm in `plategirderbridge.py` (about lines 2762-2778).

## Suggested fix
In both call sites (`crossbracingforces.py` ~619-626 and `plategirderbridge.py` ~2773-2780), after the `deepcopy`, copy the user's values into the job dict:
```python
grade = self.bridge.input_dict.get(KEY_MP_CB_MATERIAL_GRADE)      # use the real key for the bracing / end-diaphragm grade
section = self.bridge.input_dict.get(<bracing section key for this pair>)
d["Material"] = grade
d["Connector.Material"] = grade
if design_type == "Custom" and section:
    d["Member.Designation"] = [section]       # only check the user's section
```
In Custom mode the report should then show that section with its real UR (and FAIL if it does not pass). In Optimized mode the grade should still be taken from the input.

## Impact
Custom design of bracing and end diaphragm is not possible. A user who selects a heavier section or a higher grade sees no change, and the report states a section and grade that are not the ones entered.

## Evidence to attach
- Screenshot of Member Properties with `L 100 x 100 x 10` entered (Custom).
- Report pages with Tables 5.24 - 5.28 for run 2 and run 3 (`run2_report.pdf`).
- `inputscustom.osi` (run 2) and `inputsc.osi` (run 3) from the ZIP.
