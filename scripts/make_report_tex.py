"""Builds docs/report.tex from the test-case list and the hand-written sections below.
Run:  python scripts/make_report_tex.py && cd docs && pdflatex report.tex (twice)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from make_test_cases import TC  # noqa: E402

GH = "https://github.com/Nidhikhare12/OsdagBridge/issues/"
STUDENT = os.environ.get("STUDENT_NAME", "YOUR NAME")
REPO_URL = os.environ.get("REPO_URL", "https://github.com/victorysingh/osdagbridge-testing-report")


def esc(s):
    m = {"\\": "\\textbackslash{}", "&": "\\&", "%": "\\%", "$": "\\$", "#": "\\#", "_": "\\_",
         "{": "\\{", "}": "\\}", "~": "\\textasciitilde{}", "^": "\\^{}"}
    s = "".join(m.get(c, c) for c in s)
    s = s.replace("->", "$\\rightarrow$").replace(">=", "$\\geq$").replace("<=", "$\\leq$")
    s = s.replace("gamma\\_M0", "$\\gamma_{M0}$").replace("gamma\\_Mft", "$\\gamma_{Mft}$")
    return s


def link_issues(s):
    """Turn #123 into a hyperlink (after escaping)."""
    return re.sub(r"\\#(\d+)", lambda m: "\\href{%s%s}{\\#%s}" % (GH, m.group(1), m.group(1)), s)


def cell(s):
    return link_issues(esc(s))


def tc_rows():
    rows = []
    for tid, area, params, exp, act, res, find in TC:
        color = "passc" if res.startswith("PASS") and "FAIL" not in res else "failc"
        rows.append("%s & %s & %s & %s & \\textcolor{%s}{\\textbf{%s}} & %s \\\\ \\hline" % (
            tid, cell(params), cell(exp), cell(act), color, cell(res), cell(find)))
    return "\n".join(rows)


FINDINGS = [
 # id, title, severity, GitHub status
 ("F13", "Load combination factors are not applied (all combinations equal the unfactored sum)", "Critical (unsafe)", "Existing issue \\#174; comment added"),
 ("F28", "File > Save Input overwrites custom Additional Inputs with defaults", "High", "Existing issue \\#71; comment added with full list and root cause"),
 ("F29", "Fatigue / Deflection limit-state ticks are ignored", "High", "Existing issue \\#146; comment added"),
 ("F25", "Bracing and end-diaphragm steel grade have no effect", "High", "Existing issue \\#43; comment added with root cause"),
 ("F24", "Custom cross-bracing section ignored (lightest angle from a hard-coded list is used)", "High", "NEW issue \\#221"),
 ("F30", "Defaults button restores last saved values, prints dictionary to console", "Medium", "NEW issue \\#222"),
 ("F26", "Saved .osi section properties do not match entered sections", "Medium", "NEW issue \\#223"),
 ("F4", "Cross-bracing compression UR is force / 10.9 kN, not force / capacity", "High", "Existing issue \\#216; comment added"),
 ("F19", "Report summary says 'design pass' while overall status is Fail", "Medium", "Existing issue \\#65; comment added"),
 ("F22", "Optimized mode: section table and BOM use empirical default section", "Medium", "Existing issue \\#116; comment added"),
 ("F27", "Deck clear cover required 75 mm for M50 (50 mm for M40); FAIL not in overall status", "Medium", "Existing issue \\#115; comment added"),
 ("F23", "Custom per-girder sections ignored in report and design tables", "High", "Related to existing \\#151; see also \\#223"),
 ("F21", "End-diaphragm tables duplicate cross-bracing tables", "Medium", "Existing issue \\#72"),
 ("F18", "Several menu actions do nothing", "Medium", "Existing issues \\#123, \\#53"),
 ("F20", "Report: placeholders, wrong units, empty tables", "Medium", "Existing issues \\#66, \\#68, \\#70, \\#48, \\#104"),
 ("F11", "Support reaction R\\_B disagrees with shear and diagram", "Medium", "Related to existing \\#73 (not posted separately)"),
 ("F5", "Cross-bracing frame count and spacing differ between 3D and panel", "Medium", "Related to existing \\#93 (not posted separately)"),
 ("F16", "Crash barrier load much lower than input", "Medium (to verify)", "Existing issue \\#143 (not posted separately)"),
 ("F1", "Skew 15: Girder 1 plots start at negative x, spike, Vd differs from plotted Vy", "Medium", "Not posted: root cause not traced; related \\#198, \\#132, \\#89"),
 ("F10", "Stiffener preview shows 11 interior lines, 3D and table about 7", "Low", "Not posted: root cause not traced"),
 ("F31", "Table 4.1 row order is not deterministic", "Low", "Not posted (minor)"),
]

COMPARE = [
 ("Deck thickness", "275", "250.0 (after Save Input)", "275.0 (Design without Save Input)"),
 ("Studs dia / spacing / count", "22 / 125 / 3", "20 / 100 / 2", "22 / 125 / 3"),
 ("$\\gamma_{M0}$, $\\gamma_{Mft}$", "1.25, 1.15", "1.10, default", "1.25, 1.15 (capacity 108.58 x 1.15 = 124.86)"),
 ("Clear cover top / bottom", "40 / 60", "50 / 50", "40 / 60"),
 ("Fatigue, Deflection ticks", "unticked", "ticked", "checks still run and are reported"),
 ("Girder grade / deck grade", "E 450A / M50", "E 450A / M50", "limits change correctly (fy 450, Ecm for M50)"),
 ("Bracing / end-diaphragm grade", "E 250A / E 410A", "E 250A / E 410A", "Table 2.3 prints them, design tables unchanged"),
 ("Bracing section (Custom)", "L 100x100x10", "L 100x100x10", "design 40 x 40 x 3 for every pair"),
 ("G1 section (Custom)", "web 1200, flanges 360 x 18", "area saved '2.23e-02' (string)", "Table 5.1: 1120, 340 x 16, A 202.48 cm$^2$"),
 ("G2, G3 section (Custom)", "web 1120, 340x16 / 340x18, tw 8 (hand A 0.020248 m$^2$)", "area 0.01559201 m$^2$", "A 202.48 cm$^2$ (matches hand)"),
 ("G4 section (Custom)", "top 340 x 16, bottom 400 x 18 (hand A 0.021328 m$^2$)", "area 0.01741475 m$^2$", "A 202.48 cm$^2$ (G2 section)"),
 ("Number of girders, spacing", "4, 1.2875 m", "4 (plus phantom G0 keys)", "4, 1.2875 m"),
]

RUNS = [
 ("0", "Optimized, defaults, skew 0 / 15", "5", "512.24 (skew 0)", "passes in UI; F1, F4, F5, F10, F11, F13"),
 ("1", "Optimized, defaults", "3", "690.518", "UR 1.35 Fail (fatigue)"),
 ("2", "Custom, per-girder sections", "4", "724.837", "UR 1.20 Fail; F23, F24"),
 ("3", "Run 2 + grades E 450A / E 250A / E 410A, deck M50", "4", "724.837", "Fail (stiffener leg, fatigue); F25, F27"),
 ("4", "Optimized + custom Additional Inputs (no Save Input)", "3", "723.775", "Fail (fatigue UR 1.18); F28, F29"),
 ("5", "Restart, same as run 1", "3", "690.518", "identical to run 1"),
]


def comp_rows():
    return "\n".join("%s & %s & %s & %s \\\\ \\hline" % (a, b, c, d) for a, b, c, d in COMPARE)


def run_rows():
    return "\n".join("%s & %s & %s & %s & %s \\\\ \\hline" % tuple(esc(x) if i != 0 else x for i, x in enumerate(r)) for r in RUNS)


def find_rows():
    return "\n".join("%s & %s & %s & %s \\\\ \\hline" % (fid, t, sev, st) for fid, t, sev, st in FINDINGS)


TEX = r"""\documentclass[10pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[margin=1.6cm,landscape]{geometry}
\usepackage{longtable,array,tabularx,booktabs,xcolor,hyperref,graphicx,fancyhdr,enumitem}
\definecolor{passc}{HTML}{1B7F3B}
\definecolor{failc}{HTML}{B3261E}
\hypersetup{colorlinks=true,linkcolor=blue!60!black,urlcolor=blue!60!black}
\setlength{\parindent}{0pt}\setlength{\parskip}{4pt}
\renewcommand{\arraystretch}{1.15}
\pagestyle{fancy}\fancyhf{}\fancyfoot[C]{\thepage}\fancyhead[L]{OsdagBridge testing report}\fancyhead[R]{FOSSEE Winter Internship 2026}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}
\begin{document}
\begin{center}
{\LARGE\bfseries OsdagBridge: Software Testing and Issue Reporting}\\[4pt]
FOSSEE Winter Internship 2026 screening task, Osdag (IIT Bombay)\\[2pt]
Author: __STUDENT__ \quad Date: 22 November 2026\\[2pt]
Test repository: \href{__REPO__}{__REPO__}
\end{center}

\section{Summary}
I tested OsdagBridge (plate girder bridge module, \texttt{dev} branch, commit \texttt{d74f56d}) with __NTC__ test cases and 6 consecutive design runs, using default values and custom values for the steel girders, stiffeners, bracing, end diaphragms and the concrete deck. __NPASS__ cases passed, the rest found problems. Input validation, repeatability across restarts, and the grade and deck propagation for girder and deck work correctly. The main problems are that several user inputs are not used or are reset (Save Input, Defaults button, bracing and end-diaphragm grade and section, limit-state ticks), that load combination factors are not applied, and that the report contradicts itself.

I posted \textbf{3 new GitHub issues} (\href{__GH__221}{\#221}, \href{__GH__222}{\#222}, \href{__GH__223}{\#223}), each with trigger conditions, evidence, root cause with file and line, and a suggested fix. For bugs that were already reported by others I did not open duplicates; I added \textbf{8 comments} with extra evidence and root cause to \href{__GH__174}{\#174}, \href{__GH__71}{\#71}, \href{__GH__146}{\#146}, \href{__GH__43}{\#43}, \href{__GH__216}{\#216}, \href{__GH__65}{\#65}, \href{__GH__115}{\#115} and \href{__GH__116}{\#116}. I checked all 136 existing issues and 84 pull requests before posting.

\section{Environment and method}
\begin{itemize}[nosep]
\item Windows, conda environment \texttt{osdagbridge-env}, started with \texttt{python -m osdagbridge.desktop} from \texttt{src}. Source: fork of \texttt{Nidhikhare12/OsdagBridge}, branch \texttt{dev}, commit \texttt{d74f56d}.
\item Defaults unless stated: Pehalgam (J\&K), no median, no footpath, Optimized design type, steel E~350A, deck M40.
\item Each design run produced a PDF design report and, where stated, a saved \texttt{.osi} input file (folders \texttt{reports/} and \texttt{osi\_files/} in the repository).
\item Checks: (1) compare the UI values with the saved input file and with the report; (2) compare numbers between runs that differ in one input; (3) hand calculations (section areas, utilisation ratios, load sums); (4) read the source code to find the cause of each failure.
\end{itemize}

\section{Test cases}
Result colours: \textcolor{passc}{\textbf{PASS}} = worked as expected, \textcolor{failc}{\textbf{FAIL}} = error, mismatch or ignored input.

{\small
\begin{longtable}{|p{1.2cm}|p{6.2cm}|p{3.6cm}|p{7.2cm}|p{1.8cm}|p{3.6cm}|}
\hline \textbf{ID} & \textbf{Exact parameters} & \textbf{Expected} & \textbf{Actual} & \textbf{Result} & \textbf{Finding / GitHub} \\ \hline \endhead
__TCROWS__
\end{longtable}}

\section{UI inputs vs input dictionary (\texttt{.osi}) vs report}
The \texttt{.osi} file is the saved Input Dictionary. The ``Report'' column is the design report of the run in which the value was entered (Design without File $>$ Save Input, except where stated).

{\small
\begin{longtable}{|p{4cm}|p{6cm}|p{5.5cm}|p{7cm}|}
\hline \textbf{Input} & \textbf{Entered in UI} & \textbf{Saved \texttt{.osi}} & \textbf{Design report} \\ \hline \endhead
__COMPROWS__
\end{longtable}}

Reading: custom values do reach the design when \emph{File $>$ Save Input} is not used (deck 275, studs, $\gamma$ factors, covers). \emph{File $>$ Save Input} replaces them with defaults before writing the file, so a saved \texttt{.osi} cannot carry those values (finding F28). Bracing and end-diaphragm grade and section are stored and printed in the inputs table but never used by the design (F24, F25).

\section{Multi-run stability}
{\small
\begin{longtable}{|p{1cm}|p{8cm}|p{2cm}|p{4cm}|p{7cm}|}
\hline \textbf{Run} & \textbf{Inputs} & \textbf{Girders} & \textbf{Envelope ULS max BM (kNm)} & \textbf{Outcome} \\ \hline \endhead
__RUNROWS__
\end{longtable}}

Six runs completed without a crash. Each run reflected the changed inputs (girder count 3 $\rightarrow$ 4 $\rightarrow$ 3, sections, grades), and run 5 after an application restart reproduced run 1 exactly (Envelope ULS 690.518 kNm, UR 1.35, all tables equal except date and author lines). Run 3 repeated with the same inputs gave an identical report. I did not observe the stale segment-table problem reported in \href{__GH__168}{\#168} and \href{__GH__125}{\#125} in my runs, so I did not comment on them. Table 4.1 of the report lists its rows in a different order between run 1 and run 5 (F31, minor).

\section{3D CAD and plots}
\begin{itemize}[nosep]
\item \textbf{Works:} 3D model generated in all runs; layer toggles, node and element numbering, rotation, TOP/front/left views and hover highlighting work without a crash; skew 15 is drawn correctly in the top view; girder web, flange and stiffener tooltips equal the Details tables.
\item \textbf{Fails:} at skew 15 the Girder 1 plots start at $x=-1.407$~m with a spike near 4~m, and the design shear (8.25~kN) differs from the plotted maximum (7.61~kN), while skew 0 is consistent (F1). The stiffener preview shows 11 interior lines against about 7 in the 3D model and table (F10). The 3D model has 7 cross-bracing frames, the panel lists 9 at 3.000~m (F5). Reaction R\_B in the analysis panel disagrees with the diagram and the shear (F11).
\end{itemize}

\section{Findings and GitHub status}
{\small
\begin{longtable}{|p{1.1cm}|p{12cm}|p{3cm}|p{7cm}|}
\hline \textbf{ID} & \textbf{Finding} & \textbf{Severity} & \textbf{GitHub} \\ \hline \endhead
__FINDROWS__
\end{longtable}}

\subsection*{The three new issues in short}
\textbf{\href{__GH__221}{\#221} Custom bracing section ignored (F24).} \texttt{crossbracingforces.py} (\texttt{run\_member\_designs}, about lines 619--626) copies the template dictionary \texttt{design\_dict\_tension\_bolted} / \texttt{design\_dict\_struts\_bolted} from \texttt{core/utils/connect.py} (lines 130 and 376) and changes only load and length. The template hard-codes material E~250 and the full angle list, so Osdag picks the lightest passing angle (40$\times$40$\times$3). The same pattern is in \texttt{plategirderbridge.py} (about lines 2762--2778). Fix: put the user's section into \texttt{Member.Designation} for Custom mode and the user's grade into \texttt{Material}.

\textbf{\href{__GH__222}{\#222} Defaults button (F30).} In \texttt{additional\_inputs.py}, \texttt{reset\_active\_tab\_defaults} (about line 446) restores from \texttt{default\_input\_dict}, which is the same object as the main \texttt{input\_dict} (line about 223) and is overwritten by \texttt{\_save\_inputs} (line about 519). Fix: keep a deep copy of the factory defaults; remove the leftover \texttt{pprint} (lines about 158--161).

\textbf{\href{__GH__223}{\#223} Stale section properties in the saved file (F26).} G2--G4 areas equal the empirical default section (0.01559201 m$^2$) instead of the entered one (hand: 0.020248 and 0.021328 m$^2$); G1 is saved as a 3-digit string; \texttt{web\_depth} is wrong. Fix: recompute properties for every girder before saving and store floats.

\section{Limitations and work not done}
\begin{itemize}[nosep]
\item I compared the Input Dictionary with the UI values and the reports in detail (section above). I did not compare every field of the Output Dictionary with the report and the Output Dock; I checked the cross-bracing forces, section properties and the load-case results only.
\item The deck design tables (Tables 5.16--5.22) were not hand-checked.
\item F1 (skew plots) and F10 (stiffener preview) are documented here but their root cause is not traced, so no issue was posted. F16 and F17 (double-angle properties) need further verification.
\item The saved \texttt{.osi} files cannot hold the custom deck, stud, $\gamma$ and tick values because of F28. These values are shown by the reports and in the screen recording instead.
\item Clear cover $=0/300$ and negative or text $\gamma$ values were not tested.
\end{itemize}

\section{Repository contents}
\begin{tabular}{ll}
\texttt{test\_cases/} & TEST\_CASES.csv and .md (same table as section 3) \\
\texttt{osi\_files/} & saved input files of runs 2 and 3 and the two files that show F28 \\
\texttt{reports/} & the six generated design reports (runs 1 to 5, run 3 twice) \\
\texttt{issues/}, \texttt{comments/} & text of the 3 new issues and the 8 comments \\
\texttt{scripts/} & scripts that generate the test-case table and this report \\
\end{tabular}

\end{document}
"""


def main():
    n = len(TC)
    npass = sum(1 for r in TC if r[5].startswith("PASS") and "FAIL" not in r[5])
    tex = TEX
    for k, v in {
        "__STUDENT__": esc(STUDENT), "__REPO__": REPO_URL, "__GH__": GH, "__NTC__": str(n), "__NPASS__": str(npass),
        "__TCROWS__": tc_rows(), "__COMPROWS__": comp_rows(), "__RUNROWS__": run_rows(), "__FINDROWS__": find_rows(),
    }.items():
        tex = tex.replace(k, v)
    out = os.path.join(ROOT, "docs")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "report.tex"), "w", encoding="utf-8") as f:
        f.write(tex)
    print("written", n, "cases")


if __name__ == "__main__":
    main()
