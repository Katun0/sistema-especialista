class Diagnostico:
    def __init__(self, base_conhecimento):
        self.base_conhecimento = base_conhecimento

    def diagnosticar(self, dados):
        possiveis_diag = []

        for diagnostico, regras in self.base_conhecimento.items():
            intersecao = regras.intersection(dados)
            if intersecao:
                porcentagem = len(intersecao) / len(regras)
                possiveis_diag.append((diagnostico, porcentagem))

        possiveis_diag.sort(key=lambda x: x[1], reverse=True)

        return [diag for diag, score in possiveis_diag if score >= 0.5]
