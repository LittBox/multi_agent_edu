import logging

from openai import AsyncOpenAI

from app.config.settings import settings

logger = logging.getLogger(__name__)


class LLMService:
    """统一的大模型调用服务。"""

    def __init__(self) -> None:
        self.deepseek_client = (
            AsyncOpenAI(
                api_key=settings.deepseek_api_key,
                base_url="https://api.deepseek.com",
            )
            if settings.deepseek_api_key
            else None
        )

    async def chat_with_deepseek(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        if self.deepseek_client is None:
            raise RuntimeError("DeepSeek API key is not configured.")

        response = await self.deepseek_client.chat.completions.create(
            model=settings.deepseek_model,
            messages=messages,
            temperature=temperature,
        )

        content = response.choices[0].message.content or ""
        return content.strip()


llm_service = LLMService()