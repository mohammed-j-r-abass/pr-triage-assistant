#=================================================================================
# SPLIT DOCUMENTS FOR EMBEDDINGS
#=================================================================================
import voyageai
import os
from dotenv import load_dotenv
from langchain_experimental.text_splitter import SemanticChunker

load_dotenv()

# Initialize Voyage AI client
vo_client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))

class VoyageEmbeddings:
    """A wrapper class to make Voyage AI compatible with LangChain's SemanticChunker."""
    
    def embed_documents(self, texts):
        """Embed a list of documents."""
        if isinstance(texts, str):
            texts = [texts]
        result = vo_client.embed(texts, model="voyage-4-large")
        return result.embeddings
    
    def embed_query(self, text):
        """Embed a single query."""
        if isinstance(text, str):
            text = [text]
        result = vo_client.embed(text, model="voyage-4-large")
        return result.embeddings[0]

# Create the embedding object
voyage_embeddings = VoyageEmbeddings()

# Create the semantic chunker
text_splitter = SemanticChunker(
    embeddings=voyage_embeddings,  # Pass the object, not the function
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount = 65,
    min_chunk_size= 80
)