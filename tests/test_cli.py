from pathlib import Path

from typer.testing import CliRunner

from ai_study.cli import app


runner = CliRunner()


def test_cli_init_creates_data_dirs(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("AI_STUDY_PROVIDER", "mock")
    monkeypatch.setenv("AI_STUDY_DATA_DIR", str(tmp_path / "data"))

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0
    assert (tmp_path / "data" / "documents").is_dir()
    assert (tmp_path / "data" / "study.db").is_file()


def test_cli_add_list_ask_and_review(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("AI_STUDY_PROVIDER", "mock")
    monkeypatch.setenv("AI_STUDY_DATA_DIR", str(tmp_path / "data"))
    note = tmp_path / "vllm.md"
    note.write_text("# PagedAttention\n\nKV cache block table.", encoding="utf-8")

    init_result = runner.invoke(app, ["init"])
    add_result = runner.invoke(app, ["add-md", str(note), "--topic", "vllm"])
    list_result = runner.invoke(app, ["list-docs"])
    ask_result = runner.invoke(app, ["ask", "如何理解 PagedAttention?", "--topic", "vllm"])
    socratic_result = runner.invoke(
        app,
        ["socratic", "vllm", "--goal", "理解 KV cache block table", "--once"],
    )
    review_result = runner.invoke(app, ["review"])

    assert init_result.exit_code == 0
    assert add_result.exit_code == 0
    assert "Added document #1" in add_result.output
    assert "[vllm] PagedAttention" in list_result.output
    assert "更好的问法" in ask_result.output
    assert "你认为" in socratic_result.output
    assert "理解 KV cache block table" in review_result.output


def test_cli_socratic_interactive_loop(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("AI_STUDY_PROVIDER", "mock")
    monkeypatch.setenv("AI_STUDY_DATA_DIR", str(tmp_path / "data"))

    result = runner.invoke(
        app,
        ["socratic", "vllm", "--goal", "理解 KV cache"],
        input="我认为主要是带宽瓶颈\n/exit\n",
    )

    assert result.exit_code == 0
    assert "输入你的回答继续" in result.output
    assert "已结束本次学习" in result.output
