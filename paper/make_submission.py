"""Assemble the Applied Energy submission package in submission/ (repository root).

    python paper/build.py --docx          # first: manuscript and supplementary material
    python paper/make_submission.py       # then: the upload files

Uses the manuscript-template skill (md2docx.py, split_submission.py, render_docx.py) and Pillow.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
OUT = REPO / "submission"
SKILL = Path(os.environ.get("MANUSCRIPT_TEMPLATE", Path.home() / ".claude/skills/manuscript-template/scripts"))
PY = sys.executable

FIGURES = [  # (number, file stem, short name) in order of first citation
    (1, "framework", "framework"),
    (2, "bdg2_cvrmse", "bdg2_cvrmse"),
    (3, "skill_by_target", "skill_by_target"),
    (4, "mv", "mv_pseudo_savings"),
    (5, "protocol_r2", "protocol"),
    (6, "lifecycle_bdg2", "lifecycle"),
]


def run(*args) -> str:
    r = subprocess.run([PY, *map(str, args)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise SystemExit(f"failed: {' '.join(map(str, args))}\n{r.stdout}\n{r.stderr}")
    return r.stdout.strip()


def tiff(src: Path, dst: Path) -> None:
    im = Image.open(src)
    if im.mode in ("RGBA", "P"):
        bg = Image.new("RGB", im.size, "white")
        bg.paste(im.convert("RGBA"), mask=im.convert("RGBA").split()[-1])
        im = bg
    im.save(dst, compression="tiff_lzw", dpi=(600, 600))


def main() -> None:
    build = HERE / "build"
    paper, supp = build / "paper.docx", build / "supplementary.docx"
    if not paper.exists():
        raise SystemExit("run python paper/build.py --docx first")
    if OUT.exists():
        for p in OUT.iterdir():
            if p.name != "README.md":
                shutil.rmtree(p) if p.is_dir() else p.unlink()
    OUT.mkdir(exist_ok=True)

    # 1. Manuscript and highlights (split from the one source document)
    tmp = build / "split"
    shutil.rmtree(tmp, ignore_errors=True)
    print(run(SKILL / "split_submission.py", paper, "--out-dir", tmp))
    shutil.copy(next(tmp.glob("*_Manuscript.docx")), OUT / "02_Manuscript.docx")
    shutil.copy(next(tmp.glob("*_Highlights.docx")), OUT / "03_Highlights.docx")

    # 2. Cover letter
    print(run(SKILL / "md2docx.py", HERE / "submission_sources" / "cover_letter.md", "-o", OUT / "01_Cover_Letter.docx"))

    # 3. Graphical abstract and figures (TIFF at 600 dpi, plus vector PDF)
    figs = OUT / "Figures"
    figs.mkdir()
    tiff(HERE / "figures" / "graphical_abstract.png", OUT / "04_Graphical_Abstract.tif")
    shutil.copy(HERE / "figures" / "graphical_abstract.pdf", OUT / "04_Graphical_Abstract.pdf")
    for n, stem, name in FIGURES:
        tiff(HERE / "figures" / f"{stem}.png", figs / f"Fig{n}_{name}.tif")
        shutil.copy(HERE / "figures" / f"{stem}.pdf", figs / f"Fig{n}_{name}.pdf")

    # 4. Supplementary material
    if supp.exists():
        shutil.copy(supp, OUT / "06_Supplementary_Material.docx")

    # 5. Reviewer suggestions and the declaration placeholder (author completes)
    for name in ("05_Suggested_Reviewers.md", "07_Declaration_of_Competing_Interest_README.md"):
        src = HERE / "submission_sources" / name
        if src.exists():
            shutil.copy(src, OUT / name)

    # 6. PDF of the manuscript for checking (Word engine on Windows)
    try:
        print(run(SKILL / "render_docx.py", OUT / "02_Manuscript.docx", "--out-dir", build / "render", "--update-fields"))
        pdf = next((build / "render").glob("*.pdf"))
        shutil.copy(pdf, OUT / "02_Manuscript_preview.pdf")
    except (SystemExit, StopIteration) as e:
        print(f"PDF preview skipped: {e}")
    print(f"Wrote {OUT}")
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(OUT)}  ({p.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
