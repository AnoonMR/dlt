"""
Generates index.html + i10..i60.html (long form) and s.html + is10..is60.html
(short form) for the AnoonMR/dlt GitHub Pages site - NLP lab programs.

Each page is visually blank (white space only) - the Aim, Procedure (long form
only, where available) and full Code for each program live inside an HTML
comment, visible via View Source (Ctrl+U) or Inspect (F12), for quick
copy-paste.

Sources (nothing is retyped here):
  - Long form title/Aim/Procedure: NLP_Lab_Programs_1to4.txt (Programs 1-4) and
    NLP_Lab_Program5.txt / NLP_Lab_Program6.txt, all in the nlp folder
    (read-only). Confirmed identical, code-for-code, to the already-tested
    notebooks in that same folder.
  - Short form Aim: the markdown cell of NLP_Lab_Programs_Short\\Program1..6.ipynb
    (read-only) - no Procedure is documented for the short forms (the short
    code often uses a different approach, e.g. Program 4 short uses
    pyspellchecker instead of a hand-rolled noisy channel model, so the long
    form's procedure would not describe it correctly - omitted rather than
    guessed).
  - Code (both forms): the two cells of the verified lt1 notebooks built by
    make_lt1_notebooks.py - auto-install/download cell merged in front of the
    program cell, so one paste into a fresh notebook cell installs what's
    missing and runs.

No datasets for this subject - everything is either a hardcoded string or an
NLTK corpus fetched by nltk.download() (idempotent, part of the verified code
itself), so there's no "Dataset:" line here (unlike PADV).

Run: python make_github_pages.py   (writes into this same lt1 folder)
"""
import os
import re

import nbformat

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
NLP_DIR = r"C:\Users\Anoon M R\Documents\nlp"
SHORT_DIR = os.path.join(NLP_DIR, "NLP_Lab_Programs_Short")

# Tab title is deliberately neutral on every page (user preference, set in the
# repo directly on 2026-09-09) so the tab never reveals what the page holds.
TAB_TITLE = "htnkl"

PAGE_CSS = "<style>html,body{margin:0;padding:0;background:#fff;min-height:100vh}</style>"

LONG_PROGRAMS = [
    ("1", "i10.html", "Program1_NLTK_SpaCy_Intro.ipynb"),
    ("2", "i20.html", "Program2_Tokenization_Normalization.ipynb"),
    ("3", "i30.html", "Program3_Edit_Distance.ipynb"),
    ("4", "i40.html", "Program4_Noisy_Channel_Spelling_Correction.ipynb"),
    ("5", "i50.html", "Program5_NGram_Model.ipynb"),
    ("6", "i60.html", "Program6_HMM_POS_Tagging.ipynb"),
]

SHORT_PROGRAMS = [
    ("1", "is10.html", "Short_Program1_NLTK_Intro.ipynb"),
    ("2", "is20.html", "Short_Program2_Tokenization_Normalization.ipynb"),
    ("3", "is30.html", "Short_Program3_Edit_Distance.ipynb"),
    ("4", "is40.html", "Short_Program4_Noisy_Channel_Spelling_Correction.ipynb"),
    ("5", "is50.html", "Short_Program5_NGram_Model.ipynb"),
    ("6", "is60.html", "Short_Program6_HMM_POS_Tagging.ipynb"),
]


def parse_multi(path):
    """Parse NLP_Lab_Programs_1to4.txt: several 'PROGRAM N: Title\\n----\\n' sections."""
    text = open(path, encoding="utf-8").read()
    parts = re.split(r"\nPROGRAM (\d+): (.+?)\n-{10,}\n", text)
    out = {}
    for i in range(1, len(parts), 3):
        num, title, body = parts[i], parts[i + 1].strip(), parts[i + 2]
        out[num] = dict(title=title, **_extract(body))
    return out


def parse_single(path):
    """Parse NLP_Lab_Program5.txt / Program6.txt: one 'PROGRAM N: Title\\n====\\n' section."""
    text = open(path, encoding="utf-8").read()
    m = re.match(r"PROGRAM (\d+): (.+?)\n=+\n", text)
    num, title = m.group(1), m.group(2).strip()
    return {num: dict(title=title, **_extract(text))}


def _extract(body):
    aim = re.search(r"AIM:\n(.+?)\n\n", body, re.S).group(1).replace("\n", " ").strip()
    proc = re.search(r"PROCEDURE:\n(.+?)\n\nCODE:", body, re.S).group(1)
    steps = [re.sub(r"^\s*\d+\.\s*", "", s).strip() for s in proc.splitlines() if s.strip()]
    return dict(aim=aim, procedure=steps)


def short_aim(nb_file):
    """Short forms only carry an Aim (no Procedure - see module docstring)."""
    nb = nbformat.read(os.path.join(SHORT_DIR, nb_file), as_version=4)
    md = nb.cells[0].source
    return re.search(r"\*\*AIM:\*\*\s*(.+)", md).group(1).strip()


def full_code(nb_file):
    nb = nbformat.read(os.path.join(OUT_DIR, nb_file), as_version=4)
    setup, program = [c.source.rstrip() for c in nb.cells if c.cell_type == "code"][:2]
    return setup + "\n\n" + program + "\n"


def long_block(num, record, code):
    title = f"Program {num}: {record['title']}"
    steps = "\n".join(f"{i}. {s}" for i, s in enumerate(record["procedure"], start=1))
    return (
        f"{title}\n{'=' * len(title)}\n\n"
        f"Aim\n---\n{record['aim']}\n\n"
        f"Procedure\n---------\n{steps}\n\n"
        f"Code\n----\n{code}"
    )


def short_block(num, title, aim, code):
    full_title = f"Program {num} (short): {title}"
    return (
        f"{full_title}\n{'=' * len(full_title)}\n\n"
        f"Aim\n---\n{aim}\n\n"
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


# ---- Long form: i10..i60.html + index.html ----
records = parse_multi(os.path.join(NLP_DIR, "NLP_Lab_Programs_1to4.txt"))
records.update(parse_single(os.path.join(NLP_DIR, "NLP_Lab_Program5.txt")))
records.update(parse_single(os.path.join(NLP_DIR, "NLP_Lab_Program6.txt")))

long_blocks = []
for num, page, nb_file in LONG_PROGRAMS:
    b = long_block(num, records[num], full_code(nb_file))
    long_blocks.append(b)
    write_page(page, b)
write_page("index.html", "\n\n\n".join(long_blocks))

# ---- Short form: is10..is60.html + s.html ----
short_blocks = []
for num, page, nb_file in SHORT_PROGRAMS:
    title = records[num]["title"]
    short_nb_file_in_short_dir = f"Program{num}.ipynb"
    aim = short_aim(short_nb_file_in_short_dir)
    b = short_block(num, title, aim, full_code(nb_file))
    short_blocks.append(b)
    write_page(page, b)
write_page("s.html", "\n\n\n".join(short_blocks))

print("Done.")
