from pathlib import Path

from ai_study.config import load_settings


def test_load_settings_from_env_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "AI_STUDY_PROVIDER=deepseek",
                "AI_STUDY_API_KEY=test-key",
                f"AI_STUDY_DATA_DIR={tmp_path / 'data'}",
            ]
        ),
        encoding="utf-8",
    )

    settings = load_settings(env_file)

    assert settings.provider == "deepseek"
    assert settings.api_key == "test-key"
    assert settings.model == "deepseek-chat"
    assert settings.db_path == tmp_path / "data" / "study.db"


def test_minimax_default_model(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "AI_STUDY_PROVIDER=minimax",
                "AI_STUDY_API_KEY=test-key",
                f"AI_STUDY_DATA_DIR={tmp_path / 'data'}",
            ]
        ),
        encoding="utf-8",
    )

    settings = load_settings(env_file)

    assert settings.model == "MiniMax-M2.7"
