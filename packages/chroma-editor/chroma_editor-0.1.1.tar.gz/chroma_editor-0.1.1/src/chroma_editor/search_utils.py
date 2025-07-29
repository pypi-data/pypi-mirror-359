"""
Thin wrapper around Chroma's semantic search.
"""
from typing import Dict, Any
import os

# Try to import OpenAI dependencies conditionally
try:
    from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Always import the default embedding function
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

def get_embedding_function():
    """Get the appropriate embedding function based on availability and configuration."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if OPENAI_AVAILABLE and openai_api_key:
        return OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name="text-embedding-3-small"
        )
    else:
        # Use ChromaDB's default embedding function (all-MiniLM-L6-v2)
        return DefaultEmbeddingFunction()

# One global embedding function object is enough.
_embed_fn = get_embedding_function()

def search(collection, query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Return a dict containing ids, documents, metadata and distances
    for the `top_k` closest results to `query`.
    """
    result = collection.query(
        query_texts=[query], n_results=top_k
    )

    # Chroma returns every field as a list-of-list ➜ take the inner list (idx 0).
    return dict(
        id=result["ids"][0],
        document=result["documents"][0],
        metadata=result["metadatas"][0],
        score=result["distances"][0],
    )
