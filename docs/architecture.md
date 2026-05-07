# Architecture

The repository contains code, prompts, examples, and deployment helpers. Real study data stays outside Git in `AI_STUDY_DATA_DIR`.

## Runtime

```text
CLI command
  -> settings loader
  -> SQLite study store
  -> local document search
  -> LLM provider
  -> terminal output
```

## Data Boundaries

Tracked:

- source code
- prompt templates
- examples
- docs

Ignored:

- `.env`
- SQLite databases
- uploaded documents
- vector databases
- logs
- private notes

