from typing import Any

from anthropic import AsyncAnthropic

from denbot.ai.config import DENJAMIN_SYSTEM_PROMPT


class ClaudeHandler:
    def __init__(self, api_key: str | None) -> None:
        self.client = AsyncAnthropic(api_key=api_key)

    async def generate_response(
        self,
        user_input: str,
        conversation_context: list[dict[str, Any]] | None,
        image_data: list[dict[str, Any]],
        model: str = "claude-sonnet-4-20250514",
    ) -> str:
        """
        Generate a response from Claude based on the user input.

        Args:
            user_input (str): The user's message to the bot.
            conversation_context (list): Prior messages in the conversation.
            image_data (list): Image content blocks for vision.
            model (str): The Anthropic model to use.

        Returns:
            str: The AI's response.
        """
        content: str | list[dict[str, Any]] = user_input
        if image_data:
            new_user_input: dict[str, Any] = {
                "type": "text",
                "text": user_input,
            }
            content = [new_user_input, *image_data]

        messages: list[dict[str, Any]] = []
        if conversation_context:
            messages.extend(conversation_context)
        messages.append({"role": "user", "content": content})

        messages = self._coalesce_messages(messages)

        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=1024,
                system=DENJAMIN_SYSTEM_PROMPT,
                messages=messages,  # type: ignore[arg-type]
            )
            return response.content[0].text  # type: ignore[union-attr]
        except Exception as e:
            return f"Error: {e}"

    def _coalesce_messages(
        self, messages: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Merge consecutive same-role messages for Anthropic API compatibility."""
        if not messages:
            return messages
        coalesced = [messages[0].copy()]
        for msg in messages[1:]:
            if msg["role"] == coalesced[-1]["role"]:
                prev_content = coalesced[-1]["content"]
                new_content = msg["content"]
                if isinstance(prev_content, str) and isinstance(new_content, str):
                    coalesced[-1]["content"] = prev_content + "\n" + new_content
                else:
                    coalesced.append(msg.copy())
            else:
                coalesced.append(msg.copy())
        return coalesced
