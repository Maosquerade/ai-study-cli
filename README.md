# AI Study CLI

A terminal-first AI learning assistant for focused technical study. It is designed for SSH-friendly use on a Linux server while keeping real study data outside the Git repository.

## Quick Start

Recommended on this workspace and most servers:

```bash
uv run learn init
uv run learn ask "Explain vLLM PagedAttention from a CUDA engineer perspective"
uv run --extra test pytest -q
```

Standard virtual environment flow:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
cp .env.example .env
learn init
learn ask "Explain vLLM PagedAttention from a CUDA engineer perspective"
learn socratic vllm --goal "Understand KV cache paging"
```

The default provider is `mock`, so the CLI works without an API key for local testing.

## Data Policy

Keep source code in Git. Keep real documents, notes, chat history, vector databases, and API keys outside Git.

Default data directory:

```text
~/ai-study-data/
  documents/
  notes/
  study.db
  logs/
```

## Providers

Set environment variables in `.env`:

```bash
AI_STUDY_PROVIDER=deepseek
AI_STUDY_API_KEY=...
AI_STUDY_MODEL=deepseek-chat
```

Supported runtime providers:

- `mock`: offline deterministic responses for testing
- `deepseek`: DeepSeek OpenAI-compatible API
- `minimax`: MiniMax OpenAI-compatible API

MiniMax example:

```bash
AI_STUDY_PROVIDER=minimax
AI_STUDY_API_KEY=...
AI_STUDY_MODEL=MiniMax-M2.7
```

## Commands

```bash
learn init
learn ask "question"
learn socratic vllm --goal "learn PagedAttention"
learn add-md ./notes/vllm.md --topic vllm
learn list-docs
learn review
```
