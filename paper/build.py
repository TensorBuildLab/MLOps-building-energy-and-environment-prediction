"""Assemble the manuscript and the supplementary material, then build the Word files.

Retired on 2026-11-08: the Word masters paper/Manuscript.docx and paper/Supplementary_Material.docx are now the
paper and are edited in Word. The Markdown in paper/sections/ and paper/supplementary/ is the version they were
created from; this script still rebuilds it, into paper/build/ only, and never touches the masters.

    python paper/build.py            # Markdown only: paper/build/paper.md, paper/build/supplementary.md
    python paper/build.py --docx     # also Word files, with md2docx from the manuscript-template skill

Sections live in paper/sections/ (main text) and paper/supplementary/ (supplementary material). A line
`<!-- table: NAME -->` directly under a `Table:` caption is replaced by paper/tables/NAME.md, so every
number in a table comes from the generated results.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "build"
MD2DOCX = Path(os.environ.get("MD2DOCX", Path.home() / ".claude/skills/manuscript-template/scripts/md2docx.py"))


def expand_tables(text: str) -> str:
    def table(m):
        f = HERE / "tables" / f"{m.group(1)}.md"
        if not f.exists():
            raise SystemExit(f"missing generated table: {f}")
        return f.read_text(encoding="utf-8").strip()
    return re.sub(r"<!-- table: (\w+) -->", table, text)


def assemble(folder: Path, name: str) -> Path:
    parts = [expand_tables(f.read_text(encoding="utf-8")).strip() for f in sorted(folder.glob("*.md"))]
    OUT.mkdir(exist_ok=True)
    out = OUT / name
    out.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    body = re.sub(r"^---.*?---", "", out.read_text(encoding="utf-8"), flags=re.S)
    body = body.split("# References {-}")[0]
    words = len(re.sub(r"^\|.*\|$", "", body, flags=re.M).split())
    print(f"Wrote {out.relative_to(HERE.parent)} ({words} words outside tables, before the references)")
    return out


def docx(md: Path) -> None:
    target = md.with_suffix(".docx")
    r = subprocess.run([sys.executable, str(MD2DOCX), str(md), "-o", str(target)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    print(r.stdout.strip())
    if r.stderr.strip():
        print(r.stderr.strip())
    if r.returncode:
        raise SystemExit(f"md2docx failed for {md.name}")


def main() -> None:
    paper = assemble(HERE / "sections", "paper.md")
    supp = assemble(HERE / "supplementary", "supplementary.md") if (HERE / "supplementary").exists() else None
    if "--docx" in sys.argv:
        docx(paper)
        if supp:
            docx(supp)


if __name__ == "__main__":
    main()
