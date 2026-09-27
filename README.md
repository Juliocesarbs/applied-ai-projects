# Applied AI Projects

Repositório para projetos e provas de conceito envolvendo Inteligência Artificial, Machine Learning, Data Science e Generative AI.

O objetivo é explorar diferentes abordagens, arquiteturas e técnicas por meio de implementações práticas, experimentos e análises reproduzíveis.

## Projects

### ajudAI

POC de um assistente financeiro baseado em múltiplos agentes especializados.

O projeto explora:

- LangGraph para orquestração
- Qwen3 4B executado localmente com Ollama
- agentes especializados
- tools com dados sintéticos
- comparação entre roteamento por regras e LLM
- avaliação de qualidade e latência

**Resultado do experimento de roteamento:**

| Abordagem | Accuracy | Macro F1 |
|---|---:|---:|
| Rules Router | 72,5% | 73,5% |
| Qwen3 4B | 97,5% | 97,5% |

Os resultados foram obtidos em um conjunto de teste sintético com 40 mensagens.

[Ver projeto ajudAI](./ajudAI)

---

### Eleições 2026 — Análise de Dados

Projeto de análise de dados das candidaturas à Presidência da República nas Eleições 2026 utilizando dados oficiais disponibilizados pelo Tribunal Superior Eleitoral (TSE).

O projeto explora:

- ingestão e processamento de dados públicos
- construção e validação de datasets analíticos
- análise exploratória de dados
- análise de bens declarados ao TSE
- tratamento de candidaturas deferidas, pendentes, indeferidas e substituídas
- visualização e comunicação de resultados
- preparação da base para futuras análises com NLP e LLMs

A análise principal considera candidaturas com situação de julgamento **DEFERIDO** no snapshot dos dados utilizado.

Próximas etapas incluem análise de propostas de governo utilizando técnicas de NLP, embeddings, clustering e LLMs.

[Ver projeto Eleições 2026](./eleicoes-2026-data-analysis)

## Repository Structure

```text
applied-ai-projects/
├── ajudAI/
└── eleicoes-2026-data-analysis/
```

Cada projeto possui documentação, dependências e estrutura próprias.