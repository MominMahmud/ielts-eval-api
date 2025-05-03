import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

class ChromaService:
    def __init__(self):
        self.client = chromadb.Client(Settings(allow_reset=True))
        self.collection = self.client.get_or_create_collection("essays")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def add_essay(self, essay_id: str, content: str, metadata: dict):
        embedding = self.model.encode(content).tolist()
        self.collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata],
            ids=[essay_id]
        )
    
    def get_essay(self, essay_id: str):
        results = self.collection.get(ids=[essay_id])
        if results['documents']:
            return {
                'content': results['documents'][0],
                'metadata': results['metadatas'][0]
            }
        return None
    
    def list_essays(self, limit: int = 100, offset: int = 0):
        results = self.collection.get()
        start = offset
        end = min(offset + limit, len(results['documents']))
        return [{
            'id': results['ids'][i],
            'content': results['documents'][i],
            'metadata': results['metadatas'][i]
        } for i in range(start, end)]
    
    def search_similar_essays(self, query: str, n_results: int = 5):
        query_embedding = self.model.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return [{
            'id': results['ids'][0][i],
            'content': results['documents'][0][i],
            'metadata': results['metadatas'][0][i],
            'distance': results['distances'][0][i]
        } for i in range(len(results['ids'][0]))] 