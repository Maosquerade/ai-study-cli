from pathlib import Path


def test_gitignore_protects_runtime_data() -> None:
    gitignore = Path(".gitignore").read_text(encoding="utf-8")

    required_patterns = [
        ".env",
        ".venv/",
        "__pycache__/",
        ".pytest_cache/",
        "data/",
        "documents/",
        "vector_db/",
        "*.db",
        "*.sqlite",
        "logs/",
    ]

    for pattern in required_patterns:
        assert pattern in gitignore

