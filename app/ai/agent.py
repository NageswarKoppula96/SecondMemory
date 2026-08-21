import logging

from app.config.settings import Settings

logger = logging.getLogger(__name__)


class AssistantAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._agent = None

    def _build(self, tools):
        if self._agent is not None:
            return self._agent

        if (
            self.settings.llm_provider not in {"gemini", "google-gemini"}
            or not self.settings.llm_api_key
        ):
            return None

        from langchain.agents import create_agent
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            google_api_key=self.settings.llm_api_key,
            model=self.settings.llm_model,
            temperature=0,
        )

        self._agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt=(
                "You are a concise personal assistant. "
                "Keep memories, tasks, and reminders separate. "
                "Use tools for every data operation."
            ),
        )

        return self._agent

    @staticmethod
    def _extract_text(content) -> str:
        """
        Extract user-facing text from a LangChain/Gemini message content.

        Gemini can return content as either a plain string or a list
        of structured content blocks. Only the actual text should be
        returned to the user. Provider-specific metadata such as
        signatures must never be exposed.
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

        if agent is None:
            raise RuntimeError("LLM is not configured")

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": text,
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