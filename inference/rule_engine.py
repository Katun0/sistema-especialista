def symptom_match_score(fact_sintomas, diag_sintomas):
    """
    Score simples baseado em overlap entre sintomas textuais.
    Retorna proporção de sintomas do diagnóstico cobertos pelos fatos.
    """
    if not fact_sintomas:
        return 0.0
    set_fact = set(fact_sintomas)
    set_diag = set(diag_sintomas)
    inter = set_diag.intersection(set_fact)
    # score: |inter| / |diag_sintomas|
    return len(inter) / max(1, len(set_diag))

class RuleEngine:
    def evaluate(self, facts, evidence):
        """
        facts: dict com 'sintomas' etc.
        evidence: lista de {"doc":..., "score":...} já ordenada por similaridade
        Gera conclusões combinando:
         - overlap de sintomas (symptom_match_score)
         - evidência semântica (score)
        """
        conclusions = []
        fact_sintomas = facts.get("sintomas", [])

        for ev in evidence:
            diag = ev["doc"]
            diag_id = diag["id"]
            diag_sintomas = []
            # recuperar sintomas do texto meta (o embedder não guarda raw sintomas), então vamos tentar
            # extrair da string "text" usando split após 'Sintomas:'
            txt = diag.get("text","")
            if "Sintomas:" in txt:
                diag_sintomas = [s.strip() for s in txt.split("Sintomas:")[1].split(".") if s.strip()]
            # fallback: checar meta (não temos raw list), assim usamos diag_sintomas
            symptom_score = symptom_match_score(fact_sintomas, diag_sintomas)
            # combinar: weight_semantic * score_semantic + weight_symptom * symptom_score
            weight_sem = 0.6
            weight_sym = 0.4
            combined = weight_sem * ev["score"] + weight_sym * symptom_score
            # thresholds ajustáveis: 0.45 para teste, 0.7 para mais precisão
            if combined >= 0.45:
                conclusions.append({
                    "diagnostico": diag_id,
                    "titulo": diag.get("title"),
                    "descricao": diag.get("text"),
                    "evidence_score": ev["score"],
                    "symptom_overlap": symptom_score,
                    "combined_score": combined,
                    "tratamento": diag.get("meta", {}).get("tratamento", [])
                })
        # ordenar por combined_score desc
        conclusions = sorted(conclusions, key=lambda x: x["combined_score"], reverse=True)
        return conclusions
