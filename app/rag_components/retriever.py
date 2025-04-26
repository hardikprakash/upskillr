from sentence_transformers import SentenceTransformer
from rag_components.init_db import get_jobs_collection
from prompts import job_query_prompt_template
import torch

class JobRetriever:
    def __init__(self, model_name="all-MiniLM-L6-v2", top_k=5):
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = SentenceTransformer(model_name, device=device)
        self.collection = get_jobs_collection()
        self.top_k = top_k

    def embed_query(self, query: str):
        return self.model.encode([query])[0]

    def retrieve_similar_jobs(self, job_role_str: str, skills_str: str, education_str :str, experience_str: str):
        
        job_query_prompt = job_query_prompt_template.format(
            job_role=job_role_str,
            skills=skills_str,
            education=education_str,
            experience=experience_str
        )
        
        embedding = self.embed_query(job_query_prompt)

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=self.top_k
        )
        return results