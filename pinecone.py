import os

from pinecone import Pinecone, ServerlessSpec

# Setup Pinecone client
PINECONE_KEY = os.getenv("PINECONE_KEY")
pc = Pinecone(api_key=PINECONE_KEY)
