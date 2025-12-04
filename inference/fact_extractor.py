import re

# Padrões simples baseados na base de dados fornecida
SINTOMAS_KNOWN = [
    "choro intenso","dor abdominal","noite","chora",
    "coriza","dificuldade respirar","febre baixa",
    "febre alta","mal estar",
    "vomito","pós alimentação","irritação",
    "erupção na pele"
]

class FactExtractor:
    def extract(self, text):
        t = text.lower()
        facts = {}
        # extrair sintomas que aparecem na lista
        found = []
        for s in SINTOMAS_KNOWN:
            if s in t:
                found.append(s)
        if found:
            facts["sintomas"] = found

        # detectar palavras que falam de ingestão / tempo / idade simples
        if re.search(r"\b(beb[eé]s|bebes|crian(ca|ças)|criança|bebê)\b", t):
            facts["idade"] = "criança/bebê"
        if re.search(r"\b(ontem|hoje|amanh[ãa]|noite|manhã|tarde)\b", t):
            facts["tempo_mencao"] = re.search(r"\b(ontem|hoje|amanh[ãa]|noite|manhã|tarde)\b", t).group(0)
        # flag para dificuldade respiratória textual
        if "dificuldade" in t and "respir" in t:
            facts.setdefault("sintomas", []).append("dificuldade respirar")
        return facts
