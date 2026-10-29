"""Download the public datasets used in the case studies, and verify every file's checksum.

Run:  python case_studies/download.py [aalborg] [robod] [bdg2]

Files go to data/raw/<dataset>/ (git-ignored). Nothing is redistributed by this
repository; each dataset keeps its own licence (see case_studies/README.md).
LBNL Building 59 cannot be downloaded by a script (Dryad requires a login);
see case_studies/lbnl_b59/README.md for the manual steps.
"""

from __future__ import annotations

import hashlib
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "data" / "raw"

BDG2 = "https://media.githubusercontent.com/media/buds-lab/building-data-genome-project-2/master/data"
DATASETS = {
    "aalborg": [
        ("dataset__2023_02_27__2023_12_31.csv",
         "https://zenodo.org/api/records/10673763/files/dataset__2023_02_27__2023_12_31.csv/content",
         "md5", "51b6528edbc2ccd0d78282a2e75668e1"),
    ],
    "robod": [
        ("SupplementaryData.zip", "https://ndownloader.figshare.com/files/36228765",
         "md5", "92161b84b4d5e29499bae308cd672100"),
    ],
    "bdg2": [
        ("electricity_cleaned.csv", f"{BDG2}/meters/cleaned/electricity_cleaned.csv",
         "sha256", "b6ffc9b4dfcefe5c753594730a08ae822b0d50fec6815abb8f185591e6c630a3"),
        ("weather.csv", f"{BDG2}/weather/weather.csv",
         "sha256", "a8189f1c6acdf3b9933a9e6354b8e7c1278cd56a7075929623a17565d44f04bd"),
        ("metadata.csv", f"{BDG2}/metadata/metadata.csv",
         "sha256", "992d0b29f24f96ad4332bc4dbb534b7bdd7dd2689aad093f94e93068ecddca02"),
    ],
}


def _digest(path: Path, algo: str) -> str:
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(dataset: str) -> Path:
    folder = ROOT / dataset
    folder.mkdir(parents=True, exist_ok=True)
    for name, url, algo, expected in DATASETS[dataset]:
        path = folder / name
        if path.exists() and _digest(path, algo) == expected:
            print(f"ok    {dataset}/{name} (already downloaded)")
            continue
        print(f"get   {dataset}/{name} from {url}")
        tmp = path.with_suffix(path.suffix + ".part")
        req = urllib.request.Request(url, headers={"User-Agent": "bemlops-case-studies"})
        with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)
        got = _digest(tmp, algo)
        if got != expected:
            tmp.unlink()
            raise RuntimeError(f"Checksum mismatch for {name}: expected {expected}, got {got}")
        tmp.replace(path)
        print(f"ok    {dataset}/{name} ({algo} verified)")
        if path.suffix == ".zip":
            with zipfile.ZipFile(path) as z:
                for member in z.namelist():  # extract data files only, never outside the folder
                    target = (folder / member).resolve()
                    if folder.resolve() in target.parents and member.lower().endswith((".csv", ".md")):
                        z.extract(member, folder)
    return folder


if __name__ == "__main__":
    for ds in sys.argv[1:] or list(DATASETS):
        fetch(ds)
