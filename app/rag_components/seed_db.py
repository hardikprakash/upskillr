import pandas as pd
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import torch
from sentence_transformers import SentenceTransformer
import re

try:
    from app.rag_components.init_db import get_jobs_collection
except ImportError:
    from init_db import get_jobs_collection

def clean_dataset(dataset):
    jobs_data = dataset[['title', 'description']]
    return jobs_data
    
def chunk_text(title: str, description: str, max_word_count=100):
    if not description:
        return []
    
    chunks = []

    # Remove invisible Unicode chars (zero-width, non-breaking spaces, etc.)
    description = re.sub(r'[\u200B-\u200D\uFEFF]', '', description)
    # Remove control chars except newlines (\x0A, \x0D) and tabs (\x09)
    description = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1f\x7f-\x9f]', '', description)

    # Collapse excessive whitespace
    description = re.sub(r'\n+', '\n', description)
    description = re.sub(r'[ \t]+', ' ', description)
    description = re.sub(r'\s{2,}', ' ', description)

    # Replace common bullets with "-"
    description = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25AB]', '\n-', description)
    description = description.replace('•', '\n-')
    description = re.sub(r'\so\s', '\n-', description)

    description_words = description.split()

    # Iteratively build chunks
    for i in range(0, len(description_words), max_word_count):
        chunk_words = description_words[i:i + max_word_count]
        chunk_text = ' '.join(chunk_words)
        
        # Add title context to each chunk
        formatted_chunk = f"Job Title: {title}\nDescription: {chunk_text}"
        chunks.append(formatted_chunk)
        
    # print(len(chunks))
    return chunks        

def main():
    path = os.getcwd()
    path = Path(path) / 'data' / 'cleaned_job_postings.csv'
    
    dataset = pd.read_csv(path)
    dataset = clean_dataset(dataset)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = SentenceTransformer('all-MiniLM-L6-v2', device=device)

    collection = get_jobs_collection()

    documents = []
    metadatas = []
    ids = []
    embeddings = []
    document_id = 0


    for idx, row in dataset.iterrows():
        if pd.notna(row.get('description')):
            title = str(row.get('title', 'Undefined')).strip()
            description = str(row.get('description', 'Undefined')).strip()
            
            if not title or not description or description == 'Undefined':
                continue

            chunks = chunk_text(title, description)

            for chunk_idx, chunk in enumerate(chunks):
                documents.append(chunk)

                metadata = {
                    'title': title,
                    'word_count': len(chunk.split())
                }

                metadatas.append(metadata)
                ids.append(document_id)

                document_id+=1

    BATCH_SIZE = 100

    for i in range(0, len(documents), BATCH_SIZE):
        batch_docs = documents[i: i+BATCH_SIZE]
        batch_embeddings = model.encode(batch_docs, show_progress_bar=True)
        embeddings.extend(batch_embeddings.tolist())
        print(f"Processed batch {i//BATCH_SIZE + 1}/{(len(documents)-1)//BATCH_SIZE + 1}")

        print("Storing in ChromaDB...")
    
    # collection.add(
    #     embeddings=embeddings,
    #     documents=documents,
    #     metadatas=metadatas,
    #     ids=ids
    # )

if __name__ == '__main__':
    main()