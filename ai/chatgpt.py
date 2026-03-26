from openai import AsyncOpenAI

from ai.config import DENJAMIN_ROLE


class ChatGPTHandler:
    def __init__(self, openai_key):
        self.openai_client = AsyncOpenAI(api_key=openai_key)

    async def generate_response(self, user_input, conversation_context, image_data, model="gpt-4o-mini"):
        """
        Generate a response from ChatGPT based on the user input.

        Args:
            user_input (str): The user's message to the bot.
            model (str): The OpenAI model to use (default: gpt-4o-mini).

        Returns:
            str: The AI's response.
        """
        content = user_input
        if image_data:
            # format user input text for content array.
            new_user_input = {
                "type": "text",
                "text": user_input,
            }
            content = [new_user_input, *image_data]

        # Construct the messages list dynamically
        input_messages = [DENJAMIN_ROLE]
        if conversation_context:
            input_messages.extend(conversation_context)
        input_messages.append({"role": "user", "content": content})

        # generate response
        try:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=input_messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"
