import faiss
import numpy as np

class ContentStore:
    def __init__(self, chunk_entries):
        self.chunk_entries = chunk_entries
        self.embedding_matrix = self.build_embedding_matrix()
        self.index = self.build_index()
        self.chunk_id_map = self.build_chunk_map()


    def build_embedding_matrix(self, normalize=True):
        embedding_matrix = np.array([entry["embedding"] for entry in self.chunk_entries]).astype("float32")
        if normalize:
            embedding_matrix = embedding_matrix / np.linalg.norm(embedding_matrix, axis=1, keepdims=True)

        return embedding_matrix
    

    def build_index(self):
        index = faiss.IndexFlatIP(self.embedding_matrix.shape[1])
        index.add(self.embedding_matrix)

        return index
    

    def build_chunk_map(self):
        return {i: entry for i, entry in enumerate(self.chunk_entries)}


    def query(self, query_embedding, top_k=5):
        top_k = min(len(self.chunk_entries), top_k)
        D, I = self.index.search(np.array([query_embedding]), top_k)
        return [self.chunk_id_map[i]["text"] for i in I[0]]