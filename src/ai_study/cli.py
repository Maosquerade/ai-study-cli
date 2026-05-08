from __future__ import annotations

from pathlib import Path

import typer

from ai_study.config import load_settings
from ai_study.llm import create_llm_client
from ai_study.storage import StudyStore
from ai_study.study import add_markdown, ask as ask_question, socratic_next, socratic_prompt

app = typer.Typer(help="Terminal-first AI study assistant.")


def _store() -> StudyStore:
    settings = load_settings()
    return StudyStore(settings.db_path)


def _client():
    return create_llm_client(load_settings())


@app.command()
def init() -> None:
    """Create the data directory and SQLite database."""
    settings = load_settings()
    store = StudyStore(settings.db_path)
    store.init()
    for name in ["documents", "notes", "logs"]:
        (settings.data_dir / name).mkdir(parents=True, exist_ok=True)
    typer.echo(f"Initialized data directory: {settings.data_dir}")


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to ask."),
    topic: str | None = typer.Option(None, "--topic", "-t", help="Optional topic filter."),
) -> None:
    """Ask a question with optional local document context."""
    answer = ask_question(_client(), _store(), question, topic)
    typer.echo(answer)


@app.command()
def socratic(
    topic: str = typer.Argument(..., help="Study topic."),
    goal: str = typer.Option(..., "--goal", "-g", help="Learning goal for this session."),
    once: bool = typer.Option(False, "--once", help="Ask only the first question and exit."),
) -> None:
    """Start a focused Socratic learning session."""
    client = _client()
    store = _store()
    answer = socratic_prompt(client, store, topic, goal)
    typer.echo(answer)
    if once:
        return

    typer.echo("\n输入你的回答继续；输入 /exit 或 /quit 结束。")
    while True:
        user_answer = typer.prompt("你")
        if user_answer.strip().lower() in {"/exit", "/quit", "exit", "quit", "q"}:
            typer.echo("已结束本次学习。")
            return
        answer = socratic_next(client, store, topic, goal, user_answer)
        typer.echo(answer)


@app.command("add-md")
def add_md(
    path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    topic: str | None = typer.Option(None, "--topic", "-t", help="Topic name."),
) -> None:
    """Add a Markdown file to the local study store."""
    doc_id = add_markdown(_store(), path, topic)
    typer.echo(f"Added document #{doc_id}: {path}")


@app.command("list-docs")
def list_docs() -> None:
    """List local study documents."""
    docs = _store().list_documents()
    if not docs:
        typer.echo("No documents added yet.")
        return
    for doc in docs:
        typer.echo(f"#{doc.id} [{doc.topic}] {doc.title} - {doc.path}")


@app.command()
def review(limit: int = typer.Option(5, "--limit", "-n")) -> None:
    """Show pending active-recall review questions."""
    reviews = _store().pending_reviews(limit=limit)
    if not reviews:
        typer.echo("No pending review questions.")
        return
    for review_id, topic, question in reviews:
        typer.echo(f"#{review_id} [{topic}] {question}")


if __name__ == "__main__":
    app()
