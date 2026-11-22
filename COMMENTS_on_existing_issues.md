# Comments to post on existing issues (extra evidence only, no new issue)

Post each block as a comment on the issue number in its heading. Attach the named file or screenshot where noted.

---
## #174  ospgrillage load combination factors are omitted
I reproduced this independently in the GUI and it shows up in the report.

Setup: span 20 m, carriageway 4.25 m, Optimized, default inputs (also in 4 more runs, including Custom mode with 4 girders).
Table 4.1 "Summary of Maximum Demands", max bending moment (kNm), run 1:
- BASIC 1 = BASIC 5 = SLS RARE = SLS FREQUENT = Envelope SLS (same number in every case)
- SEISMIC 1 = 2 = 4 (same number, although the factors differ)
- SLS QP 1 = SLS QP 2
Custom run: BASIC 1 = BASIC 5 = ... = 687.989, SEISMIC 1 = 2 = 4 = 572.464, SLS QP 1 = QP 2 = 459.564.

Where: `core/bridge_types/plate_girder/analyser.py` around lines 2344-2349, 2406, 2539-2544 and 2593 build the load commands, and in the ospgrillage package `load.py` (~1157-1167) and `osp_grillage.py::_distribute_load_types_to_model` the `load_dict["factor"]` is not applied to the element loads. Everything is solved with factor 1.0, so all combinations that differ only by factors collapse to one result.

---
## #71  Save Input overwrites committed deck and wearing-course thicknesses with defaults
Same bug, but it is wider than the deck and wearing-course thickness. I confirmed it by testing 3 times (values entered, Save Input, reopen):
- Deck thickness 275 -> 250
- Studs: dia 22 / spacing 125 / count 3 -> 20 / default / 2
- γM0 1.25 -> 1.1 and γMft 1.15 -> default
- Clear covers 40 / 60 -> defaults
- Limit State ticks (Fatigue, Deflection) unticked -> ticked again
- Loading tab values

Root cause: `core/bridge_types/plate_girder/defaults.py`, lines ~181-385 (`_update_typical_section_defaults`, `_update_loading_tab_defaults`, `_update_design_options_defaults`, `_update_design_options_cont_defaults`). The docstrings say "Fill ... keys that are None", but the code does `input_dict.update({key: value})` or `input_dict[key] = value` unconditionally (e.g. the deck-thickness line ~185; a comment at ~363 says "Update dict (solves some osi values not being loaded)").

They run from `solve_extend_basic_input_dict()` (defaults.py ~870), which is called from `desktop/ui/template_page.py` at ~648 (Design, if a basic field changed), ~797 (`saveOSI_inputs`), ~867 and ~896.

Fix: set a default only when the key is empty:
```python
if input_dict.get(key) in (None, ""):
    input_dict[key] = value
```
Side effect: a saved .osi file can never contain custom values for these keys, which makes this a good test for any fix.
It looks like the behaviour appeared with commit 4519d16 "fix: put defaults when value is Not None".

---
## #146  Turning off design checks in Design Options (Cont.) does nothing
Confirmed with Fatigue and Deflection unticked: the report still contains the fatigue and deflection checks and the status still fails on them. The keys `KEY_DO_ULS_*` / `KEY_DO_SLS_*` are not read in `plategirderbridge.py`, `designer.py` or `core/reports` (search for them: no consumer). Also, `defaults.py::_update_design_options_cont_defaults` resets them to True on Save Input (see my comment on #71), so the ticks can not even be stored in a .osi file.

---
## #43  Cross-bracing and end-diaphragm custom grades are stored but unused in design
Root cause found, and it covers the standard grades too (not only custom grades): `core/utils/connect.py`, `design_dict_tension_bolted` (line 130) and `design_dict_struts_bolted` (line 376) hard-code `"Material": "E 250 (Fe 410 W)A"` and `"Connector.Material"`. `crossbracingforces.py::run_member_designs` (~619-626) and `plategirderbridge.py` (~2773-2780) deep-copy those dicts and override only `Load.Axial` and `Member.Length`.
Test: Custom run with Cross Bracing grade E 350A, then E 250A, End Diaphragm E 410A: the design tables of both runs are identical line by line. (The girder grade E 450A and the deck M50 did change the output, so the problem is limited to the bracing / end-diaphragm path.)
Fix: copy the grade (and in Custom mode the section) into `d["Material"]`, `d["Connector.Material"]`, `d["Member.Designation"]`. Section part is in my new issue (link it here once posted).

---
## #216  Cross-bracing UR is not demand / capacity
Extra evidence that a constant is used as the denominator. Custom run, G1-G2:
- diagonal compression: demand 9.052 kN, capacity 30.600 kN, printed UR 0.830 = 9.052 / **10.9**
- chord: demand 7.278 kN, capacity 36.810 kN, printed UR 0.670 = 7.278 / **10.9**
In the Optimized run the same 10.9 appears while the member capacity was 24.22 kN, so the denominator does not follow the member. Reproduced in 3 runs.

---
## #65  Executive Summary says "design pass" even when Overall Status is Fail
Hard-coded pass lines in `core/reports/executive_summary.py` (~lines 233-236). In my Custom run 3 the Overall Design Status listed only "Int. Stiff: Leg H limit, Fatigue Normal Stress", while Key Design Outcomes still said "Deck design pass" and "Girder design pass" although Table 5.13 shows 4 girders FAIL (G1/G3/G4 stiffener UR 1.107, G2 fatigue 1.196). The deck clear-cover FAIL (M50, required >= 75 mm, provided 50) and the deflection FAIL are also left out of the overall status.

---
## #115  Deck cover check infers exposure class from concrete grade
Reproduced: M40 -> "Clear Cover required >= 50 mm PASS"; M50 -> ">= 75 mm (Table 14.2), Top 50 / Bottom 50 FAIL". The FAIL is not included in the overall status (see #65).

---
## #116  Optimized mode uses the un-rounded initial-sizing section
Matches what I see: in Optimized mode the BOM and section table use the empirical default properties (A = 0.015592 m², mass 122.3973, Iz 0.0035369979) from `additional_inputs.py::_compute_welded_section_properties` (~line 1677) and `initial_sizing.py` (~line 424). In Custom mode the BOM area follows the entered section, so it is specific to Optimized mode.
