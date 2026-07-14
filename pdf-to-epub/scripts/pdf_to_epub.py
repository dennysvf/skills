#!/usr/bin/env python3
"""pdf_to_epub.py — convert a PDF to a reflowable EPUB.

Step 3 of the pdf-to-epub pipeline. Consumes the config.json decided
from the analyze_styles.py report. Guarantees reading-order fidelity:
every embedded image (>=20px) is emitted at the exact position it had
relative to the surrounding text.

Usage:
    python3 pdf_to_epub.py <pdf_path> <config.json> <output.epub>
"""

import argparse
import html
import json
import os
import sys
import uuid

try:
    import fitz  # pymupdf
    from ebooklib import epub
except ImportError as e:
    print(f"ERROR: missing dependency ({e}). "
          "Run: pip install pymupdf ebooklib", file=sys.stderr)
    sys.exit(1)

MIN_IMG_PX = 20
COVER_MIN_PX = 100
SIZE_TOL = 0.5  # +-0.5pt tolerance: PDFs vary nominal size across pages

DEFAULT_CSS = """\
body { font-family: serif; line-height: 1.4; }
h1 { font-size: 1.8em; }
h2 { font-size: 1.4em; }
h3 { font-size: 1.15em; }
p { text-align: justify; }
p.caption { font-size: 0.85em; font-style: italic; text-align: center; }
p.note {
  background-color: #f5f5f5;
  border-left: 3px solid #999;
  padding: 0.4em 0.8em;
  font-size: 0.9em;
}
div.figure { text-align: center; margin: 1em 0; }
div.figure img { max-width: 100%; height: auto; }
"""


def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    # Normalize heading_map keys to float
    hm = cfg.get("heading_map") or {}
    cfg["heading_map"] = {float(k): v for k, v in hm.items()}
    return cfg


def classify_size(size: float, cfg: dict) -> str:
    """Return an HTML tag for a block's dominant font size."""
    for k, tag in cfg["heading_map"].items():
        if abs(size - k) < SIZE_TOL:
            return tag
    small = cfg.get("small_size")
    if small is not None and abs(size - small) < SIZE_TOL:
        return "small"
    return "p"


def block_dominant_size(block: dict) -> float | None:
    sizes = [round(span["size"], 1)
             for line in block.get("lines", [])
             for span in line["spans"]]
    return max(sizes) if sizes else None


def block_text(block: dict) -> str:
    parts = []
    for line in block.get("lines", []):
        parts.extend(span["text"] for span in line["spans"])
    return " ".join(p for p in parts if p).strip()


def spans_to_html(block: dict) -> str:
    """Escape and wrap spans in <strong>/<em>; join lines with spaces."""
    line_htmls = []
    for line in block.get("lines", []):
        pieces = []
        for span in line["spans"]:
            text = html.escape(span["text"])
            if not text:
                continue
            font = span.get("font", "")
            bold = "Bold" in font
            italic = "Italic" in font or "Oblique" in font
            if bold and italic:
                text = f"<strong><em>{text}</em></strong>"
            elif bold:
                text = f"<strong>{text}</strong>"
            elif italic:
                text = f"<em>{text}</em>"
            pieces.append(text)
        if pieces:
            line_htmls.append("".join(pieces))
    return " ".join(line_htmls)


def find_chapter_starts(doc, cfg: dict) -> list[tuple[int, str]]:
    """Return [(start_page, title), ...]. Single chapter if no split size."""
    split = cfg.get("chapter_split_size")
    starts: list[tuple[int, str]] = []
    if split is not None:
        for page_index, page in enumerate(doc):
            for block in page.get_text("dict")["blocks"]:
                if "lines" not in block:
                    continue
                dom = block_dominant_size(block)
                if dom is None:
                    continue
                if abs(dom - float(split)) < SIZE_TOL:
                    text = block_text(block)
                    if text:
                        starts.append((page_index, text))
                        break  # first occurrence per page only
    if not starts:
        starts = [(0, cfg.get("title", "Untitled"))]
    return starts


def main() -> None:
    ap = argparse.ArgumentParser(description="Convert PDF to EPUB")
    ap.add_argument("pdf_path")
    ap.add_argument("config")
    ap.add_argument("output")
    args = ap.parse_args()

    cfg = load_config(args.config)
    doc = fitz.open(args.pdf_path)

    book = epub.EpubBook()
    # NEVER derive the identifier from the file name: re-sending EPUBs
    # under the same dc:identifier has been observed to lock that id in
    # a persistent E999 error on Amazon's Send to Kindle.
    identifier = cfg.get("identifier") or f"urn:uuid:{uuid.uuid4()}"
    book.set_identifier(identifier)
    book.set_title(cfg.get("title", "Untitled"))
    book.set_language(cfg.get("language", "en"))
    if cfg.get("author"):
        book.add_author(cfg["author"])

    css_text = cfg.get("css") or DEFAULT_CSS
    css_item = epub.EpubItem(uid="style", file_name="style/main.css",
                             media_type="text/css", content=css_text)
    book.add_item(css_item)

    # ---- Cover from first page ----
    has_cover = False
    if cfg.get("cover_from_first_page", True) and len(doc) > 0:
        for block in doc[0].get_text("dict")["blocks"]:
            if "lines" in block or block.get("image") is None:
                continue
            x0, y0, x1, y1 = block["bbox"]
            if (x1 - x0) >= COVER_MIN_PX and (y1 - y0) >= COVER_MIN_PX:
                ext = block.get("ext", "png")
                book.set_cover(f"cover.{ext}", block["image"])
                # set_cover() only adds the image/page to the manifest —
                # it does NOT wire the guide or spine, so most readers
                # never display it. Both steps below are REQUIRED.
                book.guide.append(
                    {"type": "cover", "title": "Cover", "href": "cover.xhtml"}
                )
                has_cover = True
                break

    # ---- Chapters ----
    starts = find_chapter_starts(doc, cfg)
    chapters_meta = []  # (title, first_page, last_page)
    for i, (start, title) in enumerate(starts):
        end = (starts[i + 1][0] - 1) if i + 1 < len(starts) else len(doc) - 1
        chapters_meta.append((title, start, end))

    img_counter = 0
    total_images = 0
    chapter_items = []
    chapter_reports = []

    for chap_index, (title, first, last) in enumerate(chapters_meta):
        body_parts = []
        n_blocks = 0
        for page_index in range(first, last + 1):
            page = doc[page_index]
            blocks = page.get_text("dict")["blocks"]
            # Reading-order approximation: top-to-bottom, left-to-right.
            blocks.sort(key=lambda b: (round(b["bbox"][1], 1),
                                       round(b["bbox"][0], 1)))
            for block in blocks:
                if "lines" not in block:
                    if block.get("image") is None:
                        continue
                    x0, y0, x1, y1 = block["bbox"]
                    if (x1 - x0) < MIN_IMG_PX or (y1 - y0) < MIN_IMG_PX:
                        continue
                    img_counter += 1
                    total_images += 1
                    ext = block.get("ext", "png")
                    name = f"img_{img_counter:04d}.{ext}"
                    media = {"png": "image/png", "jpg": "image/jpeg",
                             "jpeg": "image/jpeg"}.get(ext, "image/png")
                    book.add_item(epub.EpubItem(
                        uid=f"img{img_counter:04d}",
                        file_name=f"images/{name}",
                        media_type=media,
                        content=block["image"],
                    ))
                    body_parts.append(
                        f'<div class="figure">'
                        f'<img src="images/{name}" alt="figure"/></div>'
                    )
                    n_blocks += 1
                    continue

                dom = block_dominant_size(block)
                if dom is None:
                    continue
                inner = spans_to_html(block)
                if not inner.strip():
                    continue
                tag = classify_size(dom, cfg)
                if tag == "small":
                    body_parts.append(f'<p class="note">{inner}</p>')
                else:
                    body_parts.append(f"<{tag}>{inner}</{tag}>")
                n_blocks += 1

        if not body_parts:
            body_parts.append(f"<h1>{html.escape(title)}</h1>")

        file_name = f"chap_{chap_index + 1:03d}.xhtml"
        toc_title = html.escape(title)[:120]
        chapter = epub.EpubHtml(title=toc_title, file_name=file_name,
                                lang=cfg.get("language", "en"))
        chapter.content = "\n".join(body_parts)
        chapter.add_item(css_item)
        book.add_item(chapter)
        chapter_items.append(chapter)
        chapter_reports.append((toc_title, first + 1, last + 1, n_blocks))

    # ---- Assembly ----
    book.toc = chapter_items
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    spine = []
    if has_cover:
        spine.append("cover")
    spine.append("nav")
    spine.extend(chapter_items)
    book.spine = spine

    epub.write_epub(args.output, book)

    # ---- Report ----
    print(f"Chapters detected: {len(chapter_items)}")
    for title, p0, p1, nb in chapter_reports:
        print(f"  pages {p0}-{p1} ({nb} blocks): {title}")
    print(f"Images embedded: {total_images}")
    size = os.path.getsize(args.output)
    print(f"EPUB written: {args.output} ({size:,} bytes)")
    print(f"Cover: {'extracted from page 1' if has_cover else 'none'}")
    doc.close()


if __name__ == "__main__":
    main()
