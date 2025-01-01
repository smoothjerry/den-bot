import os

from pinecone import Pinecone

# Setup Pinecone client
PINECONE_KEY = os.getenv("PINECONE_KEY")
pc = Pinecone(api_key=PINECONE_KEY)

index_name = "knights-peen"
if index_name not in pc.list_indexes().names():
    raise ValueError(
        f"No '{index_name}' index exists. You must create the index before "
        "running this notebook. Please refer to the walkthrough at "
        "'github.com/pinecone-io/examples'."  # TODO add full link
    )

def upsert_embeddings_from_discord_messages():
    """
    Given a list of discord messages, generate the embeddings via chatGPT,
    append the metadata to the JSON, and upsert the new embedding to Pinecone.
    """

def query_embedding():
    """
    Given a discord message, genearte the embedding via chatGPT,
    and query for similar messages from the index.

    This will return a list of results. These results need to be 
    prepended during chatGPT prompt generation to the bot.
    """
