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
