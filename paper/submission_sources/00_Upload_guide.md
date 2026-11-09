# Upload guide: Applied Energy (Editorial Manager)

Built by `paper/make_submission.py` from the Markdown sources and checked against the Applied Energy Guide for
Authors (captured 2026-11-08; compliance report in `checks/`, not committed). Article type: **Full Length Research
Article**. Review is single anonymized, so the manuscript keeps the title page with the author's name.

| File | Upload as | Note |
|---|---|---|
| 01_Cover_Letter.docx | Cover letter | Complete the date and the bracketed note first. |
| 02_Manuscript.docx | Manuscript | Title page, highlights, abstract, text, tables, figures and declarations in one file. Citations are plain text; the EndNote-linked master is `paper/Manuscript.docx`. |
| 03_Highlights.docx | Highlights | 5 bullets, at most 85 characters each. |
| 04_Graphical_Abstract.tif | Graphical abstract | 3070 × 1181 px (at least 1328 px wide), readable at 13 cm. |
| Figures/Fig1–7 *.tif | Figure | One file per figure, 1100 dpi; vector PDFs are in `paper/figures` if the editorial office asks for them. |
| 06_Supplementary_Material.docx | Supplementary material | Caption for the description field: see below. |
| Declaration of competing interest (.docx) | Declaration of interest | Generate it with the Elsevier declarations tool (https://declarations.elsevier.com/); see 07_Declaration_of_Competing_Interest_README.md. |

**Caption of the supplementary file:** Supplementary material: history and changes of the bemlops package (S1); division of labor between agent and package, and package modules (S2); formative usability study with LLM agents (S3); evaluation protocols per task (S4); lifecycle of the Aalborg case (S5); data-check issue types on the untouched data (S6); results of every task (S7); sensitivity of the promotion gates and Guideline 14 verdicts by protocol (S8).

**Entered in the submission system, not uploaded:** suggested reviewers (05_Suggested_Reviewers.md, a draft to
verify), the data statement (code on GitHub, archived release on Zenodo; the three datasets are public, with DOIs),
and the competing-interest declaration.

**Before uploading, complete the bracketed items** in `paper/Manuscript.docx` (CRediT, competing interests,
Zenodo DOI, generative-AI statement, funding and acknowledgements) and in
`paper/submission_sources/Cover_Letter.docx`. In Word, run EndNote > Update Citations and Bibliography and save;
then rebuild this folder with `python paper/make_submission.py`.
