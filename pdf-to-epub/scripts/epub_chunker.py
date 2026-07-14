#!/usr/bin/env python3
"""epub_chunker.py — HTML chunking helper for translate_epub.py.

Imported as a module, not executed directly (a self-test lives in
__main__). Splits a chapter's <body> HTML into chunks of complete
top-level elements, never cutting an element in half.
"""

from bs4 import BeautifulSoup

HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}


def count_tokens(text: str) -> int:
    """Cheap token estimate: len//4, min 1.

    Deliberately NOT tiktoken — downloading the BPE vocabulary needs
    network access; precision doesn't matter, only a consistent budget.
    """
    return max(1, len(text) // 4)


def chunk_chapter_html(html_body: str, max_tokens: int = 1500) -> list[str]:
    """Split body-inner HTML into chunks of complete top-level elements.

    Rules:
    - No element is ever cut in half.
    - A new chunk starts when adding the next element would exceed the
      budget (and the current chunk is non-empty). An element bigger
      than the whole budget gets its own chunk.
    - Headings stick to the following content when there's room.
    """
    soup = BeautifulSoup(html_body, "html.parser")
    elements = [str(el) for el in soup.find_all(recursive=False)]
    # Keep tag names in parallel to apply the heading-glue rule
    names = [el.name for el in soup.find_all(recursive=False)]

    if not elements:
        stripped = html_body.strip()
        return [stripped] if stripped else []

    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0
    pending_heading: list[str] = []  # heading(s) waiting to glue to content
    pending_tokens = 0

    def flush_current():
        nonlocal current, current_tokens
        if current:
            chunks.append("\n".join(current))
            current = []
            current_tokens = 0

    for el_html, name in zip(elements, names):
        el_tokens = count_tokens(el_html)

        if name in HEADING_TAGS:
            # Defer heading; try to keep it with the next element(s).
            pending_heading.append(el_html)
            pending_tokens += el_tokens
            continue

        needed = pending_tokens + el_tokens
        if current and current_tokens + needed > max_tokens:
            flush_current()
        current.extend(pending_heading)
        current_tokens += pending_tokens
        pending_heading = []
        pending_tokens = 0
        current.append(el_html)
        current_tokens += el_tokens

        if current_tokens >= max_tokens:
            flush_current()

    # Trailing headings with no following content
    if pending_heading:
        if current and current_tokens + pending_tokens > max_tokens:
            flush_current()
        current.extend(pending_heading)
    flush_current()

    return chunks


def reassemble(chunks: list[str]) -> str:
    return "\n".join(chunks)


if __name__ == "__main__":
    # Self-test
    html = (
        "<h1>Title</h1>\n"
        + "\n".join(f"<p>{'word ' * 100}paragraph {i}</p>" for i in range(10))
        + '\n<div class="figure"><img src="images/img_0001.png" alt="figure"/></div>'
        + "\n<h2>Section</h2>\n<p>short tail</p>"
    )
    chunks = chunk_chapter_html(html, max_tokens=300)
    assert len(chunks) > 1, "expected multiple chunks"
    # No element cut in half: reassembly parses to same element count
    orig = BeautifulSoup(html, "html.parser")
    rejoined = BeautifulSoup(reassemble(chunks), "html.parser")
    orig_tags = [t.name for t in orig.find_all(True)]
    rejoined_tags = [t.name for t in rejoined.find_all(True)]
    assert orig_tags == rejoined_tags, f"{orig_tags} != {rejoined_tags}"
    # Heading glue: h2 must be in the same chunk as the following <p>
    for c in chunks:
        if "<h2>" in c:
            assert "short tail" in c, "heading not glued to following content"
    # Oversized single element gets its own chunk
    big = f"<p>{'x' * 5000}</p>"
    solo = chunk_chapter_html(big, max_tokens=100)
    assert len(solo) == 1
    print(f"self-test OK — {len(chunks)} chunks, structure preserved")
