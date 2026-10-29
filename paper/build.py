"""Assemble paper/manuscript.md from the section files, the generated tables and the reference list.

    python paper/build.py

A line `<!-- table: NAME -->` in a section is replaced by paper/tables/NAME.md.
"""

from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORDER = ["00_front", "01_introduction", "02_related_work", "03_framework", "04_implementation",
         "05_case_studies", "06_results", "07_discussion", "08_conclusion"]


def main() -> None:
    parts = []
    for name in ORDER:
        f = HERE / "sections" / f"{name}.md"
        if f.exists():
            text = f.read_text(encoding="utf-8")
            text = re.sub(r"<!-- table: (\w+) -->",
                          lambda m: (HERE / "tables" / f"{m.group(1)}.md").read_text(encoding="utf-8")
                          if (HERE / "tables" / f"{m.group(1)}.md").exists() else f"*[table {m.group(1)} missing]*",
                          text)
            parts.append(text.strip())
    parts.append((HERE / "references.md").read_text(encoding="utf-8").strip())
    out = "\n\n".join(parts) + "\n"
    (HERE / "manuscript.md").write_text(out, encoding="utf-8")
    words = len(re.sub(r"\|.*\|", "", out).split())
    print(f"Wrote paper/manuscript.md ({words} words outside tables)")


if __name__ == "__main__":
    main()
