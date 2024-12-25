import openai

class ChatGPTHandler:
    def __init__(self, api_key):
        # Initialize the OpenAI client
        openai.api_key = api_key

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
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful and funny assistant."},
                    {"role": "user", "content": user_input}
                ]
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            return f"Error: {e}"
