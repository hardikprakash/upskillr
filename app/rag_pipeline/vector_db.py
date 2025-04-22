import chromadb
from chromadb.config import Settings
from pathlib import Path
import os

def get_chroma_client():
    store_path = str((Path(os.getcwd()).parent / 'data') if os.getcwd().endswith('app') else (Path(os.getcwd()) / 'data'))
    return chromadb.PersistentClient(path=store_path)

def get_jobs_collection(client=None):
    if client is None:
        client = get_chroma_client()
    return client.get_or_create_collection(name='jobs-collection')
