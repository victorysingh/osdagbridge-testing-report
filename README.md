# OsdagBridge testing and issue reporting

FOSSEE Winter Internship 2026 screening task: **OsdagBridge Software Testing and Issue Reporting** (https://github.com/Nidhikhare12/OsdagBridge, `dev` branch, commit `d74f56d`).

Main document: [`docs/report.pdf`](docs/report.pdf) (LaTeX source `docs/report.tex`).

## What was done
- 29 test cases and 6 consecutive design runs: default values and custom steel / deck values, boundary inputs, restart and repeat runs, 3D CAD and plots, design reports.
- Input Dictionary (`.osi`) compared with the values entered in the UI and with the design reports.
- All 136 existing issues and 84 pull requests were read before posting, to avoid duplicates.

## GitHub issues raised
| Issue | Topic |
|---|---|
| [#221](https://github.com/Nidhikhare12/OsdagBridge/issues/221) | Custom cross-bracing / end-diaphragm section is ignored (hard-coded template in `core/utils/connect.py`) |
| [#222](https://github.com/Nidhikhare12/OsdagBridge/issues/222) | "Defaults" button in Additional Inputs restores the last saved values, prints the dictionary |
| [#223](https://github.com/Nidhikhare12/OsdagBridge/issues/223) | Saved `.osi` section properties for G2-G4 do not match the entered sections |

## Comments added to existing issues
[#174](https://github.com/Nidhikhare12/OsdagBridge/issues/174) (load combination factors), [#71](https://github.com/Nidhikhare12/OsdagBridge/issues/71) (Save Input resets values), [#146](https://github.com/Nidhikhare12/OsdagBridge/issues/146) (limit-state ticks), [#43](https://github.com/Nidhikhare12/OsdagBridge/issues/43) (bracing grade, root cause), [#216](https://github.com/Nidhikhare12/OsdagBridge/issues/216), [#65](https://github.com/Nidhikhare12/OsdagBridge/issues/65), [#115](https://github.com/Nidhikhare12/OsdagBridge/issues/115), [#116](https://github.com/Nidhikhare12/OsdagBridge/issues/116). Text in `comments/`.

## Folders
| Folder | Content |
|---|---|
| `test_cases/` | `TEST_CASES.csv` and `TEST_CASES.md`: ID, exact parameters, expected, actual, pass / fail, finding |
| `osi_files/` | saved input files: runs 2 and 3, and two files showing that File > Save Input resets custom values |
| `reports/` | the generated design reports of runs 1-5 |
| `issues/`, `comments/` | text of the new issues and of the comments |
| `scripts/` | scripts that generate the test-case table and the LaTeX report |
| `docs/` | `report.pdf`, `report.tex` |

## Note on the `.osi` files
Because of the bug in File > Save Input (comment on #71), a saved `.osi` file cannot contain custom deck thickness, stud, partial-factor, cover or limit-state values. Those runs are documented through the reports (`reports/run4_*`) and the screen recording.

## Rebuild the table and report
```
python scripts/make_test_cases.py
python scripts/make_report_tex.py
cd docs && pdflatex report.tex && pdflatex report.tex
```
