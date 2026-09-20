# Applied AI Projects

Repos para projetos e provas de conceito envolvendo Inteligência Artificial, Machine Learning e Generative AI.

O objetivo é explorar diferentes abordagens, arquiteturas e técnicas através de implementações práticas e protótipos.

## Projects

### ajudAI

POC de um assistente financeiro com múltiplos agentes.

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