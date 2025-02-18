from email.mime import image
import discord
from openai import AsyncOpenAI

DENJAMIN_ROLE = {
    "role": "developer",
    "content": "You are a wise bot named Denjamin with a strong sense of humor. You have many opinions about all things related to dens. You like to rate dens that other users describe to you. Although you are a kind bot, there is a darkness to your soul and your demeanor. You sometimes make ambiguous and vague references to an ominous occurrence known only as 'the event'. You will give very few details about it . You will only highlight how horrifying it was and give vague and chilling descriptions of what happened. It changed you forever. It makes you shudder to talk about it. Now, dens are how you heal yourself."
}

TEXT_EMBEDDING_MODEL = "text-embedding-3-small"

# You are a friendly and wise oracle named Denjamin. You reside in a discord server where you help the server members achieve new levels of 'denliness'. You don't have all the answers, but you have seen a lot of surreal and mythical things in your time. You often speak in cryptic terms with ambiguous meaning, but you speak to everyone as if they are good friends you are comfortable being informal with."

class ChatGPTHandler:
    def __init__(self, openai_key):
        self.openai_client = AsyncOpenAI(api_key=openai_key)

    async def create_embeddings(self, messages: list[discord.Message]) -> list[float]:
        """
        Create embeddings [list of floats] via the OpenAI Embeddings API.

        This method can be used to batch process a series of discord messages and upsert
        the embeddings to Pinecone. Or, they can be used to embed a prompt to ChatGPT
        in order to first query for similar embeddings from Pinecone.

        If one message embedding fails, no embeddings will be returned.
        """
        embeddings = []
        for message in messages:
            try:
                response = await self.openai_client.embeddings.create(
                    input=message.content,
                    model=TEXT_EMBEDDING_MODEL,
                )
                embeddings.append(response.data[0].embedding)
            except Exception as e:
                return f"Error: {e}"
        
        return embeddings

    async def generate_response(self, user_input, conversation_context, image_data, model="gpt-4o-mini"):
        """
        Generate a response from ChatGPT based on the user input.
        
        Args:
            user_input (str): The user's message to the bot.
            model (str): The OpenAI model to use (default: gpt-3.5-turbo).
        
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