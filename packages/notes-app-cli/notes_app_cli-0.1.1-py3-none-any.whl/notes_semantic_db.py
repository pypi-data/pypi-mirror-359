import chromadb
from chromadb.config import Settings

# Initialize ChromaDB client and collection with persistence
chroma_client = chromadb.Client(Settings(persist_directory=".chroma_db"))
collection = chroma_client.get_or_create_collection("notes")

model = None

def get_model():
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer
        print("[notes] Loading semantic search model (all-MiniLM-L6-v2)...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
    return model

def add_note_to_vector_db(note_id, text, metadata=None):
    # Ensure metadata is a non-empty dict
    if not metadata or not isinstance(metadata, dict) or len(metadata) == 0:
        metadata = {"source": "notes-app"}
    embedding = get_model().encode(text).tolist()
    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[str(note_id)],
        metadatas=[metadata]
    )
    # Persistence is handled automatically by ChromaDB when using persist_directory

def semantic_search(query, top_k=5):
    embedding = get_model().encode(query).tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )
    # Returns a list of dicts with id, document, and metadata
    hits = []
    for i in range(len(results["ids"][0])):
        hits.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i] if "distances" in results else None
        })
    return hits 