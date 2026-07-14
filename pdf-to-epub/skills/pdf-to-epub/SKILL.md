---
name: pdf-to-epub
description: >
  This skill should be used when the user wants to convert a PDF (book,
  report, article) into a reflowable EPUB while keeping images anchored
  at their correct position in the reading order — e.g. "convert this
  PDF to EPUB", "turn this book into an ebook", "make this readable on
  my Kindle". It is NOT for pixel-perfect visual cloning of the PDF
  layout, NOT for plain text extraction, and NOT for translation
  (translation of EPUBs is handled by the epub-translate skill).
version: 0.1.0
---

# PDF → EPUB conversion: judgment guide

## Context (minimum needed)

PDF is fixed layout; EPUB is flowing HTML. Visual fidelity is
impossible by definition — the guarantee of this pipeline is **reading
order fidelity**: every embedded image comes out at the same position
relative to the text it had in the PDF, and text becomes structured
HTML (h1/h2/h3/p) instead of a flat blob.

The process is deliberately two-step with a human in the loop: every
PDF uses its own font sizes and there is no universal constant. Step 1
(`analyze_styles.py`) produces a font report; a human/Claude decides
the mapping; step 2 (`pdf_to_epub.py`) converts using that mapping.
Blindly automating the mapping decision produces silently wrong
structures.

## Report → config.json decision guide (the core of this skill)

Given the analyzer report, decide each config field:

- **`body_size`**: the size with the most characters. The analyzer's
  `suggested_body_size` is almost always right — trust it unless the
  samples look wrong.
- **`chapter_split_size`**: the LARGEST heading size that recurs about
  once per chapter/part — a handful to a few dozen occurrences in a
  book. Not once per page (that's a running header), not once in the
  whole document (that's the title page). If no size shows a clear
  chapter-like recurrence, use `null` — the whole document becomes a
  single chapter, which is better than a wrong split.
- **Remaining heading sizes** (larger than body, not the chapter
  size): map to `h2`, `h3` in `heading_map`, largest first.
- **`small_size`**: a size notably smaller than body that recurs
  (captions, notes, asides). If none, `null`.

## Mandatory sanity checks before converting

1. Estimate the resulting chapter count from the block_count of the
   chosen `chapter_split_size`. Compare with the book's real table of
   contents. Hundreds of chapters = split too granular; 1 chapter for
   a clearly multi-chapter book = too coarse.
2. Scan the report for unmapped sizes whose samples look like print
   junk — repeated page headers/footers, URLs, timestamps, page
   numbers. **Flag these to the user before converting**: they leak
   into the EPUB body as ordinary `<p>` paragraphs.

## Limitations to communicate when applicable

- **Multi-column PDFs**: block ordering is (top, left); works for
  single column and most 2-column layouts, but can shuffle complex
  academic layouts. Advise manual checking near column breaks.
- **Scanned PDFs** (no text layer): unsupported. External OCR does not
  help — font-size-based heading detection is unrecoverable.
- **Code blocks**: come out as plain `<p>`, no `<code>`/`<pre>` (known
  limitation).
- **Full-page images**: preserved as a single `<img>` at that point in
  the flow (accepted behavior).
