from __future__ import annotations

from dataclasses import dataclass

import httpx

from ai_study.config import Settings


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


class LlmClient:
    def complete(self, messages: list[ChatMessage]) -> str:
        raise NotImplementedError


class MockLlmClient(LlmClient):
    def complete(self, messages: list[ChatMessage]) -> str:
        user_message = next((msg.content for msg in reversed(messages) if msg.role == "user"), "")
        if "Socratic" in messages[0].content or "苏格拉底" in messages[0].content:
            return (
                "先抓核心：这个主题要从数据结构、执行流程和瓶颈三层拆。"
                f"你刚才的问题是：{user_message[:80]}。"
                "你认为这里最可能受限的是算力、带宽还是调度开销？"
            )
        return (
            "更好的问法：请结合我的 CUDA/NCCL/推理引擎背景，从工程实现、性能瓶颈和简历表达角度分析这个问题。\n\n"
            f"回答：{user_message[:160]}\n"
            "建议先把问题拆成目标、上下文、约束和期望输出四部分。"
        )


class OpenAICompatibleClient(LlmClient):
    def __init__(self, settings: Settings) -> None:
        if not settings.api_key:
            raise ValueError("AI_STUDY_API_KEY is required for this provider")
        self.settings = settings

    def complete(self, messages: list[ChatMessage]) -> str:
        payload = {
            "model": self.settings.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "temperature": 0.3,
        }
        headers = {"Authorization": f"Bearer {self.settings.api_key}"}
        with httpx.Client(timeout=60) as client:
            response = client.post(
                f"{self._base_url()}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return str(data["choices"][0]["message"]["content"]).strip()

    def _base_url(self) -> str:
        if self.settings.base_url:
            return self.settings.base_url.rstrip("/")
        if self.settings.provider == "deepseek":
            return "https://api.deepseek.com"
        if self.settings.provider == "minimax":
            return "https://api.minimax.io/v1"
        return "https://api.openai.com/v1"


def create_llm_client(settings: Settings) -> LlmClient:
    if settings.provider == "mock":
        return MockLlmClient()
    if settings.provider in {"deepseek", "minimax"}:
        return OpenAICompatibleClient(settings)
    raise ValueError(f"Unsupported provider: {settings.provider}")
