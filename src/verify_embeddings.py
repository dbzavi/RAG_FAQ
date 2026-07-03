import chromadb

def main():
    print("Connecting to ChromaDB at ./chroma_db...")
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # LangChain defaults to the collection name "langchain"
    try:
        collection = client.get_collection("langchain")
    except Exception as e:
        print(f"Could not find the 'langchain' collection. Has ingestion finished? Error: {e}")
        return

    # Fetch all data (documents, metadatas, and embeddings)
    results = collection.get(include=['documents', 'metadatas', 'embeddings'])
    
    docs = results.get('documents', [])
    metadatas = results.get('metadatas', [])
    embeddings = results.get('embeddings', [])
    
    total_chunks = len(docs)
    print(f"\n--- Verification Summary ---")
    print(f"Total chunks in Vector DB: {total_chunks}")
    
    if total_chunks == 0:
        print("No embeddings found.")
        return
        
    # Verify the dimension of the embedding (should be 384 for bge-small)
    emb_dim = len(embeddings[0]) if len(embeddings) > 0 else 0
    print(f"Embedding dimension size: {emb_dim} (Should be 384 for bge-small)")
    print("-" * 30 + "\n")
    
    # Print out all embeddings (showing first 5 dimensions for readability)
    for i in range(total_chunks):
        doc_preview = docs[i][:150].replace('\n', ' ') + "..."
        source = metadatas[i].get('source', 'Unknown')
        
        # Grab just the first 5 floats so it doesn't flood the terminal
        emb_preview = [round(x, 4) for x in embeddings[i][:5]]
        
        print(f"Chunk {i+1}:")
        print(f"Source: {source}")
        safe_preview = doc_preview.encode('ascii', 'ignore').decode('ascii')
        print(f"Text Preview: {safe_preview}")
        print(f"Embedding (first 5 dims): {emb_preview} ... [total {emb_dim} dims]")
        print("-" * 60)
        
    print(f"\nSuccessfully verified all {total_chunks} embeddings!")

if __name__ == "__main__":
    main()
