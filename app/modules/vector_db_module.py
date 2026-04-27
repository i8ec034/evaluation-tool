# Vector DB Module
import chromadb
from chromadb.config import Settings
from app.config.settings import CHUNK_SIZE, OVERLAP, VECTOR_SEARCH_RESULTS, ENABLE_VECTOR_SEARCH

client = chromadb.PersistentClient(path="./chroma_db")

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def store_embeddings(area, chunks, document_id=None, source=None, domain=None, subdomain=None):
    """Store chunks with domain metadata - only if vector search is enabled"""
    if not ENABLE_VECTOR_SEARCH:
        print("Vector search disabled - skipping embedding storage")
        return
        
    try:
        collection = client.get_or_create_collection(name="documents", metadata={"hnsw:space": "cosine"})
        metadata = {"domain": domain or area, "area": area}
        if document_id is not None:
            metadata["document_id"] = document_id
        if source:
            metadata["source"] = source
        if subdomain:
            metadata["subdomain"] = subdomain

        for i, chunk in enumerate(chunks):
            try:
                collection.add(
                    documents=[chunk],
                    ids=[f"{domain or area}_{document_id or 'doc'}_{i}"],
                    metadatas=[{**metadata, "chunk_index": i}]
                )
            except Exception as e:
                print(f"Warning: Failed to store embedding for chunk {i}: {e}")
                # Continue without embeddings - just store metadata
                try:
                    collection.add(
                        documents=[chunk],
                        ids=[f"{domain or area}_{document_id or 'doc'}_{i}"],
                        metadatas=[{**metadata, "chunk_index": i, "embedding_failed": True}]
                    )
                except Exception as e2:
                    print(f"Error: Could not store chunk {i} even without embeddings: {e2}")
                    continue
    except Exception as e:
        print(f"Warning: ChromaDB collection error: {e}")
        print("Continuing without vector embeddings - QA will still work from SQLite")

def retrieve_relevant_chunks(domain, query=None, n=VECTOR_SEARCH_RESULTS):
    """Retrieve chunks by domain using metadata filter - only if vector search is enabled"""
    if not ENABLE_VECTOR_SEARCH:
        print("Vector search disabled - using SQLite fallback")
        return []
        
    try:
        collection = client.get_collection(name="documents")
        if query:
            results = collection.query(query_texts=[query], n_results=n, where={"domain": domain})
        else:
            # Get all results for domain
            results = collection.get(where={"domain": domain}, limit=n)
        return results.get('documents', []) or results.get('documents', [])
    except Exception as e:
        print(f"ChromaDB Error: {e}")
        return []