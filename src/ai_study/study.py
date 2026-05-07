from __future__ import annotations

from pathlib import Path

from ai_study.llm import ChatMessage, LlmClient
from ai_study.storage import StudyStore


PROMPT_DIR = Path(__file__).parent / "prompts"


def load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8").strip()


def build_context(store: StudyStore, query: str, topic: str | None = None) -> str:
    docs = store.search_documents(query=query, topic=topic)
    if not docs:
        return "No local study documents matched."
    chunks = []
    for doc in docs:
        excerpt = doc.content[:1200].strip()
        chunks.append(f"[{doc.topic}] {doc.title}\n{excerpt}")
    return "\n\n---\n\n".join(chunks)


def ask(client: LlmClient, store: StudyStore, question: str, topic: str | None = None) -> str:
    context = build_context(store, question, topic)
    messages = [
        ChatMessage("system", load_prompt("ask.md")),
        ChatMessage("user", f"Local context:\n{context}\n\nUser question:\n{question}"),
    ]
    answer = client.complete(messages)
    store.add_message("ask", "user", question, topic)
    store.add_message("ask", "assistant", answer, topic)
    return answer


def socratic_prompt(client: LlmClient, store: StudyStore, topic: str, goal: str) -> str:
    context = build_context(store, goal, topic)
    messages = [
        ChatMessage("system", load_prompt("socratic.md")),
        ChatMessage(
            "user",
            (
                f"Topic: {topic}\n"
                f"Goal: {goal}\n"
                f"Local context:\n{context}\n\n"
                "Start a focused learning session. Ask one question first."
            ),
        ),
    ]
    answer = client.complete(messages)
    store.add_message("socratic", "user", goal, topic)
    store.add_message("socratic", "assistant", answer, topic)
    store.add_review_question(topic, f"复述本次目标的核心概念：{goal}")
    return answer


def add_markdown(store: StudyStore, path: Path, topic: str | None = None) -> int:
    content = path.read_text(encoding="utf-8")
    inferred_topic = topic or path.parent.name or "general"
    title = _extract_title(content) or path.stem
    return store.add_document(
        topic=inferred_topic,
        title=title,
        path=str(path.resolve()),
        content=content,
    )


def _extract_title(content: str) -> str | None:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return None

