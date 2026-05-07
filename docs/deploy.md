# Deploy

## Server Setup

```bash
git clone git@github.com:YOUR_NAME/ai-study-cli.git
cd ai-study-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
cp .env.example .env
learn init
```

Edit `.env`:

```bash
AI_STUDY_PROVIDER=deepseek
AI_STUDY_API_KEY=...
AI_STUDY_DATA_DIR=~/ai-study-data
```

Or MiniMax:

```bash
AI_STUDY_PROVIDER=minimax
AI_STUDY_API_KEY=...
AI_STUDY_MODEL=MiniMax-M2.7
AI_STUDY_DATA_DIR=~/ai-study-data
```

## Use Over SSH

```bash
ssh user@server
learn ask "解释 vLLM PagedAttention"
learn socratic vllm --goal "理解 KV cache block table"
```
