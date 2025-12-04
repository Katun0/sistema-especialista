import json
import numpy as np
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def load_kb(self, path):
        with open(path, "r", encoding="utf8") as f:
            data = json.load(f)
        # transforma em lista de docs com id, title e text
        docs = []
        for diag_id, diag in data.get("diagnosticos", {}).items():
            title = diag_id.replace("_", " ").capitalize()
            text = diag.get("descricao", "")
            # concatenar sintomas para enriquecer embedding
            symptoms_text = ". ".join(diag.get("sintomas", []))
            full = f"{title}. {text} Sintomas: {symptoms_text}"
            docs.append({
                "id": diag_id,
                "title": title,
                "text": full,
                "meta": {
                    "faixa_etaria": diag.get("faixa_etaria"),
                    "tratamento": diag.get("tratamento", [])
                }
            })
        return docs

    def encode_documents(self, docs):
        texts = [d["text"] for d in docs]
        emb = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        # normalizar para similaridade
        emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)
        return emb
