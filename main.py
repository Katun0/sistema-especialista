# expert_system_json/main.py
import os
from embeddings.embedder import Embedder
from semantic.search import SemanticSearch
from inference.fact_extractor import FactExtractor
from inference.rule_engine import RuleEngine
from inference.inference import InferenceEngine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(BASE_DIR, "data", "knowledge.json")

def main():
    print("Carregando sistema especialista (JSON) ...")
    embedder = Embedder()
    docs = embedder.load_kb(KB_PATH)
    embeddings = embedder.encode_documents(docs)

    sem = SemanticSearch(embeddings, docs)
    extractor = FactExtractor()
    rules = RuleEngine()
    engine = InferenceEngine(embedder, sem, extractor, rules)

    print("Pronto. Digite descrições/sintomas (Enter vazio para sair).\n")
    while True:
        q = input("Descrição> ").strip()
        if not q:
            print("Saindo.")
            break
        out = engine.infer(q, top_k=4)
        print("\nFatos extraídos:", out["facts"])
        print("\nEvidência (top):")
        for e in out["evidence"]:
            print(f" - {e['doc']['id']} ({e['doc']['title']}) score_sem={e['score']:.3f}")
        print("\nConclusões possíveis:")
        if out["conclusions"]:
            for c in out["conclusions"]:
                print(f" * {c['diagnostico']} - combined={c['combined_score']:.3f} (symptom_overlap={c['symptom_overlap']:.2f})")
                print(f"   Tratamento (sugestão): {c.get('tratamento')}")
        else:
            print(" Nenhum diagnóstico confiante encontrado — revise a descrição ou verifique os documentos relacionados.")
        print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    main()
