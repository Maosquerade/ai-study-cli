from pathlib import Path

from ai_study.llm import MockLlmClient
from ai_study.storage import StudyStore
from ai_study.study import add_markdown, ask, socratic_next, socratic_prompt


def test_add_markdown_extracts_title(tmp_path: Path) -> None:
    note = tmp_path / "note.md"
    note.write_text("# KV Cache\n\nPagedAttention manages KV blocks.", encoding="utf-8")
    store = StudyStore(tmp_path / "study.db")

    doc_id = add_markdown(store, note, topic="vllm")

    assert doc_id == 1
    assert store.list_documents()[0].title == "KV Cache"


def test_ask_records_messages(tmp_path: Path) -> None:
    store = StudyStore(tmp_path / "study.db")
    client = MockLlmClient()

    answer = ask(client, store, "如何理解 PagedAttention？", topic="vllm")

    assert "更好的问法" in answer
    messages = store.recent_messages()
    assert [message[1] for message in messages] == ["user", "assistant"]


def test_socratic_adds_review_question(tmp_path: Path) -> None:
    store = StudyStore(tmp_path / "study.db")
    client = MockLlmClient()

    answer = socratic_prompt(client, store, "vllm", "理解 KV cache 管理")

    assert "你认为" in answer
    assert store.pending_reviews()[0][1] == "vllm"


def test_socratic_next_records_student_answer(tmp_path: Path) -> None:
    store = StudyStore(tmp_path / "study.db")
    client = MockLlmClient()
    socratic_prompt(client, store, "vllm", "理解 KV cache 管理")

    answer = socratic_next(client, store, "vllm", "理解 KV cache 管理", "主要瓶颈是 HBM 带宽")

    assert "你认为" in answer
    messages = store.recent_messages(limit=4)
    assert any(message[3] == "主要瓶颈是 HBM 带宽" for message in messages)
