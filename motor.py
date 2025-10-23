import json
import re

class Motor:
    def __init__(self, caminho_dados):
        with open(caminho_dados, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        
        # Converte listas em sets e normaliza para lowercase
        self.base_conhecimento = {}
        for doenca, sintomas_lista in dados.items():
            self.base_conhecimento[doenca] = {s.lower() for s in sintomas_lista}
        
        # Inicializa o modelo spaCy
        try:
            import spacy
            self.nlp = spacy.load("pt_core_news_md")  # Modelo médio português
        except:
            # Fallback: tenta carregar modelo pequeno
            try:
                import spacy
                self.nlp = spacy.load("pt_core_news_sm")
            except:
                print("AVISO: spaCy não disponível. Similaridade desabilitada.")
                self.nlp = None

    def reconhecer_similar(self, palavra1, palavra2, limiar=0.75):
        ## Compara duas palavras e retorna True se a similaridade for >= limiar
        if self.nlp is None:
            return False
        
        doc1 = self.nlp(palavra1.replace("_", " "))
        doc2 = self.nlp(palavra2.replace("_", " "))
        
        similaridade = doc1.similarity(doc2)
        return similaridade >= limiar

    def extrair_sintoma(self, texto):
        texto = texto.lower()
        sintomas = set()

        ## Obtém todos os sintomas possíveis
        sintomas_all = set()
        for sintomas_doenca in self.base_conhecimento.values():
            sintomas_all = sintomas_all.union(sintomas_doenca)

        ## Busca exata por sintomas
        for sintoma in sintomas_all:
            padrao = sintoma.replace("_", " ")
            if re.search(rf"\b{padrao}\b", texto):
                sintomas.add(sintoma)

        ## Busca por similaridade semântica (se spaCy disponível)
        if self.nlp is not None:
            texto_doc = self.nlp(texto)
            
            for sintoma in sintomas_all:
                if sintoma in sintomas:
                    continue  # Já encontrado na busca exata
                
                sintoma_formatado = sintoma.replace("_", " ")
                sintoma_doc = self.nlp(sintoma_formatado)
                
                # Compara com cada token do texto
                for token in texto_doc:
                    if token.has_vector and sintoma_doc.has_vector:
                        similaridade = token.similarity(sintoma_doc)
                        if similaridade >= 0.75:
                            sintomas.add(sintoma)
                            break
                
                # Compara também frases inteiras
                if sintoma not in sintomas:
                    for sent in texto_doc.sents:
                        if sent.has_vector and sintoma_doc.has_vector:
                            similaridade = sent.similarity(sintoma_doc)
                            if similaridade >= 0.70:
                                sintomas.add(sintoma)
                                break

        return sintomas

    def backward(self, input_sintoma):
        possiveis_diag = []

        for diagnostico, sintomas_necessarios in self.base_conhecimento.items():
            intersec = input_sintoma.intersection(sintomas_necessarios)
            if intersec:
                igualdade = len(intersec) / len(sintomas_necessarios)
                possiveis_diag.append((diagnostico, igualdade))

        possiveis_diag.sort(key=lambda x: x[1], reverse=True)
        return possiveis_diag