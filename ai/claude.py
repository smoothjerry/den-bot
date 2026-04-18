from anthropic import AsyncAnthropic

from ai.config import DENJAMIN_SYSTEM_PROMPT


class ClaudeHandler:
    def __init__(self, api_key):
        self.client = AsyncAnthropic(api_key=api_key)

    async def generate_response(self, user_input, conversation_context, image_data, model="claude-sonnet-4-20250514"):
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
        content = user_input
        if image_data:
            new_user_input = {
                "type": "text",
                "text": user_input,
            }
            content = [new_user_input, *image_data]

        messages = []
        if conversation_context:
            messages.extend(conversation_context)
        messages.append({"role": "user", "content": content})

        messages = self._coalesce_messages(messages)

        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=1024,
                system=DENJAMIN_SYSTEM_PROMPT,
                messages=messages,
            )
            return response.content[0].text
        except Exception as e:
            return f"Error: {e}"

    def _coalesce_messages(self, messages):
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
