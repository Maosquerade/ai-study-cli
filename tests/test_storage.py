from pathlib import Path

from ai_study.storage import StudyStore


def test_add_list_and_search_documents(tmp_path: Path) -> None:
    store = StudyStore(tmp_path / "study.db")

    doc_id = store.add_document(
        topic="vllm",
        title="PagedAttention",
        path="/tmp/vllm.md",
        content="KV cache blocks use block tables for paged attention.",
    )

    assert doc_id == 1
    docs = store.list_documents()
    assert docs[0].topic == "vllm"
    matches = store.search_documents("KV cache", topic="vllm")
    assert matches[0].title == "PagedAttention"


def test_review_queue(tmp_path: Path) -> None:
    store = StudyStore(tmp_path / "study.db")

    review_id = store.add_review_question("nccl", "AllReduce 的瓶颈是什么？")

    assert store.pending_reviews() == [(review_id, "nccl", "AllReduce 的瓶颈是什么？")]


def test_topic_search_falls_back_to_topic_documents(tmp_path: Path) -> None:
    store = StudyStore(tmp_path / "study.db")
    store.add_document(
        topic="vllm",
        title="PagedAttention",
        path="/tmp/vllm.md",
        content="KV cache blocks use block tables.",
    )

    matches = store.search_documents("如何理解分页注意力", topic="vllm")

    assert matches[0].title == "PagedAttention"
