# rag/retriever.py
import pickle
import chromadb
from chromadb.utils import embedding_functions

def load_embeddings_to_chroma(pkl_path: str, collection_name: str = "pr_docs"):
    """
    Load embeddings from a pickle file and store them in ChromaDB.
    """
    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)
    
    chunks = data['chunks']
    embeddings = data['embeddings']
    
    client = chromadb.PersistentClient(path="./chroma_db")
    
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_fn
    )
    
    ids = [f"doc_{i}" for i in range(len(chunks))]
    texts = [chunk['text'] for chunk in chunks]
    metadatas = [{'source': chunk['source']} for chunk in chunks]
    
    collection.add(
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"✅ Added {len(chunks)} chunks to ChromaDB")
    return client, collection


def query_chunks(query_text: str, collection, top_k: int = 5):
    """
    Query the vector database and return the top_k most relevant chunks.
    """
    results = collection.query(
        query_texts=[query_text],
        n_results=top_k
    )
    return results


def print_results(results):
    """
    Pretty print the retrieval results.
    """
    print("\n" + "="*60)
    print("RETRIEVED CHUNKS")
    print("="*60)
    
    for i, (doc, meta, dist) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        print(f"\n--- Result {i+1} ---")
        print(f"Source: {meta.get('source', 'Unknown')}")
        print(f"Distance: {dist:.4f}")
        print(f"Content: {doc[:200]}...")


if __name__ == "__main__":
    client, collection = load_embeddings_to_chroma("embeddings_data.pkl")
    
    test_queries = [
        "SQL injection vulnerability",
        "password storage best practices",
        "authentication and authorization"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {query}")
        print("="*60)
        
        results = query_chunks(query, collection, top_k=3)
        print_results(results)