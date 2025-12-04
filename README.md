<h1>Sistema Especialista com Busca Semântica e Inferência</h1>

Este projeto implementa um Sistema Especialista modularizado em Python, utilizando:

Base de conhecimento em JSON

Embeddings para correlação semântica

Motor de inferência baseado em regras

Extração automática de sintomas

Busca semântica para encontrar diagnósticos mais prováveis

O objetivo é demonstrar um exemplo moderno de IA simbólica + IA conexionista, ideal para trabalhos acadêmicos ou protótipos de diagnóstico inteligente.

---

<h1> Estrutura do Prjeto: </h1>
sistema_especialista/

│
├── data/
│   └── knowledge.json                  # Base de conhecimento
│
├── embeddings/
│   └── embedder.py                     # Geração de embeddings e carregamento da base
│
├── inference/
│   ├── fact_extractor.py               # Extrai fatos (sintomas) do texto do usuário
│   ├── rule_engine.py                  # Motor de regras
│   └── inference.py                    # Ciclo completo de inferência
│
├── semantic/
│   └── search.py                       # Busca semântica entre consulta e os diagnósticos
│
└── main.py                             # Script principal (CLI do sistema especialista)

---

📚 Base de Conhecimento (JSON)

A base utilizada contém diversos diagnósticos pediátricos, cada um com:
- sintomas
- descrição
- faixa etária
- tratamentos recomendados

---

⚙️ Funcionamento Geral

O sistema segue quatro etapas principais:

Carregamento da Base e Geração de Embeddings

O arquivo JSON é carregado.

Para cada diagnóstico:

seus sintomas e descrição são combinados

um vetor de embedding é gerado

Isso permite comparar textos de forma semântica.

Entrada do Usuário

Exemplo:
"meu filho está vomitando depois de comer e está irritado"

Extração dos Sintomas

O módulo fact_extractor.py procura termos relevantes e estrutura os fatos extraídos.

Busca Semântica + Motor de Regras

O sistema combina:
- Similaridade de embeddings (para achar diagnósticos similares)
- Motor de regras (para validar sintomas característicos)
- Ponderação final para retornar diagnósticos mais prováveis

Retorno

O usuário recebe:
- diagnóstico mais provável
- descrição
- faixa etária típica
- tratamento sugerido

---

Como Executar

1. Instalar dependências

> pip install -r requirements.txt

2. Rodar o sistema

> python main.py

3. Interagir
O sistema perguntará uma descrição:

Digite descrições/sintomas:
> "meu bebê está chorando muito e sente dor na barriga à noite"

Saída Esperada:
"Diagnóstico sugerido: cólica
Probabilidade semântica: 0.89
Faixa etária: bebês e crianças pequenas
Tratamento: massagem abdominal, analgésicos leves..."

---

<h1> Tecnologias Utilizadas</h1>
Python 3.9+
NumPy para cálculos vetoriais
SentenceTransformers (ou similar) para embeddings
JSON como base de conhecimento
Inferência simbólica baseada em regras

---

<h1> Objetivo Acadêmico</h1>

Este projeto demonstra:
conhecimento simbólico (regras)
inferência automatizada
processamento de linguagem natural
embeddings e similaridade semântica
modularização limpa
arquitetura de sistemas especialistas modernos
Ótimo para disciplinas como:
Inteligência Artificial
Sistemas Especialistas
Sistemas Baseados em Conhecimento
PLN e Representação do Conhecimento
