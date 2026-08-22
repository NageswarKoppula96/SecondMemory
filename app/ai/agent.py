from datetime import datetime
import logging
from zoneinfo import ZoneInfo

from app.config.settings import Settings

logger = logging.getLogger(__name__)


class AssistantAgent:
    """
    Provider-independent LangChain agent.

    The LLM provider, model, and API key are supplied through Settings.
    The agent itself does not contain provider-specific model classes.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self._agent = None

    def _build(self, tools):
        if self._agent is not None:
            return self._agent

        if not self.settings.llm_provider:
            raise RuntimeError("LLM_PROVIDER is not configured")

        if not self.settings.llm_api_key:
            raise RuntimeError("LLM_API_KEY is not configured")

        from langchain.agents import create_agent
        from langchain.chat_models import init_chat_model

        provider = self._normalize_provider(
            self.settings.llm_provider
        )

        model_name = self.settings.llm_model

        if not model_name:
            raise RuntimeError("LLM_MODEL is not configured")

        logger.info(
            "Initializing LLM provider=%s model=%s",
            provider,
            model_name,
        )

        self._configure_provider_api_key(
            provider,
            self.settings.llm_api_key,
        )

        llm = init_chat_model(
            model=model_name,
            model_provider=provider,
            temperature=0,
        )

        self._agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt=(
                "You are a concise personal assistant. "
                "Keep memories, tasks, and reminders separate. "
                "Use tools for every data operation. "
                "When the user asks to save information, use the "
                "memory tools. When the user asks about saved "
                "information, search the memory tools. "
                "When the user asks to create or manage a task, "
                "use the task tools. "
                "When the user asks to create, list, or cancel a "
                "reminder, use the reminder tools."
            ),
        )

        return self._agent

    @staticmethod
    def _normalize_provider(provider: str) -> str:
        """
        Normalize common provider aliases to LangChain provider names.
        """

        normalized = provider.strip().lower()

        aliases = {
            "gemini": "google_genai",
            "google": "google_genai",
            "google-gemini": "google_genai",
            "google_genai": "google_genai",
            "openai": "openai",
            "anthropic": "anthropic",
            "claude": "anthropic",
            "openrouter": "openrouter",
            "groq": "groq",
            "mistral": "mistralai",
            "mistralai": "mistralai",
            "cohere": "cohere",
            "xai": "xai",
            "deepseek": "deepseek",
        }

        return aliases.get(normalized, normalized)

    @staticmethod
    def _configure_provider_api_key(
        provider: str,
        api_key: str,
    ) -> None:
        """
        Configure the provider-specific environment variable expected
        by the corresponding LangChain integration.

        The application exposes only one generic LLM_API_KEY setting.
        """

        import os

        key_mapping = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google_genai": "GOOGLE_API_KEY",
            "groq": "GROQ_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "mistralai": "MISTRAL_API_KEY",
            "cohere": "COHERE_API_KEY",
            "xai": "XAI_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
        }

        environment_variable = key_mapping.get(provider)

        if environment_variable:
            os.environ[environment_variable] = api_key
            return

        logger.warning(
            "No standard API-key environment mapping is configured "
            "for provider '%s'. The provider integration may require "
            "additional configuration.",
            provider,
        )

    @staticmethod
    def _extract_text(content) -> str:
        """
        Extract user-facing text from LangChain/Gemini/provider
        structured message content.

        Provider-specific metadata such as signatures must never
        be exposed to the Telegram user.
        """

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            text_parts = []

            for block in content:
                if isinstance(block, str):
                    text_parts.append(block)

                elif isinstance(block, dict):
                    if block.get("type") == "text":
                        text = block.get("text")

                        if isinstance(text, str) and text.strip():
                            text_parts.append(text.strip())

            return "\n".join(text_parts).strip()

        return ""

    def invoke(self, text: str, tools) -> str:
        agent = self._build(tools)

        user_timezone = ZoneInfo("Asia/Kolkata")
        now = datetime.now(user_timezone)

        contextual_text = f"""
            Current date and time: {now.strftime("%Y-%m-%d %H:%M:%S")}
            Timezone: Asia/Kolkata

            User request:
                {text}"""

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": contextual_text,
                    }
                ]
            }
        )

        messages = result.get("messages", [])

        if not messages:
            return "I couldn't generate a response."

        content = messages[-1].content

        response = self._extract_text(content)

        if not response:
            logger.warning(
                "Agent returned an empty or unsupported response: %r",
                content,
            )
            return "I couldn't generate a response."

        return response