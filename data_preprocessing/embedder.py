from sentence_transformers import SentenceTransformer
import pandas as pd
from pathlib import Path
import os
import chromadb
from chromadb.config import Settings

def get_store_path():
    return str((Path(os.getcwd()).parent / 'database') if os.getcwd().endswith('app') else (Path(os.getcwd()) / 'database'))

def embed_jobs():

    df = pd.read_csv(Path(os.getcwd()) / 'data' / 'chunked_jobs.csv')
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    store_path = get_store_path()

    chroma_client = chromadb.PersistentClient(path=store_path)
    collection = chroma_client.get_or_create_collection(name='jobs-collection')

    batch_size = 100
    
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        
        # Combine job title and category with text
        texts = ("We are looking for candidates with the following qualifications: Target Job Role:" + batch['job_title'] + "(In the " + batch['category'] + "field)." + "Here are the job listing details:" + batch['text']).to_list()



        ids = batch['id'].astype(str).to_list()
        metadatas = batch[["job_id", "category", "job_title", "chunk_index"]].to_dict(orient="records")

        embeddings = model.encode(texts, show_progress_bar=True)

        collection.add(
            metadatas=metadatas,
            documents=texts,
            embeddings=embeddings,
            ids=ids
        )


    print(f"✅ Embedded and stored {len(df)} job chunks to ChromaDB.")

def test_embedding():
    store_path = get_store_path()
    chroma_client = chromadb.PersistentClient(path=store_path)
    collection = chroma_client.get_collection("jobs-collection")

    count = collection.count()
    print("Stored embeddings:", count)
    assert count > 0, "❌ No embeddings stored!"

    query = "senior it manager"
    results = collection.query(query_texts=[query], n_results=3)

    docs = results['documents'][0]
    print("\nTop matches:")
    for i, doc in enumerate(docs):
        print(f"{i+1}: {doc[:200]}...")  # show first 200 chars of the match

    assert len(docs) > 0, "❌ No documents returned from query!"
    print("✅ Test passed: Embedding and retrieval working correctly.")

if __name__ == '__main__':
    chroma_client = chromadb.PersistentClient(path=get_store_path())
    embed_jobs()
    # test_embedding()
