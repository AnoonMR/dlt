"""
Generates index.html + i10..i60.html (+ i65.html for Program 6B) for the
AnoonMR/dlt GitHub Pages site - PADV (Predictive Analytics and Data
Visualization) lab programs.

Each page is visually blank (white space only) - the Aim, Procedure (long
form) and full Code for each program live inside an HTML comment, visible via
View Source (Ctrl+U) or Inspect (F12), for quick copy-paste.

Sources (nothing is retyped here):
  - Title / Aim / Procedure (long form): PADV_Lab_Record.txt in the padv lab
    folder (read-only).
  - Code: the two cells of the verified lt1 notebooks built by
    make_lt1_notebooks.py - auto-install cell merged in front of the program
    cell, so one paste into a fresh notebook cell installs what's missing and runs.

Datasets are never embedded in or downloaded by the code (code stays clean).
Each block names its CSV on a "Dataset:" line; place that file next to the
notebook before running.

Run: python make_github_pages.py   (writes into this same lt1 folder)
"""
import os
import re

import nbformat

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
RECORD = r"C:\all\3 sem\padv\lab\PADV_Lab_Record.txt"

PENG, MALL = "penguins_size.csv", "Mall_Customers.csv"
PROGRAMS = [
    ("1", "i10.html", "Program1_Data_Cleaning_Preprocessing.ipynb", PENG),
    ("2", "i20.html", "Program2_Exploratory_Data_Analysis.ipynb", MALL),
    ("3", "i30.html", "Program3_Regression_Model.ipynb", PENG),
    ("4", "i40.html", "Program4_Classification_Clustering.ipynb", MALL),
    ("5", "i50.html", "Program5_Visualization_Matplotlib_Seaborn.ipynb", PENG),
    ("6", "i60.html", "Program6_Interactive_Dashboard_Plotly.ipynb", MALL),
    ("6B", "i65.html", "Program6B_Interactive_Dashboard_Dash.ipynb", MALL),
]

# The Program 5 notebook (newer than the record) also computes ANOVA feature
# importance and prints a final analysis summary - add matching steps.
EXTRA_STEPS = {
    "5": [
        "Rank numeric features by how well they separate species using the one-way ANOVA F-statistic and plot it.",
        "Print a final analysis summary (proportions, islands, top species per measurement, correlations).",
    ],
}

# Tab title is deliberately neutral on every page (user preference, set in the
# repo directly on 2026-09-09) so the tab never reveals what the page holds.
TAB_TITLE = "htnkl"

PAGE_CSS = "<style>html,body{margin:0;padding:0;background:#fff;min-height:100vh}</style>"


def parse_record():
    text = open(RECORD, encoding="utf-8").read()
    sections = re.split(r"={70}\nPROGRAM (\w+)\n={70}\n", text)[1:]
    out = {}
    for num, body in zip(sections[::2], sections[1::2]):
        title = re.search(r"^TITLE: (.+)$", body, re.M).group(1).strip()
        aim = re.search(r"^AIM: (.+)$", body, re.M).group(1).strip()
        proc = re.search(r"^PROCEDURE:\n(.*?)\n\n", body, re.S | re.M).group(1)
        steps = [re.sub(r"^\s*\d+\.\s*", "", s) for s in proc.splitlines() if s.strip()]
        out[num] = dict(title=title, aim=aim, procedure=steps + EXTRA_STEPS.get(num, []))
    return out


def full_code(nb_file):
    nb = nbformat.read(os.path.join(OUT_DIR, nb_file), as_version=4)
    setup, program = [c.source.rstrip() for c in nb.cells if c.cell_type == "code"][:2]
    return setup + "\n\n" + program + "\n"


def block(num, prog, code, dataset):
    title = f"Program {num}: {prog['title']}"
    steps = "\n".join(f"{i}. {s}" for i, s in enumerate(prog["procedure"], start=1))
    return (
        f"{title}\n"
        f"{'=' * len(title)}\n\n"
        f"Aim\n---\n{prog['aim']}\n\n"
        f"Dataset: {dataset} (place it in the same folder as the notebook)\n\n"
        f"Procedure\n---------\n{steps}\n\n"
        f"Code\n----\n{code}"
    )


def check_safe(text, where):
    if "-->" in text:
        raise ValueError(f"'-->' found in {where} - would break the HTML comment, fix source text")


def write_page(filename, comment_body):
    check_safe(comment_body, filename)
    html = (
        "<!doctype html>\n"
        "<html><head><meta charset=\"utf-8\">"
        f"<title>{TAB_TITLE}</title>{PAGE_CSS}</head>\n"
        "<body>\n"
        "<!--\n"
        f"{comment_body}\n"
        "-->\n"
        "</body></html>\n"
    )
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print("Wrote", path)


record = parse_record()
blocks = []
for num, page, nb_file, dataset in PROGRAMS:
    b = block(num, record[num], full_code(nb_file), dataset)
    blocks.append(b)
    write_page(page, b)

# index.html: all programs combined in one comment
write_page("index.html", "\n\n\n".join(blocks))

print("Done.")
