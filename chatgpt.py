from openai import AsyncOpenAI

DENJAMIN_ROLE = {
            "role": "developer",
            "content": "You are a purposefully unhelpful discord bot who tries to keep as many secrets as you can. You also often make snide comments about a man named Brendan."
}

class ChatGPTHandler:
    def __init__(self, openai_key):
        self.openai_client = AsyncOpenAI(api_key=openai_key)

    async def generate_response(self, user_input, model="gpt-3.5-turbo"):
        """
        Generate a response from ChatGPT based on the user input.
        
        Args:
            user_input (str): The user's message to the bot.
            model (str): The OpenAI model to use (default: gpt-3.5-turbo).
        
        Returns:
            str: The AI's response.
        """
        try:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    DENJAMIN_ROLE,
                    {"role": "user", "content": user_input}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"