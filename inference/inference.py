import numpy as np

class InferenceEngine:
    def __init__(self, embedder, semantic_search, fact_extractor, rule_engine):
        self.embedder = embedder
        self.semantic_search = semantic_search
        self.fact_extractor = fact_extractor
        self.rule_engine = rule_engine

    def infer(self, query, top_k=3):
        facts = self.fact_extractor.extract(query)

        # gerar embedding do query
        q_emb = self.embedder.model.encode([query], convert_to_numpy=True)
        q_emb = q_emb / np.linalg.norm(q_emb, axis=1, keepdims=True)

        evidence = self.semantic_search.query(q_emb, top_k=top_k)
        conclusions = self.rule_engine.evaluate(facts, evidence)

        return {
            "query": query,
            "facts": facts,
            "evidence": evidence,
            "conclusions": conclusions
        }
