from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from platformdirs import user_data_dir


@dataclass(frozen=True)
class Settings:
    provider: str
    api_key: str | None
    base_url: str | None
    model: str
    data_dir: Path

    @property
    def db_path(self) -> Path:
        return self.data_dir / "study.db"


def load_settings(env_file: Path | None = None) -> Settings:
    if env_file and env_file.exists():
        _clear_ai_study_env()
        load_dotenv(env_file, override=True)
    else:
        load_dotenv()

    provider = os.getenv("AI_STUDY_PROVIDER", "mock").strip().lower()
    data_dir = Path(
        os.getenv("AI_STUDY_DATA_DIR", user_data_dir("ai-study-cli", "maosquerade"))
    ).expanduser()

    return Settings(
        provider=provider,
        api_key=_empty_to_none(os.getenv("AI_STUDY_API_KEY")),
        base_url=_empty_to_none(os.getenv("AI_STUDY_BASE_URL")),
        model=os.getenv("AI_STUDY_MODEL") or _default_model(provider),
        data_dir=data_dir,
    )


def _empty_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _default_model(provider: str) -> str:
    defaults = {
        "deepseek": "deepseek-chat",
        "minimax": "MiniMax-M2.7",
        "mock": "mock-study-model",
    }
    return defaults.get(provider, "mock-study-model")


def _clear_ai_study_env() -> None:
    for key in [
        "AI_STUDY_PROVIDER",
        "AI_STUDY_API_KEY",
        "AI_STUDY_BASE_URL",
        "AI_STUDY_MODEL",
        "AI_STUDY_DATA_DIR",
    ]:
        os.environ.pop(key, None)
