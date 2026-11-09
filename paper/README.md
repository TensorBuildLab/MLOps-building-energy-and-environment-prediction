# Paper

**Domain guardrails for data-driven building energy prediction: an agent-ready MLOps framework
evaluated on real buildings** (for Applied Energy; extends arXiv:2407.03469).

## The paper is the Word file

Since 8 November 2026 the paper is written, revised and submitted in Word:

- [`Manuscript.docx`](Manuscript.docx): the manuscript (title page, highlights, abstract, text, tables,
  figures, declarations), with EndNote citation fields. Edit this file.
- [`Supplementary_Material.docx`](Supplementary_Material.docx): the supplementary material.
- `submission_sources/Cover_Letter.docx`: the cover letter (local only, not in the repository).

The citations came from `refs.ris`, not from an EndNote library. In EndNote, use
*Export Traveling Library* once to copy them into your library, choose the journal's output style and
run *Update Citations and Bibliography*.

## Building the submission files

```bash
python paper/make_submission.py
```

writes the upload files to `submission/` (local only): it refreshes caption and cross-reference
numbers in a copy (Word), flattens the citations in the uploaded manuscript, splits out the
highlights, converts the figures to TIFF and renders a PDF preview. The masters are never modified.
`submission_sources/00_Upload_guide.md` lists what to upload where.

## Numbers, tables and figures

Every number comes from the result files: `case_studies/results_v3/key_numbers.csv`, the tables in
`tables/` and the figures in `figures/`, all written by `case_studies/analysis_v3.py` (Figure 1 and
the graphical abstract by `figure_framework.py` and `figure_graphical_abstract.py`). If an analysis
is re-run, update the affected table or figure in `Manuscript.docx` by hand; the upload TIFFs are
made from `figures/*.png`.

## History

The manuscript was drafted in Markdown (`sections/`, `supplementary/`, assembled by `build.py`, with
`references.md` and `make_refs.py` producing `refs.ris`); `Manuscript.docx` was built from that
version. The Markdown is kept as the record of how the paper was written and is no longer edited.
`sections_v1/` holds the earlier draft.
