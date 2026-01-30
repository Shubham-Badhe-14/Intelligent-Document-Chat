import faiss
import numpy as np
import pickle
import os

class VectorStore:
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.chunks = {}  # Map ID to text chunk
        self.doc_map = {} # Map ID to document ID (for future multiple doc support)
        self.current_id = 0

    def add_documents(self, document_id: str, chunks: list[str], embeddings: list[list[float]]):
        """Adds document chunks and embeddings to the store."""
        if not chunks:
            return

        vectors = np.array(embeddings).astype('float32')
        num_new = vectors.shape[0]
        
        self.index.add(vectors)
        
        for i in range(num_new):
            global_id = self.current_id + i
            self.chunks[global_id] = chunks[i]
            self.doc_map[global_id] = document_id
            
        self.current_id += num_new

    def search(self, query_embedding: list[float], k: int = 5):
        """Searches for top K similar chunks."""
        if self.index.ntotal == 0:
            return []
            
        vector = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(vector, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx in self.chunks:
                results.append(self.chunks[idx])
                
        return results

    def clear(self):
        """Clears the index."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = {}
        self.doc_map = {}
        self.current_id = 0
