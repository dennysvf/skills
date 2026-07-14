#!/usr/bin/env python3
"""analyze_styles.py — font/style analysis of a PDF.

Step 1 of the pdf-to-epub pipeline. Produces a report of font sizes,
their usage (char/block counts, bold/italic flags) and text samples so
a human (or Claude) can decide the heading/body mapping and write the
config.json consumed by pdf_to_epub.py.

Usage:
    python3 analyze_styles.py <pdf_path> [--json <out.json>]
"""

import argparse
import json
import sys

try:
    import fitz  # pymupdf
except ImportError:
    print("ERROR: pymupdf not installed. Run: pip install pymupdf", file=sys.stderr)
    sys.exit(1)

MIN_IMG_PX = 20  # ignore images smaller than this (masks, decorative dots)
MAX_SAMPLES_PER_SIZE = 3
MAX_SAMPLE_LEN = 90
MAX_IMAGE_DIM_SAMPLES = 10


def analyze(pdf_path: str) -> dict:
    doc = fitz.open(pdf_path)

    num_images = 0
    image_dims_sample = []
    # size -> {"char_count", "block_count", "bold", "italic", "samples"}
    sizes: dict[float, dict] = {}

    for page_index, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                # Image block
                if block.get("image") is None:
                    continue
                x0, y0, x1, y1 = block["bbox"]
                w, h = x1 - x0, y1 - y0
                if w >= MIN_IMG_PX and h >= MIN_IMG_PX:
                    num_images += 1
                    if len(image_dims_sample) < MAX_IMAGE_DIM_SAMPLES:
                        image_dims_sample.append([round(w), round(h)])
                continue

            # Text block: collect spans
            span_sizes = []
            bold = False
            italic = False
            texts = []
            for line in block["lines"]:
                for span in line["spans"]:
                    size = round(span["size"], 1)
                    span_sizes.append(size)
                    font = span.get("font", "")
                    if "Bold" in font:
                        bold = True
                    if "Italic" in font or "Oblique" in font:
                        italic = True
                    texts.append(span["text"])

            text = " ".join(t for t in texts if t).strip()
            if not text or not span_sizes:
                continue

            # Dominant size of the block = max span size
            dom = max(span_sizes)
            entry = sizes.setdefault(
                dom,
                {"char_count": 0, "block_count": 0, "bold": False,
                 "italic": False, "samples": []},
            )
            entry["char_count"] += len(text)
            entry["block_count"] += 1
            entry["bold"] = entry["bold"] or bold
            entry["italic"] = entry["italic"] or italic
            if len(entry["samples"]) < MAX_SAMPLES_PER_SIZE:
                entry["samples"].append(
                    {"page": page_index + 1, "text": text[:MAX_SAMPLE_LEN]}
                )

    suggested_body = None
    if sizes:
        suggested_body = max(sizes.items(), key=lambda kv: kv[1]["char_count"])[0]

    size_rows = []
    for size in sorted(sizes.keys(), reverse=True):
        e = sizes[size]
        if size == suggested_body:
            hint = "BODY (most chars)"
        elif suggested_body is not None and size > suggested_body:
            hint = "heading candidate"
        else:
            hint = "small text (caption/note?)"
        size_rows.append({
            "size": size,
            "role_hint": hint,
            "char_count": e["char_count"],
            "block_count": e["block_count"],
            "bold": e["bold"],
            "italic": e["italic"],
            "samples": e["samples"],
        })

    report = {
        "pdf": pdf_path,
        "num_pages": len(doc),
        "num_images": num_images,
        "image_dims_sample": image_dims_sample,
        "suggested_body_size": suggested_body,
        "sizes": size_rows,
    }
    doc.close()
    return report


def config_template(report: dict) -> str:
    body = report["suggested_body_size"]
    headings = [r["size"] for r in report["sizes"]
                if body is not None and r["size"] > body]
    smalls = [r["size"] for r in report["sizes"]
              if body is not None and r["size"] < body]
    h1 = headings[0] if headings else None
    heading_map = {}
    tags = ["h1", "h2", "h3"]
    for i, s in enumerate(headings[:3]):
        heading_map[f"{s}"] = tags[i]
    template = {
        "title": "Book Title",
        "author": "Author Name",
        "language": "en",
        "body_size": body,
        "chapter_split_size": h1,
        "heading_map": heading_map,
        "small_size": smalls[0] if smalls else None,
        "cover_from_first_page": True,
        "identifier": None,
        "css": None,
    }
    return json.dumps(template, indent=2, ensure_ascii=False)


def print_human(report: dict) -> None:
    print(f"PDF: {report['pdf']}")
    print(f"Pages: {report['num_pages']}")
    print(f"Images >= {MIN_IMG_PX}px: {report['num_images']}")
    if report["image_dims_sample"]:
        dims = ", ".join(f"{w}x{h}" for w, h in report["image_dims_sample"])
        print(f"Image dims sample: {dims}")
    print()
    header = (f"{'size':>7} | {'role_hint':<24} | {'blocks':>6} | "
              f"{'chars':>8} | {'bold/italic':<11} | sample")
    print(header)
    print("-" * len(header))
    for row in report["sizes"]:
        bi = f"{'B' if row['bold'] else '-'}/{'I' if row['italic'] else '-'}"
        sample = ""
        if row["samples"]:
            s = row["samples"][0]
            sample = f"(p.{s['page']}) {s['text']}"
        print(f"{row['size']:>7} | {row['role_hint']:<24} | "
              f"{row['block_count']:>6} | {row['char_count']:>8} | "
              f"{bi:<11} | {sample}")
        for s in row["samples"][1:]:
            print(f"{'':>7} | {'':<24} | {'':>6} | {'':>8} | {'':<11} | "
                  f"(p.{s['page']}) {s['text']}")
    print()
    print("Next step: review the table above, decide the mapping, and save a")
    print("config.json (template below), then run pdf_to_epub.py:")
    print()
    print(config_template(report))


def main() -> None:
    ap = argparse.ArgumentParser(description="Analyze font styles of a PDF")
    ap.add_argument("pdf_path")
    ap.add_argument("--json", dest="json_out", metavar="OUT.JSON",
                    help="also write the full report as JSON")
    args = ap.parse_args()

    report = analyze(args.pdf_path)
    print_human(report)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\nJSON report written to: {args.json_out}")


if __name__ == "__main__":
    main()
