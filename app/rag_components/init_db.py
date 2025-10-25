import chromadb
from chromadb.config import Settings
from pathlib import Path
import os

def get_chroma_client():
    """
    Get ChromaDB client with persistent storage.
    Handles path resolution relative to the project root.
    """
    # Get the directory where this file is located
    current_file = Path(__file__).resolve()
    
    # Navigate up to the project root (2 levels up from rag_components)
    project_root = current_file.parent.parent.parent
    
    # Database is at project_root/database
    store_path = str(project_root / 'database')
    
    # Create directory if it doesn't exist
    Path(store_path).mkdir(parents=True, exist_ok=True)
    
    return chromadb.PersistentClient(path=store_path)

def get_jobs_collection(client=None):
    """Get or create the jobs collection."""
    if client is None:
        client = get_chroma_client()
    return client.get_or_create_collection(name='jobs-collection')