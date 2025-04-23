from sentence_transformers import SentenceTransformer
from rag_pipeline.vector_db import get_jobs_collection
import torch

class JobRetriever:
    def __init__(self, model_name="all-MiniLM-L6-v2", top_k=5):
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = SentenceTransformer(model_name, device=device)
        self.collection = get_jobs_collection()
        self.top_k = top_k

    def embed_query(self, query: str):
        return self.model.encode([query])[0]

    def retrieve_similar_jobs(self, query: str):
        embedding = self.embed_query(query)
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=self.top_k
        )
        return results
    
if __name__ == "__main__":
    retriever = JobRetriever()
    query = "Skills required by the IT candidate are"
    results = retriever.retrieve_similar_jobs(query)

    for i, doc in enumerate(results['documents'][0]):
        print(f"\nResult {i+1}")
        print("Text:", doc)
        print("Metadata:", results['metadatas'][0][i])
