from pathlib import Path

from ai_study.config import load_settings
from ai_study.llm import OpenAICompatibleClient, create_llm_client


def test_minimax_client_uses_official_base_url(tmp_path: Path) -> None:
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

    client = create_llm_client(settings)

    assert isinstance(client, OpenAICompatibleClient)
    assert client._base_url() == "https://api.minimax.io/v1"

