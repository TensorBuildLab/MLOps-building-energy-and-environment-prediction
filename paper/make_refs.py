"""Convert paper/references.md (the verified reference list) into paper/refs.ris for md2docx/EndNote.

Each entry gets the citation key <firstauthor><year> (e.g. zhang2024a) used as [@key] in the manuscript,
and the ISO 4 journal abbreviation (J2) that Elsevier's numbered style prints.

    python paper/make_refs.py
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ISO 4 abbreviations (LTWA) of the journals cited.
J2 = {
    "Renewable and Sustainable Energy Reviews": "Renew Sustain Energy Rev",
    "Information Sciences": "Inf Sci",
    "Energy and Buildings": "Energy Build",
    "Building and Environment": "Build Environ",
    "Building Simulation": "Build Simul",
    "Scientific Data": "Sci Data",
    "Patterns": "Patterns",
    "IEEE Access": "IEEE Access",
    "Control Engineering Practice": "Control Eng Pract",
    "Data in Brief": "Data Brief",
    "Journal of Building Engineering": "J Build Eng",
    "Energy and Built Environment": "Energy Built Environ",
    "Energy": "Energy",
    "Frontiers in Energy Research": "Front Energy Res",
    "Science and Technology for the Built Environment": "Sci Technol Built Environ",
    "Journal of Business & Economic Statistics": "J Bus Econ Stat",
    "Journal of the American Statistical Association": "J Am Stat Assoc",
    "Computational Statistics & Data Analysis": "Comput Stat Data Anal",
    "Monthly Weather Review": "Mon Weather Rev",
    "Proceedings of the VLDB Endowment": "Proc VLDB Endow",
    "IEEE Data Engineering Bulletin": "IEEE Data Eng Bull",
    "Journal of Machine Learning Research": "J Mach Learn Res",
}


def fold(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower()


def authors_of(auth: str) -> list:
    if not re.search(r",\s*[A-Z]\.", auth):                 # corporate author
        return [re.sub(r"\s*\(.*?\)\s*", " ", auth.split(",")[0]).strip()]
    found = re.findall(r"([^,]+?,\s*(?:[A-Z][a-z]?\.-?\s*)+)", auth)
    out = [a.strip() for a in found if not a.strip().startswith("et al")]
    return out or [auth]


def entry_to_ris(e: str):
    m = re.match(r"(?P<auth>.+?),\s*(?P<year>(?:19|20)\d\d[a-z]?)\.\s*(?P<rest>.*)$", e)
    if not m:
        raise ValueError(f"cannot parse: {e[:80]}")
    auth, year, rest = m.group("auth"), m.group("year"), m.group("rest")
    authors = authors_of(auth)
    first = re.sub(r"[^a-z]", "", fold(re.split(r"[,\s]", authors[0])[0]))
    key = f"{first}{year}"
    dois = re.findall(r"https?://doi\.org/(10\.\S+?)(?=[\s,]|;\s|;$|\)\s|\)$|$)", e)  # ';' may be inside a DOI
    doi = dois[0].rstrip(".") if dois else ""
    urls = [u.rstrip(".,;)") for u in re.findall(r"https?://\S+", e) if "doi.org" not in u]
    tm = re.match(r"(?P<title>.+?[.?!])\s+(?P<tail>(?:In:\s|arXiv:)?[A-Z(].*|arXiv:.*|https?:.*)$", rest)
    title, tail = (tm.group("title").rstrip("."), tm.group("tail")) if tm else (rest, "")
    lines = []
    ty = "JOUR"
    container = vol = iss = sp = ep = ""
    if tail.startswith("In:"):
        ty = "CPAPER"
        c = re.match(r"In:\s*(.+?)(?:,\s*pp\.\s*(\d+)\s*[–-]\s*(\d+))?\.", tail)
        if c:
            container, sp, ep = c.group(1), c.group(2) or "", c.group(3) or ""
    elif "(software" in tail or "(software" in title or "Zenodo" in tail or "github.com" in tail:
        ty = "COMP"
        container = "Zenodo" if "Zenodo" in tail else ""
    elif tail.startswith("arXiv") or tail.startswith("http") or not tail:
        ty = "GEN"
    else:
        j = re.match(r"(?P<j>[^0-9]+?)\s+(?P<vol>\d+)\s*(?:\((?P<iss>[^)]+)\))?\s*,\s*(?P<pages>[\w–\-/]+)", tail)
        if j:
            container, vol, iss = j.group("j").strip().rstrip(","), j.group("vol"), j.group("iss") or ""
            pg = j.group("pages")
            if re.search(r"[–-]", pg):
                sp, ep = re.split(r"[–-]", pg, maxsplit=1)
            else:
                sp = pg
        else:
            ty = "RPRT" if "Agency" in tail or "ASHRAE" in tail else "GEN"
            container = tail.split(".")[0]
    if "Blog" in tail:
        ty = "ELEC"
        container = tail.split(",")[0]
    if key.startswith("ashrae"):
        ty, container = "STAND", "ASHRAE, Atlanta, GA"
    lines += [f"TY  - {ty}", f"ID  - {key}"] + [f"AU  - {a}" for a in authors]
    lines += [f"PY  - {year[:4]}", f"TI  - {title}"]
    if container:
        lines.append(f"T2  - {container}")
        if container in J2:
            lines.append(f"J2  - {J2[container]}")
    for tag, v in (("VL", vol), ("IS", iss), ("SP", sp), ("EP", ep)):
        if v:
            lines.append(f"{tag}  - {v}")
    arx = re.search(r"arXiv:(\d{4}\.\d{4,5})", e)
    if arx and ty == "GEN":
        lines.append(f"T2  - arXiv preprint arXiv:{arx.group(1)}")
    if doi:
        lines.append(f"DO  - {doi}")
    for u in urls[:1]:
        lines.append(f"UR  - {u}")
    acc = re.search(r"accessed (\d{1,2} \w+ \d{4})", e)
    if acc:
        lines.append(f"Y2  - {acc.group(1)}")
    lines.append("ER  - ")
    return key, "\n".join(lines)


def main() -> None:
    entries = [l[2:].strip() for l in (HERE / "references.md").read_text(encoding="utf-8").splitlines()
               if l.startswith("- ")]
    out, keys = [], []
    for e in entries:
        k, r = entry_to_ris(e)
        keys.append(k)
        out.append(r)
    dup = {k for k in keys if keys.count(k) > 1}
    if dup:
        raise SystemExit(f"duplicate keys: {dup}")
    # Entries added in the revision: written from Crossref records (refs_extra.ris, built with the fact-check
    # skill's build-ris from refs_extra_dois.txt) and, for items without a DOI, by hand (refs_extra_manual.ris;
    # each checked on its publisher or repository page).
    extra = [(HERE / f).read_text(encoding="utf-8").strip() for f in ("refs_extra.ris", "refs_extra_manual.ris")
             if (HERE / f).exists()]
    (HERE / "refs.ris").write_text("\n\n".join(out + extra) + "\n", encoding="utf-8")
    print(f"Wrote paper/refs.ris: {len(out)} references from references.md + {len(extra)} extra file(s)")


if __name__ == "__main__":
    main()
