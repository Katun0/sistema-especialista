import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class SemanticSearch:
    def __init__(self, embeddings, docs):
        self.embeddings = embeddings
        self.docs = docs

    def query(self, query_embedding, top_k=3):
        # query_embedding: shape (1, dim)
        sims = cosine_similarity(query_embedding, self.embeddings)[0]
        idxs = np.argsort(sims)[::-1][:top_k]
        results = []
        for i in idxs:
            results.append({
                "doc": self.docs[i],
                "score": float(sims[i])
            })
        return results
