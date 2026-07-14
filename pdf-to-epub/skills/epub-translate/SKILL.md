---
name: epub-translate
description: >
  This skill should be used when the user wants to translate an EPUB
  ebook into another language while preserving HTML structure and
  images — e.g. "translate this EPUB to Portuguese", "traduzir este
  ebook", "translate my book to Spanish". It works on any well-formed
  EPUB. It is NOT for translating plain text or markdown, and NOT for
  PDF→EPUB conversion (that is the pdf-to-epub skill).
version: 0.1.0
---

# EPUB translation: decision guide

## Cost — always confirm before spending

Every chunk is a paid API call; a book means dozens of calls. **Always
get explicit user confirmation before running the translation**,
confirming the target language and the provider/model when not obvious
from the `.env`. Recommend a test run on one short chapter before
committing to the whole book.

## Model choice (cost × quality)

Budget models (the Flash/Mini/Lite tier of any provider) are enough
for technical prose and non-fiction. Reserve mid/flagship models for
literary text, or when a spot-check of the budget model's output
disappoints. Model names and prices change fast — confirm on the
provider's site before translating a large book.

## Interpreting warnings

Frequent `tag mismatch` / `flagged` chunks mean the model is weak at
structural instruction-following (observed with very small models).
Report it to the user and suggest a stronger model from the same
family. **Never edit the script to weaken or silence the structural
verification** — it is the only thing keeping corrupted HTML out of
the final EPUB.

## Configuration

Provider, model and API key are set exclusively via environment
variables or a `.env` file (see `.env.example` at the plugin root) —
never CLI flags.

| `LLM_PROVIDER` | Key | pip package | Particularity |
|---|---|---|---|
| `anthropic` | `ANTHROPIC_API_KEY` | `langchain-anthropic` | — |
| `openai` | `OPENAI_API_KEY` | `langchain-openai` | — |
| `google` | `GOOGLE_API_KEY` or `GEMINI_API_KEY` | `langchain-google-genai` | — |
| `deepseek` | `DEEPSEEK_API_KEY` | `langchain-openai` | `base_url=https://api.deepseek.com` |
| `xai` | `XAI_API_KEY` | `langchain-openai` | `base_url=https://api.x.ai/v1` |

`LLM_MODEL` selects the model.

## Resilience

The script checkpoints after every chapter
(`<output>.checkpoint.json`). If interrupted (rate limit, crash,
Ctrl+C), re-running the same command resumes without re-spending
tokens on finished chapters. The checkpoint is safe to delete after
reviewing the output.
