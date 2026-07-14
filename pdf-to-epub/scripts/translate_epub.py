#!/usr/bin/env python3
"""translate_epub.py — translate an EPUB via LLM, preserving structure.

Provider/model/keys are configured EXCLUSIVELY via environment (shell
or .env loaded by python-dotenv) — never CLI flags, so credentials and
model names don't leak into shell history.

Usage:
    python3 translate_epub.py <input.epub> <output.epub> \
        --target-lang "Brazilian Portuguese" \
        [--max-tokens-per-chunk 1500] \
        [--title "Translated title"] \
        [--lang-code pt-BR]
"""

import argparse
import json
import os
import re
import sys
import time
import uuid

from dotenv import load_dotenv

try:
    from bs4 import BeautifulSoup
    from ebooklib import epub
    import ebooklib
except ImportError as e:
    print(f"ERROR: missing dependency ({e}). "
          "Run: pip install ebooklib beautifulsoup4 python-dotenv langchain",
          file=sys.stderr)
    sys.exit(1)

from epub_chunker import chunk_chapter_html, reassemble

SYSTEM_PROMPT = """\
You are a professional book translator. Translate the HTML fragment \
provided by the user into {target_lang}. Follow these rules strictly:

1. Translate ONLY human-readable text. NEVER translate or alter: HTML \
tags, attributes (href, src, class, alt), code identifiers, \
variable/function names, URLs, or proper names of software, products, \
or companies.
2. Preserve the HTML structure EXACTLY: same tags, same nesting, same \
number of elements, same attributes.
3. Keep <strong> and <em> wrapping the same translated words, adjusted \
to the grammar of the target language.
4. Do not add any commentary, explanation, or markdown code fences — \
return ONLY the translated HTML fragment.
5. Use a natural, fluent, professional tone appropriate for a \
published technical book.
"""

LANG_CODE_MAP = {
    "brazilian portuguese": "pt-BR",
    "portuguese": "pt",
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "italian": "it",
    "japanese": "ja",
    "chinese (simplified)": "zh-Hans",
}

MAX_RETRIES = 2
RETRY_PAUSE_S = 1.0


# ---------------------------------------------------------------- provider

def build_llm():
    """Build the LangChain chat model from LLM_PROVIDER / LLM_MODEL env."""
    provider = (os.environ.get("LLM_PROVIDER") or "").strip().lower()
    model = (os.environ.get("LLM_MODEL") or "").strip()

    if not provider or not model:
        print("ERROR: LLM_PROVIDER and LLM_MODEL must be set in the "
              "environment or a .env file (see .env.example).",
              file=sys.stderr)
        sys.exit(1)

    kwargs = {"temperature": 0.2, "max_tokens": 8000}

    def need(var, *alts):
        for v in (var, *alts):
            val = os.environ.get(v)
            if val:
                return val
        print(f"ERROR: provider '{provider}' requires {var} "
              f"{'or ' + '/'.join(alts) if alts else ''} in the environment.",
              file=sys.stderr)
        sys.exit(1)

    try:
        if provider == "anthropic":
            need("ANTHROPIC_API_KEY")
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(model=model, **kwargs)
        if provider == "openai":
            need("OPENAI_API_KEY")
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=model, **kwargs)
        if provider == "google":
            key = need("GOOGLE_API_KEY", "GEMINI_API_KEY")
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(model=model, google_api_key=key,
                                          temperature=0.2,
                                          max_output_tokens=8000)
        if provider == "deepseek":
            key = need("DEEPSEEK_API_KEY")
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=model, api_key=key,
                              base_url="https://api.deepseek.com", **kwargs)
        if provider == "xai":
            key = need("XAI_API_KEY")
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=model, api_key=key,
                              base_url="https://api.x.ai/v1", **kwargs)
    except ImportError as e:
        print(f"ERROR: missing LangChain package for provider "
              f"'{provider}': {e}", file=sys.stderr)
        sys.exit(1)

    print(f"ERROR: unknown LLM_PROVIDER '{provider}'. Valid: anthropic, "
          "openai, google, deepseek, xai.", file=sys.stderr)
    sys.exit(1)


# ------------------------------------------------------------ verification

def strip_code_fences(text: str) -> str:
    """Defensively remove ``` / ```html fences the model may add."""
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    return text.strip()


def tag_signature(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    return [t.name for t in soup.find_all(True)]


def translate_chunk(llm, system_prompt: str, chunk: str) -> tuple[str, bool]:
    """Translate one chunk with structural verification.

    Returns (translated_html, flagged). NEVER weaken or remove the
    signature check — it is what keeps corrupted HTML out of the EPUB.
    """
    original_sig = tag_signature(chunk)
    best = chunk
    for attempt in range(1 + MAX_RETRIES):
        resp = llm.invoke([("system", system_prompt), ("human", chunk)])
        translated = strip_code_fences(
            resp.content if isinstance(resp.content, str)
            else "".join(str(p) for p in resp.content))
        if tag_signature(translated) == original_sig:
            return translated, False
        best = translated
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_PAUSE_S)
    return best, True


# ----------------------------------------------------------- epub plumbing

def restore_head_metadata(book) -> None:
    """Recover <title> and CSS <link>s dropped by read_epub().

    read_epub() leaves EpubHtml.title/.links empty, and get_content()
    rebuilds <head> only from those properties — without this step every
    round-trip silently drops each document's <title> and CSS <link>,
    even for untranslated documents.
    """
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        raw = item.content
        if not raw:
            continue
        soup = BeautifulSoup(raw, "html.parser")
        title_tag = soup.find("title")
        if title_tag and title_tag.string and not item.title:
            item.title = str(title_tag.string)
        for link in soup.find_all("link"):
            href = link.get("href")
            if href:
                item.add_link(href=href,
                              rel=link.get("rel", ["stylesheet"])[0]
                              if isinstance(link.get("rel"), list)
                              else (link.get("rel") or "stylesheet"),
                              type=link.get("type", "text/css"))


def ensure_toc_uids(toc) -> None:
    """Assign unique uids to every TOC entry (recursively).

    read_epub() rebuilds book.toc with Link entries of uid=None, and
    write_epub() crashes generating the NCX (navPoint without id).
    """
    counter = [0]

    def walk(entries):
        for entry in entries:
            if isinstance(entry, (list, tuple)):
                # (Section, [children]) tuples
                for sub in entry:
                    if isinstance(sub, (list, tuple)):
                        walk(sub)
                    else:
                        assign(sub)
            else:
                assign(entry)

    def assign(entry):
        if hasattr(entry, "uid") and not getattr(entry, "uid", None):
            counter[0] += 1
            entry.uid = f"navpoint_{counter[0]}"

    walk(toc)


def replace_dc(book, namespace: str, name: str, value: str) -> None:
    """Set a DC metadata entry, discarding any previous ones.

    set_title()/set_language()/set_identifier() only ADD entries — the
    old one must be dropped or the OPF ends up with two conflicting
    dc: entries.
    """
    dc = book.metadata.get(namespace, {})
    dc[name] = []
    book.metadata[namespace] = dc
    if name == "title":
        book.set_title(value)
    elif name == "language":
        book.set_language(value)
    elif name == "identifier":
        book.set_identifier(value)


def resolve_lang_code(target_lang: str, explicit: str | None) -> str | None:
    if explicit:
        return explicit
    return LANG_CODE_MAP.get(target_lang.strip().lower())


# ------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(description="Translate an EPUB via LLM")
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--target-lang", required=True,
                    help='e.g. "Brazilian Portuguese"')
    ap.add_argument("--max-tokens-per-chunk", type=int, default=1500)
    ap.add_argument("--title", help="translated title for the EPUB metadata")
    ap.add_argument("--lang-code",
                    help="BCP-47 code for the target language (e.g. pt-BR)")
    args = ap.parse_args()

    load_dotenv()
    llm = build_llm()
    system_prompt = SYSTEM_PROMPT.format(target_lang=args.target_lang)

    book = epub.read_epub(args.input)
    restore_head_metadata(book)

    checkpoint_path = args.output + ".checkpoint.json"
    checkpoint: dict[str, str] = {}
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, encoding="utf-8") as f:
            checkpoint = json.load(f)
        print(f"Resuming from checkpoint: {len(checkpoint)} document(s) "
              "already translated.")

    documents = [item for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
                 if os.path.basename(item.file_name) != "nav.xhtml"]

    total_chunks = 0
    flagged_chunks = 0

    for doc_index, item in enumerate(documents, 1):
        name = item.file_name
        if name in checkpoint:
            item.content = checkpoint[name].encode("utf-8")
            print(f"[{doc_index}/{len(documents)}] {name}: from checkpoint")
            continue

        raw = item.content.decode("utf-8") if isinstance(item.content, bytes) \
            else str(item.content)
        soup = BeautifulSoup(raw, "html.parser")
        body = soup.find("body")
        if body is None:
            checkpoint[name] = raw
            with open(checkpoint_path, "w", encoding="utf-8") as f:
                json.dump(checkpoint, f, ensure_ascii=False)
            print(f"[{doc_index}/{len(documents)}] {name}: no <body>, copied")
            continue

        inner = "".join(str(c) for c in body.contents)
        chunks = chunk_chapter_html(inner, args.max_tokens_per_chunk)
        print(f"[{doc_index}/{len(documents)}] {name}: "
              f"{len(chunks)} chunk(s)")

        translated_chunks = []
        for ci, chunk in enumerate(chunks, 1):
            translated, flagged = translate_chunk(llm, system_prompt, chunk)
            total_chunks += 1
            if flagged:
                flagged_chunks += 1
                print(f"    chunk {ci}/{len(chunks)}: TAG MISMATCH after "
                      f"{MAX_RETRIES} retries — flagged for manual review",
                      file=sys.stderr)
            else:
                print(f"    chunk {ci}/{len(chunks)}: ok")
            translated_chunks.append(translated)

        # Replace ONLY the body content
        new_body = BeautifulSoup(
            f"<body>{reassemble(translated_chunks)}</body>", "html.parser"
        ).find("body")
        body.replace_with(new_body)
        full_html = str(soup)
        item.content = full_html.encode("utf-8")

        checkpoint[name] = full_html
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, ensure_ascii=False)

    # ---- Final metadata ----
    if args.title:
        replace_dc(book, "http://purl.org/dc/elements/1.1/", "title",
                   args.title)

    # A translation is a distinct document: ALWAYS a fresh identifier.
    # Reusing the original identifier across repeated re-uploads
    # reproduces the Send to Kindle E999 error.
    replace_dc(book, "http://purl.org/dc/elements/1.1/", "identifier",
               f"urn:uuid:{uuid.uuid4()}")

    lang_code = resolve_lang_code(args.target_lang, args.lang_code)
    if lang_code:
        replace_dc(book, "http://purl.org/dc/elements/1.1/", "language",
                   lang_code)
        # Also update lang/xml:lang on each document's <html> element —
        # stale language metadata is a known E999 cause on Send to
        # Kindle and confuses reader hyphenation/TTS.
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            raw = item.content.decode("utf-8") \
                if isinstance(item.content, bytes) else str(item.content)
            soup = BeautifulSoup(raw, "html.parser")
            html_el = soup.find("html")
            if html_el is not None:
                html_el["lang"] = lang_code
                html_el["xml:lang"] = lang_code
                item.content = str(soup).encode("utf-8")
            if hasattr(item, "lang"):
                item.lang = lang_code
    else:
        print(f"WARNING: could not resolve a BCP-47 code for "
              f"'{args.target_lang}'. dc:language left unchanged — pass "
              "--lang-code to set it explicitly.", file=sys.stderr)

    ensure_toc_uids(book.toc)
    epub.write_epub(args.output, book)

    # ---- Report ----
    print()
    print(f"Chunks translated: {total_chunks}")
    print(f"Chunks flagged:    {flagged_chunks}"
          + ("  <-- spot-check these documents manually!"
             if flagged_chunks else ""))
    print(f"Output EPUB:  {args.output}")
    print(f"Checkpoint:   {checkpoint_path} (safe to delete after review)")


if __name__ == "__main__":
    main()
