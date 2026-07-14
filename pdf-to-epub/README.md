# pdf-to-epub

Claude Code plugin that converts PDFs (books, reports, articles) into
reflowable EPUBs **without losing image positions in the text**, and
optionally translates the resulting EPUB (or any well-formed EPUB) into
another language via LLM — with structural verification and checkpoint
resume.

The plugin does **not** clone the PDF's visual layout (impossible: PDF
is fixed layout, EPUB is flowing HTML). The core guarantee is **reading
order fidelity**: every image comes out at the same position relative
to the text it had in the PDF, and text becomes structured HTML
(`h1`/`h2`/`h3`/`p`) instead of a flat blob.

## Components

| Component | Purpose |
|---|---|
| `skills/pdf-to-epub` | Judgment guide: font report → config.json + sanity checks |
| `skills/epub-translate` | Decisions: model/cost, user confirmation, tag-mismatch handling |
| `agents/pdf-to-epub-runner` | Pipeline orchestration (env, sequence, validation, reporting) |
| `scripts/analyze_styles.py` | PDF font/style analysis report |
| `scripts/pdf_to_epub.py` | PDF → EPUB conversion |
| `scripts/epub_chunker.py` | HTML chunking helper (imported by the translator) |
| `scripts/translate_epub.py` | EPUB translation via LangChain with checkpointing |

## Requirements

- Linux/WSL, Python 3.12+
- A dedicated venv per project (the agent creates `.venv/` in your
  current project on first run and installs everything inside it)
- Java (JRE) for `epubcheck` validation
- For translation only: an API key for one of the supported providers

## Usage

Install via `/plugin`, then just ask in natural language:

- *"Convert mybook.pdf to EPUB"* — runs analysis, proposes the
  heading/body mapping for your confirmation, converts, and validates
  with epubcheck (0 errors required).
- *"Translate mybook.epub to Brazilian Portuguese"* — confirms target
  language, provider/model and cost first; translates chunk by chunk
  with structural verification; checkpoints after every chapter so an
  interrupted run resumes without re-spending tokens.

The two-step conversion is deliberate: every PDF uses its own font
sizes, so a human confirms the mapping before converting.

## Translation configuration

Copy `.env.example` to `.env` in your working directory and set
`LLM_PROVIDER`, `LLM_MODEL`, and the matching API key. Supported
providers: `anthropic`, `openai`, `google`, `deepseek`, `xai`.
Credentials are read exclusively from the environment — never CLI
flags. Never commit your `.env`.

## Known limitations

Multi-column academic layouts may shuffle reading order near column
breaks; scanned PDFs (no text layer) are unsupported; code blocks come
out as plain paragraphs; a full-page image is preserved as a single
image at that point in the flow.

## Privacy

Conversion and validation are 100% local. The only network calls are
to your chosen LLM provider, only during translation, only with your
key.

## License

MIT — see LICENSE.txt.
